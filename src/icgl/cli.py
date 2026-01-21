"""
ICGL — Command Line Interface
==============================

This module provides the command-line interface for interacting with
the ICGL (Iterative Co-Governance Loop) system.

Commands:
- hello: Welcome message
- consensus: Run ICGL bootstrap demo
- kb: Knowledge Base management (list, show, stats)
- icgl: ICGL cycle commands
- sentinel: Sentinel monitoring
"""

import click
import asyncio
from dotenv import load_dotenv
from pathlib import Path
from .core.runtime_guard import RuntimeIntegrityGuard, RuntimeIntegrityError

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Import new components
from .kb import PersistentKnowledgeBase, ADR, uid
from .governance import ICGL
from .sentinel import Sentinel

console = Console()


@click.group()
@click.version_option("0.1.0")
def cli():
    """ICGL: Iterative Co-Governance Loop - Governance-First Intelligence System."""
    # Lazy-load environment to avoid side effects on import
    env_path = Path(__file__).resolve().parent.parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
    rig = RuntimeIntegrityGuard()
    rig.check()

from .runtime import runtime
cli.add_command(runtime, name="runtime")

# ==========================================================================
# 🎉 General Commands
# ==========================================================================

@cli.command()
def hello():
    """Welcomes the user to Consensus AI."""
    console.print(Panel(
        "[bold blue]Welcome to ICGL![/bold blue]\n"
        "[italic]Iterative Co-Governance Loop — A Governance-First Intelligence System.[/italic]",
        title="🏛️ ICGL",
        expand=False
    ))


# ==========================================================================
# 📚 Knowledge Base Commands (Persistent)
# ==========================================================================

@cli.group()
def kb():
    """Knowledge Base management commands."""
    pass


@kb.command("stats")
def kb_stats():
    """Shows Knowledge Base statistics."""
    kb_instance = PersistentKnowledgeBase()
    stats = kb_instance.get_stats()
    
    table = Table(title="📊 Knowledge Base Statistics")
    table.add_column("Entity Type", style="cyan")
    table.add_column("Count", style="green", justify="right")
    
    for entity, count in stats.items():
        table.add_row(entity.title().replace("_", " "), str(count))
    
    console.print(table)


@kb.command("concepts")
def kb_concepts():
    """Lists all concepts in the Knowledge Base."""
    kb_instance = PersistentKnowledgeBase()
    
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
    kb_instance = PersistentKnowledgeBase()
    
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
    kb_instance = PersistentKnowledgeBase()
    
    if not kb_instance.adrs:
        console.print("[yellow]No ADRs found.[/yellow]")
        return
    
    table = Table(title="📜 Architectural Decision Records")
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Human Decision", style="magenta")
    
    for adr in kb_instance.adrs.values():
        status_color = {
            "DRAFT": "yellow",
            "CONDITIONAL": "blue",
            "ACCEPTED": "green",
            "REJECTED": "red",
            "EXPERIMENTAL": "magenta"
        }.get(adr.status, "white")
        
        human_status = "✅ Signed" if adr.human_decision_id else "❌ Pending"
        
        table.add_row(
            adr.id, 
            adr.title, 
            f"[{status_color}]{adr.status}[/{status_color}]",
            human_status
        )
    
    console.print(table)


@kb.command("show")
@click.argument("entity_type", type=click.Choice(["concept", "policy", "adr"]))
@click.argument("entity_id")
def kb_show(entity_type, entity_id):
    """Shows details of a specific entity."""
    kb_instance = PersistentKnowledgeBase()
    
    if entity_type == "concept":
        entity = kb_instance.get_concept(entity_id)
        if not entity: return console.print(f"[red]Concept '{entity_id}' not found.[/red]")
        
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
        # Supports lookup by ID or Code
        entity = kb_instance.get_policy(entity_id) or kb_instance.get_policy_by_code(entity_id)
        if not entity: return console.print(f"[red]Policy '{entity_id}' not found.[/red]")
        
        console.print(Panel(
            f"[bold]Code:[/bold] {entity.code}\n"
            f"[bold]Title:[/bold] {entity.title}\n"
            f"[bold]Rule:[/bold] {entity.rule}\n"
            f"[bold]Severity:[/bold] {entity.severity}\n"
            f"[bold]Enforced By:[/bold] {', '.join(entity.enforced_by)}",
            title=f"⚖️ Policy: {entity.code}"
        ))
    
    elif entity_type == "adr":
        entity = kb_instance.get_adr(entity_id)
        if not entity: return console.print(f"[red]ADR '{entity_id}' not found.[/red]")
        
        console.print(Panel(
            f"[bold]Title:[/bold] {entity.title}\n"
            f"[bold]Status:[/bold] {entity.status}\n"
            f"[bold]Context:[/bold] {entity.context}\n"
            f"[bold]Decision:[/bold] {entity.decision}\n"
            f"[bold]Consequences:[/bold]\n  - " + "\n  - ".join(entity.consequences) + "\n"
            f"[bold]Related Policies:[/bold] {', '.join(entity.related_policies) or 'None'}",
            title=f"📜 ADR: {entity_id}"
        ))


@kb.command("reset!!!")
@click.confirmation_option(prompt="Are you sure you want to WIPE the entire Knowledge Base?")
def kb_reset():
    """Wipes all data from the Knowledge Base."""
    kb_instance = PersistentKnowledgeBase(bootstrap=False)
    kb_instance._storage.clear_all()
    console.print("[red]Knowledge Base wiped successfully.[/red]")


@kb.command("validate")
def kb_validate():
    """Validates integrity of all Knowledge Base entities."""
    from .validator import SchemaValidator
    
    console.print("\n[bold cyan]🕵️  Starting Knowledge Base Validation...[/bold cyan]")
    
    kb_instance = PersistentKnowledgeBase()
    validator = SchemaValidator()
    
    # helper to validate a collection
    def validate_collection(name, collection):
        errors = 0
        console.print(f"[bold]Checking {name}...[/bold] ", end="")
        for entity in collection.values():
            try:
                validator.validate(entity)
            except Exception as e:
                console.print(f"\n   ❌ Error in {entity.id}: {e}")
                errors += 1
        
        if errors == 0:
            console.print("[green]OK[/green]")
        else:
            console.print(f"[red]FAILED ({errors} errors)[/red]")
        return errors

    total_errors = 0
    total_errors += validate_collection("Concepts", kb_instance.concepts)
    total_errors += validate_collection("Policies", kb_instance.policies)
    total_errors += validate_collection("ADRs", kb_instance.adrs)
    total_errors += validate_collection("Signals", kb_instance.signals)
    total_errors += validate_collection("Human Decisions", kb_instance.human_decisions)
    
    print("-" * 40)
    if total_errors == 0:
        console.print("[bold green]✅ All Systems Go. Knowledge Kernel Integrity Verified.[/bold green]")
    else:
        console.print(f"[bold red]❌ Validation Failed with {total_errors} errors.[/bold red]")


# ==============================================================================
# 🗺️ Roadmap Commands
# ==============================================================================

@cli.group()
def roadmap():
    """Manage the governed roadmap."""
    pass

@roadmap.command(name="load")
def load_roadmap():
    """Parses docs/roadmap.md and populates the Knowledge Base."""
    from pathlib import Path
    import re
    from .kb.persistent import PersistentKnowledgeBase
    from .kb.schemas import RoadmapItem, uid, now
    
    kb = PersistentKnowledgeBase()
    roadmap_path = Path("docs/roadmap.md")
    
    if not roadmap_path.exists():
        click.echo("[red]❌ docs/roadmap.md not found.[/red]")
        return
        
    content = roadmap_path.read_text(encoding="utf-8")
    lines = content.split('\n')
    
    cycles_found = 0
    click.echo("🔄 Syncing Sovereign Roadmap from Document...")
    
    # Regex for headers: "### [Icon] Cycle X: Title"
    # Matches: ### 🧠 Cycle 1: The Hitchhiker
    header_pattern = re.compile(r"^#{2,3}\s+.*Cycle\s+([0-9.]+)\s*:\s+(.+)")
    
    current_cycle = None
    
    for line in lines:
        line = line.strip()
        match = header_pattern.match(line)
        
        if match:
            # If we were processing a cycle, save it
            if current_cycle:
                kb.add_roadmap_item(current_cycle)
                click.echo(f"   ✅ Loaded Cycle {current_cycle.cycle}: {current_cycle.title} [{current_cycle.status}]")
                cycles_found += 1
            
            # Start new cycle
            cycle_num_str = match.group(1)
            title = match.group(2).strip()
            
            # Heuristic status
            status = "PLANNED"
            if "Completed" in line or cycle_num_str.startswith("0"):
                status = "COMPLETED"
            
            try:
                cycle_num = int(float(cycle_num_str))
            except:
                cycle_num = 0
                
            current_cycle = RoadmapItem(
                id=uid(),
                cycle=cycle_num,
                title=title,
                status=status,
                goals=[],
                governed_by_adr=None 
            )
            
        elif current_cycle and line.startswith("- ["):
            # Clean up checklist item: "- [ ] **Key**: Value" -> "Key: Value"
            goal_text = re.sub(r"- \[[x ]\]\s+", "", line)
            goal_text = goal_text.replace("**", "")
            current_cycle.goals.append(goal_text)

    # Add the last one
    if current_cycle:
        kb.add_roadmap_item(current_cycle)
        click.echo(f"   ✅ Loaded Cycle {current_cycle.cycle}: {current_cycle.title} [{current_cycle.status}]")
        cycles_found += 1
            
    if cycles_found == 0:
        click.echo("[yellow]⚠️ No cycles found in roadmap.md. Check formatting.[/yellow]")
    else:
        # Also persist!
        click.echo(f"[green]🎉 Successfully synced {cycles_found} cycles to Knowledge Base.[/green]")


@roadmap.command(name="list")
def list_roadmap():
    """Lists all roadmap cycles and their status."""
    from .kb.persistent import PersistentKnowledgeBase
    
    kb = PersistentKnowledgeBase()
    click.echo("\n🗺️  ICGL Sovereign Roadmap\n")
    
    if not kb.roadmap_items:
        click.echo("   (No governed roadmap items found. Use `icgl roadmap load` to import.)")
        return

    click.echo(f"   Debug: Found {len(kb.roadmap_items)} items in KB.")

    # Sort by cycle
    sorted_items = sorted(kb.roadmap_items, key=lambda x: x.cycle)

    for item in sorted_items:
        status_color = "white"
        if item.status == "COMPLETED": status_color = "green"
        elif item.status == "ACTIVE": status_color = "yellow"
        elif item.status == "BLOCKED": status_color = "red"
        
        goals_summary = ", ".join(item.goals[:2]) + ("..." if len(item.goals) > 2 else "")
        click.echo(f"   Cycle {item.cycle}: {item.title}") 
        click.echo(f"   [{click.style(item.status, fg=status_color)}] - {goals_summary}\n")
# ==========================================================================
# 🔁 ICGL Commands (Orchestrated)
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
    """Runs a full Multi-Agent Governance Cycle."""
    
    # Run async logic in sync wrapper
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
    from .agents.architect import ArchitectAgent
    from .agents.base import Problem
    from .kb.persistent import PersistentKnowledgeBase
    
    # Run async logic
    async def _run():
        console.print(Panel(f"[bold]Topic:[/bold] {topic}", title="🧠 Architect Exploration", border_style="cyan"))
        
        from .core.observability import SystemObserver
        
        agent = ArchitectAgent()
        # Observability injection
        agent.observer = SystemObserver()
        
        kb = PersistentKnowledgeBase()
        
        # Create a synthetic problem package
        problem = Problem(
            title=f"Exploration: {topic}",
            context=f"User wants to explore architectural implications of: {topic}",
            metadata={"decision": "Proposed Implementation"}
        )
        
        with console.status("[bold green]Architect is thinking (via OpenAI)...[/bold green]"):
            result = await agent.analyze(problem, kb)
        
        # Render Result
        # Render Result
        if result.confidence == 0.0:
             click.echo("\n[red]❌ Execution Failed[/red]")
             click.echo(f"Reason: {result.analysis}")
        else:
            click.echo("\n" + "="*60)
            click.echo("✅ ARCHITECT REPORT")
            click.echo("="*60 + "\n")
            
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
            click.echo("\n" + "="*60 + "\n")

    asyncio.run(_run())


@icgl.command("status")
def icgl_status():
    """Shows the current ICGL status."""
    kb_instance = PersistentKnowledgeBase()
    stats = kb_instance.get_stats()
    
    console.print(Panel(
        f"[bold]Total Cycles:[/bold] {stats['learning_logs']}\n"
        f"[bold]Total ADRs:[/bold] {stats['adrs']}\n"
        f"[bold]Human Decision Rate:[/bold] {stats['human_decisions']}/{stats['adrs']}",
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


# ==========================================================================
# 📚 Docs Refactor Commands (GOVERNED PIPELINE)
# ==========================================================================

@cli.group()
def docs():
    """Governed documentation refactor pipeline."""
    pass


@docs.command("refactor")
@click.option('--session-id', default=None, help="Resume existing session")
def docs_refactor(session_id):
    """
    Analyze and refactor documentation under strict governance.
    
    Pipeline:
    1. Snapshot /docs (read-only)
    2. DocumentationAgent analysis (LLM-backed)
    3. Stage to /staging/docs (never /docs)
    4. Human review & approval
    5. Manual promotion (no auto-commit)
    """
    from .governance.docs_pipeline import DocsRefactorPipeline
    from .kb.schemas import uid
    
    async def _run():
        pipeline = DocsRefactorPipeline()
        
        # Generate session ID if not provided
        if not session_id:
            new_session_id = f"docs_{uid()}"
        else:
            new_session_id = session_id
        
        console.print(Panel(
            "[bold]🧠 ICGL Governed Documentation Refactor[/bold]\n"
            "[italic]All modifications staged to /staging only[/italic]",
            title="📚 Documentation Pipeline",
            border_style="cyan"
        ))
        console.print(f"Session: [cyan]{new_session_id}[/cyan]\n")
        
        # Phase 1: Snapshot
        with console.status("[yellow]📸 Loading documentation snapshot...[/yellow]"):
            snapshot = pipeline.load_snapshot()
        
        console.print(f"✅ Snapshot: {snapshot.total_files} files, "
                     f"{snapshot.total_size_bytes / 1024:.1f} KB\n")
        
        # Phase 2: Agent Analysis
        console.print("[yellow]🤖 Running DocumentationAgent (this may take 30-60s)...[/yellow]")
        
        try:
            plan = await pipeline.analyze(snapshot)
        except ValueError as e:
            console.print(f"[red]❌ {e}[/red]")
            console.print("\n💡 Set OPENAI_API_KEY in your .env file")
            return
        except Exception as e:
            console.print(f"[red]❌ Analysis failed: {e}[/red]")
            return
        
        console.print(f"✅ Analysis complete. Confidence: [green]{plan.confidence_score:.1%}[/green]\n")
        
        # Show issues
        if plan.issues:
            console.print("[bold red]⚠️  Issues Detected:[/bold red]")
            for issue in plan.issues[:5]:  # Show first 5
                console.print(f"  • {issue}")
            if len(plan.issues) > 5:
                console.print(f"  ... and {len(plan.issues) - 5} more")
            console.print()
        
        # Phase 3: Stage files
        with console.status("[yellow]📝 Staging generated files...[/yellow]"):
            manifest = pipeline.stage_files(plan, new_session_id)
        
        console.print(f"✅ Staged {len(manifest.files_written)} files to "
                     f"[cyan]/staging/docs/{new_session_id}/[/cyan]\n")
        
        # Phase 4: Human Review
        console.print(Panel(
            "[bold yellow]👤 HUMAN REVIEW REQUIRED[/bold yellow]\n\n"
            "Generated files are in staging. Review before approval.",
            border_style="yellow"
        ))
        
        # Show file list
        table = Table(title="📋 Staged Files")
        table.add_column("File", style="cyan")
        table.add_column("Size", justify="right")
        
        for filepath in manifest.files_written[:10]:  # Show first 10
            from pathlib import Path
            size = Path(filepath).stat().st_size
            rel_path = str(Path(filepath).relative_to(f"staging/docs/{new_session_id}"))
            table.add_row(rel_path, f"{size:,} bytes")
        
        if len(manifest.files_written) > 10:
            table.add_row(f"... and {len(manifest.files_written) - 10} more", "")
        
        console.print(table)
        console.print()
        
        # Review options
        console.print("[bold]📋 Review Options:[/bold]")
        console.print("  1. [cyan]View files[/cyan] - Open staging directory")
        console.print("  2. [cyan]Show diffs[/cyan] - Compare with original")
        console.print("  3. [green]APPROVE[/green] - Get promotion instructions")
        console.print("  4. [red]REJECT[/red] - Discard staging")
        console.print("  5. [yellow]Exit[/yellow] - Review later\n")
        
        choice = click.prompt("Your choice", type=int, default=5)
        
        if choice == 1:
            import os
            staging_path = f"staging/docs/{new_session_id}"
            console.print(f"\n📂 Staged files: [cyan]{staging_path}[/cyan]")
            if os.name == 'nt':  # Windows
                os.system(f'explorer "{staging_path}"')
            else:  # Unix/Mac
                os.system(f'open "{staging_path}"')
        
        elif choice == 2:
            console.print("\n[bold]📊 Generating diffs...[/bold]")
            diffs = pipeline.show_diffs(new_session_id)
            
            for filepath, diff in list(diffs.items())[:3]:  # Show first 3
                console.print(f"\n[cyan]{'='*60}[/cyan]")
                console.print(f"[bold]{filepath}[/bold]")
                console.print(f"[cyan]{'='*60}[/cyan]")
                console.print(diff[:500])  # First 500 chars
                console.print("...")
            
            if len(diffs) > 3:
                console.print(f"\n... and {len(diffs) - 3} more diffs")
        
        elif choice == 3:
            console.print("\n[bold green]✅ APPROVED FOR PROMOTION[/bold green]\n")
            instructions = pipeline.get_promotion_instructions(new_session_id)
            console.print(Panel(instructions, title="🚀 Promotion Instructions", border_style="green"))
        
        elif choice == 4:
            if click.confirm("\n[red]⚠️  Discard all staged files?[/red]", default=False):
                pipeline.clear_session(new_session_id)
                console.print("[red]❌ Session discarded[/red]")
            else:
                console.print("[yellow]Cancelled[/yellow]")
        
        else:
            console.print(f"\n[yellow]Session saved: {new_session_id}[/yellow]")
            console.print(f"Resume with: [cyan]icgl docs show-session {new_session_id}[/cyan]")
    
    asyncio.run(_run())


@docs.command("list-sessions")
def docs_list_sessions():
    """List all staging sessions."""
    from .governance.staging_manager import StagingManager
    
    staging = StagingManager()
    sessions = staging.list_sessions()
    
    if not sessions:
        console.print("[yellow]No staging sessions found.[/yellow]")
        return
    
    table = Table(title="📋 Staging Sessions")
    table.add_column("Session ID", style="cyan")
    table.add_column("Files", justify="right")
    table.add_column("Agent", style="yellow")
    
    for session_id in sessions:
        manifest = staging.get_session_manifest(session_id)
        if manifest:
            table.add_row(
                session_id,
                str(len(manifest.files_written)),
                manifest.agent_id
            )
        else:
            table.add_row(session_id, "?", "unknown")
    
    console.print(table)


@docs.command("show-session")
@click.argument("session_id")
def docs_show_session(session_id):
    """Show details of a staging session."""
    from .governance.staging_manager import StagingManager
    from pathlib import Path
    
    staging = StagingManager()
    manifest = staging.get_session_manifest(session_id)
    
    if not manifest:
        console.print(f"[red]Session not found: {session_id}[/red]")
        return
    
    console.print(Panel(
        f"[bold]Session:[/bold] {manifest.session_id}\n"
        f"[bold]Agent:[/bold] {manifest.agent_id}\n"
        f"[bold]Timestamp:[/bold] {manifest.timestamp}\n"
        f"[bold]Confidence:[/bold] {manifest.confidence_score:.1%}\n"
        f"[bold]Summary:[/bold] {manifest.plan_summary}\n\n"
        f"[bold]Files:[/bold] {len(manifest.files_written)}",
        title="📋 Session Details",
        border_style="cyan"
    ))
    
    console.print("\n[bold]Files:[/bold]")
    for filepath in manifest.files_written[:20]:
        size = Path(filepath).stat().st_size
        console.print(f"  • {Path(filepath).name} ({size:,} bytes)")
    
    if len(manifest.files_written) > 20:
        console.print(f"  ... and {len(manifest.files_written) - 20} more")


@docs.command("clear-session")
@click.argument("session_id")
@click.confirmation_option(prompt="Are you sure you want to delete this session?")
def docs_clear_session(session_id):
    """Delete a staging session."""
    from .governance.staging_manager import StagingManager
    
    staging = StagingManager()
    staging.clear_session(session_id)
    console.print(f"[green]✅ Session cleared: {session_id}[/green]")


@docs.command("refactor-governed")
@click.option("--quality-threshold", default=0.90, help="Minimum quality score (0-1)")
@click.option("--max-iterations", default=3, help="Maximum improvement iterations")
def docs_refactor_governed(quality_threshold: float, max_iterations: int):
    """
    Run FULL ICGL governance cycle for documentation refactor.
    
    Includes:
    - Multi-agent review (Mediator)
    - Iterative improvement loop
    - Quality threshold enforcement
    - ADR creation
    - Sentinel and Policy checks
    """
    import asyncio
    from icgl.governance.governed_docs_refactor import GovernedDocsRefactor
    
    console.print(Panel.fit(
        "[bold cyan]ICGL Governed Documentation Refactor[/bold cyan]\\n"
        f"Quality Threshold: {quality_threshold:.1%}\\n"
        f"Max Iterations: {max_iterations}",
        border_style="cyan"
    ))
    
    async def run():
        cycle = GovernedDocsRefactor()
        result = await cycle.run_full_cycle(
            quality_threshold=quality_threshold,
            max_iterations=max_iterations
        )
        
        if result:
            console.print("\\n[bold green]✅ SUCCESS![/bold green]")
            console.print(f"ADR ID: [cyan]{result['adr_id']}[/cyan]")
            console.print(f"Iterations: [yellow]{result['iterations']}[/yellow]")
            console.print(f"Final Quality: [green]{result['final_quality']:.1%}[/green]")
            console.print(f"Session: [cyan]{result['session_id']}[/cyan]")
            
            console.print("\\n[dim]Review files in staging, then approve or reject.[/dim]")
        else:
            console.print("\\n[bold red]❌ Failed to achieve quality threshold[/bold red]")
            
    asyncio.run(run())


if __name__ == "__main__":
    cli()
