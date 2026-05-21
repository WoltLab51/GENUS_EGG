from __future__ import annotations

from genus_egg.cli import main
from genus_egg.evaluation.fitness_evaluator import FitnessEvaluator
from genus_egg.truth.sqlite_store import SQLiteStore


def _ready_request(db_path, capsys) -> str:
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
    patch_id = next(
        line.removeprefix("SandboxPatch drafted: ").strip()
        for line in patch_output.splitlines()
        if line.startswith("SandboxPatch drafted: ")
    )
    assert main(["--db", str(db_path), "tests", "run", "--patch", patch_id]) == 0
    capsys.readouterr()
    store = SQLiteStore(db_path)
    FitnessEvaluator(store).evaluate(code_proposal_id)
    store.close()
    assert (
        main(
            [
                "--db",
                str(db_path),
                "rollback",
                "plan",
                "--code-proposal",
                code_proposal_id,
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
                "activation",
                "request",
                "--code-proposal",
                code_proposal_id,
            ]
        )
        == 0
    )
    request_output = capsys.readouterr().out
    return next(
        line.removeprefix("ActivationRequest: ").strip()
        for line in request_output.splitlines()
        if line.startswith("ActivationRequest: ")
    )


def test_cli_activation_approve_requires_request(tmp_path, capsys):
    db_path = tmp_path / "genus.sqlite"

    assert main(["--db", str(db_path), "activation", "approve"]) == 2

    assert "Missing required --request REQUEST_ID" in capsys.readouterr().out


def test_cli_activation_approve_blocks_unknown_request(tmp_path, capsys):
    db_path = tmp_path / "genus.sqlite"

    assert (
        main(
            [
                "--db",
                str(db_path),
                "activation",
                "approve",
                "--request",
                "activationrequest_missing",
            ]
        )
        == 1
    )

    assert "ActivationRequest not found" in capsys.readouterr().out


def test_cli_activation_approve_backfills_and_searches(tmp_path, capsys):
    db_path = tmp_path / "genus.sqlite"
    assert main(["--db", str(db_path), "remember", "Blue Memory Seed"]) == 0
    capsys.readouterr()
    request_id = _ready_request(db_path, capsys)

    assert (
        main(["--db", str(db_path), "activation", "approve", "--request", request_id])
        == 0
    )

    approve_output = capsys.readouterr().out
    assert "Capability: index_memory" in approve_output
    assert "Activation: active" in approve_output
    assert "Backfilled: 1" in approve_output

    assert main(["--db", str(db_path), "memory", "index-status"]) == 0
    status_output = capsys.readouterr().out
    assert "Active: true" in status_output
    assert "Memories: 1" in status_output
    assert "Indexed: 1" in status_output

    assert main(["--db", str(db_path), "memory", "search", "blue"]) == 0
    search_output = capsys.readouterr().out
    assert "Blue Memory Seed" in search_output
    assert "match=blue" in search_output


def test_cli_memory_search_empty_result(tmp_path, capsys):
    db_path = tmp_path / "genus.sqlite"

    assert main(["--db", str(db_path), "memory", "search", "absent"]) == 0

    assert "No memories found" in capsys.readouterr().out
