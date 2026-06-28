"""Tests for eagleosint.audit module."""
from __future__ import annotations

import json
import os

import pytest

from eagleosint.audit import audit_log, _hash_query, AUDIT_LOG_PATH, SESSION_ID


@pytest.fixture()
def tmp_audit_log(tmp_path, monkeypatch):
    """Redirect audit log to a temporary file."""
    log_path = str(tmp_path / "audit.jsonl")
    monkeypatch.setattr("eagleosint.audit.AUDIT_LOG_PATH", log_path)
    return log_path


class TestHashQuery:

    def test_deterministic(self):
        assert _hash_query("test") == _hash_query("test")

    def test_different_inputs_differ(self):
        assert _hash_query("alice") != _hash_query("bob")

    def test_returns_hex_string(self):
        h = _hash_query("test")
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)


class TestAuditLog:

    def test_writes_jsonl_entry(self, tmp_audit_log):
        audit_log("query_start", "github", "octocat")
        with open(tmp_audit_log, "r") as f:
            lines = f.readlines()
        assert len(lines) == 1
        entry = json.loads(lines[0])
        assert entry["event"] == "query_start"
        assert entry["provider"] == "github"
        assert entry["session_id"] == SESSION_ID
        assert entry["success"] is True
        assert "timestamp" in entry

    def test_query_is_hashed_not_plaintext(self, tmp_audit_log):
        audit_log("query_start", "github", "secret_username")
        with open(tmp_audit_log, "r") as f:
            content = f.read()
        assert "secret_username" not in content
        assert _hash_query("secret_username") in content

    def test_append_mode(self, tmp_audit_log):
        audit_log("query_start", "github", "user1")
        audit_log("query_end", "github", "user1", result_count=3)
        with open(tmp_audit_log, "r") as f:
            lines = f.readlines()
        assert len(lines) == 2
        assert json.loads(lines[0])["event"] == "query_start"
        assert json.loads(lines[1])["event"] == "query_end"
        assert json.loads(lines[1])["result_count"] == 3

    def test_error_event(self, tmp_audit_log):
        audit_log(
            "query_error", "github", "user1",
            success=False, extra={"error": "timeout"},
        )
        with open(tmp_audit_log, "r") as f:
            entry = json.loads(f.readline())
        assert entry["success"] is False
        assert entry["extra"]["error"] == "timeout"

    def test_session_id_consistent(self, tmp_audit_log):
        audit_log("query_start", "github", "a")
        audit_log("query_start", "bitly", "b")
        with open(tmp_audit_log, "r") as f:
            lines = f.readlines()
        id1 = json.loads(lines[0])["session_id"]
        id2 = json.loads(lines[1])["session_id"]
        assert id1 == id2


class TestProviderRunAudit:
    """Test that BaseProvider.run() triggers audit logging."""

    def test_run_logs_start_and_end(self, tmp_audit_log, monkeypatch):
        from eagleosint.providers.github import GithubProvider
        from unittest.mock import MagicMock

        mock_resp = MagicMock()
        mock_resp.json.return_value = {"login": "test", "name": "Test"}
        mock_resp.raise_for_status.return_value = None
        monkeypatch.setattr(
            "eagleosint.providers.github._session.get",
            lambda *a, **kw: mock_resp,
        )

        provider = GithubProvider()
        results = provider.run("testuser")

        assert len(results) == 1
        with open(tmp_audit_log, "r") as f:
            lines = f.readlines()
        assert len(lines) == 2
        assert json.loads(lines[0])["event"] == "query_start"
        assert json.loads(lines[1])["event"] == "query_end"
        assert json.loads(lines[1])["result_count"] == 1