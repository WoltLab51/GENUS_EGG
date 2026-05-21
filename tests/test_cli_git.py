from __future__ import annotations

import subprocess

from genus_egg.cli import main
from genus_egg.truth.sqlite_store import SQLiteStore


def _draft_patch(db_path, capsys) -> str:
    assert main(["--db", str(db_path), "needs", "draft-memory-indexing"]) == 0
    need_output = capsys.readouterr().out
    need_id = next(
        line.removeprefix("Need: ").strip()
        for line in need_output.splitlines()
        if line.startswith("Need: ")
    )
    assert (
        main(
            [
                "--db",
                str(db_path),
                "proposals",
                "draft-memory-indexing",
                "--need",
                need_id,
            ]
        )
        == 0
    )
    proposal_output = capsys.readouterr().out
    code_proposal_id = next(
        line.removeprefix("CodeProposal: ").strip()
        for line in proposal_output.splitlines()
        if line.startswith("CodeProposal: ")
    )
    assert main(["--db", str(db_path), "patch", "approve", "--code-proposal", code_proposal_id]) == 0
    capsys.readouterr()
    assert main(["--db", str(db_path), "patch", "draft", "--code-proposal", code_proposal_id]) == 0
    patch_output = capsys.readouterr().out
    return next(
        line.removeprefix("SandboxPatch drafted: ").strip()
        for line in patch_output.splitlines()
        if line.startswith("SandboxPatch drafted: ")
    )


def _init_git_repo(path) -> None:
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True)


def test_cli_git_status_records_read_only_report(tmp_path, capsys):
    db_path = tmp_path / "genus.sqlite"
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    _init_git_repo(repo_path)

    assert main(["--db", str(db_path), "git", "status", "--repo", str(repo_path)]) == 0

    output = capsys.readouterr().out
    assert "GitStatus: " in output
    assert "Dirty: " in output
    assert "Mode: read-only" in output
    store = SQLiteStore(db_path)
    assert len(store.list_git_status_reports()) == 1
    store.close()


def test_cli_git_prepare_branch_records_preparation(tmp_path, capsys):
    db_path = tmp_path / "genus.sqlite"
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    _init_git_repo(repo_path)
    patch_id = _draft_patch(db_path, capsys)

    assert (
        main(
            [
                "--db",
                str(db_path),
                "git",
                "prepare-branch",
                "--repo",
                str(repo_path),
                "--patch",
                patch_id,
            ]
        )
        == 0
    )

    output = capsys.readouterr().out
    assert "GitBranchPreparation: " in output
    assert "Branch: genus/sandbox-" in output
    assert "Push: none" in output
    assert "Merge: none" in output
    assert "Activation: blocked" in output
    store = SQLiteStore(db_path)
    assert len(store.list_git_branch_preparations()) == 1
    store.close()


def test_cli_git_prepare_branch_requires_patch(tmp_path, capsys):
    db_path = tmp_path / "genus.sqlite"

    assert main(["--db", str(db_path), "git", "prepare-branch"]) == 2

    assert "Missing required --patch PATCH_ID" in capsys.readouterr().out
