from __future__ import annotations

from genus_egg.cli import main
from genus_egg.evaluation.fitness_evaluator import FitnessEvaluator
from genus_egg.truth.sqlite_store import SQLiteStore


def _draft_ready_code_proposal(db_path, capsys) -> str:
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
    return code_proposal_id


def test_cli_activation_request_requires_code_proposal(tmp_path, capsys):
    db_path = tmp_path / "genus.sqlite"

    assert main(["--db", str(db_path), "activation", "request"]) == 2

    assert "Missing required --code-proposal CODE_PROPOSAL_ID" in capsys.readouterr().out


def test_cli_activation_request_and_reject(tmp_path, capsys):
    db_path = tmp_path / "genus.sqlite"
    code_proposal_id = _draft_ready_code_proposal(db_path, capsys)

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

    output = capsys.readouterr().out
    assert "ActivationRequest: " in output
    assert "Status: blocked" in output
    assert "Reason: rollback_data_missing" in output
    request_id = next(
        line.removeprefix("ActivationRequest: ").strip()
        for line in output.splitlines()
        if line.startswith("ActivationRequest: ")
    )

    assert (
        main(
            [
                "--db",
                str(db_path),
                "activation",
                "reject",
                "--request",
                request_id,
                "--rationale",
                "No rollback plan.",
            ]
        )
        == 0
    )

    reject_output = capsys.readouterr().out
    assert "ActivationDecision: " in reject_output
    assert "Decision: rejected" in reject_output
    assert "Activation: blocked" in reject_output
    store = SQLiteStore(db_path)
    assert len(store.list_activation_requests()) == 1
    assert len(store.list_activation_decisions()) == 1
    store.close()
