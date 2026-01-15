import click
from rich.console import Console
from rich.panel import Panel

console = Console()

@click.group()
@click.version_option("0.1.0")
def cli():
    """AutoBeto: A powerful Python-based automation tool."""
    pass

@cli.command()
def hello():
    """Welcomes the user."""
    console.print(Panel("[bold blue]Welcome to AutoBeto![/bold blue]\n[italic]Your automation journey starts here.[/italic]", title="AutoBeto", expand=False))

@cli.command()
@click.argument("task_name", default="default")
def auto(task_name):
    """Runs an automation task."""
    from loguru import logger
    logger.info(f"Starting automation task: {task_name}")
    console.print(f"[yellow]Executing task:[/yellow] [bold]{task_name}[/bold]...")
    # Simulated work
    import time
    time.sleep(1)
    logger.success(f"Task {task_name} completed successfully.")
    console.print("[green]Task finished![/green]")

if __name__ == "__main__":
    cli()
