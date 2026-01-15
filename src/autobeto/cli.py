"""
Consensus AI — Enhanced CLI
============================

This module provides the command-line interface for interacting with
the Consensus AI system.

Commands:
- hello: Welcome message
- consensus: Run ICGL bootstrap demo
- kb: Knowledge Base management (list, show, stats)
- adr: ADR management (list, show, create)
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


@click.group()
@click.version_option("0.1.0")
def cli():
    """AutoBeto: Consensus AI - Governance-First Intelligence System."""
    pass


# ==========================================================================
# 🎉 General Commands
# ==========================================================================

@cli.command()
def hello():
    """Welcomes the user to Consensus AI."""
    console.print(Panel(
        "[bold blue]Welcome to Consensus AI![/bold blue]\n"
        "[italic]A Governance-First Intelligence System for Long-Lived Decisions.[/italic]",
        title="🏛️ Consensus AI",
        expand=False
    ))


@cli.command()
@click.option("--human", default="bakheet", help="Human decision maker ID")
def consensus(human):
    """Runs the Consensus AI (ICGL) bootstrap demo."""
    from . import run_demo
    console.print("[bold magenta]Starting Consensus AI Bootstrap...[/bold magenta]")
    run_demo()
    console.print("[bold green]Consensus AI Cycle Complete![/bold green]")


# ==========================================================================
# 📚 Knowledge Base Commands
# ==========================================================================

@cli.group()
def kb():
    """Knowledge Base management commands."""
    pass


@kb.command("stats")
def kb_stats():
    """Shows Knowledge Base statistics."""
    from . import KnowledgeBase
    kb_instance = KnowledgeBase(validate=False)
    
    table = Table(title="📊 Knowledge Base Statistics")
    table.add_column("Entity Type", style="cyan")
    table.add_column("Count", style="green", justify="right")
    
    table.add_row("Concepts", str(len(kb_instance.concepts)))
    table.add_row("Policies", str(len(kb_instance.policies)))
    table.add_row("ADRs", str(len(kb_instance.adrs)))
    table.add_row("Sentinel Signals", str(len(kb_instance.signals)))
    table.add_row("Human Decisions", str(len(kb_instance.human_decisions)))
    table.add_row("Learning Logs", str(len(kb_instance.learning_log)))
    
    console.print(table)


@kb.command("concepts")
def kb_concepts():
    """Lists all concepts in the Knowledge Base."""
    from . import KnowledgeBase
    kb_instance = KnowledgeBase(validate=False)
    
    if not kb_instance.concepts:
        console.print("[yellow]No concepts found.[/yellow]")
        return
    
    table = Table(title="🧠 Concepts")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Owner", style="yellow")
    table.add_column("Version", style="blue")
    
    for concept in kb_instance.concepts.values():
        table.add_row(concept.id, concept.name, concept.owner, concept.version)
    
    console.print(table)


@kb.command("policies")
def kb_policies():
    """Lists all policies in the Knowledge Base."""
    from . import KnowledgeBase
    kb_instance = KnowledgeBase(validate=False)
    
    if not kb_instance.policies:
        console.print("[yellow]No policies found.[/yellow]")
        return
    
    table = Table(title="⚖️ Policies")
    table.add_column("Code", style="cyan")
    table.add_column("Title", style="green")
    table.add_column("Severity", style="red")
    table.add_column("Enforced By", style="yellow")
    
    for policy in kb_instance.policies.values():
        table.add_row(
            policy.code,
            policy.title,
            policy.severity,
            ", ".join(policy.enforced_by)
        )
    
    console.print(table)


@kb.command("adrs")
def kb_adrs():
    """Lists all ADRs in the Knowledge Base."""
    from . import KnowledgeBase
    kb_instance = KnowledgeBase(validate=False)
    
    if not kb_instance.adrs:
        console.print("[yellow]No ADRs found.[/yellow]")
        return
    
    table = Table(title="📜 Architectural Decision Records")
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="green")
    table.add_column("Status", style="yellow")
    
    for adr in kb_instance.adrs.values():
        status_color = {
            "DRAFT": "yellow",
            "CONDITIONAL": "blue",
            "ACCEPTED": "green",
            "REJECTED": "red",
            "EXPERIMENTAL": "magenta"
        }.get(adr.status, "white")
        table.add_row(adr.id, adr.title, f"[{status_color}]{adr.status}[/{status_color}]")
    
    console.print(table)


@kb.command("show")
@click.argument("entity_type", type=click.Choice(["concept", "policy", "adr"]))
@click.argument("entity_id")
def kb_show(entity_type, entity_id):
    """Shows details of a specific entity."""
    from . import KnowledgeBase
    kb_instance = KnowledgeBase(validate=False)
    
    if entity_type == "concept":
        entity = kb_instance.concepts.get(entity_id)
        if not entity:
            console.print(f"[red]Concept '{entity_id}' not found.[/red]")
            return
        console.print(Panel(
            f"[bold]Name:[/bold] {entity.name}\n"
            f"[bold]Definition:[/bold] {entity.definition}\n"
            f"[bold]Invariants:[/bold] {', '.join(entity.invariants)}\n"
            f"[bold]Anti-patterns:[/bold] {', '.join(entity.anti_patterns)}\n"
            f"[bold]Owner:[/bold] {entity.owner}\n"
            f"[bold]Version:[/bold] {entity.version}",
            title=f"🧠 Concept: {entity_id}"
        ))
    
    elif entity_type == "policy":
        entity = kb_instance.policies.get(entity_id)
        if not entity:
            console.print(f"[red]Policy '{entity_id}' not found.[/red]")
            return
        console.print(Panel(
            f"[bold]Code:[/bold] {entity.code}\n"
            f"[bold]Title:[/bold] {entity.title}\n"
            f"[bold]Rule:[/bold] {entity.rule}\n"
            f"[bold]Severity:[/bold] {entity.severity}\n"
            f"[bold]Enforced By:[/bold] {', '.join(entity.enforced_by)}",
            title=f"⚖️ Policy: {entity.code}"
        ))
    
    elif entity_type == "adr":
        entity = kb_instance.adrs.get(entity_id)
        if not entity:
            console.print(f"[red]ADR '{entity_id}' not found.[/red]")
            return
        console.print(Panel(
            f"[bold]Title:[/bold] {entity.title}\n"
            f"[bold]Status:[/bold] {entity.status}\n"
            f"[bold]Context:[/bold] {entity.context}\n"
            f"[bold]Decision:[/bold] {entity.decision}\n"
            f"[bold]Consequences:[/bold]\n  - " + "\n  - ".join(entity.consequences) + "\n"
            f"[bold]Related Policies:[/bold] {', '.join(entity.related_policies) or 'None'}",
            title=f"📜 ADR: {entity_id}"
        ))


# ==========================================================================
# 🔁 ICGL Commands
# ==========================================================================

@cli.group()
def icgl():
    """ICGL (Iterative Co-Governance Loop) commands."""
    pass


@icgl.command("run")
@click.option("--title", prompt="ADR Title", help="Title of the new ADR")
@click.option("--context", prompt="Context", help="Context of the decision")
@click.option("--decision", prompt="Decision", help="The decision being made")
@click.option("--human", default="bakheet", help="Human decision maker ID")
def icgl_run(title, context, decision, human):
    """Runs an ICGL cycle with a new ADR."""
    from . import KnowledgeBase, ICGL, Sentinel, HDAL, ADR, uid
    
    console.print(f"\n[bold cyan]Creating new ADR: {title}[/bold cyan]")
    
    kb_instance = KnowledgeBase()
    sentinel = Sentinel()
    hdal = HDAL()
    icgl_instance = ICGL(kb_instance, sentinel, hdal)
    
    adr = ADR(
        id=uid(),
        title=title,
        status="DRAFT",
        context=context,
        decision=decision,
        consequences=[],
        related_policies=[],
        sentinel_signals=[],
        human_decision_id=None,
    )
    
    icgl_instance.run_cycle(adr, human_id=human)
    
    console.print(f"\n[bold green]✅ ICGL Cycle completed for: {title}[/bold green]")


@icgl.command("status")
def icgl_status():
    """Shows the current ICGL status."""
    from . import KnowledgeBase
    kb_instance = KnowledgeBase(validate=False)
    
    console.print(Panel(
        f"[bold]Total Cycles:[/bold] {len(kb_instance.learning_log)}\n"
        f"[bold]Total ADRs:[/bold] {len(kb_instance.adrs)}\n"
        f"[bold]Total Human Decisions:[/bold] {len(kb_instance.human_decisions)}",
        title="🔁 ICGL Status"
    ))


# ==========================================================================
# 🛡️ Sentinel Commands
# ==========================================================================

@cli.group()
def sentinel():
    """Sentinel monitoring commands."""
    pass


@sentinel.command("signals")
def sentinel_signals():
    """Lists all registered Sentinel signals."""
    from . import KnowledgeBase
    kb_instance = KnowledgeBase(validate=False)
    
    if not kb_instance.signals:
        console.print("[yellow]No Sentinel signals registered.[/yellow]")
        return
    
    table = Table(title="🛡️ Sentinel Signals")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Category", style="yellow")
    table.add_column("Action", style="red")
    
    for signal in kb_instance.signals.values():
        table.add_row(signal.id, signal.name, signal.category, signal.default_action)
    
    console.print(table)


if __name__ == "__main__":
    cli()
