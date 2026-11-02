import pandas as pd
import pytest

import load_csv
from load_csv import _save


@pytest.fixture
def paths(tmp_path, monkeypatch):
    curve_path = tmp_path / "curve" / "test_curve.csv"
    spread_path = tmp_path / "spread" / "test_spread.csv"
    monkeypatch.setattr(load_csv, "CURVE_PATH", curve_path)
    monkeypatch.setattr(load_csv, "SPREAD_PATH", spread_path)
    return curve_path, spread_path


def test_save_csv_with_no_parent_dirs(valid_df, paths):
    curve_path, spread_path = paths

    _save(valid_df)

    assert curve_path.is_file()
    assert spread_path.is_file()


def test_each_csv_saved_to_its_own_path(valid_df, paths, monkeypatch):
    curve_path, spread_path = paths
    fake_spread = pd.DataFrame(
        {
            "date": valid_df["date"],
            "spread_10y_2y": [9.0, 9.0],
            "spread_10y_3m": [8.0, 8.0],
        }
    )
    monkeypatch.setattr(load_csv, "_to_spread", lambda df: fake_spread)

    _save(valid_df)
    pd.testing.assert_frame_equal(
        pd.read_csv(curve_path, parse_dates=["date"]), valid_df
    )
    pd.testing.assert_frame_equal(
        pd.read_csv(spread_path, parse_dates=["date"]), fake_spread
    )


def test_overwrites_existing_csv(valid_df, paths):
    curve_path, _ = paths
    curve_path.parent.mkdir(parents=True)
    curve_path.write_text("old,data\n1,2\n")

    _save(valid_df)

    pd.testing.assert_frame_equal(
        pd.read_csv(curve_path, parse_dates=["date"]), valid_df
    )
