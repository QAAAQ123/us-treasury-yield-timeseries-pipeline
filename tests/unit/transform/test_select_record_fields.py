from transform import _select_record_fields


def test_more_than_two_records_with_mixed_fields_returns_only_date_and_yield_fields():
    fake_records = [
        {
            "NEW_DATE": "2026-10-23T00:00:00",
            "BC_1MONTH": "3.8",
            "Id": "1",
            "OTHER_FIELD": "value",
        },
        {
            "NEW_DATE": "2026-10-26T00:00:00",
            "BC_2MONTH": "3.7",
            "Id": "2",
            "OTHER_FIELD": "value",
        },
        {
            "NEW_DATE": "2026-10-27T00:00:00",
            "BC_10YEAR": "4.1",
            "Id": "3",
            "OTHER_FIELD": "value",
        },
    ]

    expected_records = [
        {"NEW_DATE": "2026-10-23T00:00:00", "BC_1MONTH": "3.8"},
        {"NEW_DATE": "2026-10-26T00:00:00", "BC_2MONTH": "3.7"},
        {"NEW_DATE": "2026-10-27T00:00:00", "BC_10YEAR": "4.1"},
    ]

    result = _select_record_fields(fake_records)

    assert result == expected_records


def test_records_with_display_tag_returns_only_date_and_yield_fields():
    fake_records = [
        {
            "NEW_DATE": "2026-10-27T00:00:00",
            "BC_1MONTH": "3.8",
            "BC_30YEARDISPLAY": "4.5",
            "Id": "1",
        }
    ]

    expected_records = [
        {
            "NEW_DATE": "2026-10-27T00:00:00",
            "BC_1MONTH": "3.8",
        }
    ]

    result = _select_record_fields(fake_records)

    assert result == expected_records


def test_empty_records_returns_empty_list():
    fake_records = []

    result = _select_record_fields(fake_records)

    assert result == []
