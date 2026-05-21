from __future__ import annotations

from genus_egg.cli import main
from genus_egg.truth.sqlite_store import SQLiteStore


def test_cli_proposals_drafts_memory_indexing_proposal(tmp_path, capsys):
    db_path = tmp_path / "genus.sqlite"
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

    output = capsys.readouterr().out
    assert "CapabilityProposal drafted: Add memory indexing reaction" in output
    assert "Proposal: " in output
    assert "CodeProposal: " in output
    assert "Status: draft" in output
    assert "Activation: blocked" in output

    store = SQLiteStore(db_path)
    assert len(store.list_capability_proposals()) == 1
    assert len(store.list_code_change_proposals()) == 1
    store.close()


def test_cli_proposal_requires_need(tmp_path, capsys):
    db_path = tmp_path / "genus.sqlite"

    assert (
        main(
            [
                "--db",
                str(db_path),
                "proposals",
                "draft-memory-indexing",
                "--need",
                "need_missing",
            ]
        )
        == 1
    )

    assert "CapabilityNeed not found: need_missing" in capsys.readouterr().out
