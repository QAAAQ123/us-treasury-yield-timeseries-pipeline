# CSV로 데이터 적재 전략
최초 작성일: 2026-10-31

## 1. Dataframe 스키마 
```text
Data columns (total 15 columns):
 #   Column      Non-Null Count  Dtype  
---  ------      --------------  -----  
 0   date        30 non-null     object 
 1   yield_1m    30 non-null     float64
 2   yield_1_5m  30 non-null     float64
 3   yield_2m    30 non-null     float64
 4   yield_3m    30 non-null     float64
 5   yield_4m    30 non-null     float64
 6   yield_6m    30 non-null     float64
 7   yield_1y    30 non-null     float64
 8   yield_2y    30 non-null     float64
 9   yield_3y    30 non-null     float64
 10  yield_5y    30 non-null     float64
 11  yield_7y    30 non-null     float64
 12  yield_10y   30 non-null     float64
 13  yield_20y   30 non-null     float64
 14  yield_30y   30 non-null     float64
dtypes: float64(14), object(1)
```

## 2. 데이터 예시
```text
date          2026-09-01
yield_1m            3.85
yield_1_5m          3.88
yield_2m            3.89
yield_3m            3.92
yield_4m            3.97
yield_6m             4.0
yield_1y            4.18
yield_2y            4.39
yield_3y            4.46
yield_5y            4.55
yield_7y            4.66
yield_10y           4.79
yield_20y           5.27
yield_30y           5.27
Name: 0, dtype: object
```
## 3. 정책
### 1. 저장 위치
  - ./data/mart/yield_curve/yield_curve.csv
  - ./data/mart/yield_spread/yield_spread.csv
### 2. 파일 관리 
- 일드 커브, 일드 스프레드 각 1개씩 총 2개의 파일로 관리한다.
  - 1990년부터 2026년까지 총 37년
  - 365 X 37 = 13505
  - 대략 1만 3천개로 데이터 양이 매우 적기 때문에 하나의 파일로 관리하기에 적합하다
  - 연도별 파일 분리 시기
    - 데이터 규모가 커짐
    - 특정 기간을 자주 조회
### 3. 파일 정보
- 기본 키: date
- 정렬: date 기준으로 오름차순
- 적재 방법: 월별 조회를 통해 데이터를 가져와 중복 제거후 적재
### 4. CSV 저장 형식
- UTF-8
- `,`(쉼표)로 구분
- 날짜 형식: YYYY-mm-dd
- 결측값: 빈 문자열로 저장

## 4. 적재 흐름
### 1. 최초 적재
1. 아카이브 및 연월별 일드 커브 DataFrame 수집
2. 수집한 DataFrame을 하나의 DataFrame으로 병합
3. 날짜 기준 오름차순 정렬
4. 일드 스프레드 계산 및 별도 DataFrame 생성
5. 일드 커브 및 일드 스프레드 CSV 각각 저장
### 2. 증분 적재
1. 신규 연월 일드 커브 DataFrame 수집
2. 일드 스프레드 계산 및 별도 DataFrame 생성
3. 기존 CSV를 DataFrame으로 변환
4. 기존 데이터에서 신규 수집 대상 연월과 이전 전체 데이터 분리
5. 기존 연월 데이터와 신규 수집 데이터 비교
6. 중복 날짜가 존재하는 경우 신규 수집 데이터 기준으로 갱신
7. 이전 전체 데이터와 갱신된 연월 데이터를 병합
8. 날짜 기준 오름차순 정렬
9.  일드 커브 및 일드 스프레드 CSV 각각 갱신

## 5. 데이터 검증
- date 컬럼 결측
- 날짜 중복
- 날짜 오름차순
- 컬럼 및 자료형 

## 6. 일드 스프레드 생성
- 대상:
  - spread_10y_2y: 10년물 - 2년물
  - spread_10y_3m: 10년물 - 3개월물
- 단위: %p(그래프를 그릴 때 bp로 변환)
- 피연산자중 하나라도 없으면 결측 처리


