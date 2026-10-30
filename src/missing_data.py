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
    """데이터를 검증하고 결측 처리 정책을 적용한다."""

    last_observed_record: dict[str, str | date | None] = None
    normalized_records: list[dict[str, str | date | None]] = []

    for record in records:
        current_record = _fill_missing_maturities(record)
        current_record = _apply_treasury_note_policy(current_record)

        normalized_records.append(current_record)

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

    last_observed_record = current_record

    return normalized_records


def _has_market_holiday_gap(current_date: date, last_observed_date: date) -> bool:
    """마지막 영업일 날짜와 현재 날짜 사이에 영업일이 존재하는지 판별한다."""
    if not last_observed_date:
        raise ValueError("empty last observed date")

    if current_date <= last_observed_date:
        raise ValueError("current observe date must later than the last observed date")

    # timedelta가 1초과(2일 이상)이면 휴장일
    return current_date - last_observed_date > timedelta(days=1)


def _create_market_holiday_records(
    last_observed_record: dict[str, float | date | None], holiday_dates: list[date]
) -> list[dict[str, float | date | None]]:
    """직전 관측값의 금리로 휴장일 레코드를 생성한다."""
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
    """일드값이 없는 만기들을 None으로 채운다"""

    for key in RECORD_KEY_MAP.values():
        if key.startswith("yield_"):
            record.setdefault(key, None)

    return record


def _apply_treasury_note_policy(
    current_record: dict[str, float | date | None],
) -> dict[str, float | date | None]:
    """재무부 주석에 따른 검증과 보정을 한다"""

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
