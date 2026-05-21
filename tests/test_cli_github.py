from __future__ import annotations

import json
import subprocess

from genus_egg.cli import main
from genus_egg.habitat.habitat_manifest import HabitatManifest
from genus_egg.ids import new_id
from genus_egg.time import utc_now
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
    assert (
        main(["--db", str(db_path), "patch", "approve", "--code-proposal", code_proposal_id])
        == 0
    )
    capsys.readouterr()
    assert (
        main(["--db", str(db_path), "patch", "draft", "--code-proposal", code_proposal_id])
        == 0
    )
    patch_output = capsys.readouterr().out
    return next(
        line.removeprefix("SandboxPatch drafted: ").strip()
        for line in patch_output.splitlines()
        if line.startswith("SandboxPatch drafted: ")
    )


def _allow_github(db_path) -> None:
    store = SQLiteStore(db_path)
    store.save_habitat_manifest(
        HabitatManifest(
            habitat_id=new_id("habitat"),
            device_id="device",
            hostname="host",
            os_name="test-os",
            python_version="3.12",
            repo_path=".",
            data_path="./data",
            sqlite_path=str(db_path),
            network_allowed=False,
            git_available=True,
            github_allowed=True,
            model_access="local_stub",
            payload_json=json.dumps({"user_approval_required": True}),
            created_at=utc_now(),
        )
    )
    store.close()


def _init_git_repo(path) -> None:
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True)


def test_cli_github_draft_pr_blocks_missing_patch(tmp_path, capsys):
    db_path = tmp_path / "genus.sqlite"

    assert main(["--db", str(db_path), "github", "draft-pr"]) == 2

    assert "Missing required --patch PATCH_ID" in capsys.readouterr().out


def test_cli_github_draft_pr_blocks_when_github_not_allowed(tmp_path, capsys):
    db_path = tmp_path / "genus.sqlite"
    patch_id = _draft_patch(db_path, capsys)

    assert main(["--db", str(db_path), "github", "draft-pr", "--patch", patch_id]) == 1

    assert "github_allowed=false" in capsys.readouterr().out


def test_cli_github_draft_pr_records_draft_only_boundary(tmp_path, capsys):
    db_path = tmp_path / "genus.sqlite"
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    _init_git_repo(repo_path)
    patch_id = _draft_patch(db_path, capsys)
    _allow_github(db_path)
    assert main(["--db", str(db_path), "tests", "run", "--patch", patch_id]) == 0
    capsys.readouterr()
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
    capsys.readouterr()

    assert (
        main(
            [
                "--db",
                str(db_path),
                "github",
                "draft-pr",
                "--patch",
                patch_id,
                "--repository",
                "WoltLab51/GENUS_EGG",
            ]
        )
        == 0
    )

    output = capsys.readouterr().out
    assert "GitHubDraftPR: " in output
    assert "Draft: true" in output
    assert "Push: none" in output
    assert "Merge: none" in output
    assert "Activation: blocked" in output
    store = SQLiteStore(db_path)
    assert len(store.list_github_draft_prs()) == 1
    store.close()
