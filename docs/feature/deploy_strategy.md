# GitHub Actions을 통한 HTML 배포 전략
최초 작성일: 2026-11-16
1차 수정일: 2026-11-17/코드 기준 동기화

## 1. workflows 구성
- workflow 간 artifact 전달은 사용하지 않음(Pages 배포용 `actions/upload-pages-artifact`만 사용)
- Collect와 Deploy의 책임을 분리하여 독립적으로 운영
- 공통: `ubuntu-latest`, Python 3.11, `timeout-minutes: 30`, `pip install -e .`
### 1. CSV 데이터 수집(collect.yaml)
- 책임: 데이터를 받아와 CSV 데이터를 data/에 저장
- 조건
  - main 브랜치에서만 실행
  - America/New_York 시간으로 20시에 실행(`cron: "0 20 * * *"`, `timezone: "America/New_York"`)
  - 매일 실행
  - 수동 실행 가능(`workflow_dispatch`)
  - jobs.collect.if를 main 브랜치 조건으로 작성(main이 아닌 다른 브랜치에서 수동 실행하는 실수 방지)
  - 권한: `contents: write`(CSV 커밋), `actions: write`(deploy workflow 실행)
- 순서
  1. pipeline 모듈의 run_incremental_pipeline 실행
  2. CSV 변화 확인: `git status --porcelain -- data/`
  3. CSV 변화가 있으면 자동 커밋 및 push(커밋 메시지: `data: update Treasury yield data`)
  4. CSV 변화가 있으면 `gh workflow run deploy.yaml --ref main`으로 deploy workflow 실행
     - GITHUB_TOKEN으로 push한 커밋은 다른 workflow를 트리거하지 않으므로 직접 실행한다
### 2. GitHub Pages에 HTML 파일 배포(deploy.yaml)
- 책임: 저장된 CSV를 기반으로 Plotly HTML을 생성하고 GitHub Pages에 배포
- 조건
  - main 브랜치에서만 실행
  - 트리거는 `workflow_dispatch`만 존재
    - collect workflow가 CSV 변경을 커밋한 경우 collect에서 실행
    - 수동 실행 가능(CSV 변경 여부와 무관)
  - jobs.deploy.if를 main 브랜치 조건으로 작성(main이 아닌 다른 브랜치에서 수동 실행하는 실수 방지)
  - 권한: `contents: read`, `pages: write`, `id-token: write`
  - `concurrency: pages`(진행 중인 배포는 취소하지 않음)
- 순서
  1. pipeline 모듈의 generate_visualizations 실행(curve HTML, spread HTML 문자열 반환)
  2. 반환된 HTML의 유효성 확인: 문자열이 비어 있지 않고 `<html`, `plotly`를 포함
  3. `html/yield_curve.html`, `html/yield_spread.html`로 저장
  4. 저장소에 커밋된 `html/index.html`과 함께 `html/` 디렉터리를 GitHub Pages에 배포
