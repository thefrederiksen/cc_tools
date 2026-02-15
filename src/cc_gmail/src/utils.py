"""Utility functions for cc_gmail."""

from datetime import datetime
from typing import Dict, Any, Optional
import html


def format_timestamp(timestamp_ms: Optional[str]) -> str:
    """Format Gmail internal timestamp to readable format."""
    if not timestamp_ms:
        return "Unknown"
    try:
        ts = int(timestamp_ms) / 1000
        dt = datetime.fromtimestamp(ts)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return "Unknown"


def truncate(text: str, max_length: int = 80) -> str:
    """Truncate text to max length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def strip_html(html_content: str) -> str:
    """Strip HTML tags and decode entities."""
    import re

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", html_content)
    # Decode HTML entities
    text = html.unescape(text)
    # Normalize whitespace
    text = " ".join(text.split())
    return text


def format_size(size_bytes: int) -> str:
    """Format byte size to human readable format."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def parse_email_address(address: str) -> Dict[str, str]:
    """
    Parse email address into name and email parts.

    Args:
        address: Email address string like "John Doe <john@example.com>"

    Returns:
        Dictionary with 'name' and 'email' keys.
    """
    import re

    # Match "Name <email>" format
    match = re.match(r'^"?([^"<]*)"?\s*<([^>]+)>$', address.strip())
    if match:
        return {"name": match.group(1).strip(), "email": match.group(2).strip()}

    # Plain email
    return {"name": "", "email": address.strip()}


def format_message_summary(msg: Dict[str, Any]) -> Dict[str, str]:
    """Format message details into a display-friendly summary."""
    headers = msg.get("headers", {})

    return {
        "id": msg.get("id", ""),
        "from": headers.get("from", "Unknown"),
        "to": headers.get("to", "Unknown"),
        "subject": headers.get("subject", "(No subject)"),
        "date": headers.get("date", "Unknown"),
        "snippet": msg.get("snippet", ""),
        "labels": ", ".join(msg.get("labels", [])),
    }
