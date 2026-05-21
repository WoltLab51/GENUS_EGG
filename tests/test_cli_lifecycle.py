from __future__ import annotations

from genus_egg.cli import main
from genus_egg.evaluation.fitness_evaluator import FitnessEvaluator
from genus_egg.truth.sqlite_store import SQLiteStore


def _ready_code_proposal(db_path, capsys) -> str:
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


def test_cli_rollback_monitor_activation_and_fossilize(tmp_path, capsys):
    db_path = tmp_path / "genus.sqlite"
    code_proposal_id = _ready_code_proposal(db_path, capsys)

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
    rollback_output = capsys.readouterr().out
    assert "RollbackPlan: " in rollback_output

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
    activation_output = capsys.readouterr().out
    assert "Status: review_required" in activation_output
    request_id = next(
        line.removeprefix("ActivationRequest: ").strip()
        for line in activation_output.splitlines()
        if line.startswith("ActivationRequest: ")
    )

    assert main(["--db", str(db_path), "monitor", "activation", "--request", request_id]) == 0
    activation_record_output = capsys.readouterr().out
    assert "CapabilityActivation: " in activation_record_output
    activation_id = next(
        line.removeprefix("CapabilityActivation: ").strip()
        for line in activation_record_output.splitlines()
        if line.startswith("CapabilityActivation: ")
    )

    assert (
        main(
            [
                "--db",
                str(db_path),
                "monitor",
                "capability",
                "--code-proposal",
                code_proposal_id,
            ]
        )
        == 0
    )
    assert "CapabilityMonitor: " in capsys.readouterr().out

    assert (
        main(
            [
                "--db",
                str(db_path),
                "fossilize",
                "record",
                "--source-kind",
                "capability_activation",
                "--source-id",
                activation_id,
            ]
        )
        == 0
    )
    assert "FossilRecord: " in capsys.readouterr().out
    store = SQLiteStore(db_path)
    assert len(store.list_rollback_plans()) == 1
    assert len(store.list_capability_activations()) == 1
    assert len(store.list_capability_monitors()) == 1
    assert len(store.list_fossil_records()) == 1
    store.close()
