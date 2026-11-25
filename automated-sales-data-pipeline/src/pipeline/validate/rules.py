from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import yaml

DEFAULT_SCHEMA = Path("config/schemas/sales_schema.yaml")
INVOICE_PATTERN = r"^[CA]?\d{6}$"
BUSINESS_COLS = [
    "invoice_no",
    "stock_code",
    "description",
    "quantity",
    "invoice_date",
    "unit_price",
    "customer_id",
    "country",
]


@dataclass
class ValidationResult:
    valid: pd.DataFrame
    rejected: pd.DataFrame  # original columns + reject_reason


def load_schema(path: Path = DEFAULT_SCHEMA) -> dict:
    data = yaml.safe_load(Path(path).read_text()) or {}
    columns = data.get("columns")
    if not columns:
        raise ValueError(f"No 'columns' defined in schema file: {path}")
    return columns


def validate_sales(
    df: pd.DataFrame,
    schema_path: Path = DEFAULT_SCHEMA,
    now: pd.Timestamp | None = None,
) -> ValidationResult:
    """Split rows into valid and rejected; every rejected row gets all its reasons."""
    schema = load_schema(schema_path)
    now = now or pd.Timestamp.now()
    checks: dict[str, pd.Series] = {}

    # Contract-driven: non-nullable columns must be present (a failed cast is NA too)
    for col, spec in schema.items():
        if not spec["nullable"]:
            checks[f"missing_or_invalid_{col}"] = df[col].isna()

    inv = df["invoice_no"]
    qty = df["quantity"]
    cancel = df["is_cancellation"]

    # Business rules
    checks["invalid_invoice_no"] = inv.notna() & ~inv.str.match(
        INVOICE_PATTERN, na=False
    )
    checks["accounting_adjustment"] = inv.str.startswith("A", na=False)
    checks["zero_quantity"] = qty == 0
    checks["negative_quantity_not_cancellation"] = (qty < 0) & ~cancel
    checks["positive_quantity_on_cancellation"] = (qty > 0) & cancel
    checks["non_positive_unit_price"] = df["unit_price"] <= 0
    checks["future_invoice_date"] = df["invoice_date"] > now
    checks["duplicate_row"] = df.duplicated(subset=BUSINESS_COLS, keep="first")

    reasons = pd.Series([""] * len(df), index=df.index)
    for name, mask in checks.items():
        mask = mask.fillna(False).astype(bool)  # comparisons on NA yield NA
        reasons[mask] = reasons[mask] + (name + ";")

    bad = reasons != ""
    rejected = df[bad].assign(reject_reason=reasons[bad].str.rstrip(";"))
    return ValidationResult(valid=df[~bad].copy(), rejected=rejected)
