from __future__ import annotations

import hashlib
import io
import logging
from dataclasses import dataclass

import pandas as pd
from sqlalchemy import Engine

from pipeline.validate.rules import BUSINESS_COLS

logger = logging.getLogger(__name__)

TABLE = "sales_transactions"
TABLE_COLUMNS = [
    "row_hash",
    "invoice_no",
    "stock_code",
    "description",
    "quantity",
    "invoice_date",
    "unit_price",
    "customer_id",
    "country",
    "is_cancellation",
    "is_non_product",
    "source_file",
    "source_row",
]


@dataclass
class LoadResult:
    attempted: int
    inserted: int

    @property
    def skipped(self) -> int:
        return self.attempted - self.inserted


def add_row_hash(df: pd.DataFrame) -> pd.DataFrame:
    """Add a sha256 `row_hash` over the business columns (deterministic, order-stable)."""
    joined = df[BUSINESS_COLS[0]].astype("string").fillna("")
    for col in BUSINESS_COLS[1:]:
        joined = joined + "|" + df[col].astype("string").fillna("")
    out = df.copy()
    out["row_hash"] = joined.map(
        lambda s: hashlib.sha256(s.encode("utf-8")).hexdigest()
    )
    return out


def load_sales(df: pd.DataFrame, engine: Engine) -> LoadResult:
    """Idempotent bulk load: COPY into a temp table, then INSERT ... ON CONFLICT DO NOTHING."""
    if df.empty:
        return LoadResult(attempted=0, inserted=0)

    prepared = add_row_hash(df)[TABLE_COLUMNS]
    cols = ", ".join(TABLE_COLUMNS)

    buffer = io.StringIO()
    prepared.to_csv(buffer, index=False, header=False)  # NA -> empty field -> NULL

    with engine.begin() as conn:
        cur = (
            conn.connection.cursor()
        )  # psycopg cursor; commit/rollback handled by engine.begin()
        cur.execute(
            f"CREATE TEMP TABLE _stage (LIKE {TABLE} INCLUDING DEFAULTS) ON COMMIT DROP"
        )
        with cur.copy(
            f"COPY _stage ({cols}) FROM STDIN WITH (FORMAT csv, NULL '')"
        ) as copy:
            copy.write(buffer.getvalue())
        cur.execute(
            f"INSERT INTO {TABLE} ({cols}) SELECT {cols} FROM _stage "
            "ON CONFLICT (row_hash) DO NOTHING"
        )
        inserted = cur.rowcount

    result = LoadResult(attempted=len(prepared), inserted=inserted)
    logger.info(
        "Loaded %d new rows (%d already present)", result.inserted, result.skipped
    )
    return result
