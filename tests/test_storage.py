"""Tests for the SQLite storage layer - uses in-memory SQLite throughout"""
import pytest
import eagleosint.storage as storage
from eagleosint.models import GitHubProfile, URLExpansion, IPResult, DomainResult

@pytest.fixture(autouse=True)
def fresh_db():
    """Each test gets an isolated in-memory database."""
    storage.init_db("sqlite:///:memory:")
    yield
    storage._engine.dispose()


# -------------------------------------------------------------
# Investigation CRUD
# -------------------------------------------------------------

class TestCreateInvestigation:
    def test_returns_row_with_correct_name(self):
        row = storage.create_investigation("John Doe")
        assert row.name == "John Doe"

    def test_id_contains_slug(self):
        row = storage.create_investigation("Test Case")
        assert "test-case" in row.id

    def test_tags_stored_as_json(self):
        row = storage.create_investigation("X", tags=["phishing", "apt"])
        import json
        assert json.loads(row.tags) == ["phishing", "apt"]

    def test_empty_tags_default(self):
        row =  storage.create_investigation("Y")
        import json
        assert json.loads(row.tags) == []

class TestGetInvestigation:
    def test_returns_none_for_unknown_id(self):
        assert storage.get_investigation("does-not-exist") is None

    def test_returns_row_for_known_id(self):
        row = storage.create_investigation("Alpha")
        fetched = storage.get_investigation(row.id)
        assert fetched is not None
        assert fetched.name == "Alpha"

class TestListInvestigation:
    def test_empty_db_returns_empty_list(self):
        assert storage.list_investigations() == []

    def test_returns_all_investigations(self):
        storage.create_investigation("A")
        storage.create_investigation("B")
        rows = storage.list_investigations()
        assert len(rows) == 2

    def test_ordered_newest_first(self):
        storage.create_investigation("First")
        storage.create_investigation("Second")
        rows = storage.list_investigations()
        assert rows[0].name == "Second"


class TestDeleteInvestigation:
    def test_returns_false_for_missing(self):
        assert storage.delete_investigation("ghost") is False

    def test_returns_true_and_removes(self):
        row = storage.create_investigation("ToDelete")
        assert storage.delete_investigation(row.id) is True
        assert storage.get_investigation(row.id) is None


# -------------------------------------------------------------
# Result persistence
# -------------------------------------------------------------

def _github_result(query="torvalds"):
    return GitHubProfile(
        query=query,
        username=query,
        name="Linus Torvalds",
        followers=200000,
    )

def _url_result():
    return URLExpansion(
        query="https://bit.ly/abc",
        short_url="https://bit.ly/abc",
        original_url="https://example.com",
    )


class TestSaveResult:
    def test_result_persisted_and_retrieved(self):
        inv = storage.create_investigation("Case A")
        storage.save_result(inv.id, _github_result())
        results = storage.get_results(inv.id)
        assert len(results) == 1
        assert isinstance(results[0], GitHubProfile)
        assert results[0].username == "torvalds"

    def test_multiple_results_stored(self):
        inv = storage.create_investigation("Case B")
        storage.save_result(inv.id, _github_result("alice"))
        storage.save_result(inv.id, _url_result())
        assert len(storage.get_results(inv.id)) == 2

    def test_updated_at_changes_after_save(self):
        inv = storage.create_investigation("Case C")
        original_ts = inv.updated_at
        storage.save_result(inv.id, _url_result())
        refreshed = storage.get_investigation(inv.id)
        assert refreshed.updated_at >= original_ts

    def test_results_deleted_with_investigation(self):
        inv = storage.create_investigation("Case D")
        storage.save_result(inv.id, _url_result())
        storage.delete_investigation(inv.id)
        assert storage.get_results(inv.id) == []


class TestDeserialization:
    def test_github_profile_roundtrip(self):
        inv = storage.create_investigation("GH")
        storage.save_result(inv.id, _github_result())
        result = storage.get_results(inv.id)[0]
        assert isinstance(result, GitHubProfile)
        assert result.name == "Linus Torvalds"

    def test_url_expansion_roundtrip(self):
        inv = storage.create_investigation("URL")
        storage.save_result(inv.id, _url_result())
        result = storage.get_results(inv.id)[0]
        assert isinstance(result, URLExpansion)
        assert result.original_url == "https://example.com"

    def test_domain_result_roundtrip(self):
        inv = storage.create_investigation("DNS")
        dr = DomainResult(
            query="example.com",
            query_type="dnslookup",
            records=["93.184.216.34"],
        )
        storage.save_result(inv.id, dr)
        result = storage.get_results(inv.id)[0]
        assert isinstance(result, DomainResult)
        assert result.records == ["93.184.216.34"]