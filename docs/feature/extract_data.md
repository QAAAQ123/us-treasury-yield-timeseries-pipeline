# 미국 재무부 Daily Treasury Par Yield Curve Rates 추출 방법
최초 작성일: 2026-10-21
1차 수정일: 2026-10-24

## 1. Daily Treasury Par Yield Curve Rates 데이터 제공 기간
#### CSV 및 유저 친화적 데이터
- 2023년 이전 데이터는 View Daily Treasury Archives에 장기 시계열 단위(10년)로 제공한다.
- 2023년 이후(2024,2025,2026) 데이터는 아카이브가 아닌 접속 화면에서 연단위로 제공한다.
- 당연도(2026)에 대해서는 월 단위의 데이터를 제공한다.
정리: 2023년 이전은 decade/2024,2025는 연단위/2026년은 월단위(매일 업데이트)

#### XML 데이터
- field_tdr_date_value의 값으로 `YYYY` 형식을 지원한다.
- field_tdr_date_value_month의 값으로 `YYYYmm`형식을 지원한다.

#### 아카이브 XML 데이터 제공 기간(2026-10-24 추가)

Daily Treasury Par Yield Curve Rates의 XML 아카이브는 다음 기간으로 제공된다.

| 데이터 기간 | 아카이브 XML 파일명 |
|---|---|
| 1990~1999 | `par-yield-curve-rates-1990-1999.xml` |
| 2000~2009 | `par-yield-curve-rates-2000-2009.xml` |
| 2010~2019 | `par-yield-curve-rates-2010-2019.xml` |
| 2020~2023 | `par-yield-curve-rates-2020-2023.xml` |
| 1990~2023 | `par-yield-curve-rates-1990-2023.xml` |

1990~2023년 전체 데이터를 초기 적재할 경우, 여러 아카이브를 순서대로 요청하는 대신 `par-yield-curve-rates-1990-2023.xml`을 우선 사용하는 방안을 검토한다.

단, 통합 아카이브와 기간별 아카이브 간 데이터 일치 여부 및 XML 필드 구조는 실제 응답을 통해 검증한다.

## 2. Daily Treasury Par Yield Curve Rates 데이터 변화
#### 1. 시계열 단절(Series Break)
미국 재무부는 수익률 곡선을 산출하는 방법론을 업데이트했습니다. 2021년 12월 6일부터 공식 액면수익률 곡선(Par Yield Curve)을 산출할 때 단조 볼록 스플라인(Monotone Convex Spline, MC) 방법을 사용하기 시작했으며, 기존의 준 3차 에르미트 스플라인(Quasi-Cubic Hermite Spline, HS) 방법은 중단했습니다. MC 방법이 도입되기 전에 HS 방법을 사용해 산출한 모든 재무부 수익률 곡선 금리는 여전히 공식 금리로 인정됩니다. 자세한 내용은 수익률 곡선 방법론 변경 안내서([Yield Curve Methodology Change Information Sheet](https://home.treasury.gov/policy-issues/financing-the-government/yield-curve-methodology-change-information-sheet))를 참조하십시오.
#### 2. 1.5개월 만기 일정 만기 시계열
1.5개월 만기 일정 만기 시계열은 2025년 2월 18일에 시작되었습니다. 이날 6주 만기 재무부 단기국채(Treasury Bill)가 기준 국채로 처음 발행되었습니다. 이 날짜 이전에는 재무부가 6주 만기의 단기국채를 현금 관리용 단기국채(Cash Management Bills)로 발행했습니다.
#### 3. 4개월 만기 일정 만기 시계열
4개월 만기 일정 만기 시계열은 2022년 10월 19일에 시작되었습니다. 이날 17주 만기 재무부 단기국채가 기준 국채로 처음 발행되었습니다. 이 날짜 이전에는 재무부가 17주 만기의 단기국채를 현금 관리용 단기국채로 발행했습니다.
#### 4. 2개월 만기 일정 만기 시계열
2개월 만기 일정 만기 시계열은 2018년 10월 16일에 시작되었습니다. 이날 8주 만기 재무부 단기국채가 처음 발행되었습니다.
### 5. 30년 만기 일정 만기 시계열
30년 만기 재무부 일정 만기 시계열은 2002년 2월 18일에 중단되었다가 2006년 2월 9일에 재개되었습니다. 2002년 2월 18일부터 2006년 2월 8일까지 재무부는 30년물 금리의 대체 지표를 발표했습니다. 자세한 내용은 [장기 평균 금리(Long-Term Average Rate)](https://home.treasury.gov/policy-issues/financing-the-government/interest-rate-statistics/treasury-yield-curve-methodology)를 참조하십시오.
#### 6. 20년 만기 일정 만기 시계열
재무부는 1986년 말에 20년 만기 일정 만기 시계열 발표를 중단했다가 1993년 10월 1일에 재개했습니다. 따라서 1987년 1월 1일부터 1993년 9월 30일까지의 기간에는 20년물 금리 데이터가 존재하지 않습니다.


## 3. Daily Treasury Par Yield Curve Rates 데이터 제공 형식
1. CSV: 웹 사이트에서 다운로드
2. XML
    1. View the XML Feed: 원본
    2. Render the XML Feed: 랜더링(사람이 보기 좋게)

#### 사용할 데이터 형식
`View the XML Feed` 사용

## 4. Daily Treasury Par Yield Curve Rates URL 형식


#### 1. 연도별·월별 XML 엔드포인트
- BaseURL: `https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml?data=daily_treasury_yield_curve&field_tdr_date_value=YYYY`
    - YYYY에 1990부터 최신연도까지 넣을 수 있다.
    - `field_tdr_date_value`를 `field_tdr_date_value_month`로 바꾸면 YYYYmm(월단위)로 검색할 수 있다.
예시:

```text
https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml?data=daily_treasury_yield_curve&field_tdr_date_value=2024

https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml?data=daily_treasury_yield_curve&field_tdr_date_value_month=202610
```
- `field_tdr_date_value`에는 조회 연도를 지정한다.
- `field_tdr_date_value_month`에는 조회 연월을 지정한다.
- 데이터 가용 시작 연도는 1990년이다.

#### 2. 아카이브 XML URL(2026-10-24 추가)

아카이브 XML은 연도별·월별 XML 엔드포인트와 달리, 기간이 포함된 정적 URL을 사용한다.

- Base URL:
  `https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rate-archives`
- URL 형식:
  `BASE_URL/par-yield-curve-rates-{start_year}-{end_year}.xml`
예시:
```text
https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rate-archives/par-yield-curve-rates-1990-1999.xml

https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rate-archives/par-yield-curve-rates-1990-2023.xml
```
현재 확인된 아카이브 기간은 다음과 같다.
```python
ARCHIVE_PERIODS = {
    (1990, 1999),
    (2000, 2009),
    (2010, 2019),
    (2020, 2023),
    (1990, 2023),
}
```

## 5. Daily Treasury Par Yield Curve Rates XML 형식

#### 2026년 XML 형식
```XML
<entry>
<id>
https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml-item?data=daily_treasury_yield_curve&id=140
</id>
<title type="text"/>
<updated>2026-10-20T16:10:56Z</updated>
<author>
<name/>
</author>
<link rel="edit" title="DailyTreasuryYieldCurveRateDatum" href="/resource-center/data-chart-center/interest-rates/pages/xml-item?data=daily_treasury_yield_curve&id=140"/>
<category term="TreasuryDataWarehouseModel.DailyTreasuryYieldCurveRateDatum" scheme="http://schemas.microsoft.com/ado/2007/08/dataservices/scheme"/>
<content type="application/xml">
<m:properties>
<d:Id m:type="Edm.Int32">140</d:Id>
<d:NEW_DATE m:type="Edm.DateTime">2026-01-02T00:00:00</d:NEW_DATE>
<d:BC_1MONTH m:type="Edm.Double">3.72</d:BC_1MONTH>
<d:BC_1_5MONTH m:type="Edm.Double">3.71</d:BC_1_5MONTH>
<d:BC_2MONTH m:type="Edm.Double">3.66</d:BC_2MONTH>
<d:BC_3MONTH m:type="Edm.Double">3.65</d:BC_3MONTH>
<d:BC_4MONTH m:type="Edm.Double">3.62</d:BC_4MONTH>
<d:BC_6MONTH m:type="Edm.Double">3.58</d:BC_6MONTH>
<d:BC_1YEAR m:type="Edm.Double">3.47</d:BC_1YEAR>
<d:BC_2YEAR m:type="Edm.Double">3.47</d:BC_2YEAR>
<d:BC_3YEAR m:type="Edm.Double">3.55</d:BC_3YEAR>
<d:BC_5YEAR m:type="Edm.Double">3.74</d:BC_5YEAR>
<d:BC_7YEAR m:type="Edm.Double">3.95</d:BC_7YEAR>
<d:BC_10YEAR m:type="Edm.Double">4.19</d:BC_10YEAR>
<d:BC_20YEAR m:type="Edm.Double">4.81</d:BC_20YEAR>
<d:BC_30YEAR m:type="Edm.Double">4.86</d:BC_30YEAR>
<d:BC_30YEARDISPLAY m:type="Edm.Double">4.86</d:BC_30YEARDISPLAY>
</m:properties>
</content>
</entry>
```

#### 1990년 XML 형식
```XML
<entry>
<id>
https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml-item?data=daily_treasury_yield_curve&id=1753
</id>
<title type="text"/>
<updated>2026-10-20T16:11:00Z</updated>
<author>
<name/>
</author>
<link rel="edit" title="DailyTreasuryYieldCurveRateDatum" href="/resource-center/data-chart-center/interest-rates/pages/xml-item?data=daily_treasury_yield_curve&id=1753"/>
<category term="TreasuryDataWarehouseModel.DailyTreasuryYieldCurveRateDatum" scheme="http://schemas.microsoft.com/ado/2007/08/dataservices/scheme"/>
<content type="application/xml">
<m:properties>
<d:Id m:type="Edm.Int32">1753</d:Id>
<d:NEW_DATE m:type="Edm.DateTime">1990-01-02T00:00:00</d:NEW_DATE>
<d:BC_3MONTH m:type="Edm.Double">7.83</d:BC_3MONTH>
<d:BC_6MONTH m:type="Edm.Double">7.89</d:BC_6MONTH>
<d:BC_1YEAR m:type="Edm.Double">7.81</d:BC_1YEAR>
<d:BC_2YEAR m:type="Edm.Double">7.87</d:BC_2YEAR>
<d:BC_3YEAR m:type="Edm.Double">7.90</d:BC_3YEAR>
<d:BC_5YEAR m:type="Edm.Double">7.87</d:BC_5YEAR>
<d:BC_7YEAR m:type="Edm.Double">7.98</d:BC_7YEAR>
<d:BC_10YEAR m:type="Edm.Double">7.94</d:BC_10YEAR>
<d:BC_30YEAR m:type="Edm.Double">8.00</d:BC_30YEAR>
<d:BC_30YEARDISPLAY m:type="Edm.Double">0.00</d:BC_30YEARDISPLAY>
</m:properties>
</content>
</entry>
```

##### 확인 결과
- 2026년과 1990년 XML 필드를 확인한 결과 [2. 데이터 변화](#2-daily-treasury-par-yield-curve-rates-데이터-변화)에서 명시적으로 1990년 이후로 추가했다고 한 만기인  BC_1_5MONTH, BC_2MONTH, BC_4MONTH와 BC_1MONTH가 추가 된 것을 제외하고는 형식이 같다.
- 따라서 100% 확신할 수는 없지만, 형식은 거의 변하지 않는다고 예측할 수 있다.

## 6. XML에서 추출할 필드
- 본 프로젝트의 목적은 만기별 일드와 T10Y2Y 및 T10Y3M 일드 스프레드를 시각화 하는 것이기 때문에 
- 개별 일드를 시각화 하기 위해 최대한 많은 만기 필드를 수집하는 것이 좋다.
-결론적으로, 1M, 1.5M, 2M, 3M, 4M, 6M, 1Y, 2Y, 3Y, 5Y, 7Y, 10Y, 20Y, 30Y 모두를 수집할 것이다.
- 제공 불가 데이터 규칙은 기본적으로 [2. 데이터 변화](#2-daily-treasury-par-yield-curve-rates-데이터-변화)를 따른다.

## 7. 추출 방법
`xml.etree.ElementTree` 사용하여 추출
예시
```python
import xml.etree.ElementTree as ET

root = ET.fromstring(xml_data)

for entry in root.findall(".//{*}entry"):
    properties = entry.find(".//{*}properties")

    if properties is None:
        continue

    data = {
        element.tag.split("}")[-1]: element.text
        for element in properties
    }

    print({
        "date": data.get("NEW_DATE"),
        "3_month": data.get("BC_3MONTH"),
        "2_year": data.get("BC_2YEAR"),
        "10_year": data.get("BC_10YEAR"),
    })
```

## 8. Extract 모듈 설계 및 적재 전략(2026-10-24 추가)

#### 1. 요청 함수 구성

데이터 제공 방식이 다르므로 아카이브 요청과 연도별·월별 요청을 별도 함수로 분리한다.

| 함수 | 책임 |
|---|---|
| `fetch_archive(start_year, end_year)` | 지정된 기간의 정적 아카이브 XML 요청 |
| `fetch_response(year, month=None)` | 기존 XML 엔드포인트에서 연도별 또는 월별 데이터 요청 |
| `_request_xml(url, params=None)` | HTTP 요청, 상태 코드 검사, 예외 처리 및 원본 응답 반환 |
| `_validate_args(year, month)` | 연도 및 월 인자 유효성 검증 |
| `_setup_params(year, month)` | 연도별·월별 XML 엔드포인트 요청 파라미터 생성 |

`_request_xml()`은 두 요청 함수가 공통으로 사용하는 내부 함수다. 이를 활용하면 HTTP 요청 및 예외 처리 로직의 중복을 줄일 수 있다.

Extract 단계에서는 XML을 파싱하거나 CSV로 저장하지 않고, 원본 응답을 반환하는 책임만 유지한다.

#### 2. 초기 적재(Initial Load)

- `fetch_archive(1990, 2023)`을 이용해 통합 아카이브 XML을 요청한다.
- 응답의 정상 여부를 확인한 후 Transform 단계에서 XML 파싱 및 데이터 정합성 검증을 수행한다.
- 통합 아카이브의 데이터 범위와 필드 구조를 검증하고, 필요한 경우 기간별 아카이브를 대안으로 사용한다.

#### 3. 증분 적재(Incremental Load)

- 2024년 이후 데이터는 기존 `fetch_response(year, month)`를 사용한다.
- 완료된 연도는 연도별 조회를 이용하고, 당연도는 월별 조회를 이용하는 방식을 기본으로 한다.
- 수집한 데이터는 Transform 단계에서 정제 및 검증한 후 Load 단계에서 기존 CSV 데이터와 병합하고 중복을 제거한다.