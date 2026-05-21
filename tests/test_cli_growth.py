from __future__ import annotations

import json

from genus_egg.cli import main
from genus_egg.development.development_boundary import GROWTH_SIMULATION_STATEMENT
from genus_egg.truth.sqlite_store import SQLiteStore


def _draft_need(db_path, capsys) -> str:
    assert main(["--db", str(db_path), "needs", "draft-memory-indexing"]) == 0
    output = capsys.readouterr().out
    return next(
        line.removeprefix("Need: ").strip()
        for line in output.splitlines()
        if line.startswith("Need: ")
    )


def test_growth_simulation_creates_draft_proposals_with_explanation(tmp_path, capsys):
    db_path = tmp_path / "genus.sqlite"
    need_id = _draft_need(db_path, capsys)

    assert (
        main(
            [
                "--db",
                str(db_path),
                "growth",
                "simulate-memory-indexing",
                "--need",
                need_id,
            ]
        )
        == 0
    )

    output = capsys.readouterr().out
    assert GROWTH_SIMULATION_STATEMENT in output
    assert "Proposal: " in output
    assert "CodeProposal: " in output
    assert (
        "Rationale: Repeated memory creation and retrieval would benefit from "
        "indexed lookup."
    ) in output
    assert "Testplan:" in output
    assert "- Add tests for index_memory ReactionSpec registration." in output
    assert "Patch: none" in output
    assert "Git: none" in output
    assert "Activation: blocked" in output

    store = SQLiteStore(db_path)
    code_proposals = store.list_code_change_proposals()
    assert len(store.list_capability_proposals()) == 1
    assert len(code_proposals) == 1
    payload = json.loads(code_proposals[0].payload_json or "{}")
    assert payload["activation"] == "blocked"
    assert payload["can_modify_files"] is False
    assert payload["can_activate"] is False
    assert payload["test_plan"] == [
        "Add tests for index_memory ReactionSpec registration.",
        "Add tests that MemoryIndexEntry records are created from MemoryObject.",
        "Add retrieval tests proving indexed lookup improves memory search.",
    ]
    store.close()


def test_growth_simulation_requires_need_argument(tmp_path, capsys):
    db_path = tmp_path / "genus.sqlite"

    assert main(["--db", str(db_path), "growth", "simulate-memory-indexing"]) == 2

    assert "Missing required --need NEED_ID" in capsys.readouterr().out


def test_growth_simulation_blocks_unknown_need(tmp_path, capsys):
    db_path = tmp_path / "genus.sqlite"

    assert (
        main(
            [
                "--db",
                str(db_path),
                "growth",
                "simulate-memory-indexing",
                "--need",
                "need_missing",
            ]
        )
        == 1
    )

    assert "CapabilityNeed not found: need_missing" in capsys.readouterr().out
