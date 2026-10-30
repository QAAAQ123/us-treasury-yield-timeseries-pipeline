import xml.etree.ElementTree as ET

import pytest

from transform import _parse_xml_records


def test_valid_xml_returns_parsed_records():
    fake_xml = b"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata"
      xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices"
      xml:base="https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml">
    <title type="text">DailyTreasuryYieldCurveRateData</title>
    <id>https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml-item?data=daily_treasury_yield_curve</id>
    <updated>2026-10-26T15:50:19Z</updated>
    <entry>
        <title type="text"/>
        <updated>2026-10-26T15:50:19Z</updated>
        <content type="application/xml">
            <m:properties>
                <d:NEW_DATE m:type="Edm.DateTime">2024-01-02T00:00:00</d:NEW_DATE>
                <d:BC_1MONTH m:type="Edm.Double">5.55</d:BC_1MONTH>
                <d:BC_2MONTH m:type="Edm.Double">5.54</d:BC_2MONTH>
                <d:BC_3MONTH m:type="Edm.Double">5.46</d:BC_3MONTH>
                <d:BC_4MONTH m:type="Edm.Double">5.41</d:BC_4MONTH>
                <d:BC_6MONTH m:type="Edm.Double">5.24</d:BC_6MONTH>
                <d:BC_1YEAR m:type="Edm.Double">4.80</d:BC_1YEAR>
                <d:BC_2YEAR m:type="Edm.Double">4.33</d:BC_2YEAR>
                <d:BC_3YEAR m:type="Edm.Double">4.09</d:BC_3YEAR>
                <d:BC_5YEAR m:type="Edm.Double">3.93</d:BC_5YEAR>
                <d:BC_7YEAR m:type="Edm.Double">3.95</d:BC_7YEAR>
                <d:BC_10YEAR m:type="Edm.Double">3.95</d:BC_10YEAR>
                <d:BC_20YEAR m:type="Edm.Double">4.25</d:BC_20YEAR>
                <d:BC_30YEAR m:type="Edm.Double">4.08</d:BC_30YEAR>
                <d:BC_30YEARDISPLAY m:type="Edm.Double">4.08</d:BC_30YEARDISPLAY>
            </m:properties>
        </content>
    </entry>
    <entry>
        <title type="text"/>
        <updated>2026-10-26T15:50:19Z</updated>
        <content type="application/xml">
            <m:properties>
                <d:NEW_DATE m:type="Edm.DateTime">2024-01-03T00:00:00</d:NEW_DATE>
                <d:BC_1MONTH m:type="Edm.Double">5.54</d:BC_1MONTH>
                <d:BC_2MONTH m:type="Edm.Double">5.54</d:BC_2MONTH>
                <d:BC_3MONTH m:type="Edm.Double">5.48</d:BC_3MONTH>
                <d:BC_4MONTH m:type="Edm.Double">5.41</d:BC_4MONTH>
                <d:BC_6MONTH m:type="Edm.Double">5.25</d:BC_6MONTH>
                <d:BC_1YEAR m:type="Edm.Double">4.81</d:BC_1YEAR>
                <d:BC_2YEAR m:type="Edm.Double">4.33</d:BC_2YEAR>
                <d:BC_3YEAR m:type="Edm.Double">4.07</d:BC_3YEAR>
                <d:BC_5YEAR m:type="Edm.Double">3.90</d:BC_5YEAR>
                <d:BC_7YEAR m:type="Edm.Double">3.92</d:BC_7YEAR>
                <d:BC_10YEAR m:type="Edm.Double">3.91</d:BC_10YEAR>
                <d:BC_20YEAR m:type="Edm.Double">4.21</d:BC_20YEAR>
                <d:BC_30YEAR m:type="Edm.Double">4.05</d:BC_30YEAR>
                <d:BC_30YEARDISPLAY m:type="Edm.Double">4.05</d:BC_30YEARDISPLAY>
            </m:properties>
        </content>
    </entry>
</feed>
"""

    result = _parse_xml_records(fake_xml)

    assert len(result) == 2
    assert result[0]["NEW_DATE"] == "2024-01-02T00:00:00"
    assert result[0]["BC_10YEAR"] == "3.95"
    assert result[1]["NEW_DATE"] == "2024-01-03T00:00:00"
    assert result[1]["BC_10YEAR"] == "3.91"


def test_empty_property_text_returns_none():
    fake_xml = b"""<?xml version="1.0" encoding="utf-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom"
          xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata"
          xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices">
        <entry>
            <content type="application/xml">
                <m:properties>
                    <d:NEW_DATE m:type="Edm.DateTime">2024-01-02T00:00:00</d:NEW_DATE>
                    <d:BC_10YEAR m:type="Edm.Double"/>
                </m:properties>
            </content>
        </entry>
    </feed>
    """

    result = _parse_xml_records(fake_xml)

    assert result == [
        {
            "NEW_DATE": "2024-01-02T00:00:00",
            "BC_10YEAR": None,
        }
    ]


def test_invalid_xml_raises_parse_error():
    with pytest.raises(ET.ParseError):
        _parse_xml_records(b"<feed>")
