"""Command line entry point for `dc-pair`.

Mirrors `marimo pair prompt` from the DataCards marimo fork
(`marimo/_cli/pair/commands.py`), pointed at the `datacards-pair` skill of
this repository. Run without installing anything:

    uvx --from git+https://github.com/cavorit/skills dc-pair prompt --url URL --claude
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field
from pathlib import Path

import click

SKILL_NAME = "datacards-pair"
SKILL_FILE = "SKILL.md"
SKILL_REPO = "cavorit/skills"
SKILL_URL = f"https://github.com/{SKILL_REPO}"

# Claude Code plugin installs nest the skill below a marketplace directory
# (`plugins/marketplaces/<marketplace>/skills/<skill>/SKILL.md`) or the
# plugin cache (`plugins/cache/<marketplace>/<plugin>/<version>/skills/...`).
_NESTED_SKILL_PATTERNS = (
    f"*/skills/{SKILL_NAME}/{SKILL_FILE}",
    f"*/*/*/skills/{SKILL_NAME}/{SKILL_FILE}",
)


_cached_token_dir: Path | None = None


def _token_dir() -> Path:
    import tempfile

    global _cached_token_dir
    if _cached_token_dir is None:
        _cached_token_dir = Path(tempfile.mkdtemp(prefix="datacards-pair-"))
    return _cached_token_dir


@dataclass(frozen=True)
class AgentConfig:
    name: str
    skill_dirs: list[Path] = field(default_factory=list)

    def has_skill(self) -> bool:
        for d in self.skill_dirs:
            if (d / SKILL_NAME / SKILL_FILE).exists():
                return True
            if d.is_dir() and any(
                any(d.glob(pattern)) for pattern in _NESTED_SKILL_PATTERNS
            ):
                return True
        return False


def _claude_skill_dirs() -> list[Path]:
    """Return all directories where a Claude Code skill may be installed.

    Skills can live under skills/, plugins/, plugins/marketplaces/ or
    plugins/cache/ in both the global (~/.claude) and local (.claude)
    config directories.
    """
    roots = [Path.home() / ".claude", Path.cwd() / ".claude"]
    subdirs = [
        "skills",
        "plugins",
        str(Path("plugins") / "marketplaces"),
        str(Path("plugins") / "cache"),
    ]
    return [root / sub for root in roots for sub in subdirs]


def _opencode_skill_dirs() -> list[Path]:
    """Return directories where an opencode skill (or compatible layout) may live.

    https://opencode.ai/docs/skills/
    Checked roots are the parent of `<skill-name>/SKILL.md` for:

    - Project opencode: `.opencode/skills/`
    - Global opencode: `~/.config/opencode/skills/`
    - Project Claude-compatible: `.claude/skills/`
    - Global Claude-compatible: `~/.claude/skills/`
    - Project agent-compatible: `.agents/skills/`
    - Global agent-compatible: `~/.agents/skills/`
    """
    cwd = Path.cwd()
    home = Path.home()
    return [
        cwd / ".opencode" / "skills",
        home / ".config" / "opencode" / "skills",
        cwd / ".claude" / "skills",
        home / ".claude" / "skills",
        cwd / ".agents" / "skills",
        home / ".agents" / "skills",
    ]


def pair_agents() -> dict[str, AgentConfig]:
    """Return agent configs; paths use `Path.cwd()` at call time."""
    cwd = Path.cwd()
    home = Path.home()
    return {
        "claude": AgentConfig(
            name="Claude Code",
            skill_dirs=_claude_skill_dirs(),
        ),
        "codex": AgentConfig(
            name="Codex",
            skill_dirs=[
                home / ".codex" / "skills",
                cwd / ".codex" / "skills",
            ],
        ),
        "opencode": AgentConfig(
            name="opencode",
            skill_dirs=_opencode_skill_dirs(),
        ),
    }


@click.group(help="Commands for pairing a coding agent with a DataCards project.")
def main() -> None:
    pass


@click.command(
    help="Generate a prompt for pair programming on a running DataCards project."
)
@click.option(
    "--url",
    required=True,
    type=str,
    help="URL of the DataCards project (or of a running marimo notebook).",
)
@click.option(
    "--claude",
    is_flag=True,
    default=False,
    help="Validate that the datacards-pair Claude Code skill is installed.",
)
@click.option(
    "--codex",
    is_flag=True,
    default=False,
    help="Validate that the datacards-pair Codex skill is installed.",
)
@click.option(
    "--opencode",
    is_flag=True,
    default=False,
    help="Validate that the datacards-pair opencode skill is installed.",
)
@click.option(
    "--with-token",
    is_flag=True,
    default=False,
    help="Prompt for a project token and store it in a temp file.",
)
def prompt(
    url: str,
    claude: bool,
    codex: bool,
    opencode: bool,
    with_token: bool,
) -> None:
    """
    Generate a prompt for pair programming.

    Example usage:

        claude "$(uvx --from git+https://github.com/cavorit/skills dc-pair prompt --url 'https://datacards.dev/team/project/' --claude)"
        codex "$(uvx --from git+https://github.com/cavorit/skills dc-pair prompt --url 'https://datacards.dev/team/project/' --codex)"
        opencode "$(uvx --from git+https://github.com/cavorit/skills dc-pair prompt --url 'https://datacards.dev/team/project/' --opencode)"

        # With a project token
        claude "$(uvx --from git+https://github.com/cavorit/skills dc-pair prompt --url 'https://datacards.dev/team/project/' --claude --with-token)"
    """
    # Validate that the selected agents have the required skills
    selected_agents = {
        "claude": claude,
        "codex": codex,
        "opencode": opencode,
    }
    for key, agent in pair_agents().items():
        if not selected_agents[key]:
            continue
        if not agent.has_skill():
            click.echo(
                f"The {SKILL_NAME} skill for {agent.name} could not be found.\n\n"
                "Please install it with:\n\n"
                f"  npx skills add {SKILL_REPO}\n\n"
                "or\n\n"
                f"  uvx deno -A npm:skills add {SKILL_REPO}\n\n"
                f"More instructions at {SKILL_URL}",
                err=True,
            )

    # Prompt for token and write it to a temp file if --with-token is set
    token_hint = ""
    if with_token:
        token_dir = _token_dir()
        url_hash = hashlib.sha256(url.encode()).hexdigest()[:6]
        token_file = token_dir / f"{url_hash}-token.txt"
        token = click.prompt("Project token", hide_input=True, err=True)
        token_dir.mkdir(parents=True, exist_ok=True)
        # Open the token file for writing, creating it with restrictive
        # permissions if needed and truncating it if it already exists.
        flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
        fd = os.open(token_file, flags, 0o600)
        try:
            os.write(fd, token.encode())
        finally:
            os.close(fd)

        token_hint = (
            f"\n\nA project token is stored at {token_file}. "
            f"Pass it via `execute-code.sh --url '{url}' "
            f"--token \"$(cat '{token_file}')\"`."
        )

    # Output the prompt to the wrapper agent CLI
    click.echo(
        f"Use the /{SKILL_NAME} skill to pair-program on a running "
        "DataCards project.\n\n"
        f"Connect to the project at: {url}\n\n"
        f"Use `execute-code.sh --url {url}` from the {SKILL_NAME} "
        "skill to execute code in the project's notebooks."
        f"{token_hint}\n\n"
        "Once you are connected, send a fun toast (dc.status.toast(...)) to the user inside DataCards letting them know you're ready to pair."
    )


main.add_command(prompt)
