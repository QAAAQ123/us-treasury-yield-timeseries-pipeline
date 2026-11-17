# XML 데이터 변환 방법
최초 작성일 2026-10-24

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
- date: date, Not Null
- yield_1m: FLOAT
- yield_1_5_m: FLOAT
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
- (정상) 주말 및 공휴일: 원본 데이터에는 관측일만 유지한다. 달력 기준의 연속적인 일별 시계열이 필요한 경우 별도 처리 단계에서 이전 관측값을 채운다.
- (정상) 특정 만기의 공시 데이터가 존재하지 않는 기간: 해당 수익률을 `None`으로 처리한다.
- (비정상) 날짜 필드 누락 또는 형식 오류: 해당 레코드를 유효한 관측 데이터로 처리하지 않는다.
- (비정상) 예상하지 못한 수익률 누락: 원본 응답을 재확인하고, 최대 3회 재요청 후에도 해결되지 않으면 오류 로그를 기록하고 파이프라인 실행을 실패 처리한다.
- (비정상) 중복 날짜 또는 잘못된 수익률 형식: 원본 데이터를 확인하고, 검증 오류가 해결되지 않으면 후속 데이터 처리를 중단한다.

## 5. 검증 결과에 따른 데이터 처리

- 모든 검증을 통과한 레코드는 데이터 변환 단계로 전달한다.
- 공시 자료에서 정상적으로 제공되지 않는 수익률은 `None`으로 유지한다.
- 동일한 날짜의 레코드가 중복되면 해당 레코드의 값이 일치하는지 확인한다. 값이 일치하면 중복을 제거하고, 값이 다르면 오류로 처리한다.
- 비정상 결측이나 자료형 오류가 발견되면 원본 응답을 재확인하고, 재검증 후에도 문제가 해결되지 않으면 파이프라인을 중단한다.
- 검증에 실패한 데이터가 기존 CSV를 덮어쓰거나 잘못된 데이터가 최종 결과에 반영되지 않도록 한다.

## 6. DataFrame 생성

- XML의 각 `entry`에서 `content/properties`를 추출하여 하나의 레코드로 변환한다.
- `NEW_DATE`를 `date` 컬럼으로, `BC_`로 시작하는 대상 태그를 해당 만기의 `yield_*` 컬럼으로 매핑한다.
- `BC_30YEARDISPLAY` 및 분석 대상이 아닌 필드는 제외한다.
- 날짜는 날짜 자료형으로 변환하고, 수익률은 숫자형(`float`)으로 변환한다.
- 정상적으로 값이 제공되지 않는 수익률은 결측값으로 유지한다.
- 모든 레코드를 하나의 DataFrame으로 결합한다
- `date`의 결측 여부와 중복 여부, 컬럼 구성 및 자료형을 최종 확인한다.
- 최종 컬럼 순서는 `date`를 첫 번째로 배치하고, 나머지는 3절에서 정의한 컬럼 순서를 따른다.