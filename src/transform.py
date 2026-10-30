"""
XML 원천 데이터를 수집·파싱하고, 데이터 품질 검증을 거쳐 Wide Format DataFrame으로 변환한다.
책임: XML 파싱, 데이터 검증 및 DataFrame 변환
"""

from locale import normalize
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

EXCLUDED_FIELDS = {"Id", "BC_30YEARDISPLAY"}



def _parse_xml_records(xml_bytes: bytes) -> list[dict[str, str | None]]:
    """XML의 각 properties 요소를 딕셔너리로 변환한다.

    Args:
        xml_bytes: 파싱할 XML 응답 본문.
    Returns:
        각 properties 요소의 자식 태그 이름과 텍스트 값을 담은 목록.
        텍스트가 없는 요소의 값은 None이다.
    Raises:
        ET.ParseError: XML 형식이 올바르지 않은 경우.
    """
    xml_root = ET.fromstring(xml_bytes)

    properties_list = xml_root.findall(
        "atom:entry/atom:content/m:properties",  # properties 태그가 있는 경로
        PROPERTIES_NAMESPACE,
    )

    return [
        {value.tag.split("}")[-1]: value.text for value in property}
        for property in properties_list
    ]


def _select_date_and_yield_fields(records: list[dict[str, str]]) -> list[dict[str, str]]:
    """각 레코드에서 날짜와 대상 금리 필드만 남긴다.

    Args:
        records: XML에서 파싱한 레코드 목록.
    Returns:
        NEW_DATE와 BC_로 시작하는 금리 필드만 포함한 레코드 목록.
        BC_30YEARDISPLAY 필드는 제외한다.
    """
    return [
        {
            key: value
            for key, value in record.items()
            if key == "NEW_DATE"
            or (key.startswith("BC_") and not key.endswith("DISPLAY"))
        }
        for record in records
    ]


def _transform_types(
    original_records: list[dict[str, str]],
) -> list[dict[str, float | date | None]]:
    """원본 필드명을 매핑하고 날짜와 금리의 자료형을 변환한다."""
    transformed_records = []

    for record in original_records:
        transformed_record: dict[str, float | date | None] = {}

        for key, value in record.items():
            new_key = RECORD_KEY_MAP.get(key)
            if new_key is None:
                continue

            value = (value or "").strip()
            if new_key == "date":
                transformed_record[new_key] = datetime.fromisoformat(value).date()
            else:
                transformed_record[new_key] = (
                    float(value) if value else None
                )  # 금리 결측값은 None

        transformed_records.append(transformed_record)
    return transformed_records


def create_dataframe(normalized_records: list[dict[str, float | date | None]]) -> pd.DataFrame:
    """레코드를 날짜 오름차순으로 정렬후 DataFrame으로 변환한다."""

    normalized_records.sort(key=lambda record: record["date"])

    yield_dataframe = pd.DataFrame(
        normalized_records,
        columns=list(RECORD_KEY_MAP.values()),
    )

    return yield_dataframe
    




