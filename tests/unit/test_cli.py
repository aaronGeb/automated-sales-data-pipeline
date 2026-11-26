from typer.testing import CliRunner

from pipeline.main import app

runner = CliRunner()


def test_run_rejects_missing_file(tmp_path):
    result = runner.invoke(app, ["run", str(tmp_path / "nope.xlsx")])
    assert result.exit_code == 2  # Typer's argument validation, before any stage runs


def test_run_help_shows_archive_default():
    result = runner.invoke(app, ["run", "--help"])
    assert result.exit_code == 0
    assert "--no-archive" in result.output
