"""
XML 원천 데이터를 수집·파싱하고, Wide Format DataFrame으로 변환한다.(품질 검증은 missing_data에서 진행)
책임: XML 파싱, 데이터 타입 변환 및 DataFrame 변환
"""

import xml.etree.ElementTree as ET
from datetime import date, datetime

import pandas as pd

from logger_config import logger

PROPERTIES_NAMESPACE = {
    "atom": "http://www.w3.org/2005/Atom",
    "m": "http://schemas.microsoft.com/ado/2007/08/dataservices/metadata",
}

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


def _parse_xml_records(xml_bytes: bytes) -> list[dict[str, str | None]]:
    """XML의 각 properties 요소를 딕셔너리로 변환한다.

    Args:
        xml_bytes: 파싱할 XML 응답 본문.
    Returns:
        각 properties 요소의 자식 태그 이름과 텍스트 값을 담은 목록.
        텍스트가 없는 요소의 값은 None이다. 입력이 비어 있으면 빈 목록을 반환한다.
    Raises:
        ET.ParseError: XML 형식이 올바르지 않은 경우.
    """

    if not xml_bytes:
        logger.warning("XML 응답 본문이 비어 있음")
        return []

    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        logger.exception("XML 파싱 실패: size=%d bytes", len(xml_bytes))
        raise

    properties_elements = root.findall(
        "atom:entry/atom:content/m:properties",  # properties 태그가 있는 경로
        PROPERTIES_NAMESPACE,
    )

    records = [
        {child.tag.split("}")[-1]: child.text for child in properties_element}
        for properties_element in properties_elements
    ]
    logger.debug("XML 레코드 파싱 완료: %d건", len(records))

    return records


def _select_record_fields(
    records: list[dict[str, str | None]],
) -> list[dict[str, str | None]]:
    """각 레코드에서 날짜와 대상 금리 필드만 남긴다.

    Args:
        records: XML에서 파싱한 레코드 목록.
    Returns:
        NEW_DATE와 BC_로 시작하는 금리 필드만 포함한 레코드 목록.
        BC_30YEARDISPLAY 필드는 제외한다.
    """
    selected_records = [
        {
            key: value
            for key, value in record.items()
            if key == "NEW_DATE"
            or (key.startswith("BC_") and not key.endswith("DISPLAY"))
        }
        for record in records
    ]
    logger.debug("대상 필드 선별 완료: %d건", len(selected_records))

    return selected_records


def _convert_record_types(
    records: list[dict[str, str | None]],
) -> list[dict[str, float | date | None]]:
    """원본 필드명을 매핑하고 날짜와 금리의 자료형을 변환한다.

    Args:
        records: 필드가 선별된 레코드 목록.
    Returns:
        필드명이 RECORD_KEY_MAP 기준으로 바뀌고, 날짜는 date, 금리는 float로
        변환된 레코드 목록. 금리 결측값은 None이다. RECORD_KEY_MAP에 없는
        필드는 제외한다.
    Raises:
        ValueError: 날짜 또는 금리 값을 변환할 수 없는 경우.
    """
    converted_records = []

    for record in records:
        converted_record: dict[str, float | date | None] = {}

        try:
            for source_key, raw_value in record.items():
                field_name = RECORD_KEY_MAP.get(source_key)
                if field_name is None:
                    continue

                text = (raw_value or "").strip()
                if field_name == "date":
                    converted_record[field_name] = datetime.fromisoformat(text).date()
                else:
                    converted_record[field_name] = (
                        float(text) if text else None
                    )  # 금리 결측값은 None
        except ValueError:
            logger.exception("자료형 변환 실패: record=%s", record)
            raise

        converted_records.append(converted_record)

    logger.debug("자료형 변환 완료: %d건", len(converted_records))

    return converted_records


def create_yield_curve_dataframe(
    records: list[dict[str, float | date | None]],
) -> pd.DataFrame:
    """레코드를 날짜 오름차순으로 정렬한 뒤 DataFrame으로 변환한다.

    Args:
        records: 자료형 변환이 끝난 레코드 목록. 정렬 시 입력 목록이 제자리에서
            변경된다.
    Returns:
        RECORD_KEY_MAP의 값을 열 순서로 갖는 Wide Format DataFrame.
        레코드에 없는 열은 결측값으로 채워진다.
    """
    records.sort(key=lambda record: record["date"])

    yield_curve_dataframe = pd.DataFrame(
        records,
        columns=list(RECORD_KEY_MAP.values()),
    )

    if yield_curve_dataframe.empty:
        logger.warning("생성된 DataFrame이 비어 있음")
    else:
        logger.info(
            "DataFrame 생성 완료: %d행, 기간 %s ~ %s",
            len(yield_curve_dataframe),
            yield_curve_dataframe["date"].iloc[0],
            yield_curve_dataframe["date"].iloc[-1],
        )

    return yield_curve_dataframe


def parse_yield_curve_records(xml_bytes: bytes) -> list[dict[str, float | date | None]]:
    """Treasury 금리 XML을 파싱하여 날짜와 금리 필드를 추출하고 자료형을 변환한다.

    Args:
        xml_bytes: Treasury 금리 XML 응답 본문.
    Returns:
        날짜(date)와 만기별 금리(float 또는 None)를 담은 레코드 목록.
        추출된 데이터가 없으면 빈 목록을 반환한다.
    Raises:
        ET.ParseError: XML 형식이 올바르지 않은 경우.
        ValueError: 날짜 또는 금리 값을 변환할 수 없는 경우.
    """
    raw_records = _parse_xml_records(xml_bytes)

    if not raw_records:
        logger.warning("추출한 데이터 없음")
        return []

    selected_records = _select_record_fields(raw_records)
    converted_records = _convert_record_types(selected_records)
    logger.info("금리 레코드 파싱 완료: %d건", len(converted_records))

    return converted_records
