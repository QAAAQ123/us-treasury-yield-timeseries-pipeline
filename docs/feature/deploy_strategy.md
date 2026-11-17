# GitHub Actions을 통한 HTML 배포 전략
최초 작성일: 2026-11-16

## 1. workflows 구성
- GitHub Actions의 artifact를 사용하지 않음
- Collect와 Deploy의 책임을 분리하여 독립적으로 운영
### 1. CSV 데이터 수집(collect.yaml)
- 책임: 데이터를 받아와 CSV 데이터를 data/에 저장
- 조건
  - main 브랜치에서만 실행
  - America/New_York 시간으로 20시에 실행
  - 매일 실행
  - 수동 실행 가능
  - jobs.collect.if를 main 브랜치 조건으로 작성(main이 아닌 다른 브랜치에서 수동 실행하는 실수 방지)
- 순서
  1. pipeline 모듈의 run_incremental_pipeline 실행
  2. CSV 변화 확인
  3. CSV 변화가 있으면 자동 커밋
### 2. GitHub Pages에 HTML 파일 배포(deploy.yaml)
- 책임: 저장된 CSV를 기반으로 Plotly HTML을 생성하고 GitHub Pages에 배포
- 조건
  - main 브랜치에서만 실행
  - collect workflow의 CSV 변경이 있고 정상 종료할 때만 실행
  - 수동 실행 가능
  - jobs.deploy.if를 main 브랜치 조건으로 작성(main이 아닌 다른 브랜치에서 수동 실행하는 실수 방지)
- 순서
  1. pipeline 모듈의 generate_visualizations 실행(html 객체 반환)
  2. 반환된 HTML 객체의 유효성 확인
  3. 유효한 HTML을 GitHub Pages에 배포