"""Each subcommand through main([...]): exit code, stdout and stderr checked separately."""

from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest
from conftest import read_json

from skills_repo import cli, config


def run(capsys: pytest.CaptureFixture[str], *argv: str) -> tuple[int, str, str]:
    code = cli.main(list(argv))
    out, err = capsys.readouterr()
    return code, out, err


@pytest.mark.parametrize("name", cli.COMMANDS)
def test_every_command_resolves(name: str) -> None:
    module_name, _, func_name = cli.COMMANDS[name][0].partition(":")
    assert callable(getattr(importlib.import_module(module_name), func_name))


@pytest.mark.parametrize("name", cli.COMMANDS)
def test_every_command_has_help(name: str, capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main([name, "--help"])
    assert exc.value.code == 0
    assert f"repo {name}" in capsys.readouterr().out


def test_version(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["--version"])
    assert exc.value.code == 0
    assert capsys.readouterr().out.strip() == "0.1.0"


def test_check_clean_repo(repo_root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code, out, err = run(capsys, "check", "--root", str(repo_root))
    assert code == 0 and out.startswith("ok ") and err == ""


def test_check_reports_problems_on_stdout(
    repo_root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (repo_root / config.README).write_text("stale\n", encoding="utf-8")
    code, out, err = run(capsys, "check", "--root", str(repo_root))
    assert code == 1 and "README.md: DOC001" in out and "1 problem(s)" in out and err == ""


def test_check_json(repo_root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code, out, err = run(capsys, "check", "--root", str(repo_root), "--json")
    payload = json.loads(out)
    assert code == 0 and payload["ok"] is True and payload["skills"] == 1 and err == ""


def test_check_select_and_paths(repo_root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    long = repo_root / "skills/alpha/skills/alpha/references/long.md"
    long.parent.mkdir(parents=True)
    long.write_text("# Long\n" + "text\n" * 120, encoding="utf-8")
    code, out, _ = run(
        capsys, "check", "--root", str(repo_root), "--select", "REF", "--paths", str(long)
    )
    assert code == 1 and "REF001" in out
    other = repo_root / "skills/alpha/skills/alpha/SKILL.md"
    code, out, _ = run(
        capsys, "check", "--root", str(repo_root), "--select", "REF", "--paths", str(other)
    )
    assert code == 0


def test_check_unknown_rule(repo_root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code, out, err = run(capsys, "check", "--root", str(repo_root), "--select", "XYZ")
    assert code == 1 and out == "" and err.startswith("error: no rule matches")


def test_check_unknown_flag_exits_2(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        cli.main(["check", "--bogus"])
    assert exc.value.code == 2
    out, err = capsys.readouterr()
    assert out == "" and "--bogus" in err


def test_no_repo_is_a_one_line_error(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code, out, err = run(capsys, "check", "--root", str(tmp_path))
    assert code == 1 and out == "" and err.startswith("error:") and err.count("\n") == 1


def test_rules_lists_every_rule(capsys: pytest.CaptureFixture[str]) -> None:
    code, out, err = run(capsys, "rules", "--json")
    ids = {r["id"] for r in json.loads(out)}
    assert code == 0 and {"SKL001", "REG003", "MAN001", "DSC001"} <= ids and err == ""


def test_new_then_readme_then_check(repo_root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = str(repo_root)
    code, out, err = run(capsys, "new", "beta", "--root", root, "--category", "skills",
                         "--description", "Beta plugin. Use when testing.")  # fmt: skip
    assert code == 0 and out.startswith("ok created skills/beta/") and err == ""
    assert (
        read_json(repo_root / "skills/beta/.claude-plugin/plugin.json")["description"]
        == "Beta plugin"
    )
    assert run(capsys, "readme", "--root", root, "--check")[0] == 1
    assert run(capsys, "readme", "--root", root)[0] == 0
    assert run(capsys, "check", "--root", root)[0] == 0


def test_new_refuses_existing_name(repo_root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code, out, err = run(capsys, "new", "alpha", "--root", str(repo_root), "--category", "skills",
                         "--description", "x")  # fmt: skip
    assert code == 1 and out == "" and "already exists" in err
    assert len(read_json(repo_root / config.MARKETPLACE)["plugins"]) == 1


def test_new_copies_skill_from_file(
    repo_root: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    source = tmp_path / "SKILL.md"
    source.write_text(
        "---\nname: gamma\ndescription: Gamma. Use when testing.\n---\n\nBody\n", encoding="utf-8"
    )
    code, _, err = run(capsys, "new", "gamma", "--root", str(repo_root), "--category", "agents",
                       "--description", "Gamma. Use when testing.", "--from", str(source))  # fmt: skip
    assert code == 0 and err == ""
    assert (
        (repo_root / "skills/gamma/skills/gamma/SKILL.md")
        .read_text(encoding="utf-8")
        .endswith("Body\n")
    )


def test_sync_needs_both_skills(repo_root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code, out, err = run(capsys, "sync", "--root", str(repo_root), "--check")
    assert code == 1 and out == "" and err.startswith("error: shared rules need")
