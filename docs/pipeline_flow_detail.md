# 초기/증분 적재 파이프라인 세부 흐름(pipeline.py)

> TimeZone은 미국 동부 시간(New York)을 기준으로 한다.
> 업데이트 시간 정책은 [Policy Issues/Treasury Yield Curve Methodology](https://home.treasury.gov/policy-issues/financing-the-government/interest-rate-statistics/treasury-yield-curve-methodology)에서 확인할 수 있다.

## 1. 초기 데이터 적재 파이프라인(run_initial_pipeline)
1. 1990-2023년의 archive 데이터 수집: fetch_yield_curve_archive_xml
2. archive 데이터를 파싱후 record(`list[dict]`)으로 변환: parse_yield_curve_records
3. 2024년부터 현재 연도까지의 연도별 데이터 수집: fetch_yield_curve_xml
4. 연도별 데이터를 record(`list[dict]`)으로 변환: parse_yield_curve_records
5. archive와 연도별 records를 합침: Python list의 extend 사용
6. 결측 데이터 처리 및 데이터 정책 적용: handle_missing_data
7. 데이터 처리를 마친 records를 DataFrame으로 변환: create_yield_curve_dataframe
8. Yield Curve, Yield Spread CSV 저장: initialize_csv

## 2. 증분 데이터 적재 파이프라인(run_incremental_pipeline)
1. 현재 연월 데이터 수집: fetch_yield_curve_xml
2. 수집한 데이터를 파싱후 record(`list[dict]`)로 변환: parse_yield_curve_records
3. 결측 데이터 처리 및 데이터 정책 적용: handle_missing_data
4. 데이터 처리를 마친 records를 DataFrame으로 변환: create_yield_curve_dataframe
5. Yield Curve, Yield Spread CSV 업데이트(Upsert): update_csv

## 3. 데이터 시각화 파이프라인(generate_visualizations)
1. Yield Curve, Yield Spread CSV를 DataFrame으로 읽어옴: pandas의 read_csv
2. Figure로 차트 생성: create_curve_chart, create_spread_chart
3. Figure를 HTML로 저장: save_to_html

## 4. GitHub Actions Workflow 및 GitHub Pages 배포

### Workflow 실행 정책
- 실행 주기: 매일 1회
- 실행 시간: 미국 동부 시간(New York) 20:00
- 시간대: America/New_York (EST / EDT 자동 적용)
- 수동 실행 지원: workflow_dispatch
- Workflow 파일: .github/workflows/deploy-pages.yml
- 초기 데이터:
  - 최초 1회 `run_initial_pipeline()`을 별도로 실행하여 전체 CSV를 생성
  - 초기 적재 완료 후 증분 적재 Workflow 활성화

### Workflow 실행 순서
1. GitHub 저장소 Checkout
2. Python 실행 환경 설정
3. 프로젝트 의존성 설치
4. 증분 데이터 적재 파이프라인 실행: run_incremental_pipeline()
5. 시각화 파이프라인 실행: generate_visualizations()
6.  CSV 변경 사항 확인
7.  변경된 CSV 파일을 GitHub 저장소에 Commit 및 Push
8.  GitHub Pages 배포용 Artifact 생성 및 업로드
    - html/ 디렉토리 업로드
9.  GitHub Pages Deploy

### 배포 조건
- 데이터 수집 및 정제 과정에서 오류 발생 시 이후 작업 중단
- 데이터 적재 및 시각화가 모두 성공한 경우에만 배포 진행
- CSV 변경 사항이 있는 경우에만 정기 배포 진행
- 수동 실행 시 CSV 변경 여부와 관계없이 배포 허용
- CSV 변경 사항은 GitHub 저장소에 Commit하여 다음 실행에서도 유지

### GitHub Actions 권한
- contents: write: CSV 변경 사항 Commit 및 Push
- pages: write: GitHub Pages 배포
- id-token: write: GitHub Pages 배포용 OIDC 인증
