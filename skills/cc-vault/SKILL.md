# cc-vault Skill

Interact with the Vault 2.0 personal data platform. Import documents, ask questions, manage contacts/tasks/goals/ideas.

## Triggers

- `/vault`
- `vault ask`
- `vault import`
- `search vault`
- `add to vault`

## Tool Location

`C:\cc-tools\cc-vault.exe`

## Quick Reference

### Main Commands

```bash
# Initialize vault
cc-vault init

# Get stats
cc-vault stats

# Ask a question (RAG)
cc-vault ask "What tasks do I have this week?"

# Search
cc-vault search "project requirements"
cc-vault search "project requirements" --hybrid
```

### Tasks

```bash
# List tasks
cc-vault tasks list
cc-vault tasks list -s completed
cc-vault tasks list -s all

# Add task
cc-vault tasks add "Task title" -d 2026-02-25 -p high

# Complete/cancel task
cc-vault tasks done 1
cc-vault tasks cancel 2
```

### Goals

```bash
# List goals
cc-vault goals list
cc-vault goals list -s achieved

# Add goal
cc-vault goals add "Goal title" -t 2026-03-01

# Update goal
cc-vault goals progress 1 75
cc-vault goals achieve 1
cc-vault goals pause 1
cc-vault goals resume 1
```

### Ideas

```bash
# List ideas
cc-vault ideas list
cc-vault ideas list -s actionable

# Add idea
cc-vault ideas add "New idea" -c product

# Update idea status
cc-vault ideas actionable 1
cc-vault ideas archive 1
```

### Contacts

```bash
# List contacts
cc-vault contacts list
cc-vault contacts list -s "john"

# Add contact
cc-vault contacts add "John Doe" -e john@example.com -c "Acme Corp"

# Show contact
cc-vault contacts show 1

# Add memory
cc-vault contacts memory 1 "Prefers morning meetings"

# Update contact
cc-vault contacts update 1 -r "VP Sales"
```

### Documents

```bash
# List documents
cc-vault docs list
cc-vault docs list -t research

# Import document (PDF, Word, Markdown, text)
cc-vault docs add document.pdf -t research
cc-vault docs add notes.md -t note --title "Meeting Notes"

# Show document
cc-vault docs show 1

# Search documents (FTS)
cc-vault docs search "keyword"
```

### Health

```bash
# List health entries
cc-vault health list
cc-vault health list -c daily -d 30

# Get AI insights
cc-vault health insights -q "sleep patterns"
```

### Configuration

```bash
# Show config
cc-vault config show

# Set config
cc-vault config set vault_path D:\Vault
```

## Environment Variables

- `CC_VAULT_PATH`: Vault directory path (default: ~/Vault)
- `OPENAI_API_KEY`: Required for RAG features

## Notes

- RAG queries require OPENAI_API_KEY to be set
- Document import supports .docx, .pdf, .md, .txt
- Vector search requires chromadb (installed with [full] dependencies)
- Hybrid search combines vector similarity + BM25 keyword matching
