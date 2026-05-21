from __future__ import annotations

from genus_egg.cli import main
from genus_egg.truth.sqlite_store import SQLiteStore


def test_cli_observations_lists_created_observation(tmp_path, capsys):
    db_path = tmp_path / "genus.sqlite"
    assert main(["--db", str(db_path), "remember", "larumipsum"]) == 0
    capsys.readouterr()

    assert main(["--db", str(db_path), "observations"]) == 0

    output = capsys.readouterr().out
    assert "reaction_chain_completed" in output


def test_cli_needs_drafts_memory_indexing_need_without_activation(tmp_path, capsys):
    db_path = tmp_path / "genus.sqlite"
    assert main(["--db", str(db_path), "remember", "larumipsum"]) == 0
    capsys.readouterr()

    assert main(["--db", str(db_path), "needs", "draft-memory-indexing"]) == 0

    output = capsys.readouterr().out
    assert "CapabilityNeed drafted:" in output
    assert "Status: draft" in output
    assert "Activation: none" in output

    store = SQLiteStore(db_path)
    needs = store.list_capability_needs()
    assert len(needs) == 1
    assert needs[0].status == "draft"
    store.close()


def test_cli_needs_detect_creates_draft_need_from_observation(tmp_path, capsys):
    db_path = tmp_path / "genus.sqlite"
    assert main(["--db", str(db_path), "remember", "larumipsum"]) == 0
    capsys.readouterr()

    assert main(["--db", str(db_path), "needs", "detect"]) == 0

    output = capsys.readouterr().out
    assert "PatternDetector detected:" in output
    assert "Need: " in output
    assert "Status: draft" in output
    assert "Activation: none" in output


def test_cli_needs_detect_reports_no_need_without_observation(tmp_path, capsys):
    db_path = tmp_path / "genus.sqlite"

    assert main(["--db", str(db_path), "needs", "detect"]) == 0

    assert "PatternDetector: no capability need detected" in capsys.readouterr().out
