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


def test_cli_shadow_plan_creates_shadow_test_plan(tmp_path, capsys):
    db_path = tmp_path / "genus.sqlite"
    code_proposal_id = _draft_code_proposal(db_path, capsys)

    assert (
        main(
            [
                "--db",
                str(db_path),
                "shadow",
                "plan",
                "--code-proposal",
                code_proposal_id,
            ]
        )
        == 0
    )

    output = capsys.readouterr().out
    assert "ShadowTestPlan created: " in output
    assert f"CodeProposal: {code_proposal_id}" in output
    assert "Status: draft" in output
    assert "Patch: none" in output
    assert "Git: none" in output
    assert "Activation: blocked" in output

    store = SQLiteStore(db_path)
    assert len(store.list_shadow_test_plans()) == 1
    store.close()


def test_cli_fitness_evaluate_stores_and_lists_evaluation(tmp_path, capsys):
    db_path = tmp_path / "genus.sqlite"
    code_proposal_id = _draft_code_proposal(db_path, capsys)

    assert (
        main(
            [
                "--db",
                str(db_path),
                "fitness",
                "evaluate",
                "--code-proposal",
                code_proposal_id,
            ]
        )
        == 0
    )

    output = capsys.readouterr().out
    assert "FitnessEvaluation created: " in output
    assert f"CodeProposal: {code_proposal_id}" in output
    assert "ShadowPlan: " in output
    assert "Score: " in output
    assert "Rationale: " in output
    assert "Patch: none" in output
    assert "Git: none" in output
    assert "Activation: blocked" in output

    assert main(["--db", str(db_path), "fitness", "list"]) == 0
    list_output = capsys.readouterr().out
    assert code_proposal_id in list_output
    assert "blocked" in list_output

    store = SQLiteStore(db_path)
    assert len(store.list_shadow_test_plans()) == 1
    assert len(store.list_fitness_evaluations()) == 1
    store.close()


def test_cli_shadow_and_fitness_require_code_proposal_argument(tmp_path, capsys):
    db_path = tmp_path / "genus.sqlite"

    assert main(["--db", str(db_path), "shadow", "plan"]) == 2
    assert (
        "Missing required --code-proposal CODE_PROPOSAL_ID"
        in capsys.readouterr().out
    )

    assert main(["--db", str(db_path), "fitness", "evaluate"]) == 2
    assert (
        "Missing required --code-proposal CODE_PROPOSAL_ID"
        in capsys.readouterr().out
    )


def test_cli_shadow_and_fitness_block_unknown_code_proposal(tmp_path, capsys):
    db_path = tmp_path / "genus.sqlite"

    assert (
        main(
            [
                "--db",
                str(db_path),
                "shadow",
                "plan",
                "--code-proposal",
                "codeproposal_missing",
            ]
        )
        == 1
    )
    assert (
        "CodeChangeProposal not found: codeproposal_missing"
        in capsys.readouterr().out
    )

    assert (
        main(
            [
                "--db",
                str(db_path),
                "fitness",
                "evaluate",
                "--code-proposal",
                "codeproposal_missing",
            ]
        )
        == 1
    )
    assert (
        "CodeChangeProposal not found: codeproposal_missing"
        in capsys.readouterr().out
    )
