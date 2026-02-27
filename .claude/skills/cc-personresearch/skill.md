---
name: cc-personresearch
description: Research a person using OSINT sources and generate a professional report. Triggers on "/cc-personresearch", "research person", "person report", "find person", "who is".
---

# cc-personresearch

Research a person using public OSINT data sources and generate a comprehensive, professionally formatted report in Markdown and HTML.

## Triggers

- `/cc-personresearch "Name" email@domain.com`
- "research person", "person report", "find person", "who is [name]"
- "find everything about [name]"

---

## Quick Reference

| Action | Command |
|--------|---------|
| Full research + report | `/cc-personresearch "James Henderson" james.henderson@mindzie.com` |
| API-only (fast) | `/cc-personresearch "James Henderson" james.henderson@mindzie.com --api-only` |
| Just run data collection | `/cc-personresearch "James Henderson" james.henderson@mindzie.com --data-only` |

---

## Workflow

### Step 1: Parse Input

Extract from the user's message:
- **name** (required) - the person's full name
- **email** (optional but strongly recommended) - their email address
- **location** (optional) - city/state hint to narrow results
- **flags** - `--api-only` (skip browser), `--data-only` (JSON only, no report)

If name is missing, ask the user.

### Step 2: Run cc-personresearch CLI

The tool is a Python CLI at `D:\ReposFred\cc-tools\src\cc-personresearch\`.

**Run the data collection:**

```bash
cd D:/ReposFred/cc-tools/src/cc-personresearch
venv/Scripts/python -m src.cli search --name "PERSON NAME" --email "EMAIL" --api-only --verbose -o OUTPUT.json
```

**Workspace option (if browser sources needed):**

```bash
venv/Scripts/python -m src.cli search --name "PERSON NAME" --email "EMAIL" --workspace edge-work --verbose -o OUTPUT.json
```

Notes:
- Use `--api-only` by default (fast, ~5 seconds). Only use browser mode if user explicitly asks for deep/full search or people-search site data.
- Save JSON output to a temp file for processing.

### Step 3: Analyze Results

Read the JSON report and analyze EVERY source result. This is the critical intelligence step.

For each source with data:

**WHOIS** - Note the domain registrar, organization, whether privacy is enabled.

**GitHub** - Check each user profile. Match by company, location, or email domain. Discard users that clearly don't match (wrong country, wrong company).

**SEC EDGAR** - Cross-reference company names with the person's known employer (from email domain). A "James Henderson" at mindzie won't be the same one at Eastman Kodak.

**FEC Donations** - Look for contributions where the employer matches the person's known company, or where the city/state makes sense. Discard obvious non-matches.

**Gravatar** - If found, this is high-confidence data tied directly to the email.

**Google Dorking** - Review URLs found. LinkedIn profiles, company team pages, and social media are most valuable.

**People Search Sites** (thatsthem, truepeoplesearch, zabasearch, nuwber) - These return raw text. Parse for phone numbers, addresses, relatives, age. Note that multiple people with the same name may appear -- use email, employer, or location to filter.

**Company Website** - If the person's name was found on their company's team/about page, extract their title, bio, photo URL.

**OpenCorporates** - Cross-reference corporate officer records with known employer.

**LinkedIn** - Professional profile data: headline, location, connections.

### Step 4: Generate Markdown Report

Create a professional Markdown report at `{name}-research.md` (e.g., `james-henderson-research.md`).

**Report structure:**

```markdown
# Person Research Report: {Full Name}

**Generated:** {date}
**Email:** {email}
**Confidence Level:** {High/Medium/Low} - based on how many sources corroborated

---

## Executive Summary

{2-3 sentence overview of who this person is based on the evidence collected}

---

## Identity

| Field | Value | Source |
|-------|-------|--------|
| Full Name | {name} | {source} |
| Email | {email} | Input |
| Location | {city, state} | {source} |
| Age | {age if found} | {source} |
| Phone | {phone if found} | {source} |

---

## Professional Profile

### Current Position
- **Title:** {title}
- **Company:** {company}
- **Industry:** {industry}

### LinkedIn
- **Profile:** {URL}
- **Headline:** {headline}
- **Connections:** {count}

### Company Details
- **Website:** {domain}
- **Registrar:** {from WHOIS}

---

## Online Presence

### Social Media & Profiles

| Platform | URL | Username |
|----------|-----|----------|
| LinkedIn | {url} | {username} |
| GitHub | {url} | {username} |
| Twitter/X | {url} | {username} |
| Gravatar | {url} | - |

### Web Mentions
{List notable web pages where this person is mentioned, from Google dorking results}

---

## Public Records

### SEC Filings
{If found, list relevant filings with company name, filing type, date}

### Political Donations
{If found, list donations with amount, recipient, date, employer listed}

### Corporate Records
{If found from OpenCorporates, list directorships}

---

## Address History

| Address | Source | Notes |
|---------|--------|-------|
| {address} | {source} | {current/previous} |

---

## Known Associates / Relatives

| Name | Relationship | Source |
|------|-------------|--------|
| {name} | {relationship} | {source} |

---

## Data Sources Queried

| Source | Status | Notes |
|--------|--------|-------|
| Gravatar | {Found/Not Found/Error} | {brief note} |
| GitHub | {status} | {brief note} |
| FEC | {status} | {brief note} |
| SEC EDGAR | {status} | {brief note} |
| WHOIS | {status} | {brief note} |
| Wayback | {status} | {brief note} |
| Google | {status} | {brief note} |
| ThatsThem | {status} | {brief note} |
| TruePeopleSearch | {status} | {brief note} |
| ZabaSearch | {status} | {brief note} |
| Nuwber | {status} | {brief note} |
| Company Website | {status} | {brief note} |
| OpenCorporates | {status} | {brief note} |
| LinkedIn | {status} | {brief note} |

---

**Disclaimer:** This report contains publicly available information gathered from open sources.
Results may include data about multiple people with the same name. All data should be independently verified.
```

**IMPORTANT rules for the report:**
- ONLY include sections where data was actually found. Do not include empty sections.
- Mark the confidence level based on source agreement (High = 3+ sources agree, Medium = 2 sources, Low = 1 source only).
- Always include the Data Sources table so the user knows what was checked.
- Use "Not found" or omit rows rather than showing empty cells.
- NO emojis, NO Unicode symbols. ASCII only.

### Step 5: Generate HTML Report

Convert the Markdown report to a professional HTML file using cc-markdown:

```bash
cc-markdown {name}-research.md -o {name}-research.html
```

If cc-markdown is not available, generate a standalone HTML file directly with embedded CSS. Use a clean, professional design:
- Dark header bar with person's name
- Card-based layout for each section
- Table styling with alternating row colors
- Professional color scheme (navy headers, white background, gray accents)
- Print-friendly styles
- Responsive design

### Step 6: Present Results

Tell the user:
1. What was found (high-level summary)
2. Path to the Markdown report
3. Path to the HTML report
4. Any sources that failed or were skipped
5. Suggest running with browser sources if only API was used

---

## Examples

### Basic Usage

**User:** `/cc-personresearch "James Henderson" james.henderson@mindzie.com`

**Agent:**
1. Runs `cc-personresearch search --name "James Henderson" --email "james.henderson@mindzie.com" --api-only -o temp.json`
2. Reads temp.json, analyzes results
3. Generates `james-henderson-research.md`
4. Converts to `james-henderson-research.html` via cc-markdown
5. Reports findings to user

### Deep Search

**User:** "Do a deep search on John Smith john@acme.com"

**Agent:**
1. Runs with `--workspace edge-work` (no `--api-only`) for full browser sources
2. Takes 3-5 minutes for browser automation
3. Generates comprehensive report with people-search data

### Quick Check

**User:** "Quick check on jane@company.com"

**Agent:**
1. Asks for full name (required)
2. Runs `--api-only` mode
3. Generates report

---

## File Locations

| File | Path |
|------|------|
| CLI tool | `D:\ReposFred\cc-tools\src\cc-personresearch\` |
| Python venv | `D:\ReposFred\cc-tools\src\cc-personresearch\venv\` |
| Run command | `venv/Scripts/python -m src.cli` |
| Output reports | Current working directory or user-specified path |

## Available Sources

### API Sources (fast, no browser)
gravatar, github, fec, sec_edgar, wayback, whois

### Browser Sources (require cc-browser daemon)
google_dorking, thatsthem, truepeoplesearch, zabasearch, nuwber, company_website, opencorporates

### Tool Sources (require cc-linkedin)
linkedin

---

## Error Handling

**cc-browser not running:**
- Browser sources will be skipped automatically
- API sources still work
- Tell user: "Browser sources skipped. Start cc-browser for deeper results."

**cc-linkedin not found:**
- LinkedIn source will return not_found
- Other sources still work

**Rate limiting (FEC, GitHub):**
- These APIs have rate limits
- FEC DEMO_KEY allows ~1000 requests/hour
- GitHub unauthenticated allows 10 searches/minute

---

**Skill Version:** 1.0
**Last Updated:** 2026-02-26
