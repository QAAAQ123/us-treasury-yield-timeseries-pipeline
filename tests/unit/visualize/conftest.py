from datetime import date

import pandas as pd
import pytest

from load_csv import _to_spread


@pytest.fixture
def curve_df():
    return pd.DataFrame(
        [
            {
                "date": date(2026, 1, 2),
                "yield_1m": 3.60,
                "yield_1_5m": 3.62,
                "yield_2m": 3.65,
                "yield_3m": 3.70,
                "yield_4m": 3.72,
                "yield_6m": 3.75,
                "yield_1y": 3.80,
                "yield_2y": 3.90,
                "yield_3y": 4.00,
                "yield_5y": 4.10,
                "yield_7y": 4.20,
                "yield_10y": 4.30,
                "yield_20y": 4.50,
                "yield_30y": 4.60,
            },
            {
                "date": date(2026, 1, 3),
                "yield_1m": 3.55,
                "yield_1_5m": 3.57,
                "yield_2m": 3.60,
                "yield_3m": 3.65,
                "yield_4m": 3.67,
                "yield_6m": 3.70,
                "yield_1y": 3.75,
                "yield_2y": 3.80,
                "yield_3y": 3.90,
                "yield_5y": 4.00,
                "yield_7y": 4.10,
                "yield_10y": 4.20,
                "yield_20y": 4.40,
                "yield_30y": 4.50,
            },
        ]
    )


@pytest.fixture
def spread_df(curve_df):
    return _to_spread(curve_df)
