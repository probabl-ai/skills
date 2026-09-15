"""Command-line interface for ``skore_skills``."""

from __future__ import annotations

from pathlib import Path

import click

from skore_skills import __version__
from skore_skills.api import get_symbol, package_version
from skore_skills.check import render_workspace_check
from skore_skills.status import render_status


@click.group()
@click.version_option(version=__version__, prog_name="skore-skills")
def cli() -> None:
    """Deterministic helpers for Probabl ML skills.

    Invoke as ``python -m skore_skills``.
    """


@cli.group("cells")
def cells_group() -> None:
    """Execute jupytext percent-format ``# %%`` files."""


@cells_group.command("run")
@click.argument("src", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.argument(
    "dst",
    type=click.Path(dir_okay=False, path_type=Path),
    required=False,
)
def cells_run(src: Path, dst: Path | None) -> None:
    """Stream a markdown digest of each cell to stdout.

    When ``DST`` is given, also write the digest to that path.
    """
    from skore_skills.cells import run

    run(src, dst)


@cli.group("api")
def api_group() -> None:
    """Look up public symbols in the running interpreter."""


@api_group.command("get")
@click.argument("symbol")
def api_get(symbol: str) -> None:
    """Print a signature card and cache it under ``scratch/api/``."""
    try:
        click.echo(get_symbol(symbol), nl=False)
    except ImportError as exc:
        raise click.ClickException(str(exc)) from exc
    except LookupError as exc:
        raise click.ClickException(str(exc)) from exc


@api_group.command("version")
@click.argument("package")
def api_version(package: str) -> None:
    """Print the installed version of ``PACKAGE``."""
    try:
        click.echo(package_version(package))
    except ImportError as exc:
        raise click.ClickException(str(exc)) from exc


@cli.command("status")
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["json", "text"], case_sensitive=False),
    default="json",
    show_default=True,
)
def status_cmd(fmt: str) -> None:
    """Print a read-only JSON snapshot of the current workspace."""
    click.echo(render_status(Path.cwd(), fmt.lower()), nl=False)


@cli.group("check")
def check_group() -> None:
    """Yes/no checks over workspace facts."""


@check_group.command("workspace")
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["json", "text"], case_sensitive=False),
    default="json",
    show_default=True,
)
def check_workspace(fmt: str) -> None:
    """Exit 1 if the tree is not scaffolded (no ``src/`` and no ``journal/``)."""
    text, code = render_workspace_check(Path.cwd(), fmt.lower())
    click.echo(text, nl=False)
    if code:
        raise SystemExit(code)


@cli.command("scaffold")
@click.option(
    "--package", "package_name", help="Snake-case import name for a full scaffold."
)
@click.option(
    "--journal",
    is_flag=True,
    help="Initialize JOURNAL.md instead of the full workspace.",
)
@click.option(
    "--stem",
    help="With --journal, also create journal/NN_short_name.md.",
)
@click.option(
    "--force",
    is_flag=True,
    help="Overwrite files owned by the selected scaffold mode.",
)
def scaffold_cmd(
    package_name: str | None,
    journal: bool,
    stem: str | None,
    force: bool,
) -> None:
    """Copy full-workspace or journal templates into the current directory."""
    from skore_skills.scaffold import scaffold, scaffold_journal

    if (package_name is None) == (not journal):
        raise click.UsageError("choose exactly one of --package or --journal")
    if stem is not None and not journal:
        raise click.UsageError("--stem requires --journal")

    try:
        if journal:
            written = scaffold_journal(Path.cwd(), stem=stem, force=force)
        else:
            assert package_name is not None
            written = scaffold(Path.cwd(), package_name, force=force)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    for path in written:
        click.echo(str(path))


@cli.command("style")
@click.argument(
    "paths",
    nargs=-1,
    type=click.Path(path_type=Path),
)
@click.option(
    "--init",
    "initialize",
    is_flag=True,
    help="Copy the packaged ruff.toml when it is missing.",
)
def style_cmd(paths: tuple[Path, ...], initialize: bool) -> None:
    """Run ruff check --fix then format on defaults or PATHS.

    Default globs: ``src/``, ``experiments/``, ``audit/``, ``data/eda.py``,
    top-level ``*.py``. ``--init`` without PATHS only writes ``ruff.toml``.
    """
    from skore_skills.style import initialize_style, run_style

    if initialize:
        created = initialize_style(Path.cwd())
        click.echo("wrote ruff.toml" if created else "ruff.toml already exists")
        if not paths:
            return

    def warn(message: str) -> None:
        click.echo(message, err=True)

    try:
        code = run_style(Path.cwd(), paths, warn=warn)
    except FileNotFoundError as exc:
        raise click.ClickException(str(exc)) from exc
    if code:
        raise SystemExit(code)


@cli.group("env")
def env_group() -> None:
    """Detect the env manager and print install commands."""


@env_group.command("detect")
def env_detect() -> None:
    """Print JSON evidence; exit non-zero when two managers are visible."""
    import json

    from skore_skills.env import detect

    payload = detect(Path.cwd())
    click.echo(json.dumps(payload, indent=2))
    if payload["ambiguous"]:
        raise SystemExit(1)


@env_group.command("add")
@click.argument("packages", nargs=-1, required=True)
@click.option(
    "--execute",
    is_flag=True,
    help="Run the install command instead of printing it.",
)
def env_add(packages: tuple[str, ...], execute: bool) -> None:
    """Print (or run) the manager-specific add command."""
    from skore_skills.env import add_packages

    text, code = add_packages(Path.cwd(), list(packages), execute=execute)
    click.echo(text, nl=False)
    if code:
        raise SystemExit(code)


@env_group.command("agent")
@click.option(
    "--execute",
    is_flag=True,
    help="Run the install and verification commands instead of printing them.",
)
@click.option("--project", help="Conda project name; defaults to package/root name.")
@click.option(
    "--requirements",
    type=click.Path(dir_okay=False, path_type=Path),
    help="pip-venv requirements file; defaults to requirements.txt.",
)
def env_agent(execute: bool, project: str | None, requirements: Path | None) -> None:
    """Print or install IPython, pyright, and the LSP environment."""
    from skore_skills.env import install_agent_feature

    text, code = install_agent_feature(
        Path.cwd(),
        execute=execute,
        project=project,
        requirements=requirements,
    )
    click.echo(text, nl=False)
    if code:
        raise SystemExit(code)


@env_group.command("check")
def env_check() -> None:
    """Check agent feature composition and pyright configuration."""
    from skore_skills.env import check_agent_feature

    text, code = check_agent_feature(Path.cwd())
    click.echo(text, nl=False)
    if code:
        raise SystemExit(code)


@cli.group("policy")
def policy_group() -> None:
    """Read and write the ``workspace`` section of ``.skore``."""


@policy_group.command("set")
@click.argument("key")
@click.argument("value")
def policy_set(key: str, value: str) -> None:
    """Set one dotted workspace policy key and print the section JSON."""
    import json

    from skore_skills.policy import set_policy_value

    try:
        payload = set_policy_value(Path.cwd(), key, value)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(json.dumps(payload, indent=2))


def main() -> None:
    """Run the CLI (``python -m skore_skills`` / console script)."""
    cli()
