"""Tests for eagleosint.session — shared Session and HEADERS."""
import requests

from eagleosint.session import HEADERS, session


class TestSession:
    def test_session_is_requests_session(self):
        assert isinstance(session, requests.Session)

    def test_headers_has_user_agent(self):
        assert "User-Agent" in HEADERS

    def test_session_headers_contain_user_agent(self):
        assert "User-Agent" in session.headers

    def test_headers_not_empty_string(self):
        assert HEADERS["User-Agent"].strip() != ""