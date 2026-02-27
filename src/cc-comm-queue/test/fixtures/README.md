# Test Fixtures: cc-comm-queue

## Overview

Test fixtures for the Communication Manager queue CLI. Tests queue operations, JSON formatting, and content validation.

## Fixtures

### input/linkedin_post.json
- **Purpose**: Test adding a LinkedIn post to the queue
- **Tests**: JSON parsing, persona assignment, tag handling

### expected/queued_item_format.json
- **Purpose**: Validate the structure of a queued item after creation
- **Tests**: Item has id, platform, type, content, persona, status, timestamp

## Notes

cc-comm-queue writes to the file system queue at the configured queue_path. Tests should use a temporary directory to avoid polluting the real queue.

## Last Validated
Date: 2026-02-26
Tool Version: 1.0.0
