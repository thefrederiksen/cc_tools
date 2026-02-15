"""Gmail API wrapper for common operations."""

import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import Optional, List, Dict, Any

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


class GmailClient:
    """Gmail API client wrapper."""

    def __init__(self, credentials: Credentials):
        """Initialize Gmail client with credentials."""
        self.service = build("gmail", "v1", credentials=credentials)
        self.user_id = "me"

    def get_profile(self) -> Dict[str, Any]:
        """Get the authenticated user's Gmail profile."""
        return self.service.users().getProfile(userId=self.user_id).execute()

    def list_labels(self) -> List[Dict[str, Any]]:
        """List all labels/folders."""
        results = self.service.users().labels().list(userId=self.user_id).execute()
        return results.get("labels", [])

    def list_messages(
        self,
        label_ids: Optional[List[str]] = None,
        query: Optional[str] = None,
        max_results: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        List messages matching criteria.

        Args:
            label_ids: Filter by label IDs (e.g., ["INBOX", "UNREAD"])
            query: Gmail search query string
            max_results: Maximum number of messages to return

        Returns:
            List of message dictionaries with id and threadId.
        """
        kwargs = {"userId": self.user_id, "maxResults": max_results}

        if label_ids:
            kwargs["labelIds"] = label_ids
        if query:
            kwargs["q"] = query

        results = self.service.users().messages().list(**kwargs).execute()
        return results.get("messages", [])

    def get_message(
        self, message_id: str, format: str = "full"
    ) -> Dict[str, Any]:
        """
        Get a specific message.

        Args:
            message_id: The message ID
            format: "full", "metadata", "minimal", or "raw"

        Returns:
            Message dictionary with headers, body, etc.
        """
        return (
            self.service.users()
            .messages()
            .get(userId=self.user_id, id=message_id, format=format)
            .execute()
        )

    def get_message_details(self, message_id: str) -> Dict[str, Any]:
        """Get message with parsed headers and body."""
        msg = self.get_message(message_id)

        # Parse headers
        headers = {}
        payload = msg.get("payload", {})
        for header in payload.get("headers", []):
            name = header.get("name", "").lower()
            if name in ["from", "to", "subject", "date", "cc", "bcc"]:
                headers[name] = header.get("value", "")

        # Get body
        body = self._extract_body(payload)

        return {
            "id": msg.get("id"),
            "thread_id": msg.get("threadId"),
            "snippet": msg.get("snippet"),
            "labels": msg.get("labelIds", []),
            "headers": headers,
            "body": body,
            "internal_date": msg.get("internalDate"),
        }

    def _extract_body(self, payload: Dict[str, Any]) -> str:
        """Extract plain text body from message payload."""
        body = ""

        # Check for simple body
        if "body" in payload and payload["body"].get("data"):
            body = self._decode_base64(payload["body"]["data"])
            return body

        # Check for multipart
        parts = payload.get("parts", [])
        for part in parts:
            mime_type = part.get("mimeType", "")
            if mime_type == "text/plain":
                if part.get("body", {}).get("data"):
                    body = self._decode_base64(part["body"]["data"])
                    break
            elif mime_type.startswith("multipart/"):
                # Recursively check nested parts
                body = self._extract_body(part)
                if body:
                    break

        # Fallback to HTML if no plain text
        if not body:
            for part in parts:
                if part.get("mimeType") == "text/html":
                    if part.get("body", {}).get("data"):
                        body = self._decode_base64(part["body"]["data"])
                        break

        return body

    def _decode_base64(self, data: str) -> str:
        """Decode base64url encoded data."""
        # Gmail uses URL-safe base64
        padding = 4 - len(data) % 4
        if padding != 4:
            data += "=" * padding
        return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")

    def send_message(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[str] = None,
        bcc: Optional[str] = None,
        html: bool = False,
        attachments: Optional[List[Path]] = None,
    ) -> Dict[str, Any]:
        """
        Send an email message.

        Args:
            to: Recipient email address(es)
            subject: Email subject
            body: Email body (plain text or HTML)
            cc: CC recipients
            bcc: BCC recipients
            html: If True, body is HTML
            attachments: List of file paths to attach

        Returns:
            Sent message response.
        """
        if attachments:
            message = MIMEMultipart()
            message.attach(MIMEText(body, "html" if html else "plain"))

            for file_path in attachments:
                with open(file_path, "rb") as f:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename={file_path.name}",
                    )
                    message.attach(part)
        else:
            message = MIMEText(body, "html" if html else "plain")

        message["to"] = to
        message["subject"] = subject

        if cc:
            message["cc"] = cc
        if bcc:
            message["bcc"] = bcc

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
        return (
            self.service.users()
            .messages()
            .send(userId=self.user_id, body={"raw": raw})
            .execute()
        )

    def create_draft(
        self,
        to: str,
        subject: str,
        body: str,
        cc: Optional[str] = None,
        html: bool = False,
    ) -> Dict[str, Any]:
        """
        Create a draft email.

        Args:
            to: Recipient email address(es)
            subject: Email subject
            body: Email body
            cc: CC recipients
            html: If True, body is HTML

        Returns:
            Created draft response.
        """
        message = MIMEText(body, "html" if html else "plain")
        message["to"] = to
        message["subject"] = subject

        if cc:
            message["cc"] = cc

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
        return (
            self.service.users()
            .drafts()
            .create(userId=self.user_id, body={"message": {"raw": raw}})
            .execute()
        )

    def list_drafts(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """List drafts."""
        results = (
            self.service.users()
            .drafts()
            .list(userId=self.user_id, maxResults=max_results)
            .execute()
        )
        return results.get("drafts", [])

    def delete_message(self, message_id: str, permanent: bool = False) -> None:
        """
        Delete a message.

        Args:
            message_id: The message ID
            permanent: If True, permanently delete. Otherwise, move to trash.
        """
        if permanent:
            self.service.users().messages().delete(
                userId=self.user_id, id=message_id
            ).execute()
        else:
            self.service.users().messages().trash(
                userId=self.user_id, id=message_id
            ).execute()

    def mark_as_read(self, message_id: str) -> Dict[str, Any]:
        """Mark a message as read."""
        return (
            self.service.users()
            .messages()
            .modify(
                userId=self.user_id,
                id=message_id,
                body={"removeLabelIds": ["UNREAD"]},
            )
            .execute()
        )

    def mark_as_unread(self, message_id: str) -> Dict[str, Any]:
        """Mark a message as unread."""
        return (
            self.service.users()
            .messages()
            .modify(
                userId=self.user_id,
                id=message_id,
                body={"addLabelIds": ["UNREAD"]},
            )
            .execute()
        )

    def search(
        self, query: str, max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search messages using Gmail query syntax.

        Args:
            query: Gmail search query (e.g., "from:foo@bar.com subject:hello")
            max_results: Maximum results to return

        Returns:
            List of matching messages.
        """
        return self.list_messages(query=query, max_results=max_results)
