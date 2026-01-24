import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..kb import PersistentKnowledgeBase

console = Console()


@click.group()
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
            policy.code, policy.title, policy.severity, ", ".join(policy.enforced_by)
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
            "EXPERIMENTAL": "magenta",
        }.get(adr.status, "white")

        human_status = "✅ Signed" if adr.human_decision_id else "❌ Pending"

        table.add_row(
            adr.id,
            adr.title,
            f"[{status_color}]{adr.status}[/{status_color}]",
            human_status,
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
        if not entity:
            return console.print(f"[red]Concept '{entity_id}' not found.[/red]")

        console.print(
            Panel(
                f"[bold]Name:[/bold] {entity.name}\n"
                f"[bold]Definition:[/bold] {entity.definition}\n"
                f"[bold]Invariants:[/bold] {', '.join(entity.invariants)}\n"
                f"[bold]Anti-patterns:[/bold] {', '.join(entity.anti_patterns)}\n"
                f"[bold]Owner:[/bold] {entity.owner}\n"
                f"[bold]Version:[/bold] {entity.version}",
                title=f"🧠 Concept: {entity_id}",
            )
        )

    elif entity_type == "policy":
        entity = kb_instance.get_policy(entity_id) or kb_instance.get_policy_by_code(
            entity_id
        )
        if not entity:
            return console.print(f"[red]Policy '{entity_id}' not found.[/red]")

        console.print(
            Panel(
                f"[bold]Code:[/bold] {entity.code}\n"
                f"[bold]Title:[/bold] {entity.title}\n"
                f"[bold]Rule:[/bold] {entity.rule}\n"
                f"[bold]Severity:[/bold] {entity.severity}\n"
                f"[bold]Enforced By:[/bold] {', '.join(entity.enforced_by)}",
                title=f"⚖️ Policy: {entity.code}",
            )
        )

    elif entity_type == "adr":
        entity = kb_instance.get_adr(entity_id)
        if not entity:
            return console.print(f"[red]ADR '{entity_id}' not found.[/red]")

        console.print(
            Panel(
                f"[bold]Title:[/bold] {entity.title}\n"
                f"[bold]Status:[/bold] {entity.status}\n"
                f"[bold]Context:[/bold] {entity.context}\n"
                f"[bold]Decision:[/bold] {entity.decision}\n"
                f"[bold]Consequences:[/bold]\n  - "
                + "\n  - ".join(entity.consequences)
                + "\n"
                f"[bold]Related Policies:[/bold] {', '.join(entity.related_policies) or 'None'}",
                title=f"📜 ADR: {entity_id}",
            )
        )


@kb.command("reset!!!")
@click.confirmation_option(
    prompt="Are you sure you want to WIPE the entire Knowledge Base?"
)
def kb_reset():
    """Wipes all data from the Knowledge Base."""
    kb_instance = PersistentKnowledgeBase(bootstrap=False)
    kb_instance._storage.clear_all()
    console.print("[red]Knowledge Base wiped successfully.[/red]")


@kb.command("validate")
def kb_validate():
    """Validates integrity of all Knowledge Base entities."""
    from ..validator import SchemaValidator

    console.print("\n[bold cyan]🕵️  Starting Knowledge Base Validation...[/bold cyan]")

    kb_instance = PersistentKnowledgeBase()
    validator = SchemaValidator()

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

    try:
        total_errors = 0
        total_errors += validate_collection("Concepts", kb_instance.concepts)
        total_errors += validate_collection("Policies", kb_instance.policies)
        total_errors += validate_collection("ADRs", kb_instance.adrs)
        total_errors += validate_collection("Signals", kb_instance.signals)
        total_errors += validate_collection(
            "Human Decisions", kb_instance.human_decisions
        )

        print("-" * 40)
        if total_errors == 0:
            console.print(
                "[bold green]✅ All Systems Go. Knowledge Kernel Integrity Verified.[/bold green]"
            )
        else:
            console.print(
                f"[bold red]❌ Validation Failed with {total_errors} errors.[/bold red]"
            )
    except Exception as e:
        console.print(f"[red]Validation failed: {e}[/red]")
        return 1


@click.group()
def roadmap():
    """Manage the governed roadmap."""
    pass


@roadmap.command(name="load")
def load_roadmap():
    """Parses docs/roadmap.md and populates the Knowledge Base."""
    import re
    from pathlib import Path

    from ..kb.schemas import RoadmapItem, uid

    kb = PersistentKnowledgeBase()
    roadmap_path = Path("docs/roadmap.md")

    if not roadmap_path.exists():
        click.echo("[red]❌ docs/roadmap.md not found.[/red]")
        return

    content = roadmap_path.read_text(encoding="utf-8")
    lines = content.split("\n")

    cycles_found = 0
    click.echo("🔄 Syncing Sovereign Roadmap from Document...")

    header_pattern = re.compile(r"^#{2,3}\s+.*Cycle\s+([0-9.]+)\s*:\s+(.+)")
    current_cycle = None

    for line in lines:
        line = line.strip()
        match = header_pattern.match(line)

        if match:
            if current_cycle:
                kb.add_roadmap_item(current_cycle)
                click.echo(
                    f"   ✅ Loaded Cycle {current_cycle.cycle}: {current_cycle.title} [{current_cycle.status}]"
                )
                cycles_found += 1

            cycle_num_str = match.group(1)
            title = match.group(2).strip()

            status = "PLANNED"
            if "Completed" in line or cycle_num_str.startswith("0"):
                status = "COMPLETED"

            try:
                cycle_num = int(float(cycle_num_str))
            except Exception:
                cycle_num = 0

            current_cycle = RoadmapItem(
                id=uid(),
                cycle=cycle_num,
                title=title,
                status=status,
                goals=[],
                governed_by_adr=None,
            )

        elif current_cycle and line.startswith("- ["):
            goal_text = re.sub(r"- \[[x ]\]\s+", "", line)
            goal_text = goal_text.replace("**", "")
            current_cycle.goals.append(goal_text)

    if current_cycle:
        kb.add_roadmap_item(current_cycle)
        click.echo(
            f"   ✅ Loaded Cycle {current_cycle.cycle}: {current_cycle.title} [{current_cycle.status}]"
        )
        cycles_found += 1

    if cycles_found == 0:
        click.echo(
            "[yellow]⚠️ No cycles found in roadmap.md. Check formatting.[/yellow]"
        )
    else:
        click.echo(
            f"[green]🎉 Successfully synced {cycles_found} cycles to Knowledge Base.[/green]"
        )


@roadmap.command(name="list")
def list_roadmap():
    """Lists all roadmap cycles and their status."""
    kb = PersistentKnowledgeBase()
    click.echo("\n🗺️  ICGL Sovereign Roadmap\n")

    if not kb.roadmap_items:
        click.echo(
            "   (No governed roadmap items found. Use `icgl roadmap load` to import.)"
        )
        return

    sorted_items = sorted(kb.roadmap_items, key=lambda x: x.cycle)

    for item in sorted_items:
        status_color = "white"
        if item.status == "COMPLETED":
            status_color = "green"
        elif item.status == "ACTIVE":
            status_color = "yellow"
        elif item.status == "BLOCKED":
            status_color = "red"

        goals_summary = ", ".join(item.goals[:2]) + (
            "..." if len(item.goals) > 2 else ""
        )
        click.echo(f"   Cycle {item.cycle}: {item.title}")
        click.echo(
            f"   [{click.style(item.status, fg=status_color)}] - {goals_summary}\n"
        )
