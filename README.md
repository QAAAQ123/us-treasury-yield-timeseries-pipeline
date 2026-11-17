# U.S. Treasury Yield Timeseries Pipeline

미국 국채의 만기별 수익률 시계열을 수집·정제하고, 이를 바탕으로 10Y–2Y 및 10Y–3M 일드 스프레드를 계산하여 일드 시계열과 스프레드 시계열을 함께 시각화하는 데이터 파이프라인 프로젝트입니다.

## 시각화 결과 보기

GitHub Pages에서 인터랙티브 그래프를 확인할 수 있습니다.

- 대시보드: https://qaaaq123.github.io/us-treasury-yield-timeseries-pipeline/
- 만기별 일드 시계열: https://qaaaq123.github.io/us-treasury-yield-timeseries-pipeline/yield_curve.html
- 10Y–2Y, 10Y–3M 스프레드 시계열: https://qaaaq123.github.io/us-treasury-yield-timeseries-pipeline/yield_spread.html

## 목적

본 프로젝트는 미국 국채의 만기별 수익률 시계열을 자동으로 수집·정제하고, 데이터 품질을 검증한 뒤 일드(Yield)와 10Y–2Y 및 10Y–3M 일드 스프레드(Yield Spread)를 계산하여 각각 시계열 그래프로 시각화하는 배치 데이터 파이프라인을 구축하는 것을 목표로 합니다.

주요 목표는 다음과 같습니다.

- 미국 국채 금리 데이터의 자동 수집
- 만기별 일드 시계열의 정제 및 데이터 정합성 검증, 중복 데이터 처리
- 10Y–2Y 및 10Y–3M 일드 스프레드 계산
- 일드 시계열과 일드 스프레드 시계열의 인터랙티브 시각화
- 정기적인 파이프라인 실행 및 결과물 자동 배포

## 대상 지표

| 지표 | 정의 | 의미 | 실제 활용 |
|---|---|---|---|
| 일드 시계열 | 만기별 국채 수익률의 날짜별 변화 | 금리 환경과 만기별 금리 추이 | 금리 추이 분석, 스프레드 계산의 기초 데이터 |
| 10Y–2Y Yield Spread | 10년물 금리 − 2년물 금리 | 장기 금리와 중기 금리 간 차이 | 장단기 금리 역전 모니터링, 채권시장 분석 및 경기 전망 |
| 10Y–3M Yield Spread | 10년물 금리 − 3개월물 금리 | 장기 금리와 단기 금리 간 차이 | 뉴욕 연은의 경기침체 확률 추정 모델, 경기 선행 지표 분석 |

일반적으로 스프레드가 음수인 상태는 수익률 곡선의 역전을 의미합니다.

## 기술 스택

| 기술 | 용도 |
|---|---|
| Python | 데이터 파이프라인 구현 |
| pandas | 데이터 정제 및 변환 |
| requests | API 데이터 수집 |
| Plotly | 인터랙티브 시계열 시각화 |
| JupyterLab | 데이터 탐색, 분석 및 시각화 검증 |
| pytest | 데이터 처리 및 계산 로직 테스트 |
| Ruff | 코드 검사 및 포맷팅 |
| GitHub Actions | 파이프라인 정기 실행 및 자동화 |
| GitHub Pages | 시각화 결과물 배포 |

## 파이프라인 구조

```text
Data Sources
    │
    ▼
Data Ingestion
    │
    ▼
Data Cleaning & Validation
    │
    ▼
Processed Yield Timeseries
    │
    ├──────────────────────────┐
    ▼                          ▼
Yield Spread Calculation   Interactive Visualization (Yield Timeseries)
    │                          │
    ▼                          │
Interactive Visualization (Spread Timeseries)
    │                          │
    └──────────────┬───────────┘
                   ▼
              GitHub Pages
```

### 1. 데이터 수집

미국 재무부에서 제공하는 XML 데이터를 활용해 만기별 국채 금리를 수집합니다. 최초 1회 전체 데이터를 수집해 CSV로 적재하고, 이후에는 당월 신규 데이터만 증분 적재합니다.

### 2. 데이터 정제 및 검증

날짜 형식, 결측치, 중복 데이터 및 금리 값의 유효성을 검증하고, 휴장일과 만기별 결측 데이터를 정책에 따라 처리합니다.

### 3. 스프레드 계산

정제된 만기별 일드 시계열을 바탕으로 10Y–2Y 및 10Y–3M 스프레드를 계산하여 CSV(`data/mart/`)로 저장합니다.

### 4. 시각화

Plotly를 활용해 다음 두 가지 인터랙티브 시계열 그래프를 생성합니다.
- 만기별 일드 시계열 그래프
- 10Y–2Y 및 10Y–3M 스프레드 시계열 그래프

### 5. 자동화 및 배포

GitHub Actions를 이용해 데이터 수집과 배포를 자동화하고, GitHub Pages를 통해 결과를 공개합니다.

- Collect: 매일 뉴욕 시간 20시에 증분 데이터를 수집하여 CSV가 변경되면 커밋하고 Deploy를 실행합니다.
- Deploy: CSV를 바탕으로 Plotly HTML을 생성하여 GitHub Pages에 배포합니다.
- CI / E2E: Pull Request에서 lint, unit·integration 테스트를 실행하고, E2E 테스트는 매주 수요일에 실행합니다.

## 시작하기

### 요구 사항

- Python 3.11 이상
- pip

### 1. 저장소 복제

```bash
git clone https://github.com/QAAAQ123/us-treasury-yield-timeseries-pipeline.git
cd us-treasury-yield-timeseries-pipeline
```

### 2. 가상환경 생성 및 활성화

Linux 환경 기준입니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. 의존성 설치

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

프로젝트 의존성은 `pyproject.toml`에서 관리합니다.

### 4. 테스트 및 코드 검사

```bash
pytest                # unit 테스트 
pytest -m integration # integration 테스트
pytest -m e2e         # E2E 테스트
ruff check .          # 린팅
ruff format --check . # 포맷팅
```

## 데이터 출처

- [U.S. Department of the Treasury(미 재무부)](https://home.treasury.gov/)

## 라이선스

이 프로젝트의 라이선스는 저장소의 `LICENSE` 파일을 참조하세요.