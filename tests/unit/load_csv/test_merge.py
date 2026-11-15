import pandas as pd
from pandas.testing import assert_frame_equal, assert_index_equal

from load_csv import _merge


def test_empty_new_df_returns_old_df(valid_df):
    old_df = valid_df.copy()
    new_df = valid_df.iloc[0:0].copy()

    merged_df, added_dates, changed_yields = _merge(old_df, new_df)

    assert_frame_equal(
        merged_df,
        old_df.sort_values("date", ignore_index=True),
    )
    assert added_dates.empty
    assert changed_yields.empty


def test_empty_old_df_returns_new_df(valid_df):
    old_df = valid_df.iloc[0:0].copy()
    new_df = valid_df.copy()

    merged_df, added_dates, changed_yields = _merge(old_df, new_df)

    assert_frame_equal(
        merged_df,
        new_df.sort_values("date", ignore_index=True),
    )
    assert_index_equal(added_dates, pd.DatetimeIndex(new_df["date"], name="date"))
    assert changed_yields.empty


def test_unchanged_values_returns_empty_changed_yields(valid_df):
    old_df = valid_df.copy()
    new_df = valid_df.copy()

    merged_df, added_dates, changed_yields = _merge(old_df, new_df)

    assert_frame_equal(
        merged_df,
        old_df.sort_values("date", ignore_index=True),
    )
    assert added_dates.empty
    assert changed_yields.empty


def test_changed_values_returns_changed_yields(valid_df):
    old_df = valid_df.copy()
    new_df = valid_df.copy()

    new_df.loc[0, "yield_2y"] = 9.0

    merged_df, added_dates, changed_yields = _merge(old_df, new_df)

    assert merged_df.loc[0, "yield_2y"] == 9.0
    assert added_dates.empty

    assert changed_yields.loc[pd.Timestamp("2024-01-01"), ("yield_2y", "self")] == 9.0
    assert changed_yields.loc[pd.Timestamp("2024-01-01"), ("yield_2y", "other")] == 1.0


def test_new_dates_are_added_to_merged_df(valid_df):
    old_df = valid_df.iloc[[0]].copy()
    new_df = valid_df.iloc[[1]].copy()

    merged_df, added_dates, changed_yields = _merge(old_df, new_df)

    assert_frame_equal(
        merged_df,
        valid_df.sort_values("date", ignore_index=True),
    )
    assert_index_equal(
        added_dates,
        pd.DatetimeIndex(["2024-01-02"], name="date"),
    )
    assert changed_yields.empty


def test_new_dates_and_changed_values_are_merged(valid_df):
    old_df = valid_df.copy()

    # 기존 날짜의 금리 값 변경
    changed_row = valid_df.iloc[[0]].copy()
    changed_row.loc[:, "yield_2y"] = 9.0

    # 신규 날짜 추가
    added_row = valid_df.iloc[[1]].copy()
    added_row.loc[:, "date"] = pd.Timestamp("2024-01-03")

    new_df = pd.concat([changed_row, added_row], ignore_index=True)

    merged_df, added_dates, changed_yields = _merge(old_df, new_df)

    expected_df = pd.concat(
        [
            old_df.iloc[[1]],
            changed_row,
            added_row,
        ],
        ignore_index=True,
    ).sort_values("date", ignore_index=True)

    assert_frame_equal(merged_df, expected_df)
    assert_index_equal(
        added_dates,
        pd.DatetimeIndex(["2024-01-03"], name="date"),
    )

    assert changed_yields.loc[pd.Timestamp("2024-01-01"), ("yield_2y", "self")] == 9.0
    assert changed_yields.loc[pd.Timestamp("2024-01-01"), ("yield_2y", "other")] == 1.0


def test_only_changed_columns_are_included_in_changed_yields(valid_df):
    old_df = valid_df.copy()
    new_df = valid_df.copy()

    new_df.loc[0, "yield_2y"] = 9.0

    _, _, changed_yields = _merge(old_df, new_df)

    assert list(changed_yields.columns) == [
        ("yield_2y", "self"),
        ("yield_2y", "other"),
    ]
    assert_index_equal(
        changed_yields.index,
        pd.DatetimeIndex(["2024-01-01"], name="date"),
    )
