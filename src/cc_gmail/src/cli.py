"""CLI for cc_gmail - Gmail from the command line with multi-account support."""

import logging
import sys
from pathlib import Path
from typing import Optional, List

# Suppress Google's file_cache warning before importing googleapiclient
logging.getLogger("googleapiclient.discovery_cache").setLevel(logging.ERROR)

import typer
from googleapiclient.errors import HttpError
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

logger = logging.getLogger(__name__)

try:
    from . import __version__
    from .auth import (
        authenticate,
        get_auth_status,
        revoke_token,
        credentials_exist,
        get_credentials_path,
        get_readme_path,
        list_accounts,
        set_default_account,
        get_default_account,
        delete_account,
        resolve_account,
        get_account_dir,
    )
    from .gmail_api import GmailClient
    from .utils import format_timestamp, truncate, format_message_summary
except ImportError:
    from src import __version__
    from src.auth import (
        authenticate,
        get_auth_status,
        revoke_token,
        credentials_exist,
        get_credentials_path,
        get_readme_path,
        list_accounts,
        set_default_account,
        get_default_account,
        delete_account,
        resolve_account,
        get_account_dir,
    )
    from src.gmail_api import GmailClient
    from src.utils import format_timestamp, truncate, format_message_summary

# Configure logging for library modules
logging.basicConfig(level=logging.INFO, format="%(message)s")

app = typer.Typer(
    name="cc_gmail",
    help="Gmail CLI: read, send, search, and manage emails from the command line.",
    add_completion=False,
)
accounts_app = typer.Typer(help="Manage Gmail accounts")
app.add_typer(accounts_app, name="accounts")

# Configure console to handle Unicode safely on Windows
# This prevents UnicodeEncodeError when emails contain emoji
if sys.platform == "win32":
    # Use UTF-8 encoding for Windows console output
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

console = Console()


def handle_api_error(error: Exception, account: str) -> None:
    """
    Parse Gmail API errors and provide user-friendly guidance.

    Handles common OAuth and API errors with specific instructions:
    - Gmail API not enabled
    - OAuth redirect mismatch (wrong client type)
    - App not verified / test user not added
    - Token expired or revoked
    - Invalid credentials file

    Args:
        error: The exception that was raised
        account: Account name for context in error messages
    """
    error_str = str(error)

    # Gmail API not enabled
    if "Gmail API has not been used in project" in error_str or "accessNotConfigured" in error_str:
        console.print("[red]Error:[/red] Gmail API is not enabled for your Google Cloud project.")
        console.print("\n[yellow]To fix this:[/yellow]")
        console.print("1. Go to: https://console.cloud.google.com/apis/library/gmail.googleapis.com")
        console.print("2. Make sure your project is selected at the top")
        console.print("3. Click 'Enable'")
        console.print("4. Wait a minute, then try again")
        return

    # OAuth redirect mismatch
    if "redirect_uri_mismatch" in error_str:
        console.print("[red]Error:[/red] OAuth client type is incorrect.")
        console.print("\n[yellow]To fix this:[/yellow]")
        console.print("1. Go to: https://console.cloud.google.com/apis/credentials")
        console.print("2. Delete your existing OAuth client")
        console.print("3. Create a new one with type 'Desktop app' (not 'Web application')")
        console.print("4. Download the new credentials.json")
        console.print(f"5. Replace: {get_credentials_path(account)}")
        return

    # App not verified / test user not added
    if "access_denied" in error_str or "has not completed the Google verification" in error_str:
        console.print("[red]Error:[/red] Your Google account is not authorized to use this app.")
        console.print("\n[yellow]To fix this:[/yellow]")
        console.print("1. Go to: https://console.cloud.google.com/apis/credentials/consent")
        console.print("2. Under 'Test users', click 'Add Users'")
        console.print("3. Add your Gmail address")
        console.print("4. Try again")
        return

    # Token expired or revoked
    if "invalid_grant" in error_str or "Token has been expired or revoked" in error_str:
        console.print("[red]Error:[/red] Your authentication token has expired or been revoked.")
        console.print("\n[yellow]To fix this:[/yellow]")
        console.print(f"  cc-gmail --account {account} auth --force")
        return

    # Invalid credentials file
    if "invalid_client" in error_str:
        console.print("[red]Error:[/red] The credentials.json file is invalid or corrupted.")
        console.print("\n[yellow]To fix this:[/yellow]")
        console.print("1. Go to: https://console.cloud.google.com/apis/credentials")
        console.print("2. Download your OAuth client credentials again")
        console.print(f"3. Replace: {get_credentials_path(account)}")
        return

    # Generic error - show the error and point to README
    console.print(f"[red]Error:[/red] {error}")
    console.print(f"\nSee README for troubleshooting: {get_readme_path()}")

# Global state for account selection
class State:
    account: Optional[str] = None

state = State()


def version_callback(value: bool) -> None:
    """Print version and exit if --version flag is set."""
    if value:
        console.print(f"cc_gmail version {__version__}")
        raise typer.Exit()


def get_client(account: Optional[str] = None) -> GmailClient:
    """Get authenticated Gmail client for the specified or default account."""
    try:
        acct = resolve_account(account or state.account)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    if not credentials_exist(acct):
        console.print(f"[red]Error:[/red] OAuth credentials not found for account '{acct}'")
        console.print(f"\nExpected location: {get_credentials_path(acct)}")
        console.print("\n[yellow]To fix this:[/yellow]")
        console.print("1. Download credentials from Google Cloud Console")
        console.print("2. Save as: credentials.json in the path above")
        console.print(f"\nSee README for detailed steps: {get_readme_path()}")
        raise typer.Exit(1)

    try:
        creds = authenticate(acct)
        return GmailClient(creds)
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except HttpError as e:
        handle_api_error(e, acct)
        raise typer.Exit(1)
    except (ValueError, OSError) as e:
        logger.error(f"Authentication error for {acct}: {e}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
    account: Optional[str] = typer.Option(
        None,
        "--account",
        "-a",
        help="Gmail account to use (default: uses default account)",
    ),
):
    """Gmail CLI: read, send, search, and manage emails."""
    state.account = account
    # Show help if no command provided
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())


# =============================================================================
# Account Management Commands
# =============================================================================

@accounts_app.command("list")
def accounts_list() -> None:
    """List all configured Gmail accounts."""
    accts = list_accounts()

    if not accts:
        console.print("[yellow]No accounts configured.[/yellow]")
        console.print("\nTo add an account:")
        console.print("  cc-gmail accounts add <name>")
        console.print(f"\nSee README for setup: {get_readme_path()}")
        return

    table = Table(title="Gmail Accounts")
    table.add_column("Account", style="cyan")
    table.add_column("Default")
    table.add_column("Credentials")
    table.add_column("Authenticated")

    for acct in accts:
        table.add_row(
            acct["name"],
            "[green]*[/green]" if acct["is_default"] else "",
            "[green]OK[/green]" if acct["credentials_exists"] else "[red]Missing[/red]",
            "[green]Yes[/green]" if acct["authenticated"] else "[yellow]No[/yellow]",
        )

    console.print(table)


@accounts_app.command("add")
def accounts_add(
    name: str = typer.Argument(..., help="Account name (e.g., 'personal', 'work')"),
    set_as_default: bool = typer.Option(False, "--default", "-d", help="Set as default account"),
):
    """Add a new Gmail account."""
    creds_path = get_credentials_path(name)
    account_dir = get_account_dir(name)

    console.print(f"[cyan]Setting up account:[/cyan] {name}")
    console.print(f"[cyan]Account directory:[/cyan] {account_dir}")
    console.print()

    if creds_path.exists():
        console.print(f"[yellow]Credentials already exist for '{name}'[/yellow]")
        console.print("Run 'cc-gmail auth' to re-authenticate.")
    else:
        console.print("[yellow]OAuth credentials needed.[/yellow]")
        console.print()
        console.print("To complete setup:")
        console.print()
        console.print("1. Go to Google Cloud Console:")
        console.print("   https://console.cloud.google.com/")
        console.print()
        console.print("2. Create or select a project")
        console.print()
        console.print("3. Enable the Gmail API:")
        console.print("   - Go to 'APIs & Services' -> 'Library'")
        console.print("   - Search for 'Gmail API'")
        console.print("   - Click 'Enable'")
        console.print()
        console.print("4. Create OAuth credentials:")
        console.print("   - Go to 'APIs & Services' -> 'Credentials'")
        console.print("   - Click 'Create Credentials' -> 'OAuth client ID'")
        console.print("   - Select 'Desktop app' as application type")
        console.print("   - Download the JSON file")
        console.print()
        console.print("5. Save the downloaded file as:")
        console.print(f"   [green]{creds_path}[/green]")
        console.print()
        console.print("6. Run authentication:")
        console.print(f"   cc-gmail --account {name} auth")

    if set_as_default or not get_default_account():
        set_default_account(name)
        console.print(f"\n[green]'{name}' set as default account.[/green]")


@accounts_app.command("default")
def accounts_default(
    name: str = typer.Argument(..., help="Account name to set as default"),
):
    """Set the default Gmail account."""
    accts = list_accounts()
    account_names = [a["name"] for a in accts]

    if name not in account_names:
        console.print(f"[red]Error:[/red] Account '{name}' not found.")
        if account_names:
            console.print(f"Available accounts: {', '.join(account_names)}")
        else:
            console.print("No accounts configured. Run 'cc-gmail accounts add <name>' first.")
        raise typer.Exit(1)

    set_default_account(name)
    console.print(f"[green]Default account set to '{name}'[/green]")


@accounts_app.command("remove")
def accounts_remove(
    name: str = typer.Argument(..., help="Account name to remove"),
    yes: bool = typer.Option(False, "-y", "--yes", help="Skip confirmation"),
):
    """Remove a Gmail account."""
    accts = list_accounts()
    account_names = [a["name"] for a in accts]

    if name not in account_names:
        console.print(f"[red]Error:[/red] Account '{name}' not found.")
        raise typer.Exit(1)

    if not yes:
        confirm = typer.confirm(f"Remove account '{name}' and all its data?")
        if not confirm:
            console.print("[yellow]Cancelled.[/yellow]")
            return

    if delete_account(name):
        console.print(f"[green]Account '{name}' removed.[/green]")
    else:
        console.print(f"[red]Failed to remove account '{name}'[/red]")


@accounts_app.command("status")
def accounts_status(
    name: Optional[str] = typer.Argument(None, help="Account name (default: current account)"),
):
    """Show detailed status for an account."""
    try:
        acct = resolve_account(name or state.account)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    info = get_auth_status(acct)

    table = Table(title=f"Account Status: {acct}")
    table.add_column("Property", style="cyan")
    table.add_column("Value")

    table.add_row("Account Directory", info["account_dir"])
    table.add_row(
        "Credentials File",
        "[green]Found[/green]" if info["credentials_exists"] else "[red]Missing[/red]",
    )
    table.add_row(
        "Token File",
        "[green]Found[/green]" if info["token_exists"] else "[yellow]Not created[/yellow]",
    )
    table.add_row(
        "Authenticated",
        "[green]Yes[/green]" if info["authenticated"] else "[red]No[/red]",
    )
    table.add_row(
        "Default Account",
        "[green]Yes[/green]" if info["is_default"] else "No",
    )

    console.print(table)

    if not info["credentials_exists"]:
        console.print(f"\n[yellow]Setup needed.[/yellow] See: {get_readme_path()}")


# =============================================================================
# Authentication Commands
# =============================================================================

@app.command()
def auth(
    force: bool = typer.Option(False, "--force", "-f", help="Force re-authentication"),
    revoke: bool = typer.Option(False, "--revoke", help="Revoke current token"),
):
    """Authenticate with Gmail."""
    try:
        acct = resolve_account(state.account)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    if revoke:
        if revoke_token(acct):
            console.print(f"[green]Token revoked for '{acct}'.[/green]")
            console.print("Run 'cc-gmail auth' to re-authenticate.")
        else:
            console.print("[yellow]No token to revoke.[/yellow]")
        return

    if not credentials_exist(acct):
        console.print(f"[red]Error:[/red] OAuth credentials not found for account '{acct}'")
        console.print(f"\nExpected location: {get_credentials_path(acct)}")
        console.print(f"\nRun 'cc-gmail accounts add {acct}' for setup instructions.")
        console.print(f"Or see README: {get_readme_path()}")
        raise typer.Exit(1)

    try:
        console.print(f"[blue]Authenticating account '{acct}'...[/blue]")
        console.print("A browser window will open for authentication.")
        creds = authenticate(acct, force=force)

        client = GmailClient(creds)
        profile = client.get_profile()

        console.print(f"\n[green]Authenticated as:[/green] {profile.get('emailAddress')}")
    except HttpError as e:
        handle_api_error(e, acct)
        raise typer.Exit(1)
    except (ValueError, OSError) as e:
        logger.error(f"Auth error: {e}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


# =============================================================================
# Email Commands
# =============================================================================

@app.command("list")
def list_emails(
    label: str = typer.Option("INBOX", "-l", "--label", help="Label/folder to list"),
    count: int = typer.Option(10, "-n", "--count", help="Number of emails to show"),
    unread: bool = typer.Option(False, "-u", "--unread", help="Show only unread"),
    include_spam: bool = typer.Option(False, "--include-spam", help="Include messages from spam and trash"),
):
    """List recent emails from a label/folder."""
    client = get_client()

    label_ids = [label.upper()]
    if unread:
        label_ids.append("UNREAD")

    try:
        messages = client.list_messages(
            label_ids=label_ids,
            max_results=count,
            include_spam_trash=include_spam,
        )

        if not messages:
            console.print(f"[yellow]No messages in {label}[/yellow]")
            return

        # Show which account
        acct = resolve_account(state.account)
        console.print(f"\n[cyan]Messages in {label} ({acct})[/cyan]\n")

        for msg_summary in messages:
            msg = client.get_message_details(msg_summary["id"])
            summary = format_message_summary(msg)

            # Highlight unread
            is_unread = "UNREAD" in msg.get("labels", [])
            style = "bold" if is_unread else ""
            marker = "[*]" if is_unread else "[ ]"

            console.print(f"{marker} [dim]{summary['id']}[/dim]", style=style)
            console.print(f"    From: {truncate(summary['from'], 50)}", style=style)
            console.print(f"    Subject: {truncate(summary['subject'], 60)}", style=style)
            console.print(f"    Date: {summary['date'][:25] if summary['date'] else ''}", style=style)
            console.print()

    except HttpError as e:
        logger.error(f"Gmail API error: {e}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except ValueError as e:
        logger.error(f"Invalid parameter: {e}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def read(
    message_id: str = typer.Argument(..., help="Message ID to read"),
    raw: bool = typer.Option(False, "--raw", help="Show raw message data"),
):
    """Read a specific email."""
    client = get_client()

    try:
        msg = client.get_message_details(message_id)
        summary = format_message_summary(msg)

        # Header panel
        header_text = Text()
        header_text.append(f"From: ", style="cyan")
        header_text.append(f"{summary['from']}\n")
        header_text.append(f"To: ", style="cyan")
        header_text.append(f"{summary['to']}\n")
        header_text.append(f"Date: ", style="cyan")
        header_text.append(f"{summary['date']}\n")
        header_text.append(f"Subject: ", style="cyan bold")
        header_text.append(f"{summary['subject']}")

        console.print(Panel(header_text, title=f"Message {message_id[:16]}"))

        # Body
        body = msg.get("body", "(No body)")
        if raw:
            console.print(body)
        else:
            console.print("\n" + body)

        # Mark as read
        client.mark_as_read(message_id)

    except HttpError as e:
        logger.error(f"Gmail API error reading message: {e}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except ValueError as e:
        logger.error(f"Invalid message: {e}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def send(
    to: str = typer.Option(..., "-t", "--to", help="Recipient email"),
    subject: str = typer.Option(..., "-s", "--subject", help="Email subject"),
    body: str = typer.Option(None, "-b", "--body", help="Email body"),
    body_file: Path = typer.Option(None, "-f", "--file", help="Read body from file"),
    cc: str = typer.Option(None, "--cc", help="CC recipients"),
    bcc: str = typer.Option(None, "--bcc", help="BCC recipients"),
    html: bool = typer.Option(False, "--html", help="Body is HTML"),
    attach: Optional[list[Path]] = typer.Option(None, "--attach", help="Attachments"),
):
    """Send an email."""
    client = get_client()

    # Get body content
    if body_file:
        if not body_file.exists():
            console.print(f"[red]Error:[/red] File not found: {body_file}")
            raise typer.Exit(1)
        body = body_file.read_text()
    elif not body:
        console.print("[red]Error:[/red] Provide --body or --file")
        raise typer.Exit(1)

    try:
        result = client.send_message(
            to=to,
            subject=subject,
            body=body,
            cc=cc,
            bcc=bcc,
            html=html,
            attachments=attach,
        )
        console.print(f"[green]Message sent.[/green] ID: {result.get('id')}")

    except HttpError as e:
        logger.error(f"Gmail API error sending: {e}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except (ValueError, FileNotFoundError) as e:
        logger.error(f"Send error: {e}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def draft(
    to: str = typer.Option(..., "-t", "--to", help="Recipient email"),
    subject: str = typer.Option(..., "-s", "--subject", help="Email subject"),
    body: str = typer.Option(None, "-b", "--body", help="Email body"),
    body_file: Path = typer.Option(None, "-f", "--file", help="Read body from file"),
    cc: str = typer.Option(None, "--cc", help="CC recipients"),
    html: bool = typer.Option(False, "--html", help="Body is HTML"),
):
    """Create a draft email."""
    client = get_client()

    # Get body content
    if body_file:
        if not body_file.exists():
            console.print(f"[red]Error:[/red] File not found: {body_file}")
            raise typer.Exit(1)
        body = body_file.read_text()
    elif not body:
        console.print("[red]Error:[/red] Provide --body or --file")
        raise typer.Exit(1)

    try:
        result = client.create_draft(
            to=to,
            subject=subject,
            body=body,
            cc=cc,
            html=html,
        )
        console.print(f"[green]Draft created.[/green] ID: {result.get('id')}")

    except HttpError as e:
        logger.error(f"Gmail API error creating draft: {e}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except ValueError as e:
        logger.error(f"Draft error: {e}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def reply(
    message_id: str = typer.Argument(..., help="Message ID to reply to"),
    body: str = typer.Option(None, "-b", "--body", help="Reply body"),
    body_file: Path = typer.Option(None, "-f", "--file", help="Read body from file"),
    reply_all: bool = typer.Option(False, "--all", help="Reply to all recipients"),
):
    """Create a draft reply to an existing email."""
    client = get_client()

    # Get body content
    if body_file:
        if not body_file.exists():
            console.print(f"[red]Error:[/red] File not found: {body_file}")
            raise typer.Exit(1)
        body = body_file.read_text()
    elif not body:
        console.print("[red]Error:[/red] Provide --body or --file")
        raise typer.Exit(1)

    try:
        # Get original message info for display
        original = client.get_message_details(message_id)
        original_from = original.get("headers", {}).get("from", "unknown")
        original_subject = original.get("headers", {}).get("subject", "")

        result = client.create_reply_draft(
            message_id=message_id,
            body=body,
            reply_all=reply_all,
        )
        console.print(f"[green]Reply draft created.[/green]")
        console.print(f"  To: {original_from}")
        console.print(f"  Subject: Re: {original_subject}" if not original_subject.lower().startswith("re:") else f"  Subject: {original_subject}")
        console.print(f"  Draft ID: {result.get('id')}")

    except HttpError as e:
        logger.error(f"Gmail API error creating reply: {e}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except ValueError as e:
        logger.error(f"Reply error: {e}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def drafts(
    count: int = typer.Option(10, "-n", "--count", help="Number of drafts to show"),
):
    """List draft emails."""
    client = get_client()

    try:
        draft_list = client.list_drafts(max_results=count)

        if not draft_list:
            console.print("[yellow]No drafts found.[/yellow]")
            return

        acct = resolve_account(state.account)
        console.print(f"\n[cyan]Drafts ({acct})[/cyan]\n")

        for draft in draft_list:
            draft_id = draft.get("id")
            msg_id = draft.get("message", {}).get("id")
            if msg_id:
                msg = client.get_message_details(msg_id)
                summary = format_message_summary(msg)
                console.print(f"[dim]{draft_id}[/dim]")
                console.print(f"    To: {truncate(summary.get('to', 'N/A'), 50)}")
                console.print(f"    Subject: {truncate(summary['subject'], 60)}")
                console.print()

    except HttpError as e:
        logger.error(f"Gmail API error listing drafts: {e}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except ValueError as e:
        logger.error(f"Drafts error: {e}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def search(
    query: str = typer.Argument(..., help="Gmail search query"),
    count: int = typer.Option(10, "-n", "--count", help="Number of results"),
    include_spam: bool = typer.Option(False, "--include-spam", help="Include messages from spam and trash"),
):
    """Search emails using Gmail query syntax."""
    client = get_client()

    try:
        messages = client.search(
            query=query,
            max_results=count,
            include_spam_trash=include_spam,
        )

        if not messages:
            console.print(f"[yellow]No messages matching:[/yellow] {query}")
            return

        acct = resolve_account(state.account)
        console.print(f"\n[cyan]Search: {query} ({acct})[/cyan]\n")

        for msg_summary in messages:
            msg = client.get_message_details(msg_summary["id"])
            summary = format_message_summary(msg)

            console.print(f"[ ] [dim]{summary['id']}[/dim]")
            console.print(f"    From: {truncate(summary['from'], 50)}")
            console.print(f"    Subject: {truncate(summary['subject'], 60)}")
            console.print(f"    Date: {summary['date'][:25] if summary['date'] else ''}")
            console.print()

        console.print(f"[dim]Found {len(messages)} message(s)[/dim]")

    except HttpError as e:
        logger.error(f"Gmail API error searching: {e}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except ValueError as e:
        logger.error(f"Search error: {e}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def count(
    query: str = typer.Argument(None, help="Gmail search query (optional)"),
    label: str = typer.Option(None, "-l", "--label", help="Label to count (e.g., INBOX)"),
):
    """Count emails matching a query (fast server-side estimate)."""
    client = get_client()

    try:
        label_ids = [label.upper()] if label else None
        result = client.count_messages(label_ids=label_ids, query=query)
        console.print(f"{result}")

    except HttpError as e:
        logger.error(f"Gmail API error counting: {e}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except ValueError as e:
        logger.error(f"Count error: {e}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def labels() -> None:
    """List all labels/folders."""
    client = get_client()

    try:
        all_labels = client.list_labels()

        # Separate system and user labels
        system_labels = []
        user_labels = []

        for label in all_labels:
            if label.get("type") == "system":
                system_labels.append(label)
            else:
                user_labels.append(label)

        # System labels table
        if system_labels:
            table = Table(title="System Labels")
            table.add_column("ID", style="cyan")
            table.add_column("Name")

            for label in sorted(system_labels, key=lambda x: x.get("name", "")):
                table.add_row(label.get("id"), label.get("name"))

            console.print(table)

        # User labels table
        if user_labels:
            table = Table(title="User Labels")
            table.add_column("ID", style="cyan")
            table.add_column("Name")

            for label in sorted(user_labels, key=lambda x: x.get("name", "")):
                table.add_row(label.get("id"), label.get("name"))

            console.print(table)

    except HttpError as e:
        logger.error(f"Gmail API error listing labels: {e}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except ValueError as e:
        logger.error(f"Labels error: {e}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def delete(
    message_id: str = typer.Argument(..., help="Message ID to delete"),
    permanent: bool = typer.Option(False, "--permanent", help="Permanently delete (no trash)"),
    yes: bool = typer.Option(False, "-y", "--yes", help="Skip confirmation"),
):
    """Delete/trash an email."""
    client = get_client()

    if not yes:
        action = "permanently delete" if permanent else "move to trash"
        confirm = typer.confirm(f"Are you sure you want to {action} message {message_id[:16]}?")
        if not confirm:
            console.print("[yellow]Cancelled.[/yellow]")
            return

    try:
        client.delete_message(message_id, permanent=permanent)

        if permanent:
            console.print(f"[green]Message permanently deleted.[/green]")
        else:
            console.print(f"[green]Message moved to trash.[/green]")

    except HttpError as e:
        logger.error(f"Gmail API error deleting: {e}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except ValueError as e:
        logger.error(f"Delete error: {e}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def untrash(
    message_id: str = typer.Argument(..., help="Message ID to restore"),
):
    """Restore an email from trash."""
    client = get_client()

    try:
        client.untrash_message(message_id)
        console.print("[green]Message restored from trash.[/green]")

    except HttpError as e:
        logger.error(f"Gmail API error untrashing: {e}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except ValueError as e:
        logger.error(f"Untrash error: {e}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def archive(
    message_ids: List[str] = typer.Argument(..., help="Message ID(s) to archive"),
):
    """Archive email(s) (remove from inbox, keep in All Mail). Accepts multiple IDs."""
    client = get_client()

    try:
        if len(message_ids) == 1:
            client.archive_message(message_ids[0])
            console.print("[green]Message archived.[/green]")
        else:
            client.batch_archive_messages(message_ids)
            console.print(f"[green]{len(message_ids)} messages archived.[/green]")

    except HttpError as e:
        logger.error(f"Gmail API error archiving: {e}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except ValueError as e:
        logger.error(f"Archive error: {e}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


def _show_archive_sample(client: GmailClient, query: str) -> None:
    """Show sample messages that would be archived in dry-run mode."""
    console.print("\n[yellow]DRY RUN - No changes made.[/yellow]")
    sample = client.list_messages(query=query, max_results=5)
    if sample:
        console.print("\nSample messages that would be archived:")
        for msg_summary in sample:
            msg = client.get_message_details(msg_summary["id"])
            summary = format_message_summary(msg)
            date_str = summary['date'][:10] if summary['date'] else 'N/A'
            console.print(f"  - {date_str} | {truncate(summary['from'], 30)} | {truncate(summary['subject'], 40)}")


def _execute_archive(client: GmailClient, query: str) -> int:
    """Fetch and archive all messages matching query. Returns count archived."""
    console.print("\n[blue]Fetching message IDs...[/blue]")
    messages = client.list_all_messages(query=query)
    total = len(messages)
    console.print(f"[blue]Found {total:,} messages to archive.[/blue]")

    if total == 0:
        return 0

    console.print("[blue]Archiving...[/blue]")
    message_ids = [m["id"] for m in messages]
    return client.batch_archive_messages(message_ids)


@app.command("archive-before")
def archive_before(
    date: str = typer.Argument(..., help="Archive messages before this date (YYYY-MM-DD)"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Show what would be archived without doing it"),
    yes: bool = typer.Option(False, "-y", "--yes", help="Skip confirmation prompt"),
    category: Optional[str] = typer.Option(None, "-c", "--category", help="Filter by category (updates, promotions, social, forums)"),
):
    """Archive all inbox messages before a specified date."""
    client = get_client()

    # Build query (convert YYYY-MM-DD to YYYY/MM/DD for Gmail)
    date_formatted = date.replace("-", "/")
    query = f"in:inbox before:{date_formatted}"
    if category:
        query += f" category:{category.lower()}"

    try:
        acct = resolve_account(state.account)
        estimate = client.count_messages(query=query)
        console.print(f"\n[cyan]Account:[/cyan] {acct}")
        console.print(f"[cyan]Query:[/cyan] {query}")
        console.print(f"[cyan]Estimated matches:[/cyan] {estimate:,}")

        if estimate == 0:
            console.print("[yellow]No messages match this query.[/yellow]")
            return

        if dry_run:
            _show_archive_sample(client, query)
            return

        if not yes:
            if not typer.confirm(f"\nArchive ~{estimate:,} messages before {date}?"):
                console.print("[yellow]Cancelled.[/yellow]")
                return

        archived = _execute_archive(client, query)
        if archived > 0:
            console.print(f"\n[green]Done! Archived {archived:,} messages.[/green]")
        else:
            console.print("[yellow]No messages to archive.[/yellow]")

    except HttpError as e:
        logger.error(f"Gmail API error in archive-before: {e}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except ValueError as e:
        logger.error(f"Archive-before error: {e}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def profile() -> None:
    """Show authenticated user profile."""
    client = get_client()

    try:
        info = client.get_profile()
        acct = resolve_account(state.account)

        table = Table(title=f"Gmail Profile ({acct})")
        table.add_column("Property", style="cyan")
        table.add_column("Value")

        table.add_row("Email", info.get("emailAddress", "Unknown"))
        table.add_row("Messages Total", str(info.get("messagesTotal", 0)))
        table.add_row("Threads Total", str(info.get("threadsTotal", 0)))
        table.add_row("History ID", info.get("historyId", "Unknown"))

        console.print(table)

    except HttpError as e:
        logger.error(f"Gmail API error getting profile: {e}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except ValueError as e:
        logger.error(f"Profile error: {e}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


def format_number(n: int) -> str:
    """Format number with thousands separator."""
    return f"{n:,}"


@app.command()
def stats(
    show_labels: bool = typer.Option(False, "-l", "--labels", help="Show user labels"),
    top: int = typer.Option(10, "-t", "--top", help="Number of top labels to show"),
):
    """Show comprehensive mailbox statistics dashboard."""
    client = get_client()

    try:
        acct = resolve_account(state.account)
        console.print(f"\n[bold cyan]Gmail Statistics Dashboard[/bold cyan] ({acct})")
        console.print("Loading stats from server...\n")

        stats_data = client.get_mailbox_stats()
        profile = stats_data["profile"]
        system = stats_data["system_labels"]
        categories = stats_data["categories"]
        user_labels = stats_data["user_labels"]

        # Profile summary
        console.print(f"[bold]Account:[/bold] {profile['email']}")
        console.print(f"[bold]Total Messages:[/bold] {format_number(profile['messages_total'])}")
        console.print(f"[bold]Total Threads:[/bold] {format_number(profile['threads_total'])}")
        console.print()

        # Inbox overview table
        inbox_table = Table(title="Inbox Overview")
        inbox_table.add_column("Folder", style="cyan")
        inbox_table.add_column("Total", justify="right")
        inbox_table.add_column("Unread", justify="right", style="yellow")

        inbox_order = ["INBOX", "UNREAD", "STARRED", "IMPORTANT", "SENT", "DRAFT", "SPAM", "TRASH"]
        for label_id in inbox_order:
            if label_id in system:
                data = system[label_id]
                inbox_table.add_row(
                    label_id.title(),
                    format_number(data["total"]),
                    format_number(data["unread"]) if data["unread"] > 0 else "-",
                )

        console.print(inbox_table)
        console.print()

        # Categories table
        if categories:
            cat_table = Table(title="Categories")
            cat_table.add_column("Category", style="cyan")
            cat_table.add_column("Total", justify="right")
            cat_table.add_column("Unread", justify="right", style="yellow")

            cat_order = ["Personal", "Updates", "Promotions", "Social", "Forums"]
            for cat_name in cat_order:
                if cat_name in categories:
                    data = categories[cat_name]
                    cat_table.add_row(
                        cat_name,
                        format_number(data["total"]),
                        format_number(data["unread"]) if data["unread"] > 0 else "-",
                    )

            console.print(cat_table)
            console.print()

        # User labels (optional, sorted by unread)
        if show_labels and user_labels:
            label_table = Table(title=f"User Labels (Top {top} by unread)")
            label_table.add_column("Label", style="cyan")
            label_table.add_column("Total", justify="right")
            label_table.add_column("Unread", justify="right", style="yellow")

            for label in user_labels[:top]:
                # Sanitize label name for display (remove problematic unicode)
                name = label["name"]
                try:
                    name.encode('cp1252')
                except UnicodeEncodeError:
                    name = name.encode('ascii', 'replace').decode('ascii')

                label_table.add_row(
                    name[:30],  # Truncate long names
                    format_number(label["total"]),
                    format_number(label["unread"]) if label["unread"] > 0 else "-",
                )

            console.print(label_table)
            console.print()

        # Quick summary
        inbox_unread = system.get("INBOX", {}).get("unread", 0)
        total_unread = system.get("UNREAD", {}).get("total", 0)

        console.print("[bold]Quick Summary:[/bold]")
        console.print(f"  Inbox unread: {format_number(inbox_unread)}")
        console.print(f"  Total unread: {format_number(total_unread)}")

        if categories:
            updates_unread = categories.get("Updates", {}).get("unread", 0)
            promos_unread = categories.get("Promotions", {}).get("unread", 0)
            social_unread = categories.get("Social", {}).get("unread", 0)
            console.print(f"  Updates: {format_number(updates_unread)} | Promotions: {format_number(promos_unread)} | Social: {format_number(social_unread)}")

        console.print()

    except HttpError as e:
        logger.error(f"Gmail API error getting stats: {e}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except ValueError as e:
        logger.error(f"Stats error: {e}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("label-stats")
def label_stats(
    label: str = typer.Argument(..., help="Label name or ID"),
):
    """Show detailed statistics for a specific label."""
    client = get_client()

    try:
        # Try as ID first, then by name
        try:
            data = client.get_label(label.upper())
        except HttpError:
            found = client.get_label_by_name(label)
            if not found:
                console.print(f"[red]Error:[/red] Label '{label}' not found")
                raise typer.Exit(1)
            data = client.get_label(found["id"])

        table = Table(title=f"Label: {data.get('name', label)}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right")

        table.add_row("Total Messages", format_number(data.get("messagesTotal", 0)))
        table.add_row("Unread Messages", format_number(data.get("messagesUnread", 0)))
        table.add_row("Total Threads", format_number(data.get("threadsTotal", 0)))
        table.add_row("Unread Threads", format_number(data.get("threadsUnread", 0)))
        table.add_row("Type", data.get("type", "user"))
        table.add_row("ID", data.get("id", ""))

        console.print(table)

    except typer.Exit:
        raise
    except HttpError as e:
        logger.error(f"Gmail API error getting label stats: {e}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except ValueError as e:
        logger.error(f"Label stats error: {e}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command("label-create")
def label_create(
    name: str = typer.Argument(..., help="Label name to create"),
):
    """Create a new label/folder."""
    client = get_client()

    try:
        # Check if exists first
        existing = client.get_label_by_name(name)
        if existing:
            console.print(f"[yellow]Label '{name}' already exists.[/yellow]")
            console.print(f"Label ID: {existing.get('id')}")
            return

        label = client.create_label(name)
        console.print(f"[green]Label created:[/green] {label.get('name')}")
        console.print(f"Label ID: {label.get('id')}")

    except HttpError as e:
        logger.error(f"Gmail API error creating label: {e}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except ValueError as e:
        logger.error(f"Label create error: {e}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def move(
    message_id: str = typer.Argument(..., help="Message ID to move"),
    label: str = typer.Option(..., "-l", "--label", help="Target label name"),
    keep_inbox: bool = typer.Option(False, "--keep-inbox", help="Keep in inbox (just add label)"),
):
    """Move an email to a label (removes from inbox by default)."""
    client = get_client()

    try:
        # Get or create the label
        target_label = client.get_or_create_label(label)
        label_id = target_label.get("id")

        # Modify labels
        add_labels = [label_id]
        remove_labels = [] if keep_inbox else ["INBOX"]

        client.modify_labels(message_id, add_labels=add_labels, remove_labels=remove_labels)

        if keep_inbox:
            console.print(f"[green]Label '{label}' added to message.[/green]")
        else:
            console.print(f"[green]Message moved to '{label}'.[/green]")

    except HttpError as e:
        logger.error(f"Gmail API error moving message: {e}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except ValueError as e:
        logger.error(f"Move error: {e}")
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
