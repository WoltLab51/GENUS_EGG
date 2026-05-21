from __future__ import annotations

from genus_egg.cli import main
from genus_egg.truth.sqlite_store import SQLiteStore


def _draft_code_proposal(db_path, capsys) -> str:
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
    return next(
        line.removeprefix("CodeProposal: ").strip()
        for line in proposal_output.splitlines()
        if line.startswith("CodeProposal: ")
    )


def test_cli_patch_approve_and_draft(tmp_path, capsys):
    db_path = tmp_path / "genus.sqlite"
    code_proposal_id = _draft_code_proposal(db_path, capsys)

    assert (
        main(
            [
                "--db",
                str(db_path),
                "patch",
                "approve",
                "--code-proposal",
                code_proposal_id,
            ]
        )
        == 0
    )
    approve_output = capsys.readouterr().out
    assert "PatchApproval created: " in approve_output
    assert "Status: approved" in approve_output
    assert "Activation: blocked" in approve_output

    assert (
        main(
            [
                "--db",
                str(db_path),
                "patch",
                "draft",
                "--code-proposal",
                code_proposal_id,
            ]
        )
        == 0
    )
    draft_output = capsys.readouterr().out
    assert "SandboxPatch drafted: " in draft_output
    assert "Risk: low" in draft_output
    assert "FileChanges: 2" in draft_output
    assert "Status: draft" in draft_output
    assert "Git: none" in draft_output
    assert "GitHub: none" in draft_output
    assert "Activation: blocked" in draft_output

    assert main(["--db", str(db_path), "patch", "list"]) == 0
    list_output = capsys.readouterr().out
    assert code_proposal_id in list_output
    assert "blocked" in list_output

    store = SQLiteStore(db_path)
    assert len(store.list_patch_approvals()) == 1
    assert len(store.list_sandbox_patches()) == 1
    assert len(store.list_patch_file_changes()) == 2
    store.close()


def test_cli_patch_draft_requires_approval(tmp_path, capsys):
    db_path = tmp_path / "genus.sqlite"
    code_proposal_id = _draft_code_proposal(db_path, capsys)

    assert (
        main(
            [
                "--db",
                str(db_path),
                "patch",
                "draft",
                "--code-proposal",
                code_proposal_id,
            ]
        )
        == 1
    )

    assert "PatchApproval required" in capsys.readouterr().out


def test_cli_patch_requires_code_proposal_argument(tmp_path, capsys):
    db_path = tmp_path / "genus.sqlite"

    assert main(["--db", str(db_path), "patch", "approve"]) == 2
    assert (
        "Missing required --code-proposal CODE_PROPOSAL_ID"
        in capsys.readouterr().out
    )

    assert main(["--db", str(db_path), "patch", "draft"]) == 2
    assert (
        "Missing required --code-proposal CODE_PROPOSAL_ID"
        in capsys.readouterr().out
    )
