# XML 데이터 변환 방법
최초 작성일 2026-10-24
1차 수정일: 2026-11-17/코드 기준 동기화

- 모듈 책임: XML 파싱·필드 선별·자료형 변환·DataFrame 생성은 `src/transform.py`,
- 결측 및 만기별 제공 정책 처리는 `src/missing_data.py`(정책 상세는 `../planning/initial_data_policy.md`)

## 1. 태그 구조
- feed
  - title
  - id
  - updated
  - link
  - entry(반복)
    - id
    - title
    - updated
    - author
      - name
    - link
    - category
    - content
      - properties
        - Id
        - NEW_DATE
        - BC_1MONTH
        - BC_1_5MONTH
        - BC_2MONTH
        - BC_3MONTH
        - BC_4MONTH
        - BC_6MONTH
        - BC_1YEAR
        - BC_2YEAR
        - BC_3YEAR
        - BC_5YEAR
        - BC_7YEAR
        - BC_10YEAR
        - BC_20YEAR
        - BC_30YEAR
        - BC_30YEARDISPLAY

## 2. 추출 대상
- entry
  - properties
    - NEW_DATE
    - `^BC_`(BC_30YEARDISPLAY는 제외)

## 3. 컬럼명 및 자료형 
   record 단계에서 date는 `datetime.date`, 금리는 `float | None`이며,
- DataFrame 변환 후 date는 `datetime64[ns]`, 금리는 `float64`(결측은 NaN)이다.

- date: date, Not Null
- yield_1m: FLOAT
- yield_1_5m: FLOAT
- yield_2m: FLOAT
- yield_3m: FLOAT
- yield_4m: FLOAT
- yield_6m: FLOAT
- yield_1y: FLOAT
- yield_2y: FLOAT
- yield_3y: FLOAT
- yield_5y: FLOAT
- yield_7y: FLOAT
- yield_10y: FLOAT
- yield_20y: FLOAT
- yield_30y: FLOAT

## 4. 데이터 정합성 검증

### 4.1. 결측 데이터 분류
- (정상) 미국 국채 금리가 공시되지 않는 주말 및 공휴일: 해당 날짜의 관측 데이터가 없음
- (정상) 재무부에서 명시한 금리 시계열의 제공 시작일 이전 또는 제공되지 않는 기간: 해당 만기의 수익률 값이 없음
- (비정상) 위의 정상 결측 사유로 설명되지 않는 관측 데이터 또는 필수 필드의 누락
- (비정상) 날짜 중복, 날짜 형식 오류, 수익률의 숫자 변환 실패 등 데이터 정합성 위반

### 4.2. 결측 데이터 처리
- (정상) 주말 및 공휴일: 관측일 사이에 빠진 모든 달력 날짜에 대해 직전 관측 레코드의 값을 복제한 레코드를 생성한다(`handle_missing_data`).
- (정상) XML에 없는 만기 필드: `None`으로 채운다(`_fill_missing_maturities`).
- (정상) 특정 만기의 공시 데이터가 존재하지 않는 기간: 값이 있더라도 해당 수익률을 `None`으로 처리한다(`_apply_treasury_note_policy`).
- (비정상) 날짜 형식 오류: `ValueError`를 발생시키고 파이프라인을 중단한다(`_convert_record_types`).
- (비정상) 수익률 숫자 변환 실패: `ValueError`를 발생시키고 파이프라인을 중단한다(`_convert_record_types`). 빈 문자열/공백은 `None`으로 처리한다.
- (비정상) 중복 날짜 또는 역순 날짜: 값 비교 없이 `ValueError`를 발생시키고 파이프라인을 중단한다(`_has_market_holiday_gap`).
- 재요청(재시도) 로직은 없다.

## 5. 검증 결과에 따른 데이터 처리

- 모든 검증을 통과한 레코드는 DataFrame 변환 단계로 전달한다.
- 공시 자료에서 정상적으로 제공되지 않는 수익률은 `None`으로 유지한다.
- 검증 오류(`ValueError`, `ET.ParseError`)가 발생하면 파이프라인이 중단되어 기존 CSV를 덮어쓰지 않는다.
- CSV 저장 직전 Load 단계(`load_csv._validate`)에서 컬럼 구성, date 결측·중복·정렬을 한 번 더 검증한다.

## 6. DataFrame 생성

- XML의 각 `entry`에서 `content/properties`를 추출하여 하나의 레코드로 변환한다.
- `NEW_DATE`를 `date` 컬럼으로, `BC_`로 시작하는 대상 태그를 해당 만기의 `yield_*` 컬럼으로 매핑한다.
- `BC_30YEARDISPLAY` 및 분석 대상이 아닌 필드는 제외한다.
- 날짜는 날짜 자료형으로 변환하고, 수익률은 숫자형(`float`)으로 변환한다.
- 정상적으로 값이 제공되지 않는 수익률은 결측값으로 유지한다.
- 레코드를 date 기준 오름차순으로 정렬한 뒤 하나의 DataFrame으로 결합한다(`create_yield_curve_dataframe`).
- date는 `datetime64[ns]`, 금리는 `float64`로 변환한다.
- 최종 컬럼 순서는 `date`를 첫 번째로 배치하고, 나머지는 3절에서 정의한 컬럼 순서를 따른다.
- date 결측·중복·정렬 및 컬럼 구성 검증은 Load 단계(`load_csv._validate`)에서 수행한다.