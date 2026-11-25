from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd


def write_rejected(
    rejected: pd.DataFrame, out_dir: Path, source_name: str
) -> Path | None:
    """Write rejected rows (with reasons) to data/rejected/. Returns the path, or None."""
    if rejected.empty:
        return None
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    path = out_dir / f"{Path(source_name).stem}_{stamp}_rejected.csv"
    rejected.to_csv(path, index=False)
    return path
