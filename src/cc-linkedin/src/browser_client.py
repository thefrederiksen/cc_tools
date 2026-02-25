"""HTTP client wrapper for cc_browser daemon."""

import httpx
import json
import os
from pathlib import Path
from typing import Optional


class BrowserError(Exception):
    """Error from cc_browser daemon."""
    pass


class ProfileError(Exception):
    """Error resolving browser profile."""
    pass


def get_cc_browser_dir() -> Path:
    """Get cc-browser profiles directory."""
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    if not local_app_data:
        raise ProfileError(
            "LOCALAPPDATA environment variable not set. "
            "Cannot locate cc-browser profiles."
        )
    return Path(local_app_data) / "cc-browser"


def resolve_profile(profile_name: str) -> dict:
    """Resolve profile name or alias to profile config.

    Scans all cc-browser profile directories for matching profile name or alias.

    Args:
        profile_name: Profile name or alias (e.g., "linkedin", "work", "chrome-work")

    Returns:
        Profile config dict with browser, profile, daemonPort, etc.

    Raises:
        ProfileError: If profile cannot be found or resolved.
    """
    cc_browser_dir = get_cc_browser_dir()

    if not cc_browser_dir.exists():
        raise ProfileError(
            f"cc-browser directory not found: {cc_browser_dir}\n"
            "Install cc-browser and create a profile first.\n"
            "Run: cc-browser profile create linkedin"
        )

    # Scan all profile directories
    for profile_dir in cc_browser_dir.iterdir():
        if not profile_dir.is_dir():
            continue

        profile_json = profile_dir / "profile.json"
        if not profile_json.exists():
            continue

        try:
            with open(profile_json, "r") as f:
                config = json.load(f)
        except (json.JSONDecodeError, IOError):
            continue

        # Check if profile name matches directory name
        if profile_dir.name == profile_name:
            return config

        # Check if profile name matches browser-profile combo
        browser = config.get("browser", "")
        profile = config.get("profile", "")
        if f"{browser}-{profile}" == profile_name:
            return config

        # Check aliases
        aliases = config.get("aliases", [])
        if profile_name in aliases:
            return config

    # Profile not found - provide helpful error
    available = []
    for profile_dir in cc_browser_dir.iterdir():
        if profile_dir.is_dir():
            profile_json = profile_dir / "profile.json"
            if profile_json.exists():
                try:
                    with open(profile_json, "r") as f:
                        config = json.load(f)
                    aliases = config.get("aliases", [])
                    available.append(f"{profile_dir.name} (aliases: {', '.join(aliases)})")
                except (json.JSONDecodeError, IOError):
                    available.append(profile_dir.name)

    available_str = "\n  - ".join(available) if available else "(none found)"
    raise ProfileError(
        f"Profile '{profile_name}' not found.\n\n"
        f"Available profiles:\n  - {available_str}\n\n"
        "To add 'linkedin' as an alias to an existing profile, edit its profile.json "
        "and add 'linkedin' to the aliases array."
    )


def get_port_for_profile(profile_name: str) -> int:
    """Get daemon port for a profile name or alias.

    Args:
        profile_name: Profile name or alias

    Returns:
        Daemon port number

    Raises:
        ProfileError: If profile not found or has no daemonPort.
    """
    config = resolve_profile(profile_name)

    port = config.get("daemonPort")
    if not port:
        raise ProfileError(
            f"Profile '{profile_name}' has no daemonPort configured.\n"
            "Edit the profile.json and add a daemonPort field."
        )

    return port


class BrowserClient:
    """HTTP client for cc_browser daemon.

    Communicates with the cc_browser daemon on localhost.
    Profile is resolved to get the daemon port.
    """

    def __init__(self, profile: str, timeout: float = 30.0):
        """Initialize browser client for a profile.

        Args:
            profile: Profile name or alias (e.g., "linkedin", "work")
            timeout: HTTP request timeout in seconds

        Raises:
            ProfileError: If profile cannot be resolved.
        """
        self.profile = profile
        self.port = get_port_for_profile(profile)
        self.base_url = f"http://localhost:{self.port}"
        self.timeout = timeout
        self._client = httpx.Client(timeout=timeout)

    def _post(self, endpoint: str, data: Optional[dict] = None) -> dict:
        """Send POST request to daemon."""
        try:
            response = self._client.post(
                f"{self.base_url}{endpoint}",
                json=data or {}
            )
            result = response.json()

            if not result.get("success", False):
                raise BrowserError(result.get("error", "Unknown error"))

            return result
        except httpx.ConnectError:
            raise BrowserError(
                f"Cannot connect to cc_browser daemon on port {self.port}.\n"
                f"Start it with: cc-browser daemon --profile {self.profile}"
            )
        except httpx.TimeoutException:
            raise BrowserError(f"Request timed out after {self.timeout}s")

    def _get(self, endpoint: str) -> dict:
        """Send GET request to daemon."""
        try:
            response = self._client.get(f"{self.base_url}{endpoint}")
            result = response.json()

            if not result.get("success", False):
                raise BrowserError(result.get("error", "Unknown error"))

            return result
        except httpx.ConnectError:
            raise BrowserError(
                f"Cannot connect to cc_browser daemon on port {self.port}.\n"
                f"Start it with: cc-browser daemon --profile {self.profile}"
            )
        except httpx.TimeoutException:
            raise BrowserError(f"Request timed out after {self.timeout}s")

    def status(self) -> dict:
        """Get daemon and browser status."""
        return self._get("/")

    def start(self, profile_dir: Optional[str] = None, headless: bool = False) -> dict:
        """Launch browser."""
        data = {"headless": headless}
        if profile_dir:
            data["profileDir"] = profile_dir
        return self._post("/start", data)

    def stop(self) -> dict:
        """Close browser."""
        return self._post("/stop")

    def navigate(self, url: str) -> dict:
        """Navigate to URL."""
        return self._post("/navigate", {"url": url})

    def reload(self) -> dict:
        """Reload current page."""
        return self._post("/reload")

    def back(self) -> dict:
        """Go back."""
        return self._post("/back")

    def forward(self) -> dict:
        """Go forward."""
        return self._post("/forward")

    def snapshot(self, interactive: bool = True) -> dict:
        """Get page snapshot with element refs."""
        return self._post("/snapshot", {"interactive": interactive})

    def info(self) -> dict:
        """Get current page info (URL, title)."""
        return self._post("/info")

    def text(self, selector: Optional[str] = None) -> dict:
        """Get page text content."""
        data = {}
        if selector:
            data["selector"] = selector
        return self._post("/text", data)

    def html(self, selector: Optional[str] = None) -> dict:
        """Get page HTML."""
        data = {}
        if selector:
            data["selector"] = selector
        return self._post("/html", data)

    def click(self, ref: str) -> dict:
        """Click element by ref."""
        return self._post("/click", {"ref": ref})

    def type(self, ref: str, text: str) -> dict:
        """Type text into element."""
        return self._post("/type", {"ref": ref, "text": text})

    def press(self, key: str) -> dict:
        """Press keyboard key."""
        return self._post("/press", {"key": key})

    def hover(self, ref: str) -> dict:
        """Hover over element."""
        return self._post("/hover", {"ref": ref})

    def select(self, ref: str, value: str) -> dict:
        """Select dropdown option."""
        return self._post("/select", {"ref": ref, "value": value})

    def scroll(self, direction: str = "down", ref: Optional[str] = None) -> dict:
        """Scroll page or element."""
        data = {"direction": direction}
        if ref:
            data["ref"] = ref
        return self._post("/scroll", data)

    def screenshot(self, full_page: bool = False) -> dict:
        """Take screenshot (returns base64)."""
        return self._post("/screenshot", {"fullPage": full_page})

    def wait_for_text(self, text: str, timeout: int = 5000) -> dict:
        """Wait for text to appear."""
        return self._post("/wait", {"text": text, "timeout": timeout})

    def wait(self, ms: int) -> dict:
        """Wait for specified time."""
        return self._post("/wait", {"time": ms})

    def evaluate(self, js: str) -> dict:
        """Execute JavaScript."""
        return self._post("/evaluate", {"js": js})

    def fill(self, fields: list) -> dict:
        """Fill multiple form fields."""
        return self._post("/fill", {"fields": fields})

    def upload(self, ref: str, path: str) -> dict:
        """Upload file."""
        return self._post("/upload", {"ref": ref, "path": path})

    def tabs(self) -> dict:
        """List all tabs."""
        return self._post("/tabs")

    def tabs_open(self, url: Optional[str] = None) -> dict:
        """Open new tab."""
        data = {}
        if url:
            data["url"] = url
        return self._post("/tabs/open", data)

    def tabs_close(self, tab_id: str) -> dict:
        """Close tab."""
        return self._post("/tabs/close", {"tab": tab_id})

    def tabs_focus(self, tab_id: str) -> dict:
        """Focus tab."""
        return self._post("/tabs/focus", {"tab": tab_id})

    def close(self):
        """Close HTTP client."""
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


# Convenience function for quick operations
def get_client(profile: str) -> BrowserClient:
    """Get a browser client instance for a profile."""
    return BrowserClient(profile=profile)
