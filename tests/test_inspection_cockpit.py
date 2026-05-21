from __future__ import annotations

from genus_egg.cockpit.data_adapter import CockpitDataAdapter
from genus_egg.cockpit.html_renderer import CockpitHtmlRenderer
from genus_egg.development.development_boundary import DevelopmentBoundary
from genus_egg.evaluation.fitness_evaluator import FitnessEvaluator
from genus_egg.evaluation.shadow_tester import ShadowTester
from genus_egg.habitat.environment_probe import EnvironmentProbe
from genus_egg.kernel.reaction_kernel import ReactionKernel
from genus_egg.maturation.maturation_seed import MaturationSeed
from genus_egg.truth.ledger import Ledger
from genus_egg.truth.sqlite_store import SQLiteStore


def _populate_cockpit_fixture(store: SQLiteStore) -> None:
    result = ReactionKernel(store, Ledger(store)).remember("larumipsum")
    store.save_habitat_manifest(EnvironmentProbe(store.db_path).probe())
    need = MaturationSeed(store).draft_memory_indexing_need(
        source_observation_id=store.list_observation_records()[-1].observation_id
    )
    _, code_proposal = DevelopmentBoundary(store).draft_memory_indexing_proposal(
        need.need_id
    )
    ShadowTester(store).plan(code_proposal.code_proposal_id)
    FitnessEvaluator(store).evaluate(code_proposal.code_proposal_id)
    assert result.ledger_entries == 7


def test_cockpit_data_adapter_reads_all_relevant_object_counts(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    _populate_cockpit_fixture(store)

    snapshot = CockpitDataAdapter(store).snapshot()

    assert snapshot.memory_count == 1
    assert snapshot.ledger_entry_count == 7
    assert snapshot.habitat_manifest_count == 1
    assert snapshot.reaction_outcome_count == 1
    assert snapshot.observation_count == 1
    assert snapshot.capability_need_count == 1
    assert snapshot.capability_proposal_count == 1
    assert snapshot.code_change_proposal_count == 1
    assert snapshot.shadow_plan_count == 1
    assert snapshot.fitness_evaluation_count == 1
    assert snapshot.latest_habitat_id is not None
    assert snapshot.latest_fitness_score is not None
    assert snapshot.activation_state == "blocked"
    store.close()


def test_cockpit_adapter_is_read_only(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    _populate_cockpit_fixture(store)
    before = {
        table: store.count_rows(table)
        for table in [
            "memory_objects",
            "ledger_entries",
            "habitat_manifest",
            "reaction_outcomes",
            "observation_records",
            "capability_needs",
            "capability_proposals",
            "code_change_proposals",
            "shadow_test_plans",
            "fitness_evaluations",
        ]
    }

    CockpitDataAdapter(store).snapshot()
    after = {table: store.count_rows(table) for table in before}

    assert after == before
    store.close()


def test_cockpit_html_renderer_is_read_only_and_shows_boundaries(tmp_path):
    store = SQLiteStore(tmp_path / "genus.sqlite")
    _populate_cockpit_fixture(store)
    snapshot = CockpitDataAdapter(store).snapshot()
    before = store.count_rows("fitness_evaluations")

    html = CockpitHtmlRenderer().render(snapshot)

    assert "GENUS EGG Inspection Cockpit" in html
    assert "Memories" in html
    assert "Ledger Entries" in html
    assert "Activation: blocked" in html
    assert "Mode: read-only" in html
    assert store.count_rows("fitness_evaluations") == before
    store.close()
