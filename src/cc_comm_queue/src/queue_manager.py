"""Queue operations for Communication Manager."""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

# Handle imports for both package and frozen executable
try:
    from .schema import ContentItem, QueueResult, QueueStats, Status
except ImportError:
    from schema import ContentItem, QueueResult, QueueStats, Status

logger = logging.getLogger(__name__)


class QueueManager:
    """Manages the communication content queue."""

    def __init__(self, queue_path: Path):
        """Initialize the queue manager.

        Args:
            queue_path: Path to the content directory (contains pending_review, approved, etc.)
        """
        self.queue_path = queue_path
        self.pending_path = queue_path / "pending_review"
        self.approved_path = queue_path / "approved"
        self.rejected_path = queue_path / "rejected"
        self.posted_path = queue_path / "posted"

    def ensure_directories(self) -> None:
        """Ensure all queue directories exist."""
        for path in [self.pending_path, self.approved_path, self.rejected_path, self.posted_path]:
            path.mkdir(parents=True, exist_ok=True)

    def add_content(self, item: ContentItem) -> QueueResult:
        """Add a content item to the pending_review queue.

        Args:
            item: The content item to add

        Returns:
            QueueResult with success status and file path
        """
        self.ensure_directories()

        filename = item.get_filename()
        file_path = self.pending_path / filename

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(item.to_json_dict(), f, indent=2, ensure_ascii=False)

            logger.info("Added content to queue: %s", filename)
            return QueueResult(
                success=True,
                id=item.id,
                file=str(file_path),
            )

        except OSError as e:
            logger.error("Failed to write content file: %s", e)
            return QueueResult(
                success=False,
                error=f"Failed to write file: {e}",
            )

    def list_content(self, status: Optional[Status] = None) -> List[Dict]:
        """List content items, optionally filtered by status.

        Args:
            status: Filter by status, or None for all

        Returns:
            List of content item dictionaries
        """
        self.ensure_directories()

        items = []
        paths = []

        if status is None:
            paths = [self.pending_path, self.approved_path, self.rejected_path, self.posted_path]
        elif status == Status.PENDING_REVIEW:
            paths = [self.pending_path]
        elif status == Status.APPROVED:
            paths = [self.approved_path]
        elif status == Status.REJECTED:
            paths = [self.rejected_path]
        elif status == Status.POSTED:
            paths = [self.posted_path]

        for path in paths:
            if path.exists():
                for file_path in path.glob("*.json"):
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            data["_file_path"] = str(file_path)
                            items.append(data)
                    except (OSError, json.JSONDecodeError) as e:
                        logger.warning("Failed to read %s: %s", file_path, e)

        # Sort by created_at descending
        items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return items

    def get_stats(self) -> QueueStats:
        """Get queue statistics.

        Returns:
            QueueStats with counts for each status
        """
        self.ensure_directories()

        return QueueStats(
            pending_review=len(list(self.pending_path.glob("*.json"))),
            approved=len(list(self.approved_path.glob("*.json"))),
            rejected=len(list(self.rejected_path.glob("*.json"))),
            posted=len(list(self.posted_path.glob("*.json"))),
        )

    def get_content_by_id(self, content_id: str) -> Optional[Dict]:
        """Get a content item by ID.

        Args:
            content_id: The content item ID (or partial ID)

        Returns:
            Content item dictionary or None if not found
        """
        self.ensure_directories()

        for path in [self.pending_path, self.approved_path, self.rejected_path, self.posted_path]:
            if path.exists():
                for file_path in path.glob("*.json"):
                    # Check if ID is in filename
                    if content_id in file_path.stem:
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                data = json.load(f)
                                data["_file_path"] = str(file_path)
                                return data
                        except (OSError, json.JSONDecodeError) as e:
                            logger.warning("Failed to read %s: %s", file_path, e)

        return None
