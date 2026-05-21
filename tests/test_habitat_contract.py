from __future__ import annotations

import json

from genus_egg.habitat.environment_probe import EnvironmentProbe
from genus_egg.habitat.habitat_contract import HabitatContract
from genus_egg.habitat.habitat_manifest import HabitatManifest
from genus_egg.habitat.resource_snapshot import ResourceSnapshot
from genus_egg.time import utc_now
from genus_egg.truth.sqlite_store import SQLiteStore


def test_resource_snapshot_and_readiness_tables_exist(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")

    assert {"resource_snapshots", "habitat_readiness_reports"}.issubset(
        store.table_names()
    )
    store.close()


def test_resource_snapshot_can_be_saved_and_loaded(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    manifest = EnvironmentProbe(tmp_path / "genus.sqlite").probe()
    snapshot = HabitatContract().snapshot_resources(manifest)

    store.save_resource_snapshot(snapshot)

    loaded = store.list_resource_snapshots()
    assert loaded == [snapshot]
    assert loaded[0].disk_total_mb > 0
    assert loaded[0].disk_free_mb >= 0
    assert json.loads(loaded[0].payload_json or "{}")["temperature"] == "unknown"
    store.close()


def test_readiness_report_can_be_saved_and_loaded(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    manifest = EnvironmentProbe(tmp_path / "genus.sqlite").probe()
    contract = HabitatContract()
    snapshot = contract.snapshot_resources(manifest)
    report = contract.assess(manifest, snapshot)

    store.save_resource_snapshot(snapshot)
    store.save_habitat_readiness_report(report)

    reports = store.list_habitat_readiness_reports()
    assert reports == [report]
    assert reports[0].status in {"ready", "limited", "blocked"}
    assert json.loads(reports[0].checks_json)["sqlite_path_present"] is True
    assert json.loads(reports[0].payload_json or "{}")["activation"] == "blocked"
    store.close()


def test_readiness_status_is_deterministic_for_ready_limited_and_blocked():
    contract = HabitatContract()
    manifest = _manifest(git_available=True, repo_path=".")
    snapshot = _snapshot(cpu_count=4, memory_total_mb=1024, disk_free_mb=100)

    assert contract.assess(manifest, snapshot).status == "ready"
    assert (
        contract.assess(_manifest(git_available=False, repo_path="."), snapshot).status
        == "limited"
    )
    assert (
        contract.assess(_manifest(git_available=True, repo_path=None), snapshot).status
        == "blocked"
    )


def _manifest(git_available: bool, repo_path: str | None) -> HabitatManifest:
    return HabitatManifest(
        habitat_id="habitat_test",
        device_id="local_machine",
        hostname="host",
        os_name="TestOS",
        python_version="3.12",
        repo_path=repo_path,
        data_path="data",
        sqlite_path="data/genus.sqlite",
        network_allowed=False,
        git_available=git_available,
        github_allowed=False,
        model_access="local_stub",
        payload_json=None,
        created_at=utc_now(),
    )


def _snapshot(
    cpu_count: int | None, memory_total_mb: int | None, disk_free_mb: int
) -> ResourceSnapshot:
    return ResourceSnapshot(
        snapshot_id="resources_test",
        habitat_id="habitat_test",
        cpu_count=cpu_count,
        cpu_label="test-cpu",
        memory_total_mb=memory_total_mb,
        memory_available_mb=512 if memory_total_mb else None,
        disk_total_mb=1000,
        disk_free_mb=disk_free_mb,
        temperature_celsius=None,
        payload_json=None,
        created_at=utc_now(),
    )
