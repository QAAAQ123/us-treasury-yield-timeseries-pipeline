"""미국 재무부 금리 데이터의 결측값 및 휴장일 처리 모듈.

Treasury 금리 데이터의 만기별 제공 정책을 적용하고, 누락된 금리 필드를
None으로 보정한다. 또한 관측 날짜 사이에 공백이 있는 경우 직전 관측값을
기준으로 누락된 날짜의 레코드를 생성한다.
"""

from datetime import date, timedelta

from logger_config import logger

# transform.py와 중복 상수-규모가 커지면 공통 상수로 분리 필요
RECORD_KEY_MAP = {
    "NEW_DATE": "date",
    "BC_1MONTH": "yield_1m",
    "BC_1_5MONTH": "yield_1_5m",
    "BC_2MONTH": "yield_2m",
    "BC_3MONTH": "yield_3m",
    "BC_4MONTH": "yield_4m",
    "BC_6MONTH": "yield_6m",
    "BC_1YEAR": "yield_1y",
    "BC_2YEAR": "yield_2y",
    "BC_3YEAR": "yield_3y",
    "BC_5YEAR": "yield_5y",
    "BC_7YEAR": "yield_7y",
    "BC_10YEAR": "yield_10y",
    "BC_20YEAR": "yield_20y",
    "BC_30YEAR": "yield_30y",
}

MATURITY_AVAILABLE_FROM = {
    "yield_1_5m": date(2025, 2, 18),
    "yield_2m": date(2018, 10, 16),
    "yield_4m": date(2022, 10, 19),
    "yield_20y": date(1993, 10, 1),
}

MATURITY_UNAVAILABLE_PERIODS = {
    "yield_30y": ((date(2002, 2, 18), date(2006, 2, 8)),),
}


def handle_missing_data(
    records: list[dict[str, float | date | None]],
) -> list[dict[str, float | date | None]]:
    """금리 데이터에 결측 처리 및 만기별 제공 정책을 적용한다.

    각 레코드의 누락된 금리 필드를 None으로 보정하고, Treasury 만기별
    제공 정책을 위반하는 금리 값을 None으로 변경한다. 또한 마지막 관측일과
    현재 관측일 사이에 공백이 있으면 누락된 날짜의 레코드를 생성한다.

    Args:
        records: 날짜와 만기별 금리 값을 포함하는 레코드 목록.
            날짜 기준 오름차순으로 정렬되어 있어야 한다.
    Returns:
        결측 처리 정책이 적용되고 누락된 날짜의 레코드가 추가된 목록.
    Notes:
        입력 레코드의 딕셔너리를 직접 수정한다.
        생성된 휴장일 레코드에는 직전 관측 레코드의 금리 값을 사용한다.
    """

    last_observed_record: dict[str, float | date | None] | None = None
    normalized_records: list[dict[str, float | date | None]] = []

    for record in records:
        current_record = _fill_missing_maturities(record)
        current_record = _apply_treasury_note_policy(current_record)

        if last_observed_record is not None:
            current_date = current_record["date"]
            last_observed_date = last_observed_record["date"]

            if _has_market_holiday_gap(current_date, last_observed_date):
                holiday_dates = [
                    last_observed_date + timedelta(days=offset)
                    for offset in range(1, (current_date - last_observed_date).days)
                ]
                holiday_records = _create_market_holiday_records(
                    last_observed_record, holiday_dates
                )
                normalized_records.extend(holiday_records)

        normalized_records.append(current_record)
        last_observed_record = current_record

    return normalized_records


def _has_market_holiday_gap(current_date: date, last_observed_date: date) -> bool:
    """두 관측일 사이에 하루를 초과하는 날짜 공백이 있는지 확인한다.

    Args:
        current_date: 현재 관측 레코드의 날짜.
        last_observed_date: 직전 관측 레코드의 날짜.
    Returns:
        두 날짜의 차이가 1일을 초과하면 True, 그렇지 않으면 False.
    Raises:
        ValueError: 현재 관측일이 직전 관측일보다 늦지 않은 경우.
    """
    if not last_observed_date:
        raise ValueError("empty last observed date")

    if current_date <= last_observed_date:
        raise ValueError("current observe date must later than the last observed date")

    # timedelta가 1초과(2일 이상)이면 휴장일
    return current_date - last_observed_date > timedelta(days=1)


def _create_market_holiday_records(
    last_observed_record: dict[str, float | date | None], holiday_dates: list[date]
) -> list[dict[str, float | date | None]]:
    """직전 관측 레코드의 금리 값을 복사하여 누락 날짜의 레코드를 생성한다.

    Args:
        last_observed_record: 금리 값을 복사할 직전 관측 레코드.
        holiday_dates: 레코드를 생성할 날짜 목록.
    Returns:
        지정된 날짜와 직전 관측 금리 값을 포함하는 레코드 목록.
    """
    last_observed_yields = {
        key: value for key, value in last_observed_record.items() if key != "date"
    }

    holiday_records: list[dict[str, float | date | None]] = []

    for holiday_date in holiday_dates:
        holiday_record = {
            "date": holiday_date,
            **last_observed_yields,
        }

        holiday_records.append(holiday_record)

    return holiday_records


def _fill_missing_maturities(
    record: dict[str, float | date | None],
) -> dict[str, float | date | None]:
    """레코드에 누락된 만기별 금리 필드를 None으로 채운다.

    Args:
        record: 날짜와 일부 만기별 금리 값을 포함하는 레코드.
    Returns:
        모든 만기별 금리 필드가 존재하는 레코드.
        기존 금리 값은 유지하고 누락된 필드에만 None을 설정한다.
    Notes:
        전달된 레코드 딕셔너리를 직접 수정한다.
    """

    for key in RECORD_KEY_MAP.values():
        if key.startswith("yield_"):
            record.setdefault(key, None)

    return record


def _apply_treasury_note_policy(
    current_record: dict[str, float | date | None],
) -> dict[str, float | date | None]:
    """Treasury의 만기별 제공 기간 정책에 따라 금리 값을 보정한다.

    만기별 최초 제공일 이전이거나 제공 중단 기간에 해당하는 날짜에
    금리 값이 존재하면 해당 값을 None으로 변경한다.

    Args:
        current_record: 만기별 제공 정책을 적용할 날짜 및 금리 레코드.
    Returns:
        만기별 제공 기간 정책이 적용된 레코드.
    Notes:
        전달된 레코드 딕셔너리를 직접 수정한다.
        정책 위반으로 금리 값이 변경되면 디버그 로그를 기록한다.
    """

    current_date = current_record["date"]

    for maturity, available_from in MATURITY_AVAILABLE_FROM.items():
        if current_date < available_from and current_record[maturity] is not None:
            logger.debug(
                "만기 시작일 정책 위반\n만기 종류: %s\n날짜: %s",
                maturity,
                current_date,
            )
            current_record[maturity] = None

    for maturity, available_periods in MATURITY_UNAVAILABLE_PERIODS.items():
        for start_date, end_date in available_periods:
            if (
                start_date <= current_date <= end_date
                and current_record[maturity] is not None
            ):
                logger.debug(
                    "만기 미제공 기간 정책 위반\n만기 종류: %s\n날짜: %s",
                    maturity,
                    current_date,
                )
                current_record[maturity] = None

    return current_record
