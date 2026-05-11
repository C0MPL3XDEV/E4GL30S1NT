"""Tests for eagleosint.cli — Click group wiring."""
from click.testing import CliRunner

from eagleosint.cli import main


class TestCliHelp:
    def test_help_exits_zero(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0

    def test_help_lists_all_commands(self):
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])
        for cmd in (
            "userrecon", "facedumper", "mailfinder", "godorker",
            "phoneinfo", "dns", "whois", "subnet", "hostfinder",
            "dnsfinder", "riplookup", "iplocation", "bitly",
            "github", "tempmail", "update", "settings",
        ):
            assert cmd in result.output

    def test_unknown_command_exits_nonzero(self):
        runner = CliRunner()
        result = runner.invoke(main, ["doesnotexist"])
        assert result.exit_code != 0

    def test_github_subcommand_help(self):
        runner = CliRunner()
        result = runner.invoke(main, ["github", "--help"])
        assert result.exit_code == 0
        assert "GitHub" in result.output