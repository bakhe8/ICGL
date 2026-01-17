from rich.console import Console
from .cli import cli
from .utils.logger import setup_logging
from .config.manager import config

console = Console()

def main():
    try:
        setup_logging()
        cli()
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        exit(1)

if __name__ == "__main__":
    main()
