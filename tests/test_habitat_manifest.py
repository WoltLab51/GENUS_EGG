from __future__ import annotations

import json

from genus_egg.habitat.environment_probe import EnvironmentProbe
from genus_egg.habitat.permission_profile import PermissionProfile
from genus_egg.truth.sqlite_store import SQLiteStore


def test_habitat_manifest_table_exists(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")

    assert "habitat_manifest" in store.table_names()
    store.close()


def test_habitat_manifest_can_be_saved_and_loaded(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    manifest = EnvironmentProbe(tmp_path / "genus.sqlite", repo_path=tmp_path).probe()

    store.save_habitat_manifest(manifest)
    loaded = store.get_latest_habitat_manifest()

    assert loaded is not None
    assert loaded.habitat_id == manifest.habitat_id
    assert loaded.sqlite_path == str(tmp_path / "genus.sqlite")
    assert loaded.network_allowed is False
    assert loaded.github_allowed is False
    assert loaded.model_access == "local_stub"
    assert json.loads(loaded.payload_json or "{}")["forbidden_paths"] == [
        ".env",
        "secrets",
        ".git/config",
    ]
    store.close()


def test_permission_profile_blocks_forbidden_paths():
    profile = PermissionProfile()

    assert profile.blocks_path(".env")
    assert profile.blocks_path("secrets/token.txt")
    assert profile.blocks_path(".git/config")
    assert profile.blocks_path(".git/config/local")
    assert not profile.blocks_path("src/genus_egg/habitat/environment_probe.py")


def test_permission_profile_defaults_keep_network_and_github_blocked():
    profile = PermissionProfile()

    assert profile.network_allowed is False
    assert profile.github_allowed is False
