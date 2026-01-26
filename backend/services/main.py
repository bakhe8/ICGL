from rich.console import Console
from rich.traceback import install

from .cli import cli
from .utils.logger import setup_logging

# Install rich traceback handler for better error reporting
install(show_locals=True)
console = Console()


def main():
    try:
        setup_logging()
        cli()
    except Exception as e:
        console.print(f"[bold red]Critical System Error:[/bold red] {e}")
        console.print_exception()
        exit(1)


if __name__ == "__main__":
    main()
