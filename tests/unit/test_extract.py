"""Test the Excel reader functions."""

import pandas as pd
import pytest

from pipeline.extract.excel_reader import ExtractError, read_sales_excel


def test_reads_and_normalizes_headers(tmp_path):
    f = tmp_path / "sales.xlsx"
    pd.DataFrame({"Order ID": ["A1"], "Order Date ": ["2026-01-05"]}).to_excel(
        f, index=False
    )

    df = read_sales_excel(f)

    assert {"order_id", "order_date", "source_row", "source_file"} <= set(df.columns)
    assert df.loc[0, "source_row"] == 2


def test_missing_file_raises(tmp_path):
    with pytest.raises(ExtractError):
        read_sales_excel(tmp_path / "nope.xlsx")


def test_drops_blank_rows_and_keeps_excel_row_numbers(tmp_path):
    f = tmp_path / "sales.xlsx"
    pd.DataFrame({"Order ID": ["A1", None, "A3"]}).to_excel(f, index=False)

    df = read_sales_excel(f)

    assert df["order_id"].tolist() == ["A1", "A3"]
    assert df["source_row"].tolist() == [
        2,
        4,
    ]  # blank row 3 is skipped, numbering preserved
    assert (df["source_file"] == "sales.xlsx").all()
