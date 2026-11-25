"""Transformations for cleaning the data."""

from __future__ import annotations
import pandas as pd

RENAME_MAPPING = {
    "InvoiceNo": "invoice_no",
    "StockCode": "stock_code",
    "Description": "description",
    "Quantity": "quantity",
    "InvoiceDate": "invoice_date",
    "UnitPrice": "unit_price",
    "CustomerID": "customer_id",
    "Country": "country",
}


def data_to_int(s: pd.Series) -> pd.Series:
    """Parse to nullable integer.non-null values will be converted to integers, null values will remain as null."""
    n = pd.to_numeric(s, errors="coerce")
    return n.where(n % 1 == 0).astype("Int64")
