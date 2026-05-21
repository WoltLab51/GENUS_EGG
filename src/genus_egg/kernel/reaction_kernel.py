from __future__ import annotations

import json
from time import perf_counter

from genus_egg.ids import new_id
from genus_egg.kernel.artifacts import (
    KernelResult,
    ReactionProduct,
    ReactionRecord,
    ValidationResult,
)
from genus_egg.kernel.guards import Guards
from genus_egg.kernel.reaction_cube import ReactionCube
from genus_egg.kernel.reaction_graph import ReactionGraph
from genus_egg.kernel.reaction_registry import ReactionRegistry
from genus_egg.kernel.reaction_spec import ReactionSpec
from genus_egg.kernel.working_set import WorkingSet
from genus_egg.maturation.maturation_seed import MaturationSeed
from genus_egg.memory.memory_object import MemoryObject
from genus_egg.semantics.raw_input import RawInput
from genus_egg.semantics.semantic_parse_adapter import SemanticParseAdapter
from genus_egg.time import utc_now
from genus_egg.truth.ledger import Ledger
from genus_egg.truth.sqlite_store import SQLiteStore


class ReactionKernel:
    def __init__(
        self,
        store: SQLiteStore,
        ledger: Ledger,
        max_chain_depth: int = 8,
        registry: ReactionRegistry | None = None,
    ) -> None:
        self.store = store
        self.ledger = ledger
        self.max_chain_depth = max_chain_depth
        self.adapter = SemanticParseAdapter()
        self.cube = ReactionCube()
        self.graph = ReactionGraph()
        self.guards = Guards()
        self.registry = registry or self._default_registry()

    def remember(self, text: str) -> KernelResult:
        started_at = perf_counter()
        chain_id = new_id("chain")
        raw_input = RawInput(
            input_id=new_id("input"),
            chain_id=chain_id,
            signal_type="text",
            source_type="cli",
            raw_text=text,
            created_at=utc_now(),
        )
        self.store.save_raw_input(raw_input)
        self.ledger.record(
            chain_id=chain_id,
            event_type="raw_input_created",
            source_kind="cli",
            source_id="remember",
            target_kind="raw_input",
            target_id=raw_input.input_id,
            payload={"raw_text": text},
        )

        working_set = WorkingSet(chain_id=chain_id)
        working_set.add("raw_input", raw_input)

        depth = 0
        while depth < self.max_chain_depth:
            enabled = self.registry.find_enabled(working_set)
            allowed = [
                reaction
                for reaction in enabled
                if self.cube.allows(reaction, working_set)
                and self.graph.allows_if_continuation(reaction, working_set)
                and self.guards.allow(reaction, working_set)
            ]

            if not allowed:
                return self._result(working_set, "stopped", "no_enabled_reaction")

            if len(allowed) > 1:
                return self._result(working_set, "stopped", "ambiguous_reaction")

            reaction = allowed[0]
            product = reaction.execute(working_set)
            working_set.add(reaction.produced_kind, product)
            self._persist_reaction_output(reaction.name, product)

            if reaction.name == "create_memory":
                self._record_maturation_success(
                    working_set,
                    reason_code="memory_created",
                    duration_ms=int((perf_counter() - started_at) * 1000),
                )
                return self._result(working_set, "completed", "memory_created")

            depth += 1

        return self._result(working_set, "stopped", "max_chain_depth")

    def _default_registry(self) -> ReactionRegistry:
        return ReactionRegistry(
            [
                ReactionSpec(
                    name="parse_user_input",
                    required_kind="raw_input",
                    produced_kind="meaning_candidate",
                    execute=self._parse_user_input,
                ),
                ReactionSpec(
                    name="validate_meaning",
                    required_kind="meaning_candidate",
                    produced_kind="validation_result",
                    execute=self._validate_meaning,
                ),
                ReactionSpec(
                    name="create_memory_proposal",
                    required_kind="validation_result",
                    produced_kind="reaction_product",
                    execute=self._create_memory_proposal,
                ),
                ReactionSpec(
                    name="create_memory",
                    required_kind="reaction_product",
                    produced_kind="memory_object",
                    execute=self._create_memory,
                ),
            ]
        )

    def _parse_user_input(self, working_set: WorkingSet) -> object:
        raw_input: RawInput = working_set.latest("raw_input")
        return self.adapter.parse(raw_input)

    def _validate_meaning(self, working_set: WorkingSet) -> object:
        meaning = working_set.latest("meaning_candidate")
        return ValidationResult(
            validation_id=new_id("validation"),
            chain_id=meaning.chain_id,
            source_meaning_id=meaning.meaning_id,
            result="allow",
            reason_code="ready",
            created_at=utc_now(),
        )

    def _create_memory_proposal(self, working_set: WorkingSet) -> object:
        validation: ValidationResult = working_set.latest("validation_result")
        meaning = working_set.latest("meaning_candidate")
        reaction = ReactionRecord(
            reaction_id=new_id("reaction"),
            chain_id=validation.chain_id,
            source_validation_id=validation.validation_id,
            reaction_type="create_memory_proposal",
            context="normal",
            reaction_state="ready",
            resolver_mode="deterministic",
            cube_coord=1,
            created_at=utc_now(),
        )
        self.store.save_reaction(reaction)
        self.ledger.record(
            chain_id=reaction.chain_id,
            event_type="reaction_created",
            source_kind="validation_result",
            source_id=validation.validation_id,
            target_kind="reaction",
            target_id=reaction.reaction_id,
            payload={"reaction_type": reaction.reaction_type},
        )
        return ReactionProduct(
            product_id=new_id("product"),
            chain_id=validation.chain_id,
            produced_by_reaction_id=reaction.reaction_id,
            product_type="memory_proposal",
            continuation_policy="required",
            payload_json=json.dumps(
                {"content": meaning.content, "memory_type": "user_memory"},
                sort_keys=True,
            ),
            created_at=utc_now(),
        )

    def _create_memory(self, working_set: WorkingSet) -> object:
        product: ReactionProduct = working_set.latest("reaction_product")
        payload = json.loads(product.payload_json)
        return MemoryObject(
            memory_id=new_id("memory"),
            chain_id=product.chain_id,
            memory_type=payload["memory_type"],
            content=payload["content"],
            memory_state="fresh",
            source_product_id=product.product_id,
            created_at=utc_now(),
        )

    def _persist_reaction_output(self, reaction_name: str, product: object) -> None:
        if reaction_name == "parse_user_input":
            self.store.save_meaning_candidate(product)
            self.ledger.record(
                chain_id=product.chain_id,
                event_type="meaning_candidate_created",
                source_kind="raw_input",
                source_id=product.source_input_id,
                target_kind="meaning_candidate",
                target_id=product.meaning_id,
                payload={"intent": product.intent, "content": product.content},
            )
            return

        if reaction_name == "validate_meaning":
            self.store.save_validation_result(product)
            self.ledger.record(
                chain_id=product.chain_id,
                event_type="validation_result_created",
                source_kind="meaning_candidate",
                source_id=product.source_meaning_id,
                target_kind="validation_result",
                target_id=product.validation_id,
                payload={"result": product.result, "reason_code": product.reason_code},
            )
            return

        if reaction_name == "create_memory_proposal":
            self.store.save_reaction_product(product)
            self.ledger.record(
                chain_id=product.chain_id,
                event_type="reaction_product_created",
                source_kind="reaction",
                source_id=product.produced_by_reaction_id,
                target_kind="reaction_product",
                target_id=product.product_id,
                payload={"product_type": product.product_type},
            )
            return

        if reaction_name == "create_memory":
            self.store.save_memory_object(product)
            self.ledger.record(
                chain_id=product.chain_id,
                event_type="memory_object_created",
                source_kind="reaction_product",
                source_id=product.source_product_id,
                target_kind="memory_object",
                target_id=product.memory_id,
                payload={"content": product.content, "memory_state": product.memory_state},
            )
            self.ledger.record(
                chain_id=product.chain_id,
                event_type="chain_completed",
                source_kind="memory_object",
                source_id=product.memory_id,
                target_kind=None,
                target_id=None,
                payload={"reason_code": "memory_created"},
            )

    def _record_maturation_success(
        self, working_set: WorkingSet, reason_code: str, duration_ms: int
    ) -> None:
        MaturationSeed(self.store).record_successful_memory_chain(
            chain_id=working_set.chain_id,
            reason_code=reason_code,
            duration_ms=duration_ms,
            ledger_entries=len(self.ledger.list_by_chain(working_set.chain_id)),
        )

    def _result(
        self, working_set: WorkingSet, outcome: str, reason_code: str
    ) -> KernelResult:
        memory_content = None
        if working_set.has("memory_object"):
            memory_content = working_set.latest("memory_object").content
        return KernelResult(
            chain_id=working_set.chain_id,
            outcome=outcome,
            reason_code=reason_code,
            ledger_entries=len(self.ledger.list_by_chain(working_set.chain_id)),
            memory_content=memory_content,
        )
