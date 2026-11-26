from __future__ import annotations

import logging
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Annotated

import typer

from pipeline.config import get_settings
from pipeline.exceptions import LoadError, PipelineError
from pipeline.extract.excel_reader import read_sales_excel
from pipeline.load.database import get_engine
from pipeline.load.loader import load_sales
from pipeline.logger import setup_logging
from pipeline.report.generator import generate_reports
from pipeline.transform.cleaning import clean_sales
from pipeline.validate.quarantine import write_rejected
from pipeline.validate.rules import validate_sales

app = typer.Typer(help="Automated sales data pipeline.", no_args_is_help=True)
logger = logging.getLogger("pipeline")


@app.callback()
def main() -> None:
    """Sales pipeline commands."""


@app.command()
def run(
    file: Annotated[
        Path, typer.Argument(exists=True, dir_okay=False, help="Path to the .xlsx file")
    ],
    archive: Annotated[
        bool,
        typer.Option(help="Copy the file to data/processed/ after a successful load"),
    ] = True,
) -> None:
    """Run extract -> clean -> validate -> load for one Excel file."""
    settings = get_settings()
    setup_logging(settings.log_dir)
    started = time.time()
    logger.info("Starting run for %s", file.name)

    try:
        df = read_sales_excel(file)
        logger.info("Extract: %d rows", len(df))

        df = clean_sales(df)
        logger.info("Transform: %d rows cleaned", len(df))

        result = validate_sales(df, schema_path=settings.schema_path)
        logger.info(
            "Validate: %d valid, %d rejected", len(result.valid), len(result.rejected)
        )

        rejected_path = write_rejected(
            result.rejected, settings.rejected_dir, file.name
        )
        if rejected_path:
            logger.info("Quarantine: rejected rows written to %s", rejected_path)

        try:
            load = load_sales(result.valid, get_engine(settings.database_url))
        except Exception as exc:
            raise LoadError(f"Load failed, nothing was committed: {exc}") from exc
        logger.info(
            "Load: %d inserted, %d already present", load.inserted, load.skipped
        )
        generate_reports(get_engine(settings.database_url), settings.reports_dir)

        if archive:
            settings.processed_dir.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now().strftime("%Y%m%dT%H%M%S")
            dest = settings.processed_dir / f"{file.stem}_{stamp}{file.suffix}"
            shutil.copy2(file, dest)
            logger.info("Archive: copied source to %s", dest)

    except PipelineError as exc:
        logger.error("Run failed: %s", exc)
        raise typer.Exit(code=1) from exc
    except Exception:
        logger.exception("Unexpected failure")
        raise typer.Exit(code=2)

    logger.info("Done in %.1fs", time.time() - started)


@app.command()
def report() -> None:
    """Generate CSV reports from the loaded data into reports/."""
    settings = get_settings()
    setup_logging(settings.log_dir)
    try:
        generate_reports(get_engine(settings.database_url), settings.reports_dir)
    except Exception:
        logger.exception("Report generation failed")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
