# 초기/증분 적재 파이프라인 세부 흐름(pipeline.py)

1차 수정일: 2026-11-16/배포 전략 수정
2차 수정일: 2026-11-17/코드 기준 동기화

> TimeZone은 미국 동부 시간(New York)을 기준으로 한다.
> 업데이트 시간 정책은 [Policy Issues/Treasury Yield Curve Methodology](https://home.treasury.gov/policy-issues/financing-the-government/interest-rate-statistics/treasury-yield-curve-methodology)에서 확인할 수 있다.

## 1. 초기 데이터 적재 파이프라인(run_initial_pipeline)
1. 1990-2023년의 archive 데이터 수집: fetch_yield_curve_archive_xml
2. archive 데이터를 파싱후 record(`list[dict]`)으로 변환: parse_yield_curve_records
3. 2024년부터 현재 연도까지의 연도별 데이터 수집: fetch_yield_curve_xml
4. 연도별 데이터를 record(`list[dict]`)으로 변환: parse_yield_curve_records
5. archive와 연도별 records를 결합
6. 결측 데이터 처리 및 데이터 정책 적용: handle_missing_data
7. 데이터 처리를 마친 records를 DataFrame으로 변환: create_yield_curve_dataframe
8. Yield Curve, Yield Spread CSV 저장: initialize_csv

## 2. 증분 데이터 적재 파이프라인(run_incremental_pipeline)
1. 현재 연월 데이터 수집: fetch_yield_curve_xml
2. 수집한 데이터를 파싱후 record(`list[dict]`)로 변환: parse_yield_curve_records
   - 수집한 record가 없으면 이후 단계를 실행하지 않고 종료
3. 결측 데이터 처리 및 데이터 정책 적용: handle_missing_data
4. 데이터 처리를 마친 records를 DataFrame으로 변환: create_yield_curve_dataframe
5. Yield Curve, Yield Spread CSV 업데이트(Upsert): update_csv

## 3. 데이터 시각화 파이프라인(generate_visualizations)
1. Yield Curve, Yield Spread CSV를 DataFrame으로 읽어옴: pandas의 read_csv
2. Plotly Figure 생성 및 HTML 문자열 변환: create_curve_chart_html, create_spread_chart_html

## 4. GitHub Actions Workflow 및 GitHub Pages 배포
- workflow별 조건, 권한 등 상세 내용은 `deploy_strategy.md` 참고

### Workflow 실행 정책
- Workflow 파일: `.github/workflows/collect.yaml`(수집), `.github/workflows/deploy.yaml`(배포)
- collect 실행 주기: 매일 1회, 미국 동부 시간(New York) 20:00
- 시간대: America/New_York
- 수동 실행 지원: 두 workflow 모두 workflow_dispatch
- 초기 데이터:
  - 최초 1회 `run_initial_pipeline()`을 별도로 실행하여 전체 CSV를 생성
  - 초기 적재 완료 후 증분 적재 Workflow 활성화

### Workflow 실행 순서
#### collect.yaml
1. GitHub 저장소 Checkout
2. Python 실행 환경 설정
3. 프로젝트 의존성 설치
4. 증분 데이터 적재 파이프라인 실행: run_incremental_pipeline()
5. CSV 변경 사항 확인
6. 변경된 CSV 파일을 GitHub 저장소에 Commit 및 Push
7. CSV 변경 시 deploy.yaml 실행

#### deploy.yaml
1. GitHub 저장소 Checkout
2. Python 실행 환경 설정
3. 프로젝트 의존성 설치
4. 시각화 파이프라인 실행 및 HTML 검증·저장: generate_visualizations()
5. GitHub Pages Deploy

### 배포 조건
- 데이터 수집 및 정제 과정에서 오류 발생 시 이후 작업 중단(커밋 및 deploy 실행 안 함)
- CSV 변경 사항이 있는 경우에만 collect에서 deploy 실행
  - collect를 수동 실행해도 CSV 변경이 없으면 배포하지 않음
- deploy.yaml을 직접 수동 실행하면 CSV 변경 여부와 관계없이 배포
- HTML 검증에 실패하면 배포 중단
- CSV 변경 사항은 GitHub 저장소에 Commit하여 다음 실행에서도 유지
