"""
미국 재무부 Daily Treasury Par Yield Curve Rates의 XML 원본을 수집하는 모듈.
책임: 일반 조회 및 정적 아카이브를 통한 원본 데이터 수집
"""

from datetime import date

import requests
from requests import Response

from logger_config import logger

YIELD_CURVE_ARCHIVE_URL = (
    "https://home.treasury.gov/resource-center/data-chart-center/"
    "interest-rates/daily-treasury-rate-archives/"
    "par-yield-curve-rates-{start}-{end}.xml"
)
YIELD_CURVE_URL = (
    "https://home.treasury.gov/resource-center/data-chart-center/"
    "interest-rates/pages/xml"
)

SUPPORTED_ARCHIVE_RANGES = (
    (1990, 1999),
    (2000, 2009),
    (2010, 2019),
    (2020, 2023),
    (1990, 2023),
)


def fetch_yield_curve_xml(year: int, month: int | None = None) -> bytes | None:
    """지정된 연도 또는 연월의 Treasury 금리 XML을 요청한다.

    Args:
        year(int): 요청할 년도
        month(int | None): 요청할 월(기본값은 None)
    Returns:
        bytes: 응답 본문의 XML 데이터 원본(entry태그 존재 여부 미확인)
        None: 데이터가 없는 경우
    Raises:
        requests.ReadTimeout: HTTP 요청 타임아웃
        requests.RequestException: HTTP 요청에 실패
        requests.HTTPError: HTTP 응답 상태 코드가 200 OK가 아닌 모든 경우
    """
    _validate_args(year, month)

    params = _setup_params(year, month)

    response = _get_response(YIELD_CURVE_URL, params)

    logger.info(
        "응답 완료: %s년 %s월 (상태 코드: %s)", year, month, response.status_code
    )

    if response.status_code != 200:
        raise requests.HTTPError(f"status={response.status_code}", response=response)

    # Extract에서는 entry 존재 유무와 상관없이 추출만 진행한다.
    return response.content or None


def fetch_yield_curve_archive_xml(
    start_year: int,
    end_year: int,
) -> bytes | None:
    """지정된 기간의 Treasury 정적 아카이브 XML을 요청한다.

    Args:
        start_year: 아카이브 시작 연도.
        end_year: 아카이브 종료 연도.
    Returns:
        응답 본문의 원본 bytes. 본문이 비어 있으면 None.
    Raises:
        TypeError: 시작 연도 또는 종료 연도가 int가 아닌 경우.
        ValueError: 지원하지 않는 연도 구간을 요청한 경우.
        requests.RequestException: HTTP 요청에 실패한 경우.
        requests.HTTPError: 응답 상태 코드가 200이 아닌 경우.
    """

    _validate_archive_args(start_year, end_year)

    url = YIELD_CURVE_ARCHIVE_URL.format(
        start=start_year,
        end=end_year,
    )

    response = _get_response(url)

    logger.info(
        "응답 완료: %s-%s (상태 코드: %s)",
        start_year,
        end_year,
        response.status_code,
    )

    if response.status_code != 200:
        raise requests.HTTPError(
            f"status={response.status_code}",
            response=response,
        )

    return response.content or None


def _validate_archive_args(start_year: int, end_year: int) -> None:
    """아카이브 조회 인자의 유효성을 검증한다.

    Args:
        start_year: 조회 시작 연도.
        end_year: 조회 종료 연도.
    Raises:
        TypeError: 시작 연도 또는 종료 연도가 int가 아닌 경우.
        ValueError: 지원하지 않는 연도 구간을 요청한 경우.
    """
    if not isinstance(start_year, int):
        raise TypeError(f"start_year must be int, got {type(start_year).__name__}")

    if not isinstance(end_year, int):
        raise TypeError(f"end_year must be int, got {type(end_year).__name__}")

    if (start_year, end_year) not in SUPPORTED_ARCHIVE_RANGES:
        raise ValueError(f"unsupported archive range: {start_year}-{end_year}")


def _get_response(url: str, params: dict[str, str] | None = None) -> Response:
    """URL에 GET 요청을 보내고 원본 Response를 반환한다.

    Args:
        url: 요청할 URL.
        params: 쿼리스트링으로 붙일 파라미터. 없으면 None.
    Returns:
        requests.Response 객체. 상태 코드 검사는 호출하는 쪽에서 한다.
    Raises:
        requests.RequestException: 연결 실패, 타임아웃 등 네트워크 오류.
    """
    return requests.get(url, params=params, timeout=30)


def _setup_params(year: int, month: int | None) -> dict[str, str]:
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
