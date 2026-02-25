"""Queue operations for Communication Manager - SQLite backend."""

import json
import logging
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional

# Handle imports for both package and frozen executable
try:
    from .schema import ContentItem, QueueResult, QueueStats, Status
except ImportError:
    from schema import ContentItem, QueueResult, QueueStats, Status

logger = logging.getLogger(__name__)


class QueueManager:
    """Manages the communication content queue using SQLite."""

    # Schema column definitions
    _COMMUNICATIONS_COLUMNS = """
        id TEXT PRIMARY KEY,
        ticket_number INTEGER UNIQUE NOT NULL,
        platform TEXT NOT NULL,
        type TEXT NOT NULL,
        persona TEXT NOT NULL,
        persona_display TEXT,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL,
        created_by TEXT DEFAULT 'claude_code',
        posted_at TEXT,
        posted_by TEXT,
        posted_url TEXT,
        post_id TEXT,
        rejected_at TEXT,
        rejected_by TEXT,
        rejection_reason TEXT,
        scheduled_for TEXT,
        status TEXT NOT NULL DEFAULT 'pending_review',
        send_timing TEXT DEFAULT 'asap',
        send_from TEXT,
        context_url TEXT,
        context_title TEXT,
        context_author TEXT,
        destination_url TEXT,
        campaign_id TEXT,
        notes TEXT,
        tags TEXT,
        linkedin_specific TEXT,
        twitter_specific TEXT,
        reddit_specific TEXT,
        email_specific TEXT,
        article_specific TEXT,
        recipient TEXT,
        thread_content TEXT
    """

    def __init__(self, queue_path: Path):
        """Initialize the queue manager.

        Args:
            queue_path: Path to the content directory (contains communications.db)
        """
        self.queue_path = queue_path
        self.db_path = queue_path / "communications.db"
        self._ensure_directory()
        self._init_schema()

    def _ensure_directory(self) -> None:
        """Ensure the queue directory exists."""
        self.queue_path.mkdir(parents=True, exist_ok=True)

    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        return sqlite3.connect(str(self.db_path))

    def _init_schema(self) -> None:
        """Initialize the database schema if needed."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            self._create_communications_table(cursor)
            self._create_media_table(cursor)
            self._create_indexes(cursor)
            conn.commit()

    def _create_communications_table(self, cursor: sqlite3.Cursor) -> None:
        """Create the communications table."""
        cursor.execute(f"CREATE TABLE IF NOT EXISTS communications ({self._COMMUNICATIONS_COLUMNS})")

    def _create_media_table(self, cursor: sqlite3.Cursor) -> None:
        """Create the media attachments table."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS media (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                communication_id TEXT NOT NULL REFERENCES communications(id) ON DELETE CASCADE,
                type TEXT NOT NULL,
                filename TEXT NOT NULL,
                data BLOB NOT NULL,
                alt_text TEXT,
                file_size INTEGER,
                mime_type TEXT
            )
        """)

    def _create_indexes(self, cursor: sqlite3.Cursor) -> None:
        """Create database indexes."""
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON communications(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_platform ON communications(platform)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON communications(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ticket_number ON communications(ticket_number)")

    def _get_next_ticket_number(self, cursor: sqlite3.Cursor) -> int:
        """Get the next available ticket number."""
        cursor.execute("SELECT COALESCE(MAX(ticket_number), 0) + 1 FROM communications")
        return cursor.fetchone()[0]

    def _serialize_item_fields(self, item: ContentItem) -> Dict[str, Optional[str]]:
        """Serialize platform-specific fields to JSON strings."""
        return {
            "linkedin": json.dumps(item.linkedin_specific.model_dump()) if item.linkedin_specific else None,
            "twitter": json.dumps(item.twitter_specific.model_dump()) if item.twitter_specific else None,
            "reddit": json.dumps(item.reddit_specific.model_dump()) if item.reddit_specific else None,
            "email": json.dumps(item.email_specific.model_dump()) if item.email_specific else None,
            "article": json.dumps(item.article_specific.model_dump()) if item.article_specific else None,
            "recipient": json.dumps(item.recipient.model_dump()) if item.recipient else None,
            "tags": json.dumps(item.tags) if item.tags else None,
            "thread": json.dumps(item.thread_content) if item.thread_content else None,
        }

    def _insert_media(self, cursor: sqlite3.Cursor, item_id: str, media_items: List) -> None:
        """Insert media attachments for a content item."""
        for media_item in media_items:
            media_path = Path(media_item.path)
            if media_path.exists():
                with open(media_path, "rb") as f:
                    data = f.read()
                cursor.execute("""
                    INSERT INTO media (communication_id, type, filename, data, alt_text, file_size)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (item_id, media_item.type, media_path.name, data, media_item.alt_text, len(data)))

    def add_content(self, item: ContentItem) -> QueueResult:
        """Add a content item to the pending_review queue.

        Args:
            item: The content item to add

        Returns:
            QueueResult with success status and ticket number
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                ticket_number = self._get_next_ticket_number(cursor)
                fields = self._serialize_item_fields(item)

                cursor.execute("""
                    INSERT INTO communications (
                        id, ticket_number, platform, type, persona, persona_display,
                        content, created_at, created_by, status,
                        context_url, context_title, context_author, destination_url,
                        campaign_id, notes, tags,
                        linkedin_specific, twitter_specific, reddit_specific,
                        email_specific, article_specific, recipient, thread_content
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    item.id, ticket_number, item.platform.value, item.type.value,
                    item.persona.value, item.persona_display, item.content,
                    item.created_at, item.created_by, "pending_review",
                    item.context_url, item.context_title, item.context_author,
                    item.destination_url, item.campaign_id, item.notes,
                    fields["tags"], fields["linkedin"], fields["twitter"], fields["reddit"],
                    fields["email"], fields["article"], fields["recipient"], fields["thread"],
                ))

                self._insert_media(cursor, item.id, item.media)
                conn.commit()

                logger.info("Added content to queue: ticket #%d", ticket_number)
                return QueueResult(success=True, id=item.id, file=f"ticket #{ticket_number}")

        except sqlite3.Error as e:
            logger.error("Failed to add content: %s", e)
            return QueueResult(success=False, error=f"Database error: {e}")

    def list_content(self, status: Optional[Status] = None) -> List[Dict]:
        """List content items, optionally filtered by status.

        Args:
            status: Filter by status, or None for all

        Returns:
            List of content item dictionaries
        """
        items = []
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                if status is None:
                    cursor.execute("""
                        SELECT * FROM communications ORDER BY created_at DESC
                    """)
                else:
                    cursor.execute("""
                        SELECT * FROM communications WHERE status = ? ORDER BY created_at DESC
                    """, (status.value,))

                columns = [description[0] for description in cursor.description]
                for row in cursor.fetchall():
                    item = dict(zip(columns, row))
                    # Parse JSON fields
                    for json_field in ['tags', 'linkedin_specific', 'twitter_specific',
                                       'reddit_specific', 'email_specific', 'article_specific',
                                       'recipient', 'thread_content']:
                        if item.get(json_field):
                            try:
                                item[json_field] = json.loads(item[json_field])
                            except json.JSONDecodeError as e:
                                logger.warning("Failed to parse JSON field '%s' in item %s: %s", json_field, item.get("id", "unknown"), e)
                    items.append(item)

        except sqlite3.Error as e:
            logger.error("Failed to list content: %s", e)

        return items

    def get_stats(self) -> QueueStats:
        """Get queue statistics.

        Returns:
            QueueStats with counts for each status
        """
        stats = QueueStats()
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT status, COUNT(*) FROM communications GROUP BY status
                """)
                for status, count in cursor.fetchall():
                    if status == "pending_review":
                        stats.pending_review = count
                    elif status == "approved":
                        stats.approved = count
                    elif status == "rejected":
                        stats.rejected = count
                    elif status == "posted":
                        stats.posted = count

        except sqlite3.Error as e:
            logger.error("Failed to get stats: %s", e)

        return stats

    def get_content_by_id(self, content_id: str) -> Optional[Dict]:
        """Get a content item by ID or ticket number.

        Args:
            content_id: The content item ID (uuid) or ticket number

        Returns:
            Content item dictionary or None if not found
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Try as ticket number first
                if content_id.isdigit():
                    cursor.execute("""
                        SELECT * FROM communications WHERE ticket_number = ?
                    """, (int(content_id),))
                else:
                    # Try as ID (exact or partial match)
                    cursor.execute("""
                        SELECT * FROM communications WHERE id = ? OR id LIKE ?
                    """, (content_id, f"{content_id}%"))

                row = cursor.fetchone()
                if row:
                    columns = [description[0] for description in cursor.description]
                    item = dict(zip(columns, row))
                    # Parse JSON fields
                    for json_field in ['tags', 'linkedin_specific', 'twitter_specific',
                                       'reddit_specific', 'email_specific', 'article_specific',
                                       'recipient', 'thread_content']:
                        if item.get(json_field):
                            try:
                                item[json_field] = json.loads(item[json_field])
                            except json.JSONDecodeError as e:
                                logger.warning("Failed to parse JSON field '%s' in item %s: %s", json_field, item.get("id", "unknown"), e)
                    return item

        except sqlite3.Error as e:
            logger.error("Failed to get content: %s", e)

        return None
