"""Tests for the structured output serialization module"""
import csv
import io
import json

import pytest

from eagleosint.models import URLExpansion, GitHubProfile
from eagleosint.output import write_results

def _url_result():
    return URLExpansion(
        source="bitly",
        query="https://bit.ly/abc",
        short_url="https://bit.ly/abc",
        original_url="https://example.com/real-page",
    )

class TestJsonOutput:
    def test_single_result_is_json_list(self):
        buf = io.StringIO()
        write_results([_url_result()], "json", buf)
        data = json.loads(buf.getvalue())
        assert isinstance(data, list)
        assert len(data) == 1

    def test_result_fields_present(self):
        buf = io.StringIO()
        write_results([_url_result()], "json", buf)
        item = json.loads(buf.getvalue())[0]
        assert item["source"] == "bitly"
        assert item["original_url"] == "https://example.com/real-page"

    def test_empty_list_writes_nothing(self):
        buf = io.StringIO()
        write_results([], "json", buf)
        assert buf.getvalue() == ""

    def test_multiple_results(self):
        buf = io.StringIO()
        write_results([_url_result(), _url_result()], "json", buf)
        data = json.loads(buf.getvalue())
        assert len(data) == 2


class TestCsvOutput:
    def test_header_row_present(self):
        buf = io.StringIO()
        write_results([_url_result()], "csv", buf)
        reader = csv.DictReader(io.StringIO(buf.getvalue()))
        assert reader.fieldnames is not None
        assert "source" in reader.fieldnames
        assert "original_url" in reader.fieldnames

    def test_data_row_values(self):
        buf = io.StringIO()
        write_results([_url_result()], "csv", buf)
        rows = list(csv.DictReader(io.StringIO(buf.getvalue())))
        assert len(rows) == 1
        assert rows[0]["original_url"] == "https://example.com/real-page"

    def test_empty_list_writes_nothing(self):
        buf = io.StringIO()
        write_results([], "csv", buf)
        assert buf.getvalue() == ""

class TestInvalidFormat:
    def test_unknown_format_raises(self):
        with pytest.raises(ValueError, match="unsupported output format"):
            write_results([_url_result()], "xml")