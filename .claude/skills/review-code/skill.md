---
name: review-code
description: Review recent code changes for security issues and bugs against CodingStyle.md. Triggers on "/review-code" or when called by commit skill.
---

# Code Review Skill

Review changed files against docs/CodingStyle.md.

## Triggers

Invoke with /review-code or when called by commit skill.

## Workflow

STEP 1: Get files to review

Use Bash tool to run: git diff --cached --name-only
Then run: git diff --name-only

Collect all .py files from the output.

STEP 2: Read the standards (MANDATORY)

Use the Read tool to read: docs/CodingStyle.md

Do NOT skip this. Do NOT rely on memory. Actually READ this file.

STEP 3: Review each changed file

For each file from Step 1:
- Use the Read tool to read the full file
- Compare against the rules from docs/CodingStyle.md
- Record issues with FULL PATH and line number

Issue severities:
- BLOCKING: Must fix. Causes review to FAIL.
- WARNING: Should fix. Review still PASSES.
- SUGGESTION: Nice to have. Review still PASSES.

STEP 4: Present findings

Use this exact format (plain text, no markdown tables):

Code Review Report

Files Reviewed: [count]
Standards Applied: CodingStyle.md
Result: PASS or FAIL

BLOCKING Issues (must fix before commit):

[full path]:[line]
Issue: [what is wrong]
Fix: [how to fix it]

WARNING Issues (should fix):

[full path]:[line]
Issue: [what is wrong]

SUGGESTIONS:

[full path]:[line]
Issue: [what could be improved]

CRITICAL: Use FULL file paths like D:\ReposFred\cc-tools\src\cc-markdown\main.py:45
Never use just the filename.

STEP 5: Return structured status

At the very end, include these lines exactly:

REVIEW_STATUS: PASS or FAIL
BLOCKING_COUNT: [number]
WARNING_COUNT: [number]
SUGGESTION_COUNT: [number]

FAIL if any BLOCKING issues exist. PASS otherwise.

## Common Issues from CodingStyle.md

BLOCKING:
- Bare `except:` clauses (swallowing all exceptions)
- Missing type hints on public functions/methods
- Mutable default arguments (def func(items=[]))
- Hard-coded credentials or API keys
- Using print() instead of proper logging in library code
- Fallback programming patterns (try/except that silently continues)
- Blocking I/O in async functions without proper handling
- Using git add . or git add -A

BLOCKING - PII (Personal Identifiable Information):
- Real email addresses (not @example.com, @test.com, or @placeholder.com)
- Phone numbers in any format (xxx-xxx-xxxx, (xxx) xxx-xxxx, +1xxxxxxxxxx)
- Physical/mailing addresses (street names, city/state/zip patterns)
- Personal names with identifying context (in comments, strings with contact info)
- Company-specific internal URLs or system names
- Employee IDs, account numbers, social security patterns

BLOCKING - Secrets and Credentials:
- OpenAI API keys (sk-...)
- AWS credentials (AKIA..., aws_access_key, aws_secret_key)
- GitHub tokens (ghp_, gho_, github_pat_)
- Azure/GCP credentials patterns
- Bearer tokens (Bearer eyJ..., Authorization: Bearer)
- Connection strings with embedded passwords
- Hard-coded passwords (password=, pwd=, passwd=, secret=)
- OAuth client secrets (client_secret=)
- Private keys (BEGIN RSA PRIVATE, BEGIN PRIVATE KEY, BEGIN EC PRIVATE)
- JWT tokens in code (eyJ...)
- Database URLs with credentials (postgres://user:pass@, mysql://user:pass@)

Exceptions (NOT blocking):
- Example/placeholder values: example@example.com, test@test.com, your-api-key-here
- Obvious test data: John Doe, Jane Doe, Test User, 555-xxx-xxxx
- Documentation showing format without real values
- Regex patterns for validation (unless they contain real data)

WARNING:
- Functions over 50 lines
- Missing `if __name__ == "__main__"` guard in scripts
- `from module import *` usage
- Unused imports
- TODO/FIXME comments in committed code
- Missing docstrings on public functions/classes
- Inconsistent naming (mixedCase instead of snake_case)

## Python-Specific Issues

BLOCKING:
- Catching Exception or BaseException without re-raising
- Missing required parameters (positional args after keyword args)
- Using eval() or exec() with untrusted input

WARNING:
- Not using context managers for file operations
- Using mutable objects as class attributes (shared state bug)
- Missing return type hints on public methods
- Long import lists that should be grouped

## PII and Secrets Scan

When reviewing each file, specifically check for:

1. Email patterns:
   - Regex: \b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b
   - Flag any that are not clearly fake (@example.com, @test.com)

2. Credential patterns to flag:
   - sk-[a-zA-Z0-9]{20,} (OpenAI)
   - AKIA[A-Z0-9]{16} (AWS)
   - ghp_[a-zA-Z0-9]{36} (GitHub PAT)
   - eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+ (JWT)
   - -----BEGIN (RSA|EC|PRIVATE) (private keys)
   - password\s*=\s*["'][^"']+["'] (hardcoded passwords)
   - (postgres|mysql|mongodb)://[^:]+:[^@]+@ (connection strings with creds)

3. Phone number patterns:
   - \b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b
   - \(\d{3}\)\s*\d{3}[-.\s]?\d{4}
   - Exception: 555-xxx-xxxx (reserved test numbers)

4. Address patterns:
   - Street suffixes: St, Street, Ave, Avenue, Blvd, etc. with numbers
   - City, State ZIP combinations

5. Comments and strings:
   - Check comments for personal information
   - Check string literals for contact information
   - Check config dictionaries for real credentials

If ANY of these are found with real values, mark as BLOCKING and require removal before commit.

## Notes

Focus on changed code, not legacy issues.
Be specific with line numbers.
The commit skill depends on the REVIEW_STATUS line.

---

**Skill Version:** 1.1
**Last Updated:** 2026-02-18
**Adapted from:** cc-director review-code skill
