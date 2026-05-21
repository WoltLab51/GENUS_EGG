from __future__ import annotations

from genus_egg.kernel.reaction_kernel import ReactionKernel
from genus_egg.kernel.reaction_registry import ReactionRegistry
from genus_egg.kernel.reaction_spec import ReactionSpec
from genus_egg.kernel.working_set import WorkingSet
from genus_egg.truth.ledger import Ledger
from genus_egg.truth.sqlite_store import SQLiteStore


def test_max_chain_depth_enforced(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    ledger = Ledger(store)

    result = ReactionKernel(store, ledger, max_chain_depth=0).remember("larumipsum")

    assert result.outcome == "stopped"
    assert result.reason_code == "max_chain_depth"
    store.close()


def test_ambiguous_reaction_stops(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    ledger = Ledger(store)

    def make_candidate(working_set: WorkingSet):
        return ReactionKernel(store, ledger)._parse_user_input(working_set)

    registry = ReactionRegistry(
        [
            ReactionSpec("parse_user_input", "raw_input", "meaning_candidate", make_candidate),
            ReactionSpec("parse_user_input", "raw_input", "meaning_candidate", make_candidate),
        ]
    )

    result = ReactionKernel(store, ledger, registry=registry).remember("larumipsum")

    assert result.outcome == "stopped"
    assert result.reason_code == "ambiguous_reaction"
    store.close()


def test_missing_graph_edge_blocks_follow_up(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    ledger = Ledger(store)
    kernel = ReactionKernel(store, ledger)
    kernel.graph._edges.remove(("raw_input", "parse_user_input"))

    result = kernel.remember("larumipsum")

    assert result.outcome == "stopped"
    assert result.reason_code == "no_enabled_reaction"
    store.close()
