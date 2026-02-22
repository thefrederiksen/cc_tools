"""CLI for cc_vault - Personal Vault from the command line."""

import json
import logging
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from types import ModuleType
from typing import Any, Optional, List

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

# Configure logger
logger = logging.getLogger(__name__)

# Handle imports for both package and frozen executable
try:
    from . import __version__
    from .config import (
        VAULT_PATH, DB_PATH, VECTORS_PATH, DOCUMENTS_PATH,
        get_vault_path, get_config
    )
except ImportError:
    # Running as frozen executable
    import __init__ as pkg
    __version__ = pkg.__version__
    from config import (
        VAULT_PATH, DB_PATH, VECTORS_PATH, DOCUMENTS_PATH,
        get_vault_path, get_config
    )

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")

app = typer.Typer(
    name="cc_vault",
    help="Personal Vault CLI: manage contacts, tasks, goals, ideas, documents, and more.",
    add_completion=False,
)

# Sub-apps
tasks_app = typer.Typer(help="Task management")
goals_app = typer.Typer(help="Goal tracking")
ideas_app = typer.Typer(help="Idea capture")
contacts_app = typer.Typer(help="Contact management")
docs_app = typer.Typer(help="Document management")
config_app = typer.Typer(help="Configuration")
health_app = typer.Typer(help="Health data")

app.add_typer(tasks_app, name="tasks")
app.add_typer(goals_app, name="goals")
app.add_typer(ideas_app, name="ideas")
app.add_typer(contacts_app, name="contacts")
app.add_typer(docs_app, name="docs")
app.add_typer(config_app, name="config")
app.add_typer(health_app, name="health")

console = Console()


def version_callback(value: bool) -> None:
    """Print version and exit if --version flag is set."""
    if value:
        console.print(f"cc_vault version {__version__}")
        raise typer.Exit()


def get_db() -> ModuleType:
    """Get initialized database module."""
    try:
        from . import db
    except ImportError:
        import db
    db.init_db(silent=True)
    return db


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
):
    """Personal Vault CLI: manage contacts, tasks, goals, ideas, and documents."""
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())


# =============================================================================
# Main Commands
# =============================================================================

@app.command()
def init(
    path: Optional[str] = typer.Argument(None, help="Vault path (default: ~/Vault)"),
    force: bool = typer.Option(False, "--force", "-f", help="Reinitialize if exists"),
):
    """Initialize a new vault."""
    try:
        from .config import ensure_directories
    except ImportError:
        from config import ensure_directories

    vault_path = Path(path) if path else VAULT_PATH

    if vault_path.exists() and not force:
        console.print(f"[yellow]Vault already exists at:[/yellow] {vault_path}")
        console.print("Use --force to reinitialize.")
        return

    try:
        ensure_directories()
        db = get_db()
        console.print(f"[green]Vault initialized at:[/green] {vault_path}")
        console.print(f"  Database: {DB_PATH}")
        console.print(f"  Documents: {DOCUMENTS_PATH}")
    except (OSError, sqlite3.Error) as e:
        console.print(f"[red]Error initializing vault:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def stats() -> None:
    """Show vault statistics."""
    db = get_db()

    try:
        stats_data = db.get_vault_stats()

        table = Table(title=f"Vault Statistics")
        table.add_column("Category", style="cyan")
        table.add_column("Count", justify="right")

        table.add_row("Contacts", str(stats_data.get('contacts', 0)))
        table.add_row("Tasks (pending)", str(stats_data.get('tasks_pending', 0)))
        table.add_row("Tasks (completed)", str(stats_data.get('tasks_completed', 0)))
        table.add_row("Goals (active)", str(stats_data.get('goals_active', 0)))
        table.add_row("Ideas", str(stats_data.get('ideas', 0)))
        table.add_row("Documents", str(stats_data.get('documents', 0)))
        table.add_row("Health Entries", str(stats_data.get('health_entries', 0)))

        console.print(table)
        console.print(f"\n[dim]Vault path: {VAULT_PATH}[/dim]")

    except sqlite3.Error as e:
        console.print(f"[red]Error getting stats:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def ask(
    question: str = typer.Argument(..., help="Question to ask the vault"),
    model: str = typer.Option("gpt-4o", "-m", "--model", help="OpenAI model to use"),
    no_hybrid: bool = typer.Option(False, "--no-hybrid", help="Disable hybrid search"),
) -> None:
    """Ask a question using RAG (Retrieval Augmented Generation)."""
    try:
        try:
            from .rag import get_vault_rag
        except ImportError:
            from rag import get_vault_rag
        rag = get_vault_rag()

        console.print(f"[dim]Searching vault...[/dim]")
        result = rag.ask(question, model=model, use_hybrid=not no_hybrid)

        if 'error' in result:
            console.print(f"[red]Error:[/red] {result['error']}")
            raise typer.Exit(1)

        console.print(f"\n[cyan]Answer:[/cyan]\n{result['answer']}")
        console.print(f"\n[dim]Sources: {result['context_used']} items, Mode: {result.get('search_mode', 'unknown')}[/dim]")

    except ImportError as e:
        console.print(f"[red]Error:[/red] RAG not available: {e}")
        console.print("Install with: pip install openai chromadb")
        raise typer.Exit(1)


@app.command("search")
def search_cmd(
    query: str = typer.Argument(..., help="Search query"),
    n: int = typer.Option(10, "-n", help="Number of results"),
    hybrid: bool = typer.Option(False, "--hybrid", help="Use hybrid search"),
):
    """Search the vault using semantic or hybrid search."""
    try:
        try:
            from .rag import get_vault_rag
        except ImportError:
            from rag import get_vault_rag
        rag = get_vault_rag()

        if hybrid:
            results = rag.hybrid_search(query, n_results=n)

            if not results:
                console.print("[yellow]No results found[/yellow]")
                return

            console.print(f"\n[cyan]Hybrid Search Results ({len(results)} chunks):[/cyan]\n")
            for r in results:
                meta = r.get('metadata', {})
                doc_title = meta.get('doc_title', 'Unknown')
                lines = f"lines {meta.get('start_line', '?')}-{meta.get('end_line', '?')}"
                content = r.get('content', '')[:150]
                combined = r.get('combined_score', 0)
                console.print(f"  [{doc_title}, {lines}] score={combined:.3f}")
                console.print(f"    {content}...")
                console.print()
        else:
            results = rag.semantic_search(query, n_results=n)

            for coll, items in results.items():
                if items:
                    console.print(f"\n[cyan]{coll.upper()} ({len(items)} results):[/cyan]")
                    for item in items[:5]:
                        doc = item.get('document', '')[:100]
                        console.print(f"  [{item['id']}] {doc}...")

    except ImportError as e:
        console.print(f"[red]Error:[/red] Vector search not available: {e}")
        raise typer.Exit(1)


@app.command()
def backup(
    output: Optional[Path] = typer.Option(None, "-o", "--output", help="Output directory"),
):
    """Create a backup of the vault database."""
    db = get_db()

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    if output:
        backup_dir = output
    else:
        backup_dir = VAULT_PATH / 'backups'

    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_file = backup_dir / f'vault_backup_{timestamp}.db'

    try:
        shutil.copy2(DB_PATH, backup_file)
        console.print(f"[green]Backup created:[/green] {backup_file}")
    except OSError as e:
        console.print(f"[red]Error creating backup:[/red] {e}")
        raise typer.Exit(1)


# =============================================================================
# Tasks Commands
# =============================================================================

@tasks_app.command("list")
def tasks_list(
    status: str = typer.Option("pending", "-s", "--status", help="Filter by status: pending, completed, all"),
    contact_id: Optional[int] = typer.Option(None, "-c", "--contact", help="Filter by contact"),
    limit: int = typer.Option(20, "-n", help="Max results"),
):
    """List tasks."""
    db = get_db()

    try:
        if status == "all":
            tasks = db.list_tasks(status=None, contact_id=contact_id, limit=limit)
        else:
            tasks = db.list_tasks(status=status, contact_id=contact_id, limit=limit)

        if not tasks:
            console.print(f"[yellow]No {status} tasks found[/yellow]")
            return

        table = Table(title=f"Tasks ({status})")
        table.add_column("ID", style="dim")
        table.add_column("Task", style="cyan")
        table.add_column("Due", style="yellow")
        table.add_column("Priority")
        table.add_column("Contact")

        for task in tasks:
            # Convert numeric priority to label
            priority_num = task.get('priority', 3)
            if isinstance(priority_num, int):
                if priority_num <= 2:
                    priority_label = 'high'
                elif priority_num >= 4:
                    priority_label = 'low'
                else:
                    priority_label = 'medium'
            else:
                priority_label = str(priority_num)

            priority_style = {'high': '[red]', 'low': '[dim]'}.get(priority_label, '')
            priority_end = '[/red]' if priority_label == 'high' else '[/dim]' if priority_label == 'low' else ''

            table.add_row(
                str(task['id']),
                task['title'][:50],
                task.get('due_date', '-')[:10] if task.get('due_date') else '-',
                f"{priority_style}{priority_label}{priority_end}",
                task.get('contact_name', '-') or '-',
            )

        console.print(table)

    except sqlite3.Error as e:
        console.print(f"[red]Error listing tasks:[/red] {e}")
        raise typer.Exit(1)


@tasks_app.command("add")
def tasks_add(
    title: str = typer.Argument(..., help="Task title"),
    due: Optional[str] = typer.Option(None, "-d", "--due", help="Due date (YYYY-MM-DD)"),
    priority: str = typer.Option("medium", "-p", "--priority", help="Priority: low, medium, high (or 1-5)"),
    contact_id: Optional[int] = typer.Option(None, "-c", "--contact", help="Link to contact"),
    goal_id: Optional[int] = typer.Option(None, "-g", "--goal", help="Link to goal"),
    description: Optional[str] = typer.Option(None, "-n", "--notes", help="Task description"),
):
    """Add a new task."""
    db = get_db()

    # Convert priority string to int (1-5)
    priority_map = {'high': 1, 'medium': 3, 'low': 5}
    if priority.lower() in priority_map:
        priority_int = priority_map[priority.lower()]
    else:
        try:
            priority_int = int(priority)
        except ValueError:
            console.print(f"[red]Error:[/red] Invalid priority. Use low, medium, high, or 1-5")
            raise typer.Exit(1)

    try:
        task_id = db.add_task(
            title=title,
            due_date=due,
            priority=priority_int,
            description=description,
            contact_id=contact_id,
            goal_id=goal_id,
        )
        console.print(f"[green]Task added:[/green] #{task_id} - {title}")

    except sqlite3.Error as e:
        console.print(f"[red]Error adding task:[/red] {e}")
        raise typer.Exit(1)


@tasks_app.command("done")
def tasks_done(
    task_id: int = typer.Argument(..., help="Task ID to complete"),
):
    """Mark a task as completed."""
    db = get_db()

    try:
        db.complete_task(task_id)
        console.print(f"[green]Task #{task_id} marked as completed[/green]")

    except sqlite3.Error as e:
        console.print(f"[red]Error completing task:[/red] {e}")
        raise typer.Exit(1)


@tasks_app.command("cancel")
def tasks_cancel(
    task_id: int = typer.Argument(..., help="Task ID to cancel"),
):
    """Cancel a task."""
    db = get_db()

    try:
        db.update_task(task_id, status='cancelled')
        console.print(f"[yellow]Task #{task_id} cancelled[/yellow]")

    except sqlite3.Error as e:
        console.print(f"[red]Error cancelling task:[/red] {e}")
        raise typer.Exit(1)


# =============================================================================
# Goals Commands
# =============================================================================

@goals_app.command("list")
def goals_list(
    status: str = typer.Option("active", "-s", "--status", help="Filter: active, achieved, paused, all"),
    category: Optional[str] = typer.Option(None, "-c", "--category", help="Filter by category"),
    timeframe: Optional[str] = typer.Option(None, "-t", "--timeframe", help="Filter by timeframe"),
):
    """List goals."""
    db = get_db()

    try:
        if status == "all":
            goals = db.list_goals(status=None, category=category, timeframe=timeframe, include_achieved=True)
        else:
            goals = db.list_goals(status=status, category=category, timeframe=timeframe)

        if not goals:
            console.print(f"[yellow]No {status} goals found[/yellow]")
            return

        table = Table(title=f"Goals ({status})")
        table.add_column("ID", style="dim")
        table.add_column("Goal", style="cyan")
        table.add_column("Target", style="yellow")
        table.add_column("Progress")
        table.add_column("Status")

        for goal in goals:
            progress = goal.get('progress', 0) or 0
            progress_bar = f"[{'=' * int(progress / 10)}{' ' * (10 - int(progress / 10))}] {progress}%"

            table.add_row(
                str(goal['id']),
                goal['title'][:40],
                goal.get('target_date', '-')[:10] if goal.get('target_date') else '-',
                progress_bar,
                goal.get('status', 'active'),
            )

        console.print(table)

    except sqlite3.Error as e:
        console.print(f"[red]Error listing goals:[/red] {e}")
        raise typer.Exit(1)


@goals_app.command("add")
def goals_add(
    title: str = typer.Argument(..., help="Goal title"),
    target: Optional[str] = typer.Option(None, "-t", "--target", help="Target date (YYYY-MM-DD)"),
    description: Optional[str] = typer.Option(None, "-d", "--description", help="Goal description"),
    category: Optional[str] = typer.Option(None, "-c", "--category", help="Goal category"),
):
    """Add a new goal."""
    db = get_db()

    try:
        goal_id = db.add_goal(
            title=title,
            target_date=target,
            description=description,
            category=category,
        )
        console.print(f"[green]Goal added:[/green] #{goal_id} - {title}")

    except sqlite3.Error as e:
        console.print(f"[red]Error adding goal:[/red] {e}")
        raise typer.Exit(1)


@goals_app.command("achieve")
def goals_achieve(
    goal_id: int = typer.Argument(..., help="Goal ID to mark as achieved"),
):
    """Mark a goal as achieved."""
    db = get_db()

    try:
        db.achieve_goal(goal_id)
        console.print(f"[green]Goal #{goal_id} marked as achieved![/green]")

    except sqlite3.Error as e:
        console.print(f"[red]Error updating goal:[/red] {e}")
        raise typer.Exit(1)


@goals_app.command("pause")
def goals_pause(
    goal_id: int = typer.Argument(..., help="Goal ID to pause"),
):
    """Pause a goal."""
    db = get_db()

    try:
        db.pause_goal(goal_id)
        console.print(f"[yellow]Goal #{goal_id} paused[/yellow]")

    except sqlite3.Error as e:
        console.print(f"[red]Error pausing goal:[/red] {e}")
        raise typer.Exit(1)


@goals_app.command("resume")
def goals_resume(
    goal_id: int = typer.Argument(..., help="Goal ID to resume"),
):
    """Resume a paused goal."""
    db = get_db()

    try:
        db.resume_goal(goal_id)
        console.print(f"[green]Goal #{goal_id} resumed[/green]")

    except sqlite3.Error as e:
        console.print(f"[red]Error resuming goal:[/red] {e}")
        raise typer.Exit(1)


@goals_app.command("update")
def goals_update(
    goal_id: int = typer.Argument(..., help="Goal ID"),
    title: Optional[str] = typer.Option(None, "--title", help="New title"),
    description: Optional[str] = typer.Option(None, "-d", "--description", help="New description"),
    category: Optional[str] = typer.Option(None, "-c", "--category", help="New category"),
    target: Optional[str] = typer.Option(None, "-t", "--target", help="New target date (YYYY-MM-DD)"),
):
    """Update a goal's details."""
    db = get_db()

    try:
        db.update_goal(
            goal_id,
            title=title,
            description=description,
            category=category,
            target_date=target,
        )
        console.print(f"[green]Goal #{goal_id} updated[/green]")

    except sqlite3.Error as e:
        console.print(f"[red]Error updating goal:[/red] {e}")
        raise typer.Exit(1)


# =============================================================================
# Ideas Commands
# =============================================================================

@ideas_app.command("list")
def ideas_list(
    status: str = typer.Option("new", "-s", "--status", help="Filter: new, actionable, archived, all"),
    domain: Optional[str] = typer.Option(None, "-d", "--domain", help="Filter by domain"),
    limit: int = typer.Option(20, "-n", help="Max results"),
):
    """List ideas."""
    db = get_db()

    try:
        if status == "all":
            ideas = db.list_ideas(status=None, domain=domain, limit=limit)
        else:
            ideas = db.list_ideas(status=status, domain=domain, limit=limit)

        if not ideas:
            console.print(f"[yellow]No {status} ideas found[/yellow]")
            return

        table = Table(title=f"Ideas ({status})")
        table.add_column("ID", style="dim")
        table.add_column("Idea", style="cyan")
        table.add_column("Domain")
        table.add_column("Created")
        table.add_column("Status")

        for idea in ideas:
            table.add_row(
                str(idea['id']),
                idea['content'][:50],
                idea.get('domain', '-') or '-',
                idea.get('created_at', '')[:10],
                idea.get('status', 'new'),
            )

        console.print(table)

    except sqlite3.Error as e:
        console.print(f"[red]Error listing ideas:[/red] {e}")
        raise typer.Exit(1)


@ideas_app.command("add")
def ideas_add(
    content: str = typer.Argument(..., help="Idea content"),
    tags: Optional[str] = typer.Option(None, "-t", "--tags", help="Tags (comma-separated)"),
    domain: Optional[str] = typer.Option(None, "-d", "--domain", help="Domain/category"),
    goal_id: Optional[int] = typer.Option(None, "-g", "--goal", help="Link to goal"),
):
    """Add a new idea."""
    db = get_db()

    try:
        idea_id = db.add_idea(
            content=content,
            tags=tags,
            domain=domain,
            goal_id=goal_id,
        )
        console.print(f"[green]Idea added:[/green] #{idea_id}")

    except sqlite3.Error as e:
        console.print(f"[red]Error adding idea:[/red] {e}")
        raise typer.Exit(1)


@ideas_app.command("actionable")
def ideas_actionable(
    idea_id: int = typer.Argument(..., help="Idea ID"),
):
    """Mark an idea as actionable."""
    db = get_db()

    try:
        db.update_idea_status(idea_id, 'actionable')
        console.print(f"[green]Idea #{idea_id} marked as actionable[/green]")

    except sqlite3.Error as e:
        console.print(f"[red]Error updating idea:[/red] {e}")
        raise typer.Exit(1)


@ideas_app.command("archive")
def ideas_archive(
    idea_id: int = typer.Argument(..., help="Idea ID"),
):
    """Archive an idea."""
    db = get_db()

    try:
        db.update_idea_status(idea_id, 'archived')
        console.print(f"[yellow]Idea #{idea_id} archived[/yellow]")

    except sqlite3.Error as e:
        console.print(f"[red]Error archiving idea:[/red] {e}")
        raise typer.Exit(1)


# =============================================================================
# Contacts Commands
# =============================================================================

@contacts_app.command("list")
def contacts_list(
    account: Optional[str] = typer.Option(None, "-a", "--account", help="Filter by account: consulting, personal, both"),
    category: Optional[str] = typer.Option(None, "-c", "--category", help="Filter by category"),
    relationship: Optional[str] = typer.Option(None, "-r", "--relationship", help="Filter by relationship"),
):
    """List contacts."""
    db = get_db()

    try:
        contacts = db.list_contacts(account=account, category=category, relationship=relationship)

        if not contacts:
            console.print("[yellow]No contacts found[/yellow]")
            return

        table = Table(title="Contacts")
        table.add_column("ID", style="dim")
        table.add_column("Name", style="cyan")
        table.add_column("Email")
        table.add_column("Company")
        table.add_column("Last Contact")

        for c in contacts:
            table.add_row(
                str(c['id']),
                c['name'],
                c.get('email', '-') or '-',
                c.get('company', '-') or '-',
                c.get('last_contact', '-')[:10] if c.get('last_contact') else '-',
            )

        console.print(table)

    except sqlite3.Error as e:
        console.print(f"[red]Error listing contacts:[/red] {e}")
        raise typer.Exit(1)


@contacts_app.command("add")
def contacts_add(
    name: str = typer.Argument(..., help="Contact name"),
    email: str = typer.Option(..., "-e", "--email", help="Email address (required)"),
    account: str = typer.Option("personal", "-a", "--account", help="Account: consulting, personal, both"),
    phone: Optional[str] = typer.Option(None, "-p", "--phone", help="Phone number"),
    company: Optional[str] = typer.Option(None, "-c", "--company", help="Company"),
    role: Optional[str] = typer.Option(None, "-r", "--role", help="Role/title"),
):
    """Add a new contact."""
    db = get_db()

    try:
        contact_id = db.add_contact(
            email=email,
            name=name,
            account=account,
            phone=phone,
            company=company,
            role=role,
        )
        console.print(f"[green]Contact added:[/green] #{contact_id} - {name}")

    except sqlite3.Error as e:
        console.print(f"[red]Error adding contact:[/red] {e}")
        raise typer.Exit(1)


@contacts_app.command("show")
def contacts_show(
    contact_id: int = typer.Argument(..., help="Contact ID"),
):
    """Show contact details."""
    db = get_db()

    try:
        contact = db.get_contact_by_id(contact_id)

        if not contact:
            console.print(f"[red]Contact #{contact_id} not found[/red]")
            raise typer.Exit(1)

        # Header
        console.print(f"\n[bold cyan]{contact['name']}[/bold cyan]")
        console.print(f"[dim]Contact #{contact_id}[/dim]\n")

        # Details
        table = Table(show_header=False, box=None)
        table.add_column("Property", style="cyan", width=15)
        table.add_column("Value")

        if contact.get('email'):
            table.add_row("Email", contact['email'])
        if contact.get('phone'):
            table.add_row("Phone", contact['phone'])
        if contact.get('company'):
            table.add_row("Company", contact['company'])
        if contact.get('role'):
            table.add_row("Role", contact['role'])
        if contact.get('last_contact'):
            table.add_row("Last Contact", contact['last_contact'][:10])
        if contact.get('notes'):
            table.add_row("Notes", contact['notes'])

        console.print(table)

        # Recent interactions (if contact has email)
        if contact.get('email'):
            interactions = db.get_interactions(contact['email'], limit=5)
            if interactions:
                console.print("\n[cyan]Recent Interactions:[/cyan]")
                for i in interactions:
                    console.print(f"  [{i.get('interaction_date', '')[:10]}] {i.get('type', '')} - {i.get('summary', '')[:50]}")

    except sqlite3.Error as e:
        console.print(f"[red]Error showing contact:[/red] {e}")
        raise typer.Exit(1)


@contacts_app.command("memory")
def contacts_memory(
    contact_id: int = typer.Argument(..., help="Contact ID"),
    fact: str = typer.Argument(..., help="Memory/fact to remember"),
    category: str = typer.Option("general", "-c", "--category", help="Memory category"),
    detail: Optional[str] = typer.Option(None, "-d", "--detail", help="Additional detail"),
):
    """Add a memory/fact about a contact."""
    db = get_db()

    try:
        # Get contact to find email
        contact = db.get_contact_by_id(contact_id)
        if not contact:
            console.print(f"[red]Contact #{contact_id} not found[/red]")
            raise typer.Exit(1)

        if not contact.get('email'):
            console.print(f"[red]Contact #{contact_id} has no email address[/red]")
            raise typer.Exit(1)

        db.add_memory(
            email=contact['email'],
            category=category,
            fact=fact,
            detail=detail,
        )
        console.print(f"[green]Memory added for {contact['name']}[/green]")

    except sqlite3.Error as e:
        console.print(f"[red]Error adding memory:[/red] {e}")
        raise typer.Exit(1)


@contacts_app.command("update")
def contacts_update(
    contact_id: int = typer.Argument(..., help="Contact ID"),
    name: Optional[str] = typer.Option(None, "--name", help="Name"),
    phone: Optional[str] = typer.Option(None, "-p", "--phone", help="Phone number"),
    company: Optional[str] = typer.Option(None, "-c", "--company", help="Company"),
    title: Optional[str] = typer.Option(None, "-t", "--title", help="Title/role"),
    category: Optional[str] = typer.Option(None, "--category", help="Category"),
    relationship: Optional[str] = typer.Option(None, "-r", "--relationship", help="Relationship"),
):
    """Update a contact."""
    db = get_db()

    try:
        # Get contact to find email
        contact = db.get_contact_by_id(contact_id)
        if not contact:
            console.print(f"[red]Contact #{contact_id} not found[/red]")
            raise typer.Exit(1)

        if not contact.get('email'):
            console.print(f"[red]Contact #{contact_id} has no email address[/red]")
            raise typer.Exit(1)

        db.update_contact(
            contact['email'],
            name=name,
            phone=phone,
            company=company,
            title=title,
            category=category,
            relationship=relationship,
        )
        console.print(f"[green]Contact #{contact_id} updated[/green]")

    except sqlite3.Error as e:
        console.print(f"[red]Error updating contact:[/red] {e}")
        raise typer.Exit(1)


@contacts_app.command("search")
def contacts_search(
    name: str = typer.Argument(..., help="Name to search for"),
    threshold: int = typer.Option(50, "--threshold", "-t", help="Minimum match score (0-100)"),
    n: int = typer.Option(10, "-n", help="Max results"),
    exact: bool = typer.Option(False, "--exact", help="Use exact matching (LIKE) instead of fuzzy"),
):
    """Search contacts by name using fuzzy/phonetic matching."""
    db = get_db()

    try:
        if exact:
            # Use existing exact search
            results = db.search_contacts(name)
            if not results:
                console.print(f"[yellow]No contacts matching:[/yellow] {name}")
                return

            table = Table(title=f"Search Results for '{name}' (exact)")
            table.add_column("ID", style="dim")
            table.add_column("Name", style="cyan")
            table.add_column("Email")
            table.add_column("Company")
            table.add_column("Match", style="green")

            for c in results[:n]:
                table.add_row(
                    str(c['id']),
                    c['name'],
                    c.get('email', '-') or '-',
                    c.get('company', '-') or '-',
                    "exact",
                )

            console.print(table)
        else:
            # Use fuzzy search
            results = db.fuzzy_search_contacts(name, threshold=threshold, limit=n)

            if not results:
                console.print(f"[yellow]No contacts matching:[/yellow] {name} (threshold={threshold})")
                console.print("[dim]Try lowering the threshold with --threshold 30[/dim]")
                return

            table = Table(title=f"Search Results for '{name}'")
            table.add_column("ID", style="dim")
            table.add_column("Name", style="cyan")
            table.add_column("Email")
            table.add_column("Company")
            table.add_column("Score", justify="right")
            table.add_column("Match", style="green")

            for c in results:
                score = c.get('match_score', 0)
                match_type = c.get('match_type', 'fuzzy')

                # Color score based on confidence
                if score >= 80:
                    score_style = "[green]"
                    score_end = "[/green]"
                elif score >= 60:
                    score_style = "[yellow]"
                    score_end = "[/yellow]"
                else:
                    score_style = "[dim]"
                    score_end = "[/dim]"

                table.add_row(
                    str(c['id']),
                    c['name'],
                    c.get('email', '-') or '-',
                    c.get('company', '-') or '-',
                    f"{score_style}{score:.0f}{score_end}",
                    match_type,
                )

            console.print(table)

    except sqlite3.Error as e:
        console.print(f"[red]Error searching contacts:[/red] {e}")
        raise typer.Exit(1)


# =============================================================================
# Documents Commands
# =============================================================================

@docs_app.command("list")
def docs_list(
    doc_type: Optional[str] = typer.Option(None, "-t", "--type", help="Filter by type: note, journal, transcript, research"),
    limit: int = typer.Option(20, "-n", help="Max results"),
):
    """List documents."""
    db = get_db()

    try:
        docs = db.list_documents(doc_type=doc_type, limit=limit)

        if not docs:
            console.print("[yellow]No documents found[/yellow]")
            return

        table = Table(title="Documents")
        table.add_column("ID", style="dim")
        table.add_column("Title", style="cyan")
        table.add_column("Type")
        table.add_column("Date")
        table.add_column("Tags")

        for doc in docs:
            table.add_row(
                str(doc['id']),
                doc.get('title', '')[:40],
                doc.get('doc_type', '-'),
                doc.get('created_at', '')[:10],
                doc.get('tags', '-') or '-',
            )

        console.print(table)

    except sqlite3.Error as e:
        console.print(f"[red]Error listing documents:[/red] {e}")
        raise typer.Exit(1)


@docs_app.command("add")
def docs_add(
    path: Path = typer.Argument(..., help="File path to import"),
    doc_type: str = typer.Option("research", "-t", "--type", help="Document type"),
    title: Optional[str] = typer.Option(None, "--title", help="Document title"),
    tags: Optional[str] = typer.Option(None, "--tags", help="Comma-separated tags"),
):
    """Import a document into the vault."""
    try:
        try:
            from .importer import import_document
        except ImportError:
            from importer import import_document

        result = import_document(str(path), doc_type=doc_type, title=title, tags=tags)

        if result.get('success'):
            console.print(f"[green]Document imported:[/green] #{result['document_id']}")
            console.print(f"  Path: {result.get('path')}")
            if result.get('chunk_count'):
                console.print(f"  Chunks: {result['chunk_count']}")
        else:
            console.print(f"[red]Error:[/red] {result.get('error')}")
            raise typer.Exit(1)

    except (OSError, sqlite3.Error, ValueError) as e:
        console.print(f"[red]Error importing document:[/red] {e}")
        raise typer.Exit(1)


@docs_app.command("show")
def docs_show(
    doc_id: int = typer.Argument(..., help="Document ID"),
):
    """Show document details."""
    db = get_db()

    try:
        doc = db.get_document(doc_id)

        if not doc:
            console.print(f"[red]Document #{doc_id} not found[/red]")
            raise typer.Exit(1)

        # Header
        console.print(f"\n[bold cyan]{doc.get('title', 'Untitled')}[/bold cyan]")
        console.print(f"[dim]Document #{doc_id}[/dim]\n")

        # Details
        table = Table(show_header=False, box=None)
        table.add_column("Property", style="cyan", width=15)
        table.add_column("Value")

        table.add_row("Type", doc.get('doc_type', '-'))
        table.add_row("Path", doc.get('path', '-'))
        table.add_row("Created", doc.get('created_at', '-')[:19] if doc.get('created_at') else '-')
        if doc.get('tags'):
            table.add_row("Tags", doc['tags'])
        if doc.get('source'):
            table.add_row("Source", doc['source'])

        console.print(table)

        # Content preview
        if doc.get('path'):
            full_path = DOCUMENTS_PATH / doc['path']
            if full_path.exists():
                content = full_path.read_text(encoding='utf-8')[:500]
                console.print(f"\n[cyan]Preview:[/cyan]\n{content}...")

    except (OSError, sqlite3.Error) as e:
        console.print(f"[red]Error showing document:[/red] {e}")
        raise typer.Exit(1)


@docs_app.command("search")
def docs_search(
    query: str = typer.Argument(..., help="Search query"),
):
    """Search documents using full-text search."""
    db = get_db()

    try:
        results = db.search_documents(query)

        if not results:
            console.print(f"[yellow]No documents matching:[/yellow] {query}")
            return

        console.print(f"\n[cyan]Search Results ({len(results)}):[/cyan]\n")

        for doc in results:
            console.print(f"  #{doc['id']} [cyan]{doc.get('title', 'Untitled')}[/cyan]")
            console.print(f"    Type: {doc.get('doc_type', '-')} | Path: {doc.get('path', '-')[:50]}")
            console.print()

    except sqlite3.Error as e:
        console.print(f"[red]Error searching documents:[/red] {e}")
        raise typer.Exit(1)


# =============================================================================
# Config Commands
# =============================================================================

@config_app.command("show")
def config_show():
    """Show current configuration."""
    import os
    config = get_config()

    table = Table(title="Vault Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value")

    table.add_row("Vault Path", str(config.vault_path))
    table.add_row("Database", str(config.db_path))
    table.add_row("Vector DB", str(config.vectors_path))
    table.add_row("Documents", str(config.documents_path))
    table.add_row("OpenAI API Key", "Set" if os.environ.get("OPENAI_API_KEY") else "[red]Not Set[/red]")

    console.print(table)


@config_app.command("set")
def config_set(
    key: str = typer.Argument(..., help="Config key to set"),
    value: str = typer.Argument(..., help="Config value"),
):
    """Set a configuration value."""
    try:
        from .config import save_config
    except ImportError:
        from config import save_config

    try:
        save_config(key, value)
        console.print(f"[green]Config updated:[/green] {key} = {value}")
    except (OSError, ValueError) as e:
        console.print(f"[red]Error setting config:[/red] {e}")
        raise typer.Exit(1)


# =============================================================================
# Health Commands
# =============================================================================

@health_app.command("list")
def health_list(
    category: Optional[str] = typer.Option(None, "-c", "--category", help="Filter by category"),
    days: int = typer.Option(30, "-d", "--days", help="Days to show"),
):
    """List health entries."""
    db = get_db()

    try:
        entries = db.list_health_entries(category=category, days=days)

        if not entries:
            console.print("[yellow]No health entries found[/yellow]")
            return

        table = Table(title="Health Entries")
        table.add_column("ID", style="dim")
        table.add_column("Date", style="cyan")
        table.add_column("Category")
        table.add_column("Summary")

        for e in entries:
            table.add_row(
                str(e['id']),
                e.get('entry_date', '-'),
                e.get('category', '-'),
                (e.get('summary', '-') or '-')[:50],
            )

        console.print(table)

    except sqlite3.Error as e:
        console.print(f"[red]Error listing health entries:[/red] {e}")
        raise typer.Exit(1)


@health_app.command("insights")
def health_insights(
    query: str = typer.Option("recent health trends", "-q", "--query", help="Health query"),
    days: int = typer.Option(30, "-d", "--days", help="Days to analyze"),
):
    """Get AI-powered health insights."""
    try:
        try:
            from .rag import get_vault_rag
        except ImportError:
            from rag import get_vault_rag
        rag = get_vault_rag()

        console.print(f"[dim]Analyzing health data...[/dim]")
        result = rag.health_insights(query, days=days)

        if 'error' in result:
            console.print(f"[red]Error:[/red] {result['error']}")
            raise typer.Exit(1)

        console.print(f"\n[cyan]Health Insights:[/cyan]\n{result['insights']}")
        console.print(f"\n[dim]Based on {result['data_points']} data points[/dim]")

    except ImportError as e:
        console.print(f"[red]Error:[/red] RAG not available: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
