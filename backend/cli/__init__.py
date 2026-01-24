from pathlib import Path

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

from ..core.runtime_guard import RuntimeIntegrityGuard

console = Console()


# Import and attach groups from specialized modules
from ..runtime import runtime
from .governance import docs, icgl, sentinel
from .kb import kb, roadmap


@click.group()
@click.version_option("0.2.0")
def cli():
    """ICGL: Iterative Co-Governance Loop - Governance-First Intelligence System."""
    env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    load_dotenv(dotenv_path=env_path)
    rig = RuntimeIntegrityGuard()
    rig.check()


@cli.command()
def hello():
    """Welcomes the user to Consensus AI."""
    console.print(
        Panel(
            "[bold blue]Welcome to ICGL![/bold blue]\n"
            "[italic]Iterative Co-Governance Loop — A Governance-First Intelligence System.[/italic]",
            title="🏛️ ICGL",
            expand=False,
        )
    )


cli.add_command(kb)
cli.add_command(roadmap)
cli.add_command(icgl)
cli.add_command(sentinel)
cli.add_command(docs)
cli.add_command(runtime)
