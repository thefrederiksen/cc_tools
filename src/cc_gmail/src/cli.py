"""CLI for cc_gmail - Gmail from the command line with multi-account support."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

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


app = typer.Typer(
    name="cc_gmail",
    help="Gmail CLI: read, send, search, and manage emails from the command line.",
    add_completion=False,
)
accounts_app = typer.Typer(help="Manage Gmail accounts")
app.add_typer(accounts_app, name="accounts")

console = Console()


def handle_api_error(error: Exception, account: str) -> None:
    """Parse API errors and provide helpful guidance."""
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
        console.print(f"  cc_gmail --account {account} auth --force")
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


def version_callback(value: bool):
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
    except Exception as e:
        handle_api_error(e, acct)
        raise typer.Exit(1)


@app.callback()
def main(
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


# =============================================================================
# Account Management Commands
# =============================================================================

@accounts_app.command("list")
def accounts_list():
    """List all configured Gmail accounts."""
    accts = list_accounts()

    if not accts:
        console.print("[yellow]No accounts configured.[/yellow]")
        console.print("\nTo add an account:")
        console.print("  cc_gmail accounts add <name>")
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
        console.print("Run 'cc_gmail auth' to re-authenticate.")
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
        console.print(f"   cc_gmail --account {name} auth")

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
            console.print("No accounts configured. Run 'cc_gmail accounts add <name>' first.")
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
            console.print("Run 'cc_gmail auth' to re-authenticate.")
        else:
            console.print("[yellow]No token to revoke.[/yellow]")
        return

    if not credentials_exist(acct):
        console.print(f"[red]Error:[/red] OAuth credentials not found for account '{acct}'")
        console.print(f"\nExpected location: {get_credentials_path(acct)}")
        console.print(f"\nRun 'cc_gmail accounts add {acct}' for setup instructions.")
        console.print(f"Or see README: {get_readme_path()}")
        raise typer.Exit(1)

    try:
        console.print(f"[blue]Authenticating account '{acct}'...[/blue]")
        console.print("A browser window will open for authentication.")
        creds = authenticate(acct, force=force)

        client = GmailClient(creds)
        profile = client.get_profile()

        console.print(f"\n[green]Authenticated as:[/green] {profile.get('emailAddress')}")
    except Exception as e:
        handle_api_error(e, acct)
        raise typer.Exit(1)


# =============================================================================
# Email Commands
# =============================================================================

@app.command("list")
def list_emails(
    label: str = typer.Option("INBOX", "-l", "--label", help="Label/folder to list"),
    count: int = typer.Option(10, "-n", "--count", help="Number of emails to show"),
    unread: bool = typer.Option(False, "-u", "--unread", help="Show only unread"),
):
    """List recent emails from a label/folder."""
    client = get_client()

    label_ids = [label.upper()]
    if unread:
        label_ids.append("UNREAD")

    try:
        messages = client.list_messages(label_ids=label_ids, max_results=count)

        if not messages:
            console.print(f"[yellow]No messages in {label}[/yellow]")
            return

        # Show which account
        acct = resolve_account(state.account)
        table = Table(title=f"Messages in {label} ({acct})")
        table.add_column("ID", style="dim", width=16)
        table.add_column("From", width=30)
        table.add_column("Subject", width=40)
        table.add_column("Date", width=20)

        for msg_summary in messages:
            msg = client.get_message_details(msg_summary["id"])
            summary = format_message_summary(msg)

            # Highlight unread
            style = "bold" if "UNREAD" in msg.get("labels", []) else ""

            table.add_row(
                summary["id"][:16],
                truncate(summary["from"], 30),
                truncate(summary["subject"], 40),
                summary["date"][:20] if summary["date"] else "",
                style=style,
            )

        console.print(table)

    except Exception as e:
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

    except Exception as e:
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

    except Exception as e:
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

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def search(
    query: str = typer.Argument(..., help="Gmail search query"),
    count: int = typer.Option(10, "-n", "--count", help="Number of results"),
):
    """Search emails using Gmail query syntax."""
    client = get_client()

    try:
        messages = client.search(query=query, max_results=count)

        if not messages:
            console.print(f"[yellow]No messages matching:[/yellow] {query}")
            return

        acct = resolve_account(state.account)
        table = Table(title=f"Search: {query} ({acct})")
        table.add_column("ID", style="dim", width=16)
        table.add_column("From", width=30)
        table.add_column("Subject", width=40)
        table.add_column("Date", width=20)

        for msg_summary in messages:
            msg = client.get_message_details(msg_summary["id"])
            summary = format_message_summary(msg)

            table.add_row(
                summary["id"][:16],
                truncate(summary["from"], 30),
                truncate(summary["subject"], 40),
                summary["date"][:20] if summary["date"] else "",
            )

        console.print(table)
        console.print(f"\n[dim]Found {len(messages)} message(s)[/dim]")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def labels():
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

    except Exception as e:
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

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def profile():
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

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
