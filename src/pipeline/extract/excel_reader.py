"""Excel reader"""

from __future__ import annotations
import logging
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)


from pipeline.exceptions import ExtractError


def read_sales_excel(
    path: Path, sheet_name: str | int = 0, header_row: int = 0
) -> pd.DataFrame:
    """Reads an Excel file without transforming its data value anf returns a pandas DataFrame."""
    path = Path(path)
    if not path.exists():
        raise ExtractError(f"File not found: {path}")
    if not path.is_file():
        raise ExtractError(f"Path is not a file: {path}")
    if path.suffix.lower() != ".xlsx":
        raise ExtractError(f"unsupported file type: {path.suffix!r}. expected '.xlsx'")
    if not isinstance(sheet_name, (str, int)):
        raise ExtractError(
            f"sheet_name must be a string or an integer, got {type(sheet_name)}"
        )
    if not isinstance(header_row, int):
        raise ExtractError(f"header_row must be an integer, got {type(header_row)}")
    try:
        df = pd.read_excel(
            path, sheet_name=sheet_name, header=header_row, dtype=str, engine="openpyxl"
        )
    except ImportError as exc:
        raise ExtractError(
            "Missing dependency for reading Excel files. Please install 'openpyxl'."
        ) from exc
    except Exception as exc:
        raise ExtractError(f"Failed to read Excel file: {exc}") from exc
    if df.empty and len(df.columns) == 0:
        raise ExtractError(f"Excel file is empty or has no columns: {path}")
    df = df.dropna(how="all").dropna(
        axis=1, how="all"
    )  # Drop rows where all elements are NaN
    # normalize header names
    normalized_columns = (
        pd.Index(df.columns.astype(str))
        .str.strip()
        .str.lower()
        .str.replace(r"\s+", "_", regex=True)
        .str.replace(r"[^a-z0-9_]", "", regex=True)
    )
    # Reject duplicate after normalize column names
    duplicate_columns = (
        normalized_columns[normalized_columns.duplicated()].unique().to_list()
    )
    if duplicate_columns:
        raise ExtractError(
            f"Duplicate column names found after normalization: {duplicate_columns}"
        )

    df.columns = normalized_columns

    # Reserve metadata names to avoid overwriting source columns
    reserved_metadata_names = {"source_row", "source_file"}
    collisions = reserved_metadata_names.intersection(df.columns)
    if collisions:
        raise ExtractError(
            f"Column names in the Excel file collide with reserved metadata names: {collisions}"
        )
    df["source_row"] = df.index + header_row + 2
    df["source_file"] = path.name
    return df
