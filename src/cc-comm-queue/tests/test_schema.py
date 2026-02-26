"""Tests for cc-comm-queue schema module."""

import sys
from pathlib import Path

# Ensure the project root is on sys.path so 'src' package resolves
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import pytest

from src.schema import (
    ContentItem,
    ContentType,
    EmailSpecific,
    MediaItem,
    PERSONA_DISPLAY_MAP,
    Persona,
    Platform,
    QueueResult,
    QueueStats,
    RecipientInfo,
    RedditSpecific,
    Status,
    Visibility,
    _remove_none_values,
)


# ---------------------------------------------------------------------------
# 1. Enum values
# ---------------------------------------------------------------------------

class TestPlatformEnum:
    """Platform enum has expected members and string values."""

    def test_linkedin(self):
        assert Platform.LINKEDIN.value == "linkedin"

    def test_twitter(self):
        assert Platform.TWITTER.value == "twitter"

    def test_reddit(self):
        assert Platform.REDDIT.value == "reddit"

    def test_youtube(self):
        assert Platform.YOUTUBE.value == "youtube"

    def test_email(self):
        assert Platform.EMAIL.value == "email"

    def test_blog(self):
        assert Platform.BLOG.value == "blog"

    def test_member_count(self):
        assert len(Platform) == 6


class TestContentTypeEnum:
    """ContentType enum has expected members."""

    def test_post(self):
        assert ContentType.POST.value == "post"

    def test_comment(self):
        assert ContentType.COMMENT.value == "comment"

    def test_reply(self):
        assert ContentType.REPLY.value == "reply"

    def test_message(self):
        assert ContentType.MESSAGE.value == "message"

    def test_article(self):
        assert ContentType.ARTICLE.value == "article"

    def test_email(self):
        assert ContentType.EMAIL.value == "email"

    def test_member_count(self):
        assert len(ContentType) == 6


class TestPersonaEnum:
    """Persona enum has expected members."""

    def test_mindzie(self):
        assert Persona.MINDZIE.value == "mindzie"

    def test_center_consulting(self):
        assert Persona.CENTER_CONSULTING.value == "center_consulting"

    def test_personal(self):
        assert Persona.PERSONAL.value == "personal"

    def test_member_count(self):
        assert len(Persona) == 3


class TestStatusEnum:
    """Status enum has expected members."""

    def test_pending_review(self):
        assert Status.PENDING_REVIEW.value == "pending_review"

    def test_approved(self):
        assert Status.APPROVED.value == "approved"

    def test_rejected(self):
        assert Status.REJECTED.value == "rejected"

    def test_posted(self):
        assert Status.POSTED.value == "posted"

    def test_member_count(self):
        assert len(Status) == 4


class TestVisibilityEnum:
    """Visibility enum has expected members."""

    def test_public(self):
        assert Visibility.PUBLIC.value == "public"

    def test_connections(self):
        assert Visibility.CONNECTIONS.value == "connections"

    def test_member_count(self):
        assert len(Visibility) == 2


# ---------------------------------------------------------------------------
# 2. PERSONA_DISPLAY_MAP
# ---------------------------------------------------------------------------

class TestPersonaDisplayMap:
    """PERSONA_DISPLAY_MAP maps every Persona to a human-readable string."""

    def test_mindzie_display(self):
        assert PERSONA_DISPLAY_MAP[Persona.MINDZIE] == "CTO of mindzie"

    def test_center_consulting_display(self):
        assert PERSONA_DISPLAY_MAP[Persona.CENTER_CONSULTING] == "President of Center Consulting"

    def test_personal_display(self):
        assert PERSONA_DISPLAY_MAP[Persona.PERSONAL] == "Soren Frederiksen"

    def test_all_personas_mapped(self):
        for persona in Persona:
            assert persona in PERSONA_DISPLAY_MAP, (
                f"Persona {persona.name} missing from PERSONA_DISPLAY_MAP"
            )


# ---------------------------------------------------------------------------
# 3. ContentItem creation with defaults
# ---------------------------------------------------------------------------

class TestContentItemDefaults:
    """ContentItem sets sensible defaults when only required fields are given."""

    @pytest.fixture()
    def item(self):
        return ContentItem(
            platform=Platform.LINKEDIN,
            type=ContentType.POST,
            content="Hello world",
        )

    def test_id_is_uuid_string(self, item):
        # UUID4 produces 36-char strings like 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'
        assert isinstance(item.id, str)
        assert len(item.id) == 36

    def test_default_persona(self, item):
        assert item.persona == Persona.PERSONAL

    def test_default_status(self, item):
        assert item.status == Status.PENDING_REVIEW

    def test_default_created_by(self, item):
        assert item.created_by == "claude_code"

    def test_created_at_is_iso_string(self, item):
        # Should look like an ISO timestamp
        assert "T" in item.created_at

    def test_optional_fields_are_none(self, item):
        assert item.context_url is None
        assert item.context_title is None
        assert item.notes is None
        assert item.campaign_id is None

    def test_default_tags_empty_list(self, item):
        assert item.tags == []

    def test_default_media_empty_list(self, item):
        assert item.media == []


# ---------------------------------------------------------------------------
# 4. ContentItem.get_filename()
# ---------------------------------------------------------------------------

class TestGetFilename:
    """get_filename() returns '{platform}_{type}_{short_id}.json'."""

    def test_filename_format(self):
        item = ContentItem(
            id="abcdef12-3456-7890-abcd-ef1234567890",
            platform=Platform.LINKEDIN,
            type=ContentType.POST,
            content="Test content",
        )
        assert item.get_filename() == "linkedin_post_abcdef12.json"

    def test_filename_uses_first_eight_chars_of_id(self):
        item = ContentItem(
            id="12345678-aaaa-bbbb-cccc-dddddddddddd",
            platform=Platform.REDDIT,
            type=ContentType.COMMENT,
            content="A comment",
        )
        filename = item.get_filename()
        assert filename.startswith("reddit_comment_12345678")
        assert filename.endswith(".json")

    def test_filename_email_type(self):
        item = ContentItem(
            id="aabbccdd-1111-2222-3333-444444444444",
            platform=Platform.EMAIL,
            type=ContentType.EMAIL,
            content="Email body",
        )
        assert item.get_filename() == "email_email_aabbccdd.json"


# ---------------------------------------------------------------------------
# 5. model_post_init() auto-fills persona_display
# ---------------------------------------------------------------------------

class TestModelPostInit:
    """model_post_init auto-fills persona_display from PERSONA_DISPLAY_MAP."""

    def test_auto_fills_mindzie(self):
        item = ContentItem(
            platform=Platform.LINKEDIN,
            type=ContentType.POST,
            persona=Persona.MINDZIE,
            content="Post",
        )
        assert item.persona_display == "CTO of mindzie"

    def test_auto_fills_center_consulting(self):
        item = ContentItem(
            platform=Platform.TWITTER,
            type=ContentType.POST,
            persona=Persona.CENTER_CONSULTING,
            content="Tweet",
        )
        assert item.persona_display == "President of Center Consulting"

    def test_auto_fills_personal(self):
        item = ContentItem(
            platform=Platform.BLOG,
            type=ContentType.ARTICLE,
            persona=Persona.PERSONAL,
            content="Article body",
        )
        assert item.persona_display == "Soren Frederiksen"

    def test_explicit_persona_display_not_overwritten(self):
        item = ContentItem(
            platform=Platform.LINKEDIN,
            type=ContentType.POST,
            persona=Persona.MINDZIE,
            persona_display="Custom Display Name",
            content="Post",
        )
        assert item.persona_display == "Custom Display Name"


# ---------------------------------------------------------------------------
# 6. ContentItem.to_json_dict() removes None values
# ---------------------------------------------------------------------------

class TestToJsonDict:
    """to_json_dict() produces a dict without any None values."""

    def test_no_none_values(self):
        item = ContentItem(
            platform=Platform.LINKEDIN,
            type=ContentType.POST,
            content="Test",
        )
        data = item.to_json_dict()
        # Recursively check for None
        self._assert_no_nones(data)

    def test_includes_required_fields(self):
        item = ContentItem(
            platform=Platform.LINKEDIN,
            type=ContentType.POST,
            content="Hello",
        )
        data = item.to_json_dict()
        assert data["platform"] == "linkedin"
        assert data["type"] == "post"
        assert data["content"] == "Hello"
        assert data["status"] == "pending_review"

    def test_excludes_optional_fields_when_none(self):
        item = ContentItem(
            platform=Platform.EMAIL,
            type=ContentType.EMAIL,
            content="Body",
        )
        data = item.to_json_dict()
        assert "context_url" not in data
        assert "notes" not in data
        assert "rejection_reason" not in data

    def test_includes_optional_fields_when_set(self):
        item = ContentItem(
            platform=Platform.REDDIT,
            type=ContentType.COMMENT,
            content="Nice post",
            context_url="https://example.com",
            notes="Follow up later",
        )
        data = item.to_json_dict()
        assert data["context_url"] == "https://example.com"
        assert data["notes"] == "Follow up later"

    # ------ helper ------
    def _assert_no_nones(self, obj, path=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                assert v is not None, f"None found at {path}.{k}"
                self._assert_no_nones(v, f"{path}.{k}")
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                assert v is not None, f"None found at {path}[{i}]"
                self._assert_no_nones(v, f"{path}[{i}]")


# ---------------------------------------------------------------------------
# 7. _remove_none_values() helper
# ---------------------------------------------------------------------------

class TestRemoveNoneValues:
    """_remove_none_values strips Nones, empty dicts, and empty lists."""

    def test_removes_top_level_none(self):
        result = _remove_none_values({"a": 1, "b": None})
        assert result == {"a": 1}

    def test_removes_nested_none(self):
        result = _remove_none_values({"a": {"x": 1, "y": None}})
        assert result == {"a": {"x": 1}}

    def test_removes_empty_nested_dict(self):
        # If all values in a sub-dict are None, the sub-dict becomes empty
        # and should be excluded.
        result = _remove_none_values({"a": {"x": None}})
        assert result == {}

    def test_removes_empty_list(self):
        result = _remove_none_values({"a": [], "b": "keep"})
        assert result == {"b": "keep"}

    def test_keeps_non_empty_list(self):
        result = _remove_none_values({"items": [1, 2, 3]})
        assert result == {"items": [1, 2, 3]}

    def test_removes_none_inside_list(self):
        result = _remove_none_values({"items": [1, None, 3]})
        assert result == {"items": [1, 3]}

    def test_cleans_dicts_inside_list(self):
        result = _remove_none_values({"items": [{"a": 1, "b": None}]})
        assert result == {"items": [{"a": 1}]}

    def test_all_none_returns_empty(self):
        result = _remove_none_values({"a": None, "b": None})
        assert result == {}

    def test_deeply_nested(self):
        data = {
            "level1": {
                "level2": {
                    "value": 42,
                    "gone": None,
                }
            }
        }
        result = _remove_none_values(data)
        assert result == {"level1": {"level2": {"value": 42}}}

    def test_preserves_falsy_values(self):
        # 0, False, empty string should NOT be removed
        result = _remove_none_values({"a": 0, "b": False, "c": ""})
        assert result == {"a": 0, "b": False, "c": ""}


# ---------------------------------------------------------------------------
# 8. QueueResult and QueueStats creation
# ---------------------------------------------------------------------------

class TestQueueResult:
    """QueueResult stores operation outcomes."""

    def test_success_result(self):
        r = QueueResult(success=True, id="abc-123", file="ticket #1")
        assert r.success is True
        assert r.id == "abc-123"
        assert r.file == "ticket #1"
        assert r.error is None

    def test_failure_result(self):
        r = QueueResult(success=False, error="Database error: constraint violation")
        assert r.success is False
        assert r.id is None
        assert r.error == "Database error: constraint violation"

    def test_defaults(self):
        r = QueueResult(success=True)
        assert r.id is None
        assert r.file is None
        assert r.error is None


class TestQueueStats:
    """QueueStats tracks counts by status."""

    def test_all_defaults_zero(self):
        stats = QueueStats()
        assert stats.pending_review == 0
        assert stats.approved == 0
        assert stats.rejected == 0
        assert stats.posted == 0

    def test_explicit_values(self):
        stats = QueueStats(pending_review=5, approved=3, rejected=1, posted=10)
        assert stats.pending_review == 5
        assert stats.approved == 3
        assert stats.rejected == 1
        assert stats.posted == 10


# ---------------------------------------------------------------------------
# 9. MediaItem and RecipientInfo creation
# ---------------------------------------------------------------------------

class TestMediaItem:
    """MediaItem stores a media attachment reference."""

    def test_required_fields(self):
        m = MediaItem(type="image", path="/photos/pic.png")
        assert m.type == "image"
        assert m.path == "/photos/pic.png"
        assert m.alt_text is None

    def test_with_alt_text(self):
        m = MediaItem(type="video", path="/videos/demo.mp4", alt_text="Demo video")
        assert m.alt_text == "Demo video"


class TestRecipientInfo:
    """RecipientInfo stores message recipient details."""

    def test_required_name(self):
        r = RecipientInfo(name="Jane Doe")
        assert r.name == "Jane Doe"
        assert r.title is None
        assert r.company is None
        assert r.profile_url is None

    def test_all_fields(self):
        r = RecipientInfo(
            name="John Smith",
            title="CTO",
            company="Acme Corp",
            profile_url="https://linkedin.com/in/johnsmith",
        )
        assert r.name == "John Smith"
        assert r.title == "CTO"
        assert r.company == "Acme Corp"
        assert r.profile_url == "https://linkedin.com/in/johnsmith"


# ---------------------------------------------------------------------------
# 10. EmailSpecific and RedditSpecific creation
# ---------------------------------------------------------------------------

class TestEmailSpecific:
    """EmailSpecific holds email-related fields."""

    def test_required_fields(self):
        e = EmailSpecific(to=["alice@example.com"], subject="Hello")
        assert e.to == ["alice@example.com"]
        assert e.subject == "Hello"
        assert e.cc == []
        assert e.bcc == []
        assert e.attachments == []
        assert e.reply_to_message_id is None

    def test_all_fields(self):
        e = EmailSpecific(
            to=["a@b.com", "c@d.com"],
            cc=["e@f.com"],
            bcc=["g@h.com"],
            subject="Subject line",
            reply_to_message_id="msg-999",
            attachments=["/tmp/report.pdf"],
        )
        assert len(e.to) == 2
        assert e.cc == ["e@f.com"]
        assert e.bcc == ["g@h.com"]
        assert e.reply_to_message_id == "msg-999"
        assert e.attachments == ["/tmp/report.pdf"]


class TestRedditSpecific:
    """RedditSpecific holds Reddit-related fields."""

    def test_required_subreddit(self):
        r = RedditSpecific(subreddit="python")
        assert r.subreddit == "python"
        assert r.title is None
        assert r.flair is None
        assert r.subreddit_url is None
        assert r.parent_comment is None

    def test_all_fields(self):
        r = RedditSpecific(
            subreddit="learnpython",
            title="How do I use pytest?",
            flair="Question",
            subreddit_url="https://reddit.com/r/learnpython",
            parent_comment="t1_abc123",
        )
        assert r.subreddit == "learnpython"
        assert r.title == "How do I use pytest?"
        assert r.flair == "Question"
        assert r.subreddit_url == "https://reddit.com/r/learnpython"
        assert r.parent_comment == "t1_abc123"
