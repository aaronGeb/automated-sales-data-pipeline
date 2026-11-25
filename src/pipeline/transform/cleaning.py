"""Transformations for cleaning the data."""

from __future__ import annotations

import pandas as pd

RENAME_MAP = {
    "invoiceno": "invoice_no",
    "stockcode": "stock_code",
    "unitprice": "unit_price",
    "invoicedate": "invoice_date",
    "customerid": "customer_id",
}


def _to_int(s: pd.Series) -> pd.Series:
    """Parse to nullable integer; non-numeric or fractional values become NA."""
    n = pd.to_numeric(s, errors="coerce")
    return n.where(n % 1 == 0).astype("Int64")


def clean_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize and cast types. Never drops rows: rejecting is validate's job."""
    out = df.rename(columns=RENAME_MAP).copy()

    for col in ("invoice_no", "stock_code", "description", "country"):
        out[col] = out[col].str.strip()
    out["invoice_no"] = out["invoice_no"].str.upper()
    out["stock_code"] = out["stock_code"].str.upper()
    out["description"] = out["description"].replace("", pd.NA)

    out["quantity"] = _to_int(out["quantity"])
    out["customer_id"] = _to_int(out["customer_id"])
    out["unit_price"] = pd.to_numeric(out["unit_price"], errors="coerce")
    out["invoice_date"] = pd.to_datetime(out["invoice_date"], errors="coerce")

    out["is_cancellation"] = out["invoice_no"].str.startswith("C", na=False)
    return out
