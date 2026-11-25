from __future__ import annotations

import logging
import sys
from pathlib import Path


def setup_logging(log_dir: Path, level: int = logging.INFO) -> None:
    """Log to the console and to logs/pipeline.log."""
    log_dir.mkdir(parents=True, exist_ok=True)
    fmt = logging.Formatter("%(asctime)s %(levelname)-7s %(name)s: %(message)s")
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    for handler in (
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(log_dir / "pipeline.log"),
    ):
        handler.setFormatter(fmt)
        root.addHandler(handler)
