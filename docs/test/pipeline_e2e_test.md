# 파이프라인 E2E 테스트 전략
최초 작성일: 2026-11-15
1차 수정일: 2026-11-17/코드 기준 동기화

## 1. 검증 대상 (`pipeline.py`)

- `run_initial_pipeline`: Treasury API를 호출하여 XML 데이터를 수집하고 CSV에 초기 적재
- `run_incremental_pipeline`: Treasury API를 호출하여 XML 데이터를 수집하고 CSV에 증분 적재

> `generate_visualizations`는 E2E 대상이 아니다. HTML 유효성은 `deploy.yaml`의 검증 step과 `tests/unit/visualize/`에서 확인한다.

## 2. 문제 상황: 증분 데이터가 없는 경우

증분 적재 파이프라인의 E2E 테스트를 수행하려면 초기 데이터가 먼저 적재되어 있어야 한다.

그러나 Treasury에서 새로운 금리 데이터를 발표하지 않았다면, API를 호출해도 기존에 수집한 데이터와 동일한 날짜까지만 가져올 수 있다.

따라서 다음과 같은 문제가 발생한다.

- 신규 데이터를 발표하지 않은 시점에 테스트를 실행하면 초기 데이터와 증분 데이터의 최종 날짜가 동일할 수 있음
- 증분 데이터가 없으면 신규 데이터 추가 및 기존 데이터 갱신을 검증할 수 없음
- 결과적으로 증분 데이터 적재 로직의 정상 동작 여부를 충분히 검증할 수 없음

## 3. 테스트 방식별 Trade-off 비교

### Fixture XML 기반 테스트
- 고정된 XML 데이터를 사용하므로 테스트 결과를 재현할 수 있음
- 기존 날짜의 금리 변경 및 신규 날짜 추가 상황을 의도적으로 구성할 수 있음
- 실제 Treasury API 요청 및 응답 과정은 검증하지 못함

### External API 기반 테스트
- 실제 API 요청부터 XML 수집, 데이터 변환, CSV 적재까지 전체 흐름을 검증할 수 있음
- 실제 데이터 발표 시점과 네트워크 상태에 따라 테스트 결과가 달라질 수 있음
- 신규 데이터가 없는 경우 증분 적재 동작을 검증하기 어려움

## 4. 테스트 전략 및 결정

### 초기 파이프라인의 책임 범위
- 과거부터 현재 연월 데이터 수집
- XML 데이터를 Python 자료구조로 파싱
- 결측 데이터 및 데이터 정책 처리
- DataFrame 생성
- 초기 CSV 적재

### 증분 파이프라인의 책임 범위
- 현재 연월 데이터 수집
- XML 데이터를 Python 자료구조로 파싱
- 결측 데이터 및 데이터 정책 처리
- DataFrame 생성
- CSV 증분 적재

### 방식별 검증 범위

| 검증 항목                       | Fixture XML | External API |
| --------------------------- | ----------- | ------------ |
| 실제 Treasury API 요청 및 XML 수집 | ✕           | ○            |
| XML 데이터 파싱                  | ○           | ○            |
| 결측 데이터 및 데이터 정책 처리          | ○           | ○            |
| DataFrame 생성                | ○           | ○            |
| CSV 증분 적재                   | ○           | ○            |
| 기존 날짜 값 갱신                  | ○           | ✕            |
| 완전히 새로운 날짜 추가               | ○           | ✕            |
### 최종 결정
- E2E 테스트는 External API 기반으로 수행한다
- 초기 데이터 적재 후, 현재 연월에 해당하는 레코드를 CSV에서 의도적으로 제거하고 증분 파이프라인을 실행하여, API에서 해당 날짜의 데이터가 다시 수집되어 CSV에 정상 추가되는지 검증한다. 
- 삭제 대상 날짜는 고정하지 않고 CSV에 존재하는 현재 연월 내 날짜 중에서 동적으로 선택한다. (주말·공휴일, 월초 데이터 미발표 상황 대응) 
- 기존 날짜 값 갱신, 신규 날짜 추가 등 E2E로 재현할 수 없는 시나리오는 Fixture XML 대신 DataFrame 기반 단위 테스트에서 보완한다. 두 방식은 대체 관계가 아니라 검증 범위가 다른 보완 관계이다.
  - `tests/unit/load_csv/test_merge.py`: 값 변경 감지, 신규 날짜 추가
  - `tests/unit/load_csv/test_update_csv.py`: 기존 날짜 덮어쓰기, 신규 날짜 병합·정렬, 검증 실패 시 저장 안 함


## 5. 테스트 시나리오

### 5.1 초기 적재 E2E 테스트
> `tests/e2e/test_run_initial_pipeline_e2e.py`

**목적**: `run_initial_pipeline`이 실제 API 데이터로 끝까지 정상 동작하는지 검증한다.

**사전 조건**
- 테스트 전용 임시 경로(`tmp_path`)를 CSV 출력 경로로 사용한다(`load_csv`, `pipeline`의 `CURVE_PATH`, `SPREAD_PATH`를 monkeypatch).

**절차**
1. `run_initial_pipeline` 실행

**검증 항목**
- CSV 파일 2종(`curve_csv`, `spread_csv`)이 생성되고 크기가 0보다 크며, 데이터 행이 비어 있지 않다.
- Curve CSV 컬럼이 `["date", *YIELD_DTYPES.keys()]`와 정확히 일치하고, Spread CSV 컬럼이 `["date", "spread_10y_2y", "spread_10y_3m"]`와 정확히 일치한다.
- `date` 컬럼이 datetime 타입이며 결측이 없고, 날짜가 중복되지 않으며 오름차순으로 정렬되어 있다.
- 숫자 컬럼(Curve의 각 금리, Spread의 두 스프레드)이 numeric 타입이다.
- Curve와 Spread의 `date` 컬럼이 완전히 일치한다.
- Spread 계산 결과가 `yield_10y - yield_2y`, `yield_10y - yield_3m`과 허용 오차 내에서 일치한다.
- 만기별 제공 기간 정책이 적용되어 있다. 다음 날짜의 해당 만기 값이 결측이다.
  - `yield_1_5m`: 2025-02-17, `yield_2m`: 2018-10-15, `yield_4m`: 2022-10-18
  - `yield_20y`: 1992-01-02, `yield_30y`: 2004-01-02
- 달력 공백 날짜가 직전 관측값으로 채워져 있다. (2024-01-06의 값이 2024-01-05와 동일)

### 5.2 증분 적재 E2E 테스트
> `tests/e2e/test_incremental_pipeline.py`

**목적**: 신규 발표가 없는 시점에도 증분 적재의 "누락 데이터 수집 및 CSV 병합" 동작을 검증한다.

**사전 조건**
- 5.1과 동일하게 임시 경로를 사용하며, 초기 적재가 완료된 CSV가 존재한다.

**절차**
1. `run_initial_pipeline` 실행 후 CSV 전체를 **스냅샷**으로 보관한다.
2. CSV에 존재하는 **현재 연월 내 날짜** 중 삭제 대상을 선택한다.
   - 현재 연월 내 가장 최근 날짜
   - 현재 연월에 해당하는 레코드가 없으면(월초 등) 테스트를 `skip` 처리한다.
3. 선택한 날짜의 레코드를 CSV에서 제거한다.
4. `run_incremental_pipeline` 실행
5. 결과 CSV를 스냅샷과 비교한다.

**검증 항목**
- 삭제한 날짜의 레코드가 Curve CSV와 Spread CSV 양쪽에 모두 복구되었다.
- 복구된 Curve 레코드의 각 금리 값(`YIELD_DTYPES`의 모든 컬럼)이 스냅샷과 일치한다. 비교는 `pd.testing.assert_frame_equal`에 `check_exact=False`, `rtol=1e-9`, `atol=1e-9`를 적용한다.
- 복구된 Spread 레코드 값이 스냅샷과 일치하며, 동시에 `yield_10y - yield_2y`, `yield_10y - yield_3m` 계산 결과와도 허용 오차 내에서 일치한다.
- 삭제하지 않은 나머지 레코드가 증분 실행 전후로 변하지 않았다.
- 증분 실행 후 Curve와 Spread 각각의 행 수가 초기 적재 직후와 같다.
- Curve와 Spread 각각에서 `date` 컬럼이 중복 없이 유일하고 오름차순으로 정렬되어 있으며, 두 CSV의 `date` 컬럼이 완전히 일치한다.
- 컬럼 스키마가 초기 적재 테스트와 동일하다. (Curve: `["date", *YIELD_DTYPES.keys()]`, Spread: `["date", "spread_10y_2y", "spread_10y_3m"]`)
- 증분 파이프라인을 한 번 더 실행해도 Curve와 Spread의 행 수 및 값이 변하지 않는다. (멱등성)

## 6. 실행 정책

- E2E 및 외부 API 테스트는 기본 테스트 실행에서 제외하고, 마커로 명시적으로 실행한다.
  - `pyproject.toml`: `addopts = "-m 'not integration and not e2e'"`, 실행 시 `pytest -m e2e`
- 모든 E2E 테스트는 임시 경로에서 실행하여 운영 CSV에 영향을 주지 않는다.
- 단위, 통합 테스트와 별개로 매주 수요일 09:00 KST(00:00 UTC)에 E2E 테스트만 실시한다(`.github/workflows/e2e.yaml`).