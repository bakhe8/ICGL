import asyncio

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..governance import ICGL
from ..kb import ADR, PersistentKnowledgeBase, uid

console = Console()


@click.group()
def icgl():
    """ICGL (Iterative Co-Governance Loop) commands."""
    pass


@icgl.command("run")
@click.option("--title", prompt="ADR Title", help="Title of the new ADR")
@click.option("--context", prompt="Context", help="Context of the decision")
@click.option("--decision", prompt="Decision", help="The decision being made")
@click.option("--human", default="bakheet", help="Human decision maker ID")
def icgl_run(title, context, decision, human):
    """Runs a full Multi-Agent Governance Cycle."""

    async def _run():
        icgl_instance = ICGL()
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
        await icgl_instance.run_governance_cycle(adr, human_id=human)

    asyncio.run(_run())


@icgl.command("explore")
@click.argument("topic", default="Refactor Authentication Module")
def icgl_explore(topic):
    """Runs a governed Architect Agent exploration on a topic."""
    from ..agents.architect import ArchitectAgent
    from ..agents.base import Problem

    async def _run():
        console.print(
            Panel(
                f"[bold]Topic:[/bold] {topic}",
                title="🧠 Architect Exploration",
                border_style="cyan",
            )
        )
        from ..core.observability import SystemObserver

        agent = ArchitectAgent()
        agent.observer = SystemObserver()
        kb = PersistentKnowledgeBase()
        problem = Problem(
            title=f"Exploration: {topic}",
            context=f"User wants to explore architectural implications of: {topic}",
            metadata={"decision": "Proposed Implementation"},
        )
        with console.status(
            "[bold green]Architect is thinking (via OpenAI)...[/bold green]"
        ):
            result = await agent.analyze(problem, kb)

        if result.confidence == 0.0:
            click.echo("\n[red]❌ Execution Failed[/red]")
            click.echo(f"Reason: {result.analysis}")
        else:
            click.echo("\n" + "=" * 60)
            click.echo("✅ ARCHITECT REPORT")
            click.echo("=" * 60 + "\n")
            click.echo(f"CONFIDENCE: {result.confidence}\n")
            click.echo("🔍 ANALYSIS:")
            click.echo("-" * 20)
            click.echo(result.analysis + "\n")
            click.echo("⚠️ RISKS:")
            click.echo("-" * 20)
            for risk in result.concerns:
                click.echo(f"- {risk}")
            click.echo("")
            click.echo("💡 RECOMMENDATIONS:")
            click.echo("-" * 20)
            for rec in result.recommendations:
                click.echo(f"- {rec}")
            click.echo("\n" + "=" * 60 + "\n")

    asyncio.run(_run())


@icgl.command("status")
def icgl_status():
    """Shows the current ICGL status."""
    kb_instance = PersistentKnowledgeBase()
    stats = kb_instance.get_stats()
    console.print(
        Panel(
            f"[bold]Total Cycles:[/bold] {stats['learning_logs']}\n"
            f"[bold]Total ADRs:[/bold] {stats['adrs']}\n"
            f"[bold]Human Decision Rate:[/bold] {stats['human_decisions']}/{stats['adrs']}",
            title="🔁 ICGL Status",
        )
    )


@click.group()
def sentinel():
    """Sentinel monitoring commands."""
    pass


@sentinel.command("signals")
def sentinel_signals():
    """Lists all registered Sentinel signals."""
    kb_instance = PersistentKnowledgeBase()
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


@click.group()
def docs():
    """Governed documentation refactor pipeline."""
    pass


@docs.command("refactor")
@click.option("--session-id", default=None, help="Resume existing session")
def docs_refactor(session_id):
    """Analyze and refactor documentation under strict governance."""
    from ..governance.docs_pipeline import DocsRefactorPipeline

    async def _run():
        pipeline = DocsRefactorPipeline()
        new_session_id = session_id or f"docs_{uid()}"
        snapshot = pipeline.load_snapshot()
        plan = await pipeline.analyze(snapshot)
        manifest = pipeline.stage_files(plan, new_session_id)
        click.echo(
            f"Staged {len(manifest.files_written)} files to staging/docs/{new_session_id}"
        )

    asyncio.run(_run())
