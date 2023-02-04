# vim:fenc=utf-8
from click.testing import CliRunner

from mightstone import cli


def test_true():
    assert 1 == 1


def test_click_cli_help():
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(cli.cli, ["--help"])
    assert result.exit_code == 0
    assert "edhrec" in result.output
    assert "version" in result.stdout
    assert "" == result.stderr


def test_click_edhrec_help():
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(cli.edhrec, ["--help"])
    assert result.exit_code == 0
    assert "cards" in result.output
    assert "combo" in result.output
    assert "combos" in result.output
    assert "commander" in result.output
    assert "commanders" in result.output
    assert "partners" in result.output
    assert "salt" in result.output
    assert "sets" in result.output
    assert "themes" in result.output
    assert "top-cards" in result.stdout
    assert "tribes" in result.stdout
    assert "" == result.stderr
