from __future__ import annotations

from genus_egg.cli import main
from genus_egg.truth.sqlite_store import SQLiteStore


def test_cli_habitat_readiness_creates_snapshot_and_report(tmp_path, capsys):
    db_path = tmp_path / "genus.sqlite"

    assert main(["--db", str(db_path), "habitat", "readiness"]) == 0

    output = capsys.readouterr().out
    assert "habitat_id: " in output
    assert "snapshot_id: " in output
    assert "readiness: " in output
    assert "reason: " in output
    assert "cpu_count: " in output
    assert "memory_total_mb: " in output
    assert "disk_free_mb: " in output
    assert "Activation: blocked" in output

    store = SQLiteStore(db_path)
    assert store.get_latest_habitat_manifest() is not None
    assert len(store.list_resource_snapshots()) == 1
    assert len(store.list_habitat_readiness_reports()) == 1
    store.close()
