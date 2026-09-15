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
    "--package", "package_name", required=True, help="Snake-case import name."
)
@click.option(
    "--force",
    is_flag=True,
    help="Overwrite an existing src/ / experiments / pyproject layout.",
)
def scaffold_cmd(package_name: str, force: bool) -> None:
    """Copy the organize-ml-workspace templates into the current directory."""
    from skore_skills.scaffold import scaffold

    try:
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
def style_cmd(paths: tuple[Path, ...]) -> None:
    """Run ruff check --fix then format on defaults or PATHS.

    Default globs: ``src/``, ``experiments/``, ``audit/``, ``data/eda.py``,
    top-level ``*.py``. Does not write ``ruff.toml``.
    """
    from skore_skills.style import run_style

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
