---
name: cc-tools-skill-manager
description: Create and maintain skills for cc-tools CLI suite. Triggers on "/cc-tools-skill-manager", "create cc-tools skill", "manage cc-tools skills".
---

# CC Tools Skill Manager

Create, update, and validate skills that integrate the cc-tools CLI suite.

## Triggers

- `/cc-tools-skill-manager <mode>` (e.g., `/cc-tools-skill-manager create`)
- "create a cc-tools skill"
- "manage cc-tools skills"
- "list cc-tools"

---

## Quick Reference

| Mode | Command | Description |
|------|---------|-------------|
| Create | `/cc-tools-skill-manager create <name>` | Create a new cc-tools-integrated skill |
| Update | `/cc-tools-skill-manager update <name>` | Update existing skill documentation |
| List | `/cc-tools-skill-manager list` | Show all cc-tools and skills |
| Validate | `/cc-tools-skill-manager validate` | Check skills for valid tool references |

---

## Available Tools

| Tool | Category | Description | Key Commands |
|------|----------|-------------|--------------|
| cc-markdown | Documents | Markdown to PDF/Word/HTML | `cc-markdown file.md -o file.pdf --theme boardroom` |
| cc-transcribe | Media | Video/audio transcription with screenshots | `cc-transcribe video.mp4 -o ./output/` |
| cc-gmail | Email | Gmail: send, read, search, manage | `cc-gmail send -t email -s subj -b body` |
| cc-outlook | Email | Outlook: mail + calendar | `cc-outlook send -t email -s subj -b body` |
| cc-youtube-info | Media | YouTube transcript/metadata | `cc-youtube-info transcript URL` |
| cc-crawl4ai | Web | AI-ready web crawler | `cc-crawl4ai crawl URL --fit` |
| cc-image | AI | Image generation/analysis/OCR | `cc-image generate "prompt" -o out.png` |
| cc-voice | AI | Text-to-speech | `cc-voice speak "text" -o audio.mp3` |
| cc-whisper | AI | Audio transcription | `cc-whisper transcribe audio.mp3` |
| cc-video | Media | Video utilities | Video manipulation |
| cc-browser | Automation | Browser automation | Playwright-based web interaction |
| cc-click | Automation | Desktop automation | Mouse/keyboard automation |
| trisight | Automation | Screen analysis | Desktop vision analysis |
| cc-reddit | Social | Reddit interaction | Reddit API access |
| cc-setup | System | Tool setup/installation | Tool configuration |

### Tool Locations

- **Source:** `D:\ReposFred\cc-tools\src\<tool_name>\`
- **Public Docs:** `D:\ReposFred\cc-tools\skills\<tool_name>\SKILL.md`
- **Internal Skills:** `D:\ReposFred\cc-tools\.claude\skills\<skill_name>\skill.md`

---

## CREATE Mode

### Workflow

1. **Parse skill name** from user input
2. **Identify required tools** based on skill purpose
3. **Choose skill type:**
   - Internal skill (`.claude/skills/`) - for Claude Code automation
   - Public docs (`skills/`) - for tool documentation
4. **Select template** based on use case
5. **Generate skill file** with tool integration
6. **Validate** tool references exist

### Templates

#### Email Automation Template

For skills that use cc-gmail or cc-outlook:

```markdown
---
name: <skill_name>
description: <description>. Triggers on "<triggers>".
---

# <Skill Title>

<Brief description>

## Requirements

- cc-gmail or cc-outlook authenticated and configured

## Usage

### Send Email

\`\`\`bash
cc-gmail send -t "to@email.com" -s "Subject" -b "Body"
cc-outlook send -t "to@email.com" -s "Subject" -b "Body"
\`\`\`

### With Attachments

\`\`\`bash
cc-gmail send -t "to@email.com" -s "Subject" -b "Body" -a file.pdf
\`\`\`

## Workflow

[Step-by-step instructions specific to skill purpose]
```

#### Document Conversion Template

For skills that use cc-markdown:

```markdown
---
name: <skill_name>
description: <description>. Triggers on "<triggers>".
---

# <Skill Title>

<Brief description>

## Requirements

- Chrome/Chromium (for PDF generation)

## Usage

### Convert Markdown

\`\`\`bash
# To PDF
cc-markdown document.md -o document.pdf --theme boardroom

# To Word
cc-markdown document.md -o document.docx

# To HTML
cc-markdown document.md -o document.html
\`\`\`

### Available Themes

| Theme | Style |
|-------|-------|
| boardroom | Corporate, executive |
| terminal | Technical, monospace |
| paper | Minimal, clean |
| thesis | Academic, scholarly |
| blueprint | Technical documentation |

## Workflow

[Step-by-step instructions specific to skill purpose]
```

#### Media Processing Template

For skills using cc-transcribe, cc-youtube-info, cc-video:

```markdown
---
name: <skill_name>
description: <description>. Triggers on "<triggers>".
---

# <Skill Title>

<Brief description>

## Requirements

- FFmpeg (for video processing)
- OpenAI API key (for transcription)

## Usage

### Transcribe Video

\`\`\`bash
cc-transcribe video.mp4 -o ./output/
# Output: transcript.txt, transcript.json, screenshots/
\`\`\`

### Get YouTube Info

\`\`\`bash
cc-youtube-info transcript URL -o transcript.txt
cc-youtube-info info URL --json
cc-youtube-info chapters URL
\`\`\`

## Workflow

[Step-by-step instructions specific to skill purpose]
```

#### Web Crawling Template

For skills using cc-crawl4ai:

```markdown
---
name: <skill_name>
description: <description>. Triggers on "<triggers>".
---

# <Skill Title>

<Brief description>

## Requirements

- Playwright browsers installed (`playwright install chromium`)

## Usage

### Crawl Page

\`\`\`bash
# Basic crawl
cc-crawl4ai crawl "https://example.com" -o page.md

# With noise filtering
cc-crawl4ai crawl URL --fit

# Stealth mode
cc-crawl4ai crawl URL --stealth
\`\`\`

### Batch Crawl

\`\`\`bash
cc-crawl4ai batch urls.txt -o ./output/
\`\`\`

## Workflow

[Step-by-step instructions specific to skill purpose]
```

#### Multi-Tool Workflow Template

For skills combining multiple tools:

```markdown
---
name: <skill_name>
description: <description>. Triggers on "<triggers>".
---

# <Skill Title>

<Brief description>

## Tools Used

| Tool | Purpose |
|------|---------|
| <tool1> | <purpose> |
| <tool2> | <purpose> |

## Requirements

[List requirements for all tools]

## Workflow

### Step 1: [Action]

\`\`\`bash
<command>
\`\`\`

### Step 2: [Action]

\`\`\`bash
<command>
\`\`\`

## Output

[Describe expected outputs]
```

### Example: Create New Skill

User: "create a skill to summarize YouTube videos"

**Generated skill:**

```markdown
---
name: youtube_summarizer
description: Extract and summarize YouTube video content. Triggers on "/youtube-summary", "summarize youtube video".
---

# YouTube Summarizer

Extract transcripts from YouTube videos and generate summaries.

## Tools Used

| Tool | Purpose |
|------|---------|
| cc-youtube-info | Extract video transcript and metadata |

## Workflow

### Step 1: Get Video Info

\`\`\`bash
cc-youtube-info info URL --json
\`\`\`

Review title, duration, and chapter information.

### Step 2: Extract Transcript

\`\`\`bash
cc-youtube-info transcript URL -o transcript.txt
\`\`\`

### Step 3: Summarize

Read the transcript and generate a summary covering:
- Main topics discussed
- Key points and takeaways
- Notable quotes or insights

## Output

Provide a structured summary with:
1. Video metadata (title, duration, channel)
2. Chapter-by-chapter breakdown (if chapters exist)
3. Key points summary
4. Full transcript reference
```

---

## UPDATE Mode

### Workflow

1. **Locate existing skill** by name
2. **Read current content**
3. **Check tool references** against current cc-tools capabilities
4. **Update** with:
   - New tool commands/options
   - Corrected syntax
   - Additional use cases
5. **Validate** updated skill

### Common Updates

| Update Type | Action |
|-------------|--------|
| New command | Add command to Usage section |
| New option | Add to Options table |
| Tool rename | Update all references |
| Deprecated | Add deprecation notice |

---

## LIST Mode

### Output Format

Display all cc-tools with their availability status:

```
CC Tools Suite
==============

Document Tools:
  [OK] cc-markdown    - Markdown to PDF/Word/HTML

Email Tools:
  [OK] cc-gmail       - Gmail CLI
  [OK] cc-outlook     - Outlook + Calendar CLI

Media Tools:
  [OK] cc-transcribe  - Video/audio transcription
  [OK] cc-youtube-info - YouTube metadata/transcript
  [--] cc-video       - Video utilities (coming soon)
  [--] cc-voice       - Text-to-speech (coming soon)
  [--] cc-whisper     - Audio transcription (coming soon)

AI Tools:
  [--] cc-image       - Image gen/analysis/OCR (coming soon)

Web Tools:
  [OK] cc-crawl4ai    - AI-ready web crawler

Automation Tools:
  [OK] cc-browser     - Browser automation
  [OK] cc-click       - Desktop automation
  [OK] trisight       - Screen analysis

Social Tools:
  [--] cc-reddit      - Reddit interaction (coming soon)

System Tools:
  [OK] cc-setup       - Tool setup/installation

Existing Skills:
  .claude/skills/cc-tool-audit/skill.md
  .claude/skills/commit/skill.md
  .claude/skills/review-code/skill.md
  skills/cc-tools/SKILL.md
  skills/cc-gmail/SKILL.md
  skills/cc-outlook/SKILL.md
```

---

## VALIDATE Mode

### Checks Performed

1. **Tool references exist** - Each tool mentioned has a source directory
2. **Commands valid** - CLI commands match actual tool syntax
3. **Options current** - Options match tool's --help output
4. **No dead links** - Internal file references exist
5. **Consistent formatting** - Follows skill template structure

### Validation Report

```
Skill Validation: <skill_name>
==============================

Tool References:
  [OK] cc-gmail - Found at src/cc-gmail/
  [OK] cc-markdown - Found at src/cc-markdown/
  [!!] cc-image - Not found (tool coming soon)

Command Syntax:
  [OK] cc-gmail send -t ... -s ... -b ...
  [!!] cc-gmail --attach (should be -a or --attach)

Options:
  [OK] All options match current --help

Overall: 2 warnings, 0 errors
```

---

## File Locations

### Where to Create Skills

| Type | Location | Format |
|------|----------|--------|
| Internal (Claude Code automation) | `.claude/skills/<name>/skill.md` | lowercase skill.md |
| Public (Tool documentation) | `skills/<tool_name>/SKILL.md` | uppercase SKILL.md |

### Skill File Structure

**Internal skill:**
```
.claude/skills/<skill_name>/
    skill.md       # Skill definition (required)
```

**Public documentation:**
```
skills/<tool_name>/
    SKILL.md       # Tool documentation (required)
```

---

## Examples

### Example 1: Create Email Digest Skill

```
/cc-tools-skill-manager create email-digest
```

Creates `.claude/skills/email-digest/skill.md` that:
- Uses cc-gmail or cc-outlook to list recent emails
- Summarizes email content
- Groups by sender or topic

### Example 2: Create Research Workflow

```
/cc-tools-skill-manager create web-research
```

Creates a skill combining:
- cc-crawl4ai for web content
- cc-youtube-info for video content
- cc-markdown for report generation

### Example 3: Update Gmail Skill

```
/cc-tools-skill-manager update cc-gmail
```

Reviews `skills/cc-gmail/SKILL.md` and updates with:
- Any new commands added to cc-gmail
- Updated option syntax
- New use case examples

---

## Best Practices

### Skill Design

1. **Single responsibility** - Each skill should do one thing well
2. **Clear triggers** - Define unambiguous trigger phrases
3. **Tool selection** - Use the simplest tool that accomplishes the task
4. **Error handling** - Include common error scenarios and solutions
5. **Examples** - Provide real-world usage examples

### Tool Integration

1. **Always use CLI format** - Skills should use `cc-tool command` syntax
2. **Include all required options** - Don't assume defaults
3. **Document prerequisites** - List required auth, API keys, dependencies
4. **Show expected output** - Help users know what to expect

### Documentation

1. **Keep in sync** - Update skills when tools change
2. **Version notes** - Track significant changes
3. **Cross-reference** - Link related skills and tools

---

## Verification

After creating a skill:

1. **Skill file exists** at correct location
2. **YAML frontmatter** has name and description
3. **Tool commands** are syntactically correct
4. **Run trigger** to verify skill loads

Test commands:
```bash
# Check skill file exists
ls -la .claude/skills/<skill_name>/skill.md

# Verify tool availability
cc-gmail --version
cc-markdown --version
```

---

**Skill Version:** 1.0
**Last Updated:** 2026-02-17
**Repository:** D:\ReposFred\cc-tools
