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
    except requests.RequestException:
        raise requests.RequestException("HTTP Request error")
    except Exception:
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
    """미국 재무부 금리 데이터 요청에 사용할 URL 파라미터를 생성한다.

    월이 지정되지 않으면 연도 기준 파라미터를 생성하고,
    월이 지정되면 연월 기준 파라미터를 생성한다.
    한 자리 월은 두 자리로 표현한다.

    Args:
        year: 조회할 연도.
        month: 조회할 월. None이면 연도 기준으로 조회한다.

    Returns:
        미국 재무부 API 요청에 사용할 URL 파라미터 딕셔너리.
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
    """year와 month 인자의 유효성을 검증한다.

    Args:
        year: 조회할 연도. 1990년부터 현재 연도까지 허용한다.
        month: 조회할 월. None 또는 1부터 12까지의 정수를 허용한다.

    Raises:
        TypeError: year가 int가 아니거나 month가 int 또는 None이 아닌 경우.
        ValueError: year 또는 month가 허용 범위를 벗어나거나,
            year와 month가 미래 날짜를 나타내는 경우.
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
