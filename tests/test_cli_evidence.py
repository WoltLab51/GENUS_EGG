from __future__ import annotations

from genus_egg.cli import main
from genus_egg.truth.sqlite_store import SQLiteStore


def _draft_patch(db_path, capsys) -> str:
    assert main(["--db", str(db_path), "needs", "draft-memory-indexing"]) == 0
    need_output = capsys.readouterr().out
    need_id = next(line[6:].strip() for line in need_output.splitlines() if line.startswith("Need: "))
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
    capsys.readouterr()
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
    patch_output = capsys.readouterr().out
    return next(
        line.removeprefix("SandboxPatch drafted: ").strip()
        for line in patch_output.splitlines()
        if line.startswith("SandboxPatch drafted: ")
    )


def test_cli_tests_run_and_evidence_list(tmp_path, capsys):
    db_path = tmp_path / "genus.sqlite"
    patch_id = _draft_patch(db_path, capsys)

    assert main(["--db", str(db_path), "tests", "run", "--patch", patch_id]) == 0
    output = capsys.readouterr().out
    assert "TestRun created: " in output
    assert "Result: passed" in output
    assert "Command: sandbox_patch_static_check" in output
    assert "Shell: none" in output
    assert "Activation: blocked" in output

    assert main(["--db", str(db_path), "evidence", "list"]) == 0
    evidence_output = capsys.readouterr().out
    assert "sandbox_patch_static_check" in evidence_output

    store = SQLiteStore(db_path)
    assert len(store.list_test_runs()) == 1
    assert len(store.list_test_results()) == 1
    assert len(store.list_evidence_records()) == 1
    assert len(store.list_evidence_chains()) == 1
    store.close()


def test_cli_tests_run_blocks_missing_patch_argument(tmp_path, capsys):
    db_path = tmp_path / "genus.sqlite"

    assert main(["--db", str(db_path), "tests", "run"]) == 2

    assert "Missing required --patch PATCH_ID" in capsys.readouterr().out


def test_cli_tests_run_blocks_unknown_patch(tmp_path, capsys):
    db_path = tmp_path / "genus.sqlite"

    assert (
        main(["--db", str(db_path), "tests", "run", "--patch", "sandboxpatch_missing"])
        == 1
    )

    assert "SandboxPatch not found: sandboxpatch_missing" in capsys.readouterr().out
