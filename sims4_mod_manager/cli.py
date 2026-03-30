"""Rich TUI CLI for Sims 4 Mod Manager."""
from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn

from sims4_mod_manager.manager import ModScanner, ModManager, format_size, find_mods_folder
from sims4_mod_manager.conflicts import ConflictDetector

console = Console()

VERSION = "0.1.0"


def show_welcome(mods_path: Optional[Path] = None) -> None:
    """Display the branded ASCII welcome screen."""
    art = Text.from_markup(
        "[bold green]"
        "\n"
        "       [bold white]/\\[/bold white]\n"
        "      [bold white]/  \\[/bold white]\n"
        "     [bold white]/    \\[/bold white]\n"
        "    [bold white]/  [bold green]<>[/bold green]  \\[/bold white]\n"
        "   [bold white]/        \\[/bold white]\n"
        "  [bold white]/____||____\\[/bold white]\n"
        "[/bold green]"
    )

    welcome = Panel(
        art,
        title="[bold green]STARK LABS MOD MANAGER[/bold green]",
        subtitle=f"[dim]The Sims 4 -- Better, One Mod at a Time[/dim]",
        border_style="green",
        padding=(1, 4),
        width=50,
    )
    console.print(welcome)
    console.print(f"  [dim]Version[/dim]  [bold]{VERSION}[/bold]")
    if mods_path:
        console.print(f"  [dim]Mods[/dim]     [bold]{mods_path}[/bold]")
    else:
        detected = find_mods_folder()
        if detected:
            console.print(f"  [dim]Mods[/dim]     [bold]{detected}[/bold]")
        else:
            console.print("  [dim]Mods[/dim]     [yellow]Not detected[/yellow]")
    console.print()


# Legacy banner kept for backwards compatibility
BANNER = r"""[bold magenta]
 ____  _                _  _    __  __           _
/ ___|(_)_ __ ___  ___ | || |  |  \/  | ___   __| |
\___ \| | '_ ` _ \/ __|| || |_ | |\/| |/ _ \ / _` |
 ___) | | | | | | \__ \|__   _|| |  | | (_) | (_| |
|____/|_|_| |_| |_|___/   |_|  |_|  |_|\___/ \__,_|
                                    [dim]Manager v0.1.0[/dim]
[/bold magenta]"""


def resolve_mods_path(mods_dir: Optional[str]) -> Path:
    """Resolve the mods directory path."""
    if mods_dir:
        path = Path(mods_dir).expanduser()
    else:
        path = find_mods_folder()
        if path is None:
            console.print(
                "[red]Could not auto-detect Sims 4 Mods folder.[/red]\n"
                "Use --mods-dir to specify the path."
            )
            sys.exit(1)
    if not path.exists():
        console.print(f"[red]Mods folder not found:[/red] {path}")
        sys.exit(1)
    return path


@click.group(invoke_without_command=True)
@click.option("--mods-dir", type=str, default=None, help="Path to Sims 4 Mods folder")
@click.pass_context
def cli(ctx: click.Context, mods_dir: Optional[str]) -> None:
    """Sims 4 Mod Manager - manage your mods from the command line."""
    ctx.ensure_object(dict)
    ctx.obj["mods_dir"] = mods_dir
    if ctx.invoked_subcommand is None:
        mods_path = Path(mods_dir).expanduser() if mods_dir else None
        show_welcome(mods_path)
        console.print("[bold]Commands:[/bold]")
        console.print("  [green]scan[/green]       Scan mods folder and display all installed mods")
        console.print("  [green]list[/green]       List mods with filtering and sorting")
        console.print("  [green]status[/green]     Quick status overview")
        console.print("  [green]install[/green]    Install mods from a .zip file")
        console.print("  [green]enable[/green]     Enable a previously disabled mod")
        console.print("  [green]disable[/green]    Disable a mod")
        console.print("  [green]info[/green]       Show detailed info about a specific mod")
        console.print("  [green]conflicts[/green]  Scan for conflicts between mods")
        console.print()
        console.print("[dim]Run[/dim] [bold]s4mm <command> --help[/bold] [dim]for details.[/dim]")


@cli.command()
@click.pass_context
def scan(ctx: click.Context) -> None:
    """Scan the Mods folder and display all installed mods."""
    mods_path = resolve_mods_path(ctx.obj["mods_dir"])
    show_welcome(mods_path)
    console.print(f"[dim]Scanning:[/dim] {mods_path}\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("Scanning mods folder...", total=None)
        scanner = ModScanner(mods_path)
        mods = scanner.scan()
        disabled = scanner.scan_disabled()

    if not mods and not disabled:
        console.print("[yellow]No mods found.[/yellow]")
        return

    # Active mods table
    if mods:
        table = Table(
            title=f"[bold green]Active Mods ({len(mods)})[/bold green]",
            show_lines=False,
            border_style="bright_black",
            header_style="bold cyan",
        )
        table.add_column("Name", style="white", max_width=45)
        table.add_column("Type", style="yellow", width=10)
        table.add_column("Size", style="green", justify="right", width=10)
        table.add_column("Resources", justify="right", width=10)
        table.add_column("Modified", style="dim", width=12)

        for mod in sorted(mods, key=lambda m: m.name.lower()):
            type_badge = "[yellow].package[/yellow]" if mod.mod_type == "package" else "[cyan].ts4script[/cyan]"
            resources = str(mod.entry_count) if mod.entry_count > 0 else "-"
            modified = mod.modified.strftime("%Y-%m-%d")
            name = mod.name
            if mod.error:
                name = f"[red]{mod.name}[/red] [dim](parse error)[/dim]"
            table.add_row(name, type_badge, format_size(mod.size), resources, modified)

        console.print(table)

    # Disabled mods table
    if disabled:
        console.print()
        table = Table(
            title=f"[bold red]Disabled Mods ({len(disabled)})[/bold red]",
            show_lines=False,
            border_style="bright_black",
            header_style="bold red",
        )
        table.add_column("Name", style="dim", max_width=45)
        table.add_column("Type", style="dim yellow", width=10)
        table.add_column("Size", style="dim green", justify="right", width=10)

        for mod in sorted(disabled, key=lambda m: m.name.lower()):
            type_badge = ".package" if mod.mod_type == "package" else ".ts4script"
            table.add_row(mod.name, type_badge, format_size(mod.size))

        console.print(table)

    # Summary
    total_size = sum(m.size for m in mods)
    console.print(
        f"\n[bold]Summary:[/bold] {len(mods)} active, {len(disabled)} disabled, "
        f"{format_size(total_size)} total"
    )


@cli.command("list")
@click.option("--type", "mod_type", type=click.Choice(["package", "ts4script", "all"]), default="all")
@click.option("--sort", "sort_by", type=click.Choice(["name", "size", "date"]), default="name")
@click.pass_context
def list_mods(ctx: click.Context, mod_type: str, sort_by: str) -> None:
    """List installed mods with filtering and sorting."""
    mods_path = resolve_mods_path(ctx.obj["mods_dir"])
    scanner = ModScanner(mods_path)
    mods = scanner.scan()

    if mod_type != "all":
        mods = [m for m in mods if m.mod_type == mod_type]

    if sort_by == "name":
        mods.sort(key=lambda m: m.name.lower())
    elif sort_by == "size":
        mods.sort(key=lambda m: m.size, reverse=True)
    elif sort_by == "date":
        mods.sort(key=lambda m: m.modified, reverse=True)

    if not mods:
        console.print("[yellow]No mods found matching criteria.[/yellow]")
        return

    for mod in mods:
        icon = "[yellow]PKG[/yellow]" if mod.mod_type == "package" else "[cyan]SCR[/cyan]"
        console.print(f"  {icon} {mod.name}  [dim]{format_size(mod.size)}[/dim]")

    console.print(f"\n[dim]{len(mods)} mod(s)[/dim]")


@cli.command()
@click.argument("mod_name")
@click.pass_context
def disable(ctx: click.Context, mod_name: str) -> None:
    """Disable a mod by moving it to _disabled/ folder."""
    mods_path = resolve_mods_path(ctx.obj["mods_dir"])
    manager = ModManager(mods_path)

    if manager.disable(mod_name):
        console.print(f"[green]Disabled:[/green] {mod_name}")
    else:
        console.print(f"[red]Failed to disable:[/red] {mod_name}")
        console.print("[dim]Check that the mod name matches exactly (without extension).[/dim]")


@cli.command()
@click.argument("mod_name")
@click.pass_context
def enable(ctx: click.Context, mod_name: str) -> None:
    """Enable a previously disabled mod."""
    mods_path = resolve_mods_path(ctx.obj["mods_dir"])
    manager = ModManager(mods_path)

    if manager.enable(mod_name):
        console.print(f"[green]Enabled:[/green] {mod_name}")
    else:
        console.print(f"[red]Failed to enable:[/red] {mod_name}")
        console.print("[dim]Check that the mod exists in _disabled/ folder.[/dim]")


@cli.command()
@click.pass_context
def conflicts(ctx: click.Context) -> None:
    """Scan for conflicts between installed mods."""
    mods_path = resolve_mods_path(ctx.obj["mods_dir"])

    console.print(f"[dim]Scanning for conflicts in:[/dim] {mods_path}\n")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        progress.add_task("Analyzing mod resources...", total=None)
        detector = ConflictDetector(mods_path)
        report = detector.scan()

    if report.total_conflicts == 0:
        console.print(
            Panel(
                "[bold green]No conflicts detected![/bold green]\n"
                f"Scanned {report.total_mods_scanned} mods in {report.scan_time:.1f}s",
                border_style="green",
            )
        )
        return

    # Conflict summary
    summary = Text()
    summary.append(f"Found {report.total_conflicts} conflict(s) ", style="bold")
    summary.append(f"across {report.total_mods_scanned} mods ", style="dim")
    summary.append(f"({report.scan_time:.1f}s)\n\n", style="dim")
    if report.high_severity > 0:
        summary.append(f"  {report.high_severity} HIGH ", style="bold red")
        summary.append("(gameplay-affecting tuning overrides)\n", style="dim")
    if report.medium_severity > 0:
        summary.append(f"  {report.medium_severity} MEDIUM ", style="bold yellow")
        summary.append("(text/data conflicts)\n", style="dim")
    if report.low_severity > 0:
        summary.append(f"  {report.low_severity} LOW ", style="bold blue")
        summary.append("(visual/mesh conflicts)\n", style="dim")

    console.print(Panel(summary, title="[bold]Conflict Report[/bold]", border_style="red"))

    # Detail table for high severity
    high_conflicts = [c for c in report.conflicts if c.severity == "high"]
    if high_conflicts:
        table = Table(
            title="[bold red]High Severity Conflicts[/bold red]",
            show_lines=True,
            border_style="red",
            header_style="bold",
        )
        table.add_column("Resource Type", style="yellow", width=20)
        table.add_column("Instance ID", style="cyan", width=20)
        table.add_column("Conflicting Mods", style="white")

        for conflict in high_conflicts[:50]:  # Limit display
            instance_hex = f"0x{conflict.instance_id:016X}"
            mods_str = "\n".join(conflict.mods)
            table.add_row(conflict.resource_type, instance_hex, mods_str)

        console.print(table)

        if len(high_conflicts) > 50:
            console.print(f"[dim]... and {len(high_conflicts) - 50} more high severity conflicts[/dim]")

    # Summary for medium/low
    med_conflicts = [c for c in report.conflicts if c.severity == "medium"]
    low_conflicts = [c for c in report.conflicts if c.severity == "low"]

    if med_conflicts:
        table = Table(
            title=f"[bold yellow]Medium Severity ({len(med_conflicts)})[/bold yellow]",
            show_lines=False,
            border_style="yellow",
        )
        table.add_column("Resource Type", width=20)
        table.add_column("Mods", style="dim")

        for conflict in med_conflicts[:20]:
            table.add_row(conflict.resource_type, ", ".join(conflict.mods))

        console.print(table)

    if low_conflicts:
        console.print(f"\n[dim]{len(low_conflicts)} low severity conflicts (visual only) - use --verbose for details[/dim]")


@cli.command()
@click.argument("zip_path", type=click.Path(exists=True))
@click.pass_context
def install(ctx: click.Context, zip_path: str) -> None:
    """Install mods from a .zip file."""
    mods_path = resolve_mods_path(ctx.obj["mods_dir"])
    zip_file = Path(zip_path)

    if not zip_file.suffix.lower() == ".zip":
        console.print("[red]Error:[/red] Only .zip files are supported.")
        return

    manager = ModManager(mods_path)
    console.print(f"[dim]Installing from:[/dim] {zip_file.name}")

    installed = manager.install_from_zip(zip_file)

    if installed:
        console.print(f"\n[bold green]Installed {len(installed)} file(s):[/bold green]")
        for name in installed:
            console.print(f"  [green]+[/green] {name}")
    else:
        console.print("[yellow]No mod files found in the archive.[/yellow]")


@cli.command()
@click.argument("mod_name")
@click.pass_context
def info(ctx: click.Context, mod_name: str) -> None:
    """Show detailed info about a specific mod."""
    mods_path = resolve_mods_path(ctx.obj["mods_dir"])
    scanner = ModScanner(mods_path)
    mods = scanner.scan() + scanner.scan_disabled()

    matching = [m for m in mods if m.name.lower() == mod_name.lower()]
    if not matching:
        # Fuzzy match
        matching = [m for m in mods if mod_name.lower() in m.name.lower()]

    if not matching:
        console.print(f"[red]Mod not found:[/red] {mod_name}")
        return

    for mod in matching:
        status = "[green]Active[/green]" if mod.enabled else "[red]Disabled[/red]"
        type_str = "[yellow].package[/yellow]" if mod.mod_type == "package" else "[cyan].ts4script[/cyan]"

        info_text = Text()
        info_text.append(f"Name:      {mod.name}\n")
        info_text.append(f"Type:      ")
        console.print(
            Panel.fit(
                f"[bold]{mod.name}[/bold]\n\n"
                f"  Status:    {status}\n"
                f"  Type:      {type_str}\n"
                f"  Size:      {format_size(mod.size)}\n"
                f"  Modified:  {mod.modified.strftime('%Y-%m-%d %H:%M')}\n"
                f"  Resources: {mod.entry_count}\n"
                f"  Path:      [dim]{mod.path}[/dim]",
                border_style="bright_black",
            )
        )


@cli.command()
@click.pass_context
def status(ctx: click.Context) -> None:
    """Quick status overview of your mods folder."""
    mods_path = resolve_mods_path(ctx.obj["mods_dir"])
    show_welcome(mods_path)

    scanner = ModScanner(mods_path)
    mods = scanner.scan()
    disabled = scanner.scan_disabled()

    packages = [m for m in mods if m.mod_type == "package"]
    scripts = [m for m in mods if m.mod_type == "ts4script"]
    total_size = sum(m.size for m in mods)

    console.print(f"[bold]Mods Folder:[/bold] {mods_path}\n")
    console.print(f"  [green]{len(mods)}[/green] active mods ({len(packages)} packages, {len(scripts)} scripts)")
    console.print(f"  [red]{len(disabled)}[/red] disabled mods")
    console.print(f"  [blue]{format_size(total_size)}[/blue] total size")


def main() -> None:
    """Entry point."""
    cli()


if __name__ == "__main__":
    main()
