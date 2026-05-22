from __future__ import annotations

import pytest

from genus_egg.cli import main
from genus_egg.memory.memory_indexer import MemoryIndexer
from genus_egg.truth.sqlite_store import SQLiteStore


def test_guide_memory_indexing_prepares_chain_without_activation(
    tmp_path, capsys, monkeypatch
):
    db_path = tmp_path / "genus.sqlite"
    assert main(["--db", str(db_path), "remember", "Blue Memory Seed"]) == 0
    capsys.readouterr()
    monkeypatch.setattr("builtins.input", lambda _prompt: "n")

    assert main(["--db", str(db_path), "guide", "memory-indexing"]) == 0

    output = capsys.readouterr().out
    assert "Guide: memory-indexing" in output
    assert "CapabilityNeed: " in output
    assert "CapabilityProposal: " in output
    assert "CodeProposal: " in output
    assert "ShadowTestPlan: " in output
    assert "FitnessEvaluation: " in output
    assert "PatchApproval: " in output
    assert "SandboxPatch: " in output
    assert "TestRun: " in output
    assert "EvidenceChain: " in output
    assert "RollbackPlan: " in output
    assert "ActivationRequest: " in output
    assert "Decision: skipped" in output
    assert "Activation: blocked" in output

    store = SQLiteStore(db_path)
    try:
        assert MemoryIndexer(store).is_active() is False
        assert len(store.list_memory_objects()) == 1
        assert len(store.list_memory_index_entries()) == 0
        assert len(store.list_activation_requests()) == 1
        assert len(store.list_capability_activations()) == 0
    finally:
        store.close()


def test_guide_memory_indexing_approves_and_backfills(tmp_path, capsys, monkeypatch):
    db_path = tmp_path / "genus.sqlite"
    assert main(["--db", str(db_path), "remember", "Blue Memory Seed"]) == 0
    capsys.readouterr()
    monkeypatch.setattr("builtins.input", lambda _prompt: "yes")

    assert main(["--db", str(db_path), "guide", "memory-indexing"]) == 0

    output = capsys.readouterr().out
    assert "ActivationDecision: " in output
    assert "CapabilityActivation: " in output
    assert "Capability: index_memory" in output
    assert "Activation: active" in output
    assert "Backfilled: 1" in output

    assert main(["--db", str(db_path), "memory", "index-status"]) == 0
    status_output = capsys.readouterr().out
    assert "Active: true" in status_output
    assert "Memories: 1" in status_output
    assert "Indexed: 1" in status_output

    assert main(["--db", str(db_path), "memory", "search", "blue"]) == 0
    search_output = capsys.readouterr().out
    assert "Blue Memory Seed" in search_output
    assert "match=blue" in search_output


def test_guide_memory_indexing_skips_chain_when_already_active(
    tmp_path, capsys, monkeypatch
):
    db_path = tmp_path / "genus.sqlite"
    assert main(["--db", str(db_path), "remember", "Blue Memory Seed"]) == 0
    capsys.readouterr()
    monkeypatch.setattr("builtins.input", lambda _prompt: "y")
    assert main(["--db", str(db_path), "guide", "memory-indexing"]) == 0
    capsys.readouterr()

    store = SQLiteStore(db_path)
    try:
        request_count = len(store.list_activation_requests())
        activation_count = len(store.list_capability_activations())
    finally:
        store.close()

    def fail_input(_prompt: str) -> str:
        pytest.fail("already active guide should not prompt")

    monkeypatch.setattr("builtins.input", fail_input)
    assert main(["--db", str(db_path), "guide", "memory-indexing"]) == 0

    output = capsys.readouterr().out
    assert "Guide: memory-indexing" in output
    assert "Active: true" in output
    assert "Next: genus-egg --db" in output
    store = SQLiteStore(db_path)
    try:
        assert len(store.list_activation_requests()) == request_count
        assert len(store.list_capability_activations()) == activation_count
    finally:
        store.close()


def test_remember_stays_at_seven_ledger_entries_after_guide(tmp_path, capsys):
    db_path = tmp_path / "genus.sqlite"

    assert main(["--db", str(db_path), "remember", "larumipsum"]) == 0

    output = capsys.readouterr().out
    assert "Ledger entries: 7" in output
