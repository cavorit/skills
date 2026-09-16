from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from dc_pair.cli import AgentConfig, _claude_skill_dirs, _opencode_skill_dirs
from dc_pair.cli import main as cli_main

_runner = CliRunner()

TEST_URL = "https://datacards.dev/cavorit/test123/"


class TestGroup:
    def test_help(self) -> None:
        result = _runner.invoke(cli_main, ["--help"])
        assert result.exit_code == 0
        assert "datacards" in result.output.lower()
        assert "prompt" in result.output

    def test_prompt_help(self) -> None:
        result = _runner.invoke(cli_main, ["prompt", "--help"])
        assert result.exit_code == 0
        assert "--url" in result.output
        assert "--claude" in result.output
        assert "--codex" in result.output
        assert "--opencode" in result.output
        assert "--with-token" in result.output


class TestPrompt:
    def test_prompt_requires_url(self) -> None:
        result = _runner.invoke(cli_main, ["prompt"])
        assert result.exit_code != 0

    def test_prompt_outputs_url(self) -> None:
        result = _runner.invoke(cli_main, ["prompt", "--url", TEST_URL])
        assert result.exit_code == 0
        assert TEST_URL in result.output
        assert "execute-code.sh" in result.output
        assert "/datacards-pair" in result.output
        assert "marimo-pair" not in result.output

    def test_prompt_skill_missing(self) -> None:
        with patch.object(AgentConfig, "has_skill", return_value=False):
            for flag in ("--claude", "--codex", "--opencode"):
                result = _runner.invoke(
                    cli_main, ["prompt", "--url", TEST_URL, flag]
                )
                assert result.exit_code == 0, flag
                assert "could not be found" in result.output, flag
                assert "npx skills add cavorit/skills" in result.output, flag

    def test_prompt_skill_installed(self) -> None:
        with patch.object(AgentConfig, "has_skill", return_value=True):
            for flag in ("--claude", "--codex", "--opencode"):
                result = _runner.invoke(
                    cli_main, ["prompt", "--url", TEST_URL, flag]
                )
                assert result.exit_code == 0, flag
                assert TEST_URL in result.output, flag
                assert "could not be found" not in result.output, flag


class TestPromptWithToken:
    def test_with_token_writes_file_and_outputs_prompt(
        self, tmp_path: Path
    ) -> None:
        with patch("dc_pair.cli._token_dir", return_value=tmp_path):
            result = _runner.invoke(
                cli_main,
                ["prompt", "--url", TEST_URL, "--with-token"],
                input="my-secret-token\n",
            )
        assert result.exit_code == 0
        assert TEST_URL in result.output
        assert "execute-code.sh" in result.output
        assert "token" in result.output.lower()
        assert "cat" in result.output

        url_hash = hashlib.sha256(TEST_URL.encode()).hexdigest()[:6]
        token_file = tmp_path / f"{url_hash}-token.txt"
        assert token_file.exists()
        assert token_file.read_text() == "my-secret-token"
        if sys.platform != "win32":
            assert oct(token_file.stat().st_mode & 0o777) == "0o600"

    def test_with_token_still_requires_url(self) -> None:
        result = _runner.invoke(
            cli_main, ["prompt", "--with-token"], input="tok\n"
        )
        assert result.exit_code != 0

    def test_with_token_and_skill_missing_still_prints(self) -> None:
        with patch.object(AgentConfig, "has_skill", return_value=False):
            result = _runner.invoke(
                cli_main,
                ["prompt", "--url", TEST_URL, "--claude", "--with-token"],
                input="secret\n",
            )
        assert result.exit_code == 0
        assert "could not be found" in result.output
        assert TEST_URL in result.output

    def test_without_token_no_token_hint(self) -> None:
        result = _runner.invoke(cli_main, ["prompt", "--url", TEST_URL])
        assert result.exit_code == 0
        assert "cat" not in result.output


class TestSkillDirs:
    def test_opencode_skill_dirs(self) -> None:
        cwd = Path.cwd()
        home = Path.home()
        assert _opencode_skill_dirs() == [
            cwd / ".opencode" / "skills",
            home / ".config" / "opencode" / "skills",
            cwd / ".claude" / "skills",
            home / ".claude" / "skills",
            cwd / ".agents" / "skills",
            home / ".agents" / "skills",
        ]

    def test_claude_skill_dirs_include_plugin_layouts(self) -> None:
        dirs = _claude_skill_dirs()
        home = Path.home() / ".claude"
        assert home / "skills" in dirs
        assert home / "plugins" / "marketplaces" in dirs
        assert home / "plugins" / "cache" in dirs


class TestAgentConfig:
    def _write_skill(self, path: Path) -> None:
        path.mkdir(parents=True)
        (path / "SKILL.md").write_text("test")

    def test_has_skill_flat_layout(self, tmp_path: Path) -> None:
        skill_dir = tmp_path / "skills"
        self._write_skill(skill_dir / "datacards-pair")
        agent = AgentConfig(name="test", skill_dirs=[skill_dir])
        assert agent.has_skill() is True

    def test_has_skill_marketplace_layout(self, tmp_path: Path) -> None:
        marketplaces = tmp_path / "plugins" / "marketplaces"
        self._write_skill(
            marketplaces / "datacards-skills" / "skills" / "datacards-pair"
        )
        agent = AgentConfig(name="test", skill_dirs=[marketplaces])
        assert agent.has_skill() is True

    def test_has_skill_plugin_cache_layout(self, tmp_path: Path) -> None:
        cache = tmp_path / "plugins" / "cache"
        self._write_skill(
            cache
            / "datacards-skills"
            / "datacards-pair"
            / "0.0.19"
            / "skills"
            / "datacards-pair"
        )
        agent = AgentConfig(name="test", skill_dirs=[cache])
        assert agent.has_skill() is True

    def test_has_skill_ignores_other_skills(self, tmp_path: Path) -> None:
        skill_dir = tmp_path / "skills"
        self._write_skill(skill_dir / "marimo-pair")
        agent = AgentConfig(name="test", skill_dirs=[skill_dir])
        assert agent.has_skill() is False

    def test_has_skill_false(self, tmp_path: Path) -> None:
        agent = AgentConfig(name="test", skill_dirs=[tmp_path / "nonexistent"])
        assert agent.has_skill() is False

    def test_has_skill_empty_dirs(self) -> None:
        agent = AgentConfig(name="test", skill_dirs=[])
        assert agent.has_skill() is False

    def test_has_skill_multiple_dirs_second_match(self, tmp_path: Path) -> None:
        dir1 = tmp_path / "a" / "skills"
        dir2 = tmp_path / "b" / "skills"
        self._write_skill(dir2 / "datacards-pair")
        agent = AgentConfig(name="test", skill_dirs=[dir1, dir2])
        assert agent.has_skill() is True
