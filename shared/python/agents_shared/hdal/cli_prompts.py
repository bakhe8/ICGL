"""
Consensus AI — HDAL Prompts
============================

Rich text prompts for the HDAL interface.
Used to display decision packets and agent reports to the human.
"""

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
from rich.columns import Columns

from ..agents import SynthesizedResult
from ..kb.schemas import ADR

console = Console()


def display_adr_review(adr, synthesis, policy_report=None, sentinel_alerts=None):
    """Displays an ADR review screen with agent synthesis."""
    
    # 1. Header
    console.print(Panel(
        f"[bold blue]🏛️ Sovereign Decision Required[/bold blue]\n\n"
        f"**Title:** {adr.title}\n"
        f"**Status:** {adr.status}\n"
        f"**ID:** {adr.id}",
        title="HDAL Review",
        expand=False
    ))
    
    # 2. Context & Decision
    console.print(Panel(
        f"[bold]Context:[/bold]\n{adr.context}\n\n"
        f"[bold]Decision:[/bold]\n{adr.decision}\n\n"
        f"[bold]Consequences:[/bold]\n" + "\n".join([f"- {c}" for c in adr.consequences]),
        title="Proposal Details",
        border_style="cyan"
    ))

    # 3. Governance Reports (Policy & Sentinel side-by-side)
    # Note: policy_report and sentinel_alerts passed from orchestration
    
    policy_text = "[green]✅ All Policies Passed[/green]"
    if policy_report:
        if policy_report.status != "PASS":
            policy_text = f"[red]⛔ Status: {policy_report.status}[/red]\n"
            for v in policy_report.violated_policies:
                policy_text += f"- {v['code']}: {v['message']} ({v['severity']})\n"
        else:
            policy_text = f"[green]✅ PASS ({len(policy_report.passed_policies)} checks)[/green]\n"

    sentinel_text = "[green]🛡️ No Critical Alerts[/green]"
    if sentinel_alerts:
        sentinel_text = "[yellow]⚠️ Sentinel Alerts:[/yellow]\n"
        for alert in sentinel_alerts:
            color = "red" if alert.severity == "CRITICAL" else "yellow"
            sentinel_text += f"[{color}]- {alert.rule_id}: {alert.message} ({alert.severity})[/{color}]\n"

    console.print(Columns([
        Panel(policy_text, title="⚖️ Policy Gate", border_style="blue"),
        Panel(sentinel_text, title="🛡️ Sentinel Watch", border_style="yellow")
    ]))
    
    # 4. Agent Synthesis
    console.print("\n[bold yellow]🤖 Agent Consensus Report[/bold yellow]")
    console.print(Markdown(synthesis.to_markdown()))
    
    # 5. Prompt
    console.print("\n[bold]Instructions:[/bold] You are the sovereign authority. "
                  "You may Approve, Reject, or Request Changes.")


def prompt_decision() -> str:
    """Prompts the user for a decision action."""
    choices = ["APPROVE", "REJECT", "MODIFY", "EXPERIMENT"]
    return Prompt.ask(
        "[bold cyan]Select Action[/bold cyan]", 
        choices=choices, 
        default="APPROVE"
    )

def prompt_rationale() -> str:
    """Prompts for decision rationale."""
    return Prompt.ask("[bold cyan]Enter Rationale (for immutable log)[/bold cyan]")

def prompt_signature(human_id: str) -> bool:
    """Simulates a cryptographic signature step."""
    return Confirm.ask(f"✍️  [bold red]Sign as '{human_id}'?[/bold red]")
