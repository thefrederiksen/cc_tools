"""Simple CDP helper for clicking buttons - no Playwright needed."""
import json
import httpx


def click_element_by_text(port: int, text: str, tag: str = "button") -> dict:
    """Click an element by its text content using CDP."""
    base_url = f"http://localhost:{port}"

    # Get the websocket URL for CDP
    try:
        resp = httpx.get(f"{base_url}/json/version", timeout=5)
        ws_url = resp.json().get("webSocketDebuggerUrl")
    except Exception as e:
        return {"success": False, "error": f"Cannot connect to browser: {e}"}

    # Use cc-browser's /evaluate endpoint instead of raw CDP
    js_code = f'''
    (function() {{
        const elements = document.querySelectorAll('{tag}');
        for (const el of elements) {{
            if (el.textContent.trim() === '{text}') {{
                el.click();
                return 'clicked';
            }}
        }}
        return 'not found';
    }})()
    '''

    try:
        resp = httpx.post(f"{base_url}/evaluate", json={"js": js_code}, timeout=10)
        result = resp.json()
        if result.get("result") == "clicked":
            return {"success": True, "message": f"Clicked {tag} with text '{text}'"}
        else:
            return {"success": False, "error": f"{tag} with text '{text}' not found"}
    except Exception as e:
        return {"success": False, "error": f"Evaluate failed: {e}"}


def create_post_via_js(port: int, content: str) -> dict:
    """Create a LinkedIn post using JavaScript evaluation."""
    base_url = f"http://localhost:{port}"

    # Step 1: Navigate to feed
    try:
        httpx.post(f"{base_url}/navigate", json={"url": "https://www.linkedin.com/feed/"}, timeout=30)
    except Exception as e:
        return {"success": False, "error": f"Navigate failed: {e}"}

    import time
    time.sleep(2)

    # Step 2: Click "Start a post"
    result = click_element_by_text(port, "Start a post", "button")
    if not result.get("success"):
        # Try clicking the placeholder text area instead
        js_click_start = '''
        (function() {
            const el = document.querySelector('[data-placeholder*="Start a post"]');
            if (el) { el.click(); return 'clicked'; }
            return 'not found';
        })()
        '''
        try:
            resp = httpx.post(f"{base_url}/evaluate", json={"js": js_click_start}, timeout=10)
            if resp.json().get("result") != "clicked":
                return {"success": False, "error": "Could not find Start a post element"}
        except Exception as e:
            return {"success": False, "error": f"Click start post failed: {e}"}

    time.sleep(2)

    # Step 3: Type content
    escaped_content = content.replace("'", "\\'").replace("\n", "\\n")
    js_type = f'''
    (function() {{
        const editor = document.querySelector('[role="textbox"][contenteditable="true"]');
        if (editor) {{
            editor.focus();
            editor.textContent = '{escaped_content}';
            editor.dispatchEvent(new Event('input', {{ bubbles: true }}));
            return 'typed';
        }}
        return 'editor not found';
    }})()
    '''
    try:
        resp = httpx.post(f"{base_url}/evaluate", json={"js": js_type}, timeout=10)
        if resp.json().get("result") != "typed":
            return {"success": False, "error": "Could not type into editor"}
    except Exception as e:
        return {"success": False, "error": f"Type failed: {e}"}

    time.sleep(1)

    # Step 4: Click Post button
    result = click_element_by_text(port, "Post", "button")
    if not result.get("success"):
        return {"success": False, "error": "Could not find Post button"}

    time.sleep(3)

    # Step 5: Handle visibility modal if it appears
    for _ in range(10):
        result = click_element_by_text(port, "Done", "button")
        if result.get("success"):
            time.sleep(2)
            # Click Post again
            click_element_by_text(port, "Post", "button")
            time.sleep(3)
            break
        time.sleep(0.5)

    return {"success": True, "message": "Post created"}
