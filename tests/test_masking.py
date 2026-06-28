"""Tests for PII masking utilities."""
import pytest

from eagleosint.masking import (
    mask_email,
    mask_ip,
    mask_phone,
    mask_result,
    mask_results,
    mask_string,
    mask_value,
)
from eagleosint.models import (
    AccountHit,
    AccountStatus,
    EmailResult,
    EmailStatus,
    GitHubProfile,
    IPResult,
    PhoneResult,
)


class TestMaskEmail:
    def test_standard_email(self):
        assert mask_email("john.doe@gmail.com") == "joh***@gm***.com"

    def test_short_local(self):
        assert mask_email("ab@example.org") == "a***@ex***.org"

    def test_long_local(self):
        assert mask_email("administrator@company.net") == "adm***@co***.net"


class TestMaskPhone:
    def test_international(self):
        result = mask_phone("+39 333 1234567")
        assert result.startswith("393")
        assert result.endswith("567")
        assert "*" in result

    def test_short_number(self):
        assert mask_phone("1234") == "1234"

    def test_plain_digits(self):
        result = mask_phone("3331234567")
        assert result == "333****567"


class TestMaskIp:
    def test_ipv4(self):
        assert mask_ip("192.168.1.42") == "192.168.*.*"

    def test_preserves_first_two_octets(self):
        assert mask_ip("10.0.0.1") == "10.0.*.*"


class TestMaskString:
    def test_masks_email_in_text(self):
        text = "Contact john.doe@gmail.com for info"
        result = mask_string(text)
        assert "john.doe@gmail.com" not in result
        assert "joh***@gm***.com" in result

    def test_masks_ip_in_text(self):
        text = "Server at 192.168.1.42 is down"
        result = mask_string(text)
        assert "192.168.*.*" in result

    def test_no_pii(self):
        text = "No sensitive data here"
        assert mask_string(text) == text


class TestMaskValue:
    def test_pii_field_masked(self):
        assert "***" in mask_value("test@example.com", "email")

    def test_non_pii_field_unchanged(self):
        assert mask_value("test@example.com", "source") == "test@example.com"

    def test_list_recursion(self):
        result = mask_value(["test@a.com", "b@c.org"], "email")
        assert all("***" in v for v in result)

    def test_dict_recursion(self):
        data = {"email": "x@y.com", "name": "John"}
        result = mask_value(data)
        assert "***" in result["email"]
        assert result["name"] == "John"

    def test_non_string_passthrough(self):
        assert mask_value(42, "email") == 42
        assert mask_value(None, "email") is None
        assert mask_value(True, "phone") is True


class TestMaskResult:
    def test_email_result_masked(self):
        r = EmailResult(
            query="john", email="john@example.com", status=EmailStatus.VALID
        )
        masked = mask_result(r)
        assert "***" in masked["email"]
        assert masked["query"] == "john"
        assert masked["status"] == "valid"

    def test_phone_result_masked(self):
        r = PhoneResult(
            query="+391234567890", phone="+391234567890",
            international_number="+39 123 456 7890",
        )
        masked = mask_result(r)
        assert "***" not in masked["query"]
        assert "*" in masked["phone"]
        assert "*" in masked["international_number"]

    def test_ip_result_masked(self):
        r = IPResult(query="myip", ip="8.8.8.8", hostname="dns.google")
        masked = mask_result(r)
        assert masked["ip"] == "8.8.*.*"
        assert "***" in masked["hostname"]

    def test_account_hit_no_pii_fields(self):
        r = AccountHit(
            query="testuser", platform="github",
            url="https://github.com/testuser",
            status=AccountStatus.FOUND, http_status_code=200,
        )
        masked = mask_result(r)
        assert masked["url"] == "https://github.com/testuser"
        assert masked["platform"] == "github"

    def test_github_email_masked(self):
        r = GitHubProfile(
            query="octocat", username="octocat",
            email="octocat@github.com",
        )
        masked = mask_result(r)
        assert "***" in masked["email"]
        assert masked["username"] == "octocat"


class TestMaskResults:
    def test_multiple_results(self):
        results = [
            EmailResult(query="a", email="a@b.com", status=EmailStatus.VALID),
            EmailResult(query="b", email="x@y.org", status=EmailStatus.INVALID),
        ]
        masked = mask_results(results)
        assert len(masked) == 2
        assert all("***" in m["email"] for m in masked)

    def test_empty_list(self):
        assert mask_results([]) == []