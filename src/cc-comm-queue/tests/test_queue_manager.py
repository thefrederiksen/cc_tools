"""Tests for cc-comm-queue queue_manager module."""

import sys
from pathlib import Path

# Ensure the project root is on sys.path so 'src' package resolves
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import pytest

from src.queue_manager import QueueManager
from src.schema import ContentItem, ContentType, Persona, Platform, Status


def _make_item(**overrides) -> ContentItem:
    """Helper: create a minimal ContentItem, applying any overrides."""
    defaults = {
        "platform": Platform.LINKEDIN,
        "type": ContentType.POST,
        "content": "Default test content",
    }
    defaults.update(overrides)
    return ContentItem(**defaults)


# ---------------------------------------------------------------------------
# 1. QueueManager init creates database
# ---------------------------------------------------------------------------

class TestQueueManagerInit:
    """Initializing QueueManager should create the SQLite database file."""

    def test_creates_db_file(self, tmp_path):
        qm = QueueManager(tmp_path)
        assert qm.db_path.exists()

    def test_db_path_is_communications_db(self, tmp_path):
        qm = QueueManager(tmp_path)
        assert qm.db_path.name == "communications.db"

    def test_creates_directory_if_missing(self, tmp_path):
        nested = tmp_path / "a" / "b" / "c"
        qm = QueueManager(nested)
        assert nested.exists()
        assert qm.db_path.exists()

    def test_creates_tables(self, tmp_path):
        """The communications and media tables should exist after init."""
        import sqlite3

        qm = QueueManager(tmp_path)
        conn = sqlite3.connect(str(qm.db_path))
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = {row[0] for row in cursor.fetchall()}
        conn.close()
        assert "communications" in tables
        assert "media" in tables


# ---------------------------------------------------------------------------
# 2. add_content() returns QueueResult with success
# ---------------------------------------------------------------------------

class TestAddContent:
    """add_content() inserts a row and returns a successful QueueResult."""

    def test_returns_success(self, tmp_path):
        qm = QueueManager(tmp_path)
        item = _make_item()
        result = qm.add_content(item)
        assert result.success is True

    def test_result_contains_id(self, tmp_path):
        qm = QueueManager(tmp_path)
        item = _make_item()
        result = qm.add_content(item)
        assert result.id == item.id

    def test_result_file_contains_ticket(self, tmp_path):
        qm = QueueManager(tmp_path)
        item = _make_item()
        result = qm.add_content(item)
        assert result.file is not None
        assert "ticket" in result.file

    def test_no_error_on_success(self, tmp_path):
        qm = QueueManager(tmp_path)
        item = _make_item()
        result = qm.add_content(item)
        assert result.error is None


# ---------------------------------------------------------------------------
# 3. add_content() assigns sequential ticket numbers
# ---------------------------------------------------------------------------

class TestTicketNumbers:
    """Ticket numbers should start at 1 and increment sequentially."""

    def test_first_ticket_is_one(self, tmp_path):
        qm = QueueManager(tmp_path)
        result = qm.add_content(_make_item())
        assert result.file == "ticket #1"

    def test_sequential_tickets(self, tmp_path):
        qm = QueueManager(tmp_path)
        r1 = qm.add_content(_make_item(content="First"))
        r2 = qm.add_content(_make_item(content="Second"))
        r3 = qm.add_content(_make_item(content="Third"))
        assert r1.file == "ticket #1"
        assert r2.file == "ticket #2"
        assert r3.file == "ticket #3"

    def test_ticket_number_stored_in_db(self, tmp_path):
        qm = QueueManager(tmp_path)
        item = _make_item()
        qm.add_content(item)
        row = qm.get_content_by_id(item.id)
        assert row is not None
        assert row["ticket_number"] == 1


# ---------------------------------------------------------------------------
# 4. list_content() returns all items
# ---------------------------------------------------------------------------

class TestListContentAll:
    """list_content() without a filter should return every item."""

    def test_empty_queue(self, tmp_path):
        qm = QueueManager(tmp_path)
        assert qm.list_content() == []

    def test_returns_all_items(self, tmp_path):
        qm = QueueManager(tmp_path)
        qm.add_content(_make_item(content="A"))
        qm.add_content(_make_item(content="B"))
        qm.add_content(_make_item(content="C"))
        items = qm.list_content()
        assert len(items) == 3

    def test_items_are_dicts(self, tmp_path):
        qm = QueueManager(tmp_path)
        qm.add_content(_make_item())
        items = qm.list_content()
        assert isinstance(items[0], dict)

    def test_item_has_expected_keys(self, tmp_path):
        qm = QueueManager(tmp_path)
        qm.add_content(_make_item())
        item = qm.list_content()[0]
        assert "id" in item
        assert "platform" in item
        assert "type" in item
        assert "content" in item
        assert "status" in item
        assert "ticket_number" in item


# ---------------------------------------------------------------------------
# 5. list_content() filters by status
# ---------------------------------------------------------------------------

class TestListContentFiltered:
    """list_content(status=...) should only return items with that status."""

    def test_filter_pending_review(self, tmp_path):
        qm = QueueManager(tmp_path)
        # All items default to pending_review
        qm.add_content(_make_item(content="Item 1"))
        qm.add_content(_make_item(content="Item 2"))
        items = qm.list_content(status=Status.PENDING_REVIEW)
        assert len(items) == 2

    def test_filter_returns_empty_when_no_match(self, tmp_path):
        qm = QueueManager(tmp_path)
        qm.add_content(_make_item())
        items = qm.list_content(status=Status.APPROVED)
        assert items == []

    def test_filter_approved_after_status_update(self, tmp_path):
        """Manually update a row's status and verify the filter works."""
        import sqlite3

        qm = QueueManager(tmp_path)
        item = _make_item()
        qm.add_content(item)

        # Manually update status in the DB
        conn = sqlite3.connect(str(qm.db_path))
        conn.execute(
            "UPDATE communications SET status = ? WHERE id = ?",
            (Status.APPROVED.value, item.id),
        )
        conn.commit()
        conn.close()

        pending = qm.list_content(status=Status.PENDING_REVIEW)
        approved = qm.list_content(status=Status.APPROVED)
        assert len(pending) == 0
        assert len(approved) == 1
        assert approved[0]["id"] == item.id


# ---------------------------------------------------------------------------
# 6. get_stats() returns correct counts
# ---------------------------------------------------------------------------

class TestGetStats:
    """get_stats() should return accurate counts per status."""

    def test_empty_queue(self, tmp_path):
        qm = QueueManager(tmp_path)
        stats = qm.get_stats()
        assert stats.pending_review == 0
        assert stats.approved == 0
        assert stats.rejected == 0
        assert stats.posted == 0

    def test_counts_pending(self, tmp_path):
        qm = QueueManager(tmp_path)
        qm.add_content(_make_item(content="A"))
        qm.add_content(_make_item(content="B"))
        stats = qm.get_stats()
        assert stats.pending_review == 2

    def test_mixed_statuses(self, tmp_path):
        """Insert items then manually set various statuses."""
        import sqlite3

        qm = QueueManager(tmp_path)
        items = []
        for i in range(5):
            item = _make_item(content=f"Item {i}")
            qm.add_content(item)
            items.append(item)

        conn = sqlite3.connect(str(qm.db_path))
        # 2 pending (items 0, 1), 1 approved (item 2), 1 rejected (item 3), 1 posted (item 4)
        conn.execute(
            "UPDATE communications SET status = ? WHERE id = ?",
            (Status.APPROVED.value, items[2].id),
        )
        conn.execute(
            "UPDATE communications SET status = ? WHERE id = ?",
            (Status.REJECTED.value, items[3].id),
        )
        conn.execute(
            "UPDATE communications SET status = ? WHERE id = ?",
            (Status.POSTED.value, items[4].id),
        )
        conn.commit()
        conn.close()

        stats = qm.get_stats()
        assert stats.pending_review == 2
        assert stats.approved == 1
        assert stats.rejected == 1
        assert stats.posted == 1


# ---------------------------------------------------------------------------
# 7. get_content_by_id() finds by UUID
# ---------------------------------------------------------------------------

class TestGetContentById:
    """get_content_by_id() retrieves a single item by its UUID."""

    def test_find_by_full_id(self, tmp_path):
        qm = QueueManager(tmp_path)
        item = _make_item(content="Find me")
        qm.add_content(item)
        result = qm.get_content_by_id(item.id)
        assert result is not None
        assert result["id"] == item.id
        assert result["content"] == "Find me"

    def test_find_by_partial_id(self, tmp_path):
        qm = QueueManager(tmp_path)
        item = _make_item(content="Partial match")
        qm.add_content(item)
        short_id = item.id[:8]
        result = qm.get_content_by_id(short_id)
        assert result is not None
        assert result["id"] == item.id

    def test_find_by_ticket_number(self, tmp_path):
        qm = QueueManager(tmp_path)
        item = _make_item(content="Ticket lookup")
        qm.add_content(item)
        result = qm.get_content_by_id("1")
        assert result is not None
        assert result["content"] == "Ticket lookup"

    def test_result_has_parsed_json_fields(self, tmp_path):
        """JSON fields stored as strings should be parsed back to Python objects."""
        qm = QueueManager(tmp_path)
        item = _make_item(
            content="Tagged item",
            tags=["tag1", "tag2"],
        )
        qm.add_content(item)
        result = qm.get_content_by_id(item.id)
        assert result is not None
        assert result["tags"] == ["tag1", "tag2"]


# ---------------------------------------------------------------------------
# 8. get_content_by_id() returns None for missing ID
# ---------------------------------------------------------------------------

class TestGetContentByIdMissing:
    """get_content_by_id() returns None when the item does not exist."""

    def test_missing_uuid(self, tmp_path):
        qm = QueueManager(tmp_path)
        result = qm.get_content_by_id("00000000-0000-0000-0000-000000000000")
        assert result is None

    def test_missing_ticket_number(self, tmp_path):
        qm = QueueManager(tmp_path)
        result = qm.get_content_by_id("999")
        assert result is None

    def test_missing_partial_id(self, tmp_path):
        qm = QueueManager(tmp_path)
        result = qm.get_content_by_id("ffffffff")
        assert result is None

    def test_empty_queue_returns_none(self, tmp_path):
        qm = QueueManager(tmp_path)
        result = qm.get_content_by_id("anything")
        assert result is None
