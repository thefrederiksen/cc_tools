"""OAuth2 authentication for Gmail API with multi-account support."""

import json
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from cc_shared.config import get_data_dir

logger = logging.getLogger(__name__)


# Gmail API scopes
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.modify",
]

# Config directory - uses shared data directory for service compatibility
CONFIG_DIR = get_data_dir() / "gmail"
ACCOUNTS_DIR = CONFIG_DIR / "accounts"
CONFIG_FILE = CONFIG_DIR / "config.json"

# README location for help messages
README_PATH = Path(__file__).parent.parent / "README.md"


def get_readme_path() -> str:
    """Get the path to the README file for help messages."""
    if README_PATH.exists():
        return str(README_PATH)
    return "https://github.com/CenterConsulting/cc_tools/tree/main/src/cc_gmail"


def get_config_dir() -> Path:
    """Get the configuration directory, creating it if necessary."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    ACCOUNTS_DIR.mkdir(parents=True, exist_ok=True)
    return CONFIG_DIR


def get_account_dir(account: str) -> Path:
    """Get the directory for a specific account."""
    account_dir = ACCOUNTS_DIR / account
    account_dir.mkdir(parents=True, exist_ok=True)
    return account_dir


def get_credentials_path(account: str) -> Path:
    """Get the path to the OAuth credentials file for an account."""
    return get_account_dir(account) / "credentials.json"


def get_token_path(account: str) -> Path:
    """Get the path to the token file for an account."""
    return get_account_dir(account) / "token.json"


def load_config() -> Dict[str, Any]:
    """Load the global config file."""
    get_config_dir()  # Ensure directory exists
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {"default_account": None}


def save_config(config: Dict[str, Any]) -> None:
    """Save the global config file."""
    get_config_dir()
    CONFIG_FILE.write_text(json.dumps(config, indent=2))


def get_default_account() -> Optional[str]:
    """Get the default account name."""
    config = load_config()
    return config.get("default_account")


def set_default_account(account: str) -> None:
    """Set the default account."""
    config = load_config()
    config["default_account"] = account
    save_config(config)


def list_accounts() -> List[Dict[str, Any]]:
    """List all configured accounts."""
    get_config_dir()
    accounts = []
    default = get_default_account()

    if not ACCOUNTS_DIR.exists():
        return accounts

    for account_dir in ACCOUNTS_DIR.iterdir():
        if account_dir.is_dir():
            name = account_dir.name
            creds_exist = (account_dir / "credentials.json").exists()
            token_exist = (account_dir / "token.json").exists()

            # Try to get email from token
            email = None
            if token_exist:
                try:
                    creds = load_credentials(name)
                    if creds:
                        # Email is retrieved when API is used
                        pass
                except RefreshError as e:
                    logger.debug(f"Could not load credentials for '{name}': {e}")

            accounts.append({
                "name": name,
                "is_default": name == default,
                "credentials_exists": creds_exist,
                "authenticated": token_exist and creds_exist,
            })

    return sorted(accounts, key=lambda x: x["name"])


def credentials_exist(account: str) -> bool:
    """Check if OAuth credentials file exists for an account."""
    return get_credentials_path(account).exists()


def token_exists(account: str) -> bool:
    """Check if token file exists for an account."""
    return get_token_path(account).exists()


def load_credentials(account: str) -> Optional[Credentials]:
    """Load credentials from token file if available and valid."""
    token_path = get_token_path(account)
    if not token_path.exists():
        return None

    creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    # If credentials are expired, try to refresh
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            save_credentials(account, creds)
        except RefreshError as e:
            logger.warning(f"Token refresh failed for account '{account}': {e}")
            return None

    return creds if creds and creds.valid else None


def save_credentials(account: str, creds: Credentials) -> None:
    """Save credentials to token file."""
    get_account_dir(account)  # Ensure directory exists
    get_token_path(account).write_text(creds.to_json())


def authenticate(account: str, force: bool = False) -> Credentials:
    """
    Authenticate with Gmail API for a specific account.

    Args:
        account: Account name
        force: If True, force re-authentication even if valid token exists.

    Returns:
        Valid credentials for Gmail API.

    Raises:
        FileNotFoundError: If credentials.json is missing.
        Exception: If authentication fails.
    """
    creds_path = get_credentials_path(account)

    if not creds_path.exists():
        raise FileNotFoundError(
            f"OAuth credentials not found for account '{account}'\n\n"
            f"Expected location: {creds_path}\n\n"
            f"See README for setup instructions: {get_readme_path()}"
        )

    creds = None

    # Try to load existing credentials if not forcing re-auth
    if not force:
        creds = load_credentials(account)

    # If no valid credentials, run OAuth flow
    if not creds:
        flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
        creds = flow.run_local_server(port=0)
        save_credentials(account, creds)

    return creds


def revoke_token(account: str) -> bool:
    """Delete the token file to force re-authentication."""
    token_path = get_token_path(account)
    if token_path.exists():
        token_path.unlink()
        return True
    return False


def delete_account(account: str) -> bool:
    """Delete an account and all its files."""
    import shutil
    account_dir = get_account_dir(account)
    if account_dir.exists():
        shutil.rmtree(account_dir)
        # If this was the default, clear it
        if get_default_account() == account:
            config = load_config()
            config["default_account"] = None
            save_config(config)
        return True
    return False


def get_auth_status(account: str) -> dict:
    """Get the authentication status for an account."""
    status = {
        "account": account,
        "account_dir": str(get_account_dir(account)),
        "credentials_exists": credentials_exist(account),
        "token_exists": token_exists(account),
        "authenticated": False,
        "is_default": get_default_account() == account,
    }

    creds = load_credentials(account)
    if creds and creds.valid:
        status["authenticated"] = True

    return status


def resolve_account(account: Optional[str]) -> str:
    """
    Resolve which account to use.

    Args:
        account: Explicit account name, or None to use default.

    Returns:
        Account name to use.

    Raises:
        ValueError: If no account specified and no default set.
    """
    if account:
        return account

    default = get_default_account()
    if default:
        return default

    # Check if there's only one account
    accounts = list_accounts()
    if len(accounts) == 1:
        return accounts[0]["name"]

    if len(accounts) == 0:
        raise ValueError(
            "No accounts configured.\n\n"
            "To add an account:\n"
            "  1. Run: cc-gmail accounts add <name>\n"
            "  2. Follow the setup instructions\n\n"
            f"See README for details: {get_readme_path()}"
        )

    raise ValueError(
        "Multiple accounts configured but no default set.\n\n"
        "Either:\n"
        "  - Specify an account: cc-gmail --account <name> <command>\n"
        "  - Set a default: cc-gmail accounts default <name>\n\n"
        f"Available accounts: {', '.join(a['name'] for a in accounts)}"
    )
