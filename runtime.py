import click
from core.runtime_guard import RuntimeIntegrityGuard, RuntimeIntegrityError

@click.group()
def runtime():
    """Runtime integrity commands."""
    pass

@runtime.command("repair")
def runtime_repair():
    """Run Runtime Integrity Guard repair routine."""
    guard = RuntimeIntegrityGuard()
    try:
        guard.repair()
        click.echo("[green]✅ Runtime repair completed[/green]")
    except Exception as e:
        click.echo(f"[red]❌ Runtime repair failed: {e}[/red]")
