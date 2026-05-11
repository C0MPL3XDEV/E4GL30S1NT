"""Tests for eagleosint.display — constants and display_progress."""
import io
import sys

from eagleosint.display import (
    BLUE, RED, WHITE, SPACE_PREFIX, LINES_SEPARATOR,
    display_progress,
)


class TestColorConstants:
    def test_colors_are_ansi_strings(self):
        for color in (RED, BLUE, WHITE):
            assert color.startswith("\033[") or color.startswith("\u001b[")

    def test_space_prefix_is_nonempty(self):
        assert len(SPACE_PREFIX) > 0

    def test_lines_separator_starts_with_space_prefix(self):
        assert LINES_SEPARATOR.startswith(SPACE_PREFIX)


class TestDisplayProgress:
    def test_prints_percentage(self, capsys):
        display_progress(1, 4)
        captured = capsys.readouterr()
        assert "25.0%" in captured.out

    def test_full_progress_adds_newline(self, capsys):
        display_progress(4, 4)
        captured = capsys.readouterr()
        # final call must end with a newline
        assert captured.out.endswith("\n")

    def test_optional_text_appears_in_output(self, capsys):
        display_progress(2, 10, text="FOUND: 1")
        captured = capsys.readouterr()
        assert "FOUND: 1" in captured.out