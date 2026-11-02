import pandas as pd
import pytest

from load_csv import CURVE_DTYPE_MAP


@pytest.fixture
def valid_df() -> pd.DataFrame:
    data = {col: [1.0, 2.0] for col in CURVE_DTYPE_MAP if col != "date"}
    data["date"] = pd.to_datetime(["2024-01-01", "2024-01-02"])
    return pd.DataFrame(data)
