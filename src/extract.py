"""
`https://home.treasury.gov/`에 Daily Treasury Par Yield Curve Rates를 요청해 XML을 추출하는 모듈
책임: 네트워크 요청 및 원본 데이터 반환
"""

from datetime import date

import requests

from logger_config import logger

BASE_URL = (
    "https://home.treasury.gov/resource-center/"
    "data-chart-center/interest-rates/pages/xml"
)

# 1. 인자 유효성 검증
# 2. month 존재 여부에 따라 파라미터 다르게 생성
# 3. requests 요청
# 4. http respone의 상태코드에 따라 다르게 응답
# 4.1 200 OK이고 데이터가 있는 경우 => bytes return
# 4.2 200 OK가 아닌 경우 => raise
# 4.3 200 OK이지만 데이터가 없는 경우 => None return
def fetch_response(year: int, month: int | None = None) -> bytes | None:
    """URL로 XML 데이터를 요청한다.

    Args:
        year(int): 요청할 년도
        month(int | None): 요청할 월(기본값은 None)
    Returns:
        bytes: 응답 본문의 XML 데이터 원본
        None: 데이터가 없는 경우
    Raises:
        requests.ReadTimeout: HTTP 요청 타임아웃
        requests.RequestException: HTTP 요청에 실패한 경우
    """

    _validate_args(year, month)

    params = _setup_params(year, month)

    try:
        response = requests.get(
            BASE_URL,
            params=params,
            timeout=30,
        )
    except requests.ReadTimeout as e:
        raise requests.ReadTimeout("HTTP Request Timeout error") from e
    except requests.RequestException as e:
        raise requests.RequestException("HTTP Request error")
    except Exception as e:
        raise
    else:
        logger.info(f"요청 성공: {year}년 {month}월")

        status_code = response.status_code
        content = response.content
        logger.info(f"상태 코드: {response.status_code}")

        # 4.2 200 OK가 아닌 경우 => raise
        if status_code != 200:
            raise requests.HTTPError(f"status={status_code}", response=response)

        # 4.3 200 OK이지만 데이터가 없는 경우 => None return
        if not content:
            return None
        # 4.1 200 OK이고 데이터가 있는 경우 => bytes return
        return content


def _setup_params(year: int, month: int | None) -> dict:
    """URL 파라미터 생성
    month == None then field_tdr_date_value
    month != None then field_tdr_date_value_month
    """
    if month is None:
        return {
            "data": "daily_treasury_yield_curve",
            "field_tdr_date_value": f"{year!s}",
        }

    return {
        "data": "daily_treasury_yield_curve",
        "field_tdr_date_value_month": f"{year!s}{month:02d}",
    }


def _validate_args(year: int, month: int | None) -> None:
    """인자(year, month) 유효성 검증
    1. year이 1990 이상
    2. month가 1과 12사이
    3. date(year, month,1)와 오늘 날짜 비교
    4. year의 타입이 int
    5. month의 타입이 int or None
    """
    if not isinstance(year, int):
        raise TypeError(f"year must be int, year: {type(year).__name__}")
    if month is not None and not isinstance(month, int):
        raise TypeError(f"month must be int or None, month: {type(month).__name__}")

    today = date.today()

    if year < 1990 or year > today.year:
        raise ValueError(f"year out of range: {year}")
    if month is not None and not 1 <= month <= 12:
        raise ValueError(f"month out of range: {month}")

    if month is not None and date(year, month, 1) > today:
        raise ValueError(f"requested: {year}-{month}")
