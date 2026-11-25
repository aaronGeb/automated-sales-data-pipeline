from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd
from sqlalchemy import Engine, text

logger = logging.getLogger(__name__)


def generate_reports(
    engine: Engine,
    out_dir: Path = Path("reports"),
    sql_dir: Path = Path("sql/analytics"),
) -> list[Path]:
    """Run every .sql file in sql_dir and write its result to out_dir/<name>.csv.

    Reports are a snapshot of the current table, so each run overwrites the last.
    """
    sql_files = sorted(sql_dir.glob("*.sql"))
    if not sql_files:
        raise FileNotFoundError(f"No .sql files found in {sql_dir}")

    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for sql_file in sql_files:
        with engine.connect() as conn:
            df = pd.read_sql_query(text(sql_file.read_text()), conn)
        path = out_dir / f"{sql_file.stem}.csv"
        df.to_csv(path, index=False)
        logger.info("Report %s: %d rows -> %s", sql_file.stem, len(df), path)
        written.append(path)
    return written
