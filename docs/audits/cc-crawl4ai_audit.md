# cc_tool_audit: cc-crawl4ai

## Summary

- **Tool**: cc-crawl4ai
- **API**: crawl4ai library (v0.8.x)
- **Current Commands**: `crawl`, `batch`, `session` (list, create, delete, rename, info)
- **API Coverage**: ~40% of available capabilities
- **Quick Wins Found**: 8
- **BUGS Found**: 2 (stealth and timeout flags don't work)

---

## BUGS - Must Fix

### 1. `--stealth` flag does nothing

**Severity**: HIGH - Feature is documented but broken
**Current Status**: Flag is declared in CLI and CrawlOptions, but `enable_stealth` is never passed to BrowserConfig
**Impact**: Users expect stealth mode to work based on documentation

**Fix**:
```python
# In crawler.py _build_browser_config():
return BrowserConfig(
    browser_type=options.browser,
    headless=options.headless,
    viewport_width=options.viewport_width,
    viewport_height=options.viewport_height,
    user_data_dir=user_data_dir,
    proxy=options.proxy,
    ignore_https_errors=True,
    enable_stealth=options.stealth,  # ADD THIS LINE
)
```

### 2. `--timeout` flag does nothing

**Severity**: MEDIUM - Flag is declared but not wired up
**Current Status**: `timeout` is in CrawlOptions but never passed to CrawlerRunConfig as `page_timeout`
**Impact**: Users cannot override default timeout

**Fix**:
```python
# In crawler.py _build_crawler_config():
config_kwargs = {
    "cache_mode": _get_cache_mode(options.cache),
    "wait_for": options.wait_for,
    "screenshot": options.screenshot,
    "page_timeout": options.timeout,  # ADD THIS LINE
}
```

---

## Current Implementation Map

### BrowserConfig Usage

```
PARAMS USED:
  - browser_type, headless, viewport_width, viewport_height
  - user_data_dir, proxy, ignore_https_errors

PARAMS NOT USED:
  - enable_stealth (BUG - declared but not passed)
  - verbose
  - user_agent, user_agent_mode
  - text_mode (disable images)
  - light_mode (performance mode)
  - cookies, headers
  - use_persistent_context
  - extra_args
  - browser_mode, cdp_url, use_managed_browser
```

### CrawlerRunConfig Usage

```
PARAMS USED:
  - cache_mode, wait_for, screenshot
  - js_code, extraction_strategy, markdown_generator

PARAMS NOT USED:
  - page_timeout (BUG - declared but not passed)
  - pdf (generate PDF!)
  - capture_mhtml (MHTML archive)
  - word_count_threshold
  - scan_full_page (native scroll)
  - scroll_delay (native)
  - remove_overlay_elements
  - exclude_external_links
  - excluded_tags
  - locale, timezone_id, geolocation
  - delay_before_return_html
  - wait_until ("networkidle")
  - session_id (native session)
  - css_selector (native, not just extraction)
  - proxy_rotation_strategy
```

### CrawlResult Fields Usage

```
FIELDS USED:
  - success, error_message
  - markdown (fit_markdown, raw_markdown)
  - html, raw_html
  - links (internal, external)
  - media (images)
  - metadata, extracted_content, screenshot

FIELDS NOT USED:
  - cleaned_html
  - status_code
  - response_headers
  - ssl_certificate
  - network_requests (API calls page made!)
  - console_messages (JS errors)
  - downloaded_files
  - pdf (bytes)
  - mhtml
```

---

## Prioritized Recommendations

| Priority | Feature | Effort | LLM Value | Use Case |
|----------|---------|--------|-----------|----------|
| 1 | Fix stealth bug | Trivial | High | "Crawl this protected site" |
| 2 | Fix timeout bug | Trivial | High | "Wait longer for slow pages" |
| 3 | PDF capture | Trivial | High | "Save this page as PDF" |
| 4 | text_mode | Trivial | High | "Fast crawl, text only" |
| 5 | scan_full_page | Trivial | Medium | Simplifies scroll, more reliable |
| 6 | remove_overlay_elements | Trivial | Medium | "Remove popups" |
| 7 | status_code | Trivial | Medium | "Did the page load OK?" |
| 8 | wait_until=networkidle | Trivial | Medium | "Wait for all AJAX to finish" |
| 9 | MHTML capture | Small | Medium | "Archive this page completely" |
| 10 | network_requests | Small | High | "What API calls did this page make?" |

---

## Quick Wins (Trivial Effort, High LLM Value)

### 1. PDF Capture

**API Feature**: `pdf=True` in CrawlerRunConfig
**Current Status**: Not exposed
**Implementation**: Add --pdf flag to crawl command
**LLM Use Case**: "Save this page as a PDF for offline reading"

**Code Sketch**:
```python
# In crawler.py CrawlOptions:
pdf: bool = False
pdf_path: Optional[str] = None

# In _build_crawler_config():
config_kwargs["pdf"] = options.pdf

# In crawl_url() after result:
if options.pdf and hasattr(result, 'pdf') and result.pdf:
    pdf_path = options.pdf_path or f"page_{url_safe}.pdf"
    Path(pdf_path).write_bytes(result.pdf)
    return CrawlResult(..., pdf_path=pdf_path)

# In cli.py:
pdf: bool = typer.Option(False, "--pdf", help="Generate PDF of page"),
pdf_path: Optional[Path] = typer.Option(None, "--pdf-path", help="PDF output path"),
```

### 2. text_mode (Fast Text-Only Crawl)

**API Feature**: `text_mode=True` in BrowserConfig
**Current Status**: Not exposed
**Implementation**: Add --text-only flag
**LLM Use Case**: "Just get the text fast, skip images"

**Code Sketch**:
```python
# In crawler.py CrawlOptions:
text_only: bool = False

# In _build_browser_config():
return BrowserConfig(
    ...
    text_mode=options.text_only,  # Disables image loading
)

# In cli.py:
text_only: bool = typer.Option(False, "--text-only", help="Disable image loading for faster crawl"),
```

### 3. scan_full_page (Replace Custom Scroll JS)

**API Feature**: `scan_full_page=True` in CrawlerRunConfig
**Current Status**: Using custom JS for scrolling
**Implementation**: Replace custom JS with native param
**LLM Use Case**: "Load all lazy content"

**Code Sketch**:
```python
# In _build_crawler_config(), replace the custom scroll JS with:
if options.scroll:
    config_kwargs["scan_full_page"] = True
    config_kwargs["scroll_delay"] = options.scroll_delay / 1000  # Convert ms to seconds

# DELETE the custom scroll_js code block
```

This simplifies the code and uses crawl4ai's native implementation.

### 4. remove_overlay_elements

**API Feature**: `remove_overlay_elements=True` in CrawlerRunConfig
**Current Status**: Not exposed
**Implementation**: Add --remove-overlays flag
**LLM Use Case**: "Remove cookie banners and popups"

**Code Sketch**:
```python
# In crawler.py CrawlOptions:
remove_overlays: bool = False

# In _build_crawler_config():
config_kwargs["remove_overlay_elements"] = options.remove_overlays

# In cli.py:
remove_overlays: bool = typer.Option(False, "--remove-overlays", help="Remove popups and cookie banners"),
```

### 5. status_code Exposure

**API Feature**: `result.status_code` - HTTP status code
**Current Status**: Field ignored
**Implementation**: Include in CrawlResult
**LLM Use Case**: "Did the page return 404?" / "Was there a redirect?"

**Code Sketch**:
```python
# In crawler.py CrawlResult:
status_code: Optional[int] = None

# In crawl_url():
return CrawlResult(
    ...
    status_code=result.status_code if hasattr(result, 'status_code') else None,
)

# In cli.py output:
if result.status_code:
    console.print(f"[cyan]Status:[/cyan] {result.status_code}")
```

### 6. wait_until="networkidle"

**API Feature**: `wait_until` param - "domcontentloaded" or "networkidle"
**Current Status**: Not exposed (uses default)
**Implementation**: Add --wait-until flag
**LLM Use Case**: "Wait for all AJAX calls to finish before extracting"

**Code Sketch**:
```python
# In crawler.py CrawlOptions:
wait_until: str = "domcontentloaded"  # or "networkidle"

# In _build_crawler_config():
config_kwargs["wait_until"] = options.wait_until

# In cli.py:
wait_until: str = typer.Option("domcontentloaded", "--wait-until",
    help="Wait condition: domcontentloaded or networkidle"),
```

### 7. cleaned_html Output Format

**API Feature**: `result.cleaned_html` - sanitized HTML
**Current Status**: Only raw_html and html exposed
**Implementation**: Add "cleaned" as output format option
**LLM Use Case**: "Give me the HTML but cleaned up"

**Code Sketch**:
```python
# In _get_content_by_format():
elif options.output_format == "cleaned":
    return result.cleaned_html if hasattr(result, 'cleaned_html') else (result.html or "")

# In cli.py help text:
format: str = typer.Option("markdown", "-f", "--format",
    help="Output format: markdown, json, html, raw, cleaned"),
```

### 8. exclude_external_links

**API Feature**: `exclude_external_links=True` in CrawlerRunConfig
**Current Status**: Not exposed
**Implementation**: Add --internal-links-only flag
**LLM Use Case**: "Only keep links to the same domain"

**Code Sketch**:
```python
# In crawler.py CrawlOptions:
internal_links_only: bool = False

# In _build_crawler_config():
config_kwargs["exclude_external_links"] = options.internal_links_only

# In cli.py:
internal_links_only: bool = typer.Option(False, "--internal-links-only",
    help="Exclude external links from output"),
```

---

## Small-Effort Improvements

### 1. MHTML Archive Capture

**API Feature**: `capture_mhtml=True` returns MHTML string
**Current Status**: Not exposed
**Implementation**: Add --mhtml flag to save complete page archive
**LLM Use Case**: "Archive this page with all resources"

**Code Sketch**:
```python
# In crawler.py CrawlOptions:
mhtml: bool = False
mhtml_path: Optional[str] = None

# In _build_crawler_config():
config_kwargs["capture_mhtml"] = options.mhtml

# In crawl_url():
if options.mhtml and hasattr(result, 'mhtml') and result.mhtml:
    mhtml_path = options.mhtml_path or f"archive_{url_safe}.mhtml"
    Path(mhtml_path).write_text(result.mhtml, encoding='utf-8')
```

### 2. Network Request Capture

**API Feature**: `result.network_requests` - all HTTP requests page made
**Current Status**: Not exposed
**Implementation**: Add --capture-network flag
**LLM Use Case**: "What API endpoints does this page call?"

This is valuable for LLM debugging - understanding what data a page fetches.

**Code Sketch**:
```python
# In CrawlResult:
network_requests: list = field(default_factory=list)

# In crawl_url():
network_requests=result.network_requests if hasattr(result, 'network_requests') else []

# CLI output:
if result.network_requests:
    console.print(f"\n[cyan]Network Requests ({len(result.network_requests)}):[/cyan]")
    for req in result.network_requests[:20]:
        console.print(f"  {req.get('method', 'GET')} {req.get('url', '')[:80]}")
```

### 3. Cookie/Header Support

**API Feature**: `cookies` and `headers` in BrowserConfig
**Current Status**: Not exposed
**Implementation**: Add --cookie and --header options
**LLM Use Case**: "Crawl with this auth token"

**Code Sketch**:
```python
# In CrawlOptions:
cookies: Optional[str] = None  # JSON string or file path
headers: Optional[dict] = None

# In _build_browser_config():
cookies_list = None
if options.cookies:
    # Parse JSON or load from file
    cookies_list = json.loads(options.cookies) if options.cookies.startswith('[') else ...

return BrowserConfig(
    ...
    cookies=cookies_list,
    headers=options.headers,
)
```

### 4. Locale/Timezone Spoofing

**API Feature**: `locale`, `timezone_id`, `geolocation` in CrawlerRunConfig
**Current Status**: Not exposed
**Implementation**: Add --locale, --timezone flags
**LLM Use Case**: "Crawl as if from France" / "See region-specific content"

**Code Sketch**:
```python
# In CrawlOptions:
locale: Optional[str] = None  # e.g., "fr-FR"
timezone: Optional[str] = None  # e.g., "Europe/Paris"

# In _build_crawler_config():
if options.locale:
    config_kwargs["locale"] = options.locale
if options.timezone:
    config_kwargs["timezone_id"] = options.timezone
```

---

## Medium-Effort Improvements

### 1. Use Native arun_many() for Batch

**API Feature**: `crawler.arun_many()` with adaptive concurrency
**Current Status**: Rolling our own parallel implementation
**Benefit**: Memory-aware, automatic rate limiting, streaming support
**Consideration**: Would require significant refactor of batch.py

The current implementation works, but the native arun_many() provides:
- Memory-adaptive dispatch
- Automatic exponential backoff
- URL-specific config matching
- Streaming mode for large batches

### 2. Console Message Capture

**API Feature**: `result.console_messages` - browser console output
**Current Status**: Not exposed
**Implementation**: Add --capture-console flag
**LLM Use Case**: "Are there JS errors on this page?"

### 3. SSL Certificate Info

**API Feature**: `result.ssl_certificate` - certificate details
**Current Status**: Not exposed
**Implementation**: Add --ssl-info flag
**LLM Use Case**: "Check if site has valid SSL" / "When does the cert expire?"

---

## API Features Not Used

| Feature | API | Purpose | Potential Use Case |
|---------|-----|---------|-------------------|
| `browser_mode="docker"` | BrowserConfig | Run in Docker | Isolated crawling |
| `cdp_url` | BrowserConfig | Remote browser | Scale across machines |
| `user_agent_mode="random"` | BrowserConfig | Randomize UA | Better stealth |
| `word_count_threshold` | CrawlerRunConfig | Min content | Skip thin pages |
| `excluded_tags` | CrawlerRunConfig | Remove elements | Skip nav, footer |
| `delay_before_return_html` | CrawlerRunConfig | Final delay | Wait for animations |
| `chunking_strategy` | CrawlerRunConfig | LLM chunking | Long document handling |
| `RegexExtractionStrategy` | Extraction | Pattern matching | Fast structured extraction |

---

## Documentation Assessment

| Criteria | Status | Notes |
|----------|--------|-------|
| Clear purpose | OK | "AI-ready web crawler that extracts clean markdown" |
| What it does NOT do | Missing | Should clarify: not a sitemap crawler, not for mass scraping |
| Descriptive name | OK | `cc-crawl4ai` - clearly indicates crawl4ai wrapper |
| LLM use cases | OK | Examples show typical LLM workflows |
| **BUG documentation** | FAIL | --stealth and --timeout are documented but don't work |

### Documentation Recommendations

1. **Fix the bugs** - stealth and timeout must work as documented
2. **Add "What This Tool Does NOT Do" section**:
   ```markdown
   ## Limitations

   - Not a sitemap/recursive crawler - crawls one URL at a time
   - Not for mass scraping - use responsibly
   - No JavaScript rendering debugging - use browser DevTools
   ```
3. **Add LLM-specific tips**:
   ```markdown
   ## Tips for LLM Usage

   - Use `--fit` to reduce noise and token count
   - Use `--query "topic"` to extract only relevant content
   - Use `--links` to get all URLs for follow-up crawls
   ```

---

## Notes

1. **Bug fixes are critical** - The stealth and timeout flags being broken is a significant issue. Users relying on stealth mode for protected sites will fail silently.

2. **PDF capture is high value** - Many LLM use cases involve saving content. PDF is a universal format.

3. **text_mode is a quick performance win** - For text-only extraction, skipping images significantly speeds up crawls.

4. **scan_full_page simplifies code** - The current custom scroll JS can be replaced with native parameter, reducing code complexity.

5. **Network request capture is unique** - This feature lets LLMs understand what data a page fetches, useful for debugging SPAs and understanding API structures.

6. **Consider keeping batch.py** - While arun_many() is more sophisticated, the current implementation is simpler and works well. Only refactor if specific features (streaming, memory adaptation) are needed.

---

## Sources

- [Crawl4AI GitHub Repository](https://github.com/unclecode/crawl4ai)
- [Crawl4AI Documentation - Browser & Crawler Config](https://docs.crawl4ai.com/core/browser-crawler-config/)
- [Crawl4AI Complete SDK Reference](https://docs.crawl4ai.com/complete-sdk-reference/)
- [Crawl4AI Advanced Features](https://docs.crawl4ai.com/advanced/advanced-features/)

---

**Audit Date**: 2026-02-17
**Audited By**: Claude (cc_tool_audit skill)
