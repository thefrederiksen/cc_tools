# cc-photos

Photo organization CLI: scan directories, detect duplicates and screenshots, generate AI descriptions, search by content.

## Commands

```bash
# Manage source directories
cc-photos source add "D:\Photos" --category private --label "Family" --priority 1
cc-photos source list
cc-photos source remove "Family"

# Scan photos
cc-photos scan
cc-photos scan --source "Family"

# Find and manage duplicates
cc-photos dupes
cc-photos dupes --cleanup
cc-photos dupes --review

# List photos
cc-photos list --category private
cc-photos list --screenshots

# AI analysis
cc-photos analyze
cc-photos analyze --limit 50 --provider openai

# Search
cc-photos search "beach vacation"

# Statistics
cc-photos stats
```

## Options

| Option | Description |
|--------|-------------|
| `--category` | Filter: private, work, other |
| `--label` | Source label name |
| `--priority` | Lower = higher priority (keeps that copy for dedup) |
| `--limit` | Limit number of items |
| `--provider` | AI provider: openai or claude_code |
| `--screenshots` | Filter to screenshots only |
| `--cleanup` | Auto-remove duplicates |
| `--review` | Interactive duplicate review |

## Requirements

- OPENAI_API_KEY (for AI analysis)
- Database: ~/.cc-tools/photos.db
