from __future__ import annotations

from genus_egg.cli import main
from genus_egg.truth.sqlite_store import SQLiteStore


def test_cli_habitat_creates_and_prints_manifest(tmp_path, capsys):
    db_path = tmp_path / "habitat.sqlite"

    exit_code = main(["--db", str(db_path), "habitat"])

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "os_name:" in output
    assert "repo_path:" in output
    assert f"sqlite_path: {db_path}" in output
    assert "git_available:" in output
    assert "network_allowed: false" in output

    store = SQLiteStore(db_path)
    assert store.get_latest_habitat_manifest() is not None
    store.close()


def test_cli_habitat_accepts_command_local_db_argument(tmp_path, capsys):
    db_path = tmp_path / "local-arg.sqlite"

    exit_code = main(["habitat", "--db", str(db_path)])

    assert exit_code == 0
    assert f"sqlite_path: {db_path}" in capsys.readouterr().out
