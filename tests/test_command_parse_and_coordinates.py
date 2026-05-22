from __future__ import annotations

from genus_egg.kernel.artifacts import ValidationResult
from genus_egg.kernel.reaction_cube import (
    ReactionCode,
    ReactionCoordinate,
    ReactionCube,
)
from genus_egg.kernel.working_set import WorkingSet
from genus_egg.semantics.command_parse_adapter import CommandParseAdapter
from genus_egg.semantics.raw_input import RawInput
from genus_egg.semantics.semantic_parse_adapter import SemanticParseAdapter


def test_command_parse_adapter_marks_explicit_remember_path():
    raw_input = RawInput(
        input_id="input_1",
        chain_id="chain_1",
        signal_type="text",
        source_type="cli",
        raw_text="larumipsum",
        created_at="2026-05-23T00:00:00Z",
    )

    meaning = CommandParseAdapter().parse(raw_input)

    assert meaning.intent == "memory_request"
    assert meaning.adapter_version == "command-remember-v0"


def test_semantic_parse_adapter_is_compatibility_wrapper_not_free_language():
    raw_input = RawInput(
        input_id="input_1",
        chain_id="chain_1",
        signal_type="text",
        source_type="cli",
        raw_text="larumipsum",
        created_at="2026-05-23T00:00:00Z",
    )

    meaning = SemanticParseAdapter().parse(raw_input)

    assert meaning.intent == "memory_request"
    assert meaning.adapter_version == "command-remember-v0"


def test_reaction_coordinate_maps_memory_request_normal_ready_to_code():
    coordinate = ReactionCoordinate(
        intent="memory_request",
        context="normal",
        reaction_state="ready",
    )

    assert coordinate.code == ReactionCode.MEMORY_REQUEST_NORMAL_READY
    assert int(coordinate.code) == 7


def test_reaction_coordinate_blocks_unknown_axis():
    coordinate = ReactionCoordinate(
        intent="free_language",
        context="normal",
        reaction_state="ready",
    )

    assert coordinate.code == ReactionCode.BLOCKED


def test_reaction_cube_calculates_coordinate_from_working_set():
    raw_input = RawInput(
        input_id="input_1",
        chain_id="chain_1",
        signal_type="text",
        source_type="cli",
        raw_text="larumipsum",
        created_at="2026-05-23T00:00:00Z",
    )
    working_set = WorkingSet("chain_1")
    working_set.add("meaning_candidate", CommandParseAdapter().parse(raw_input))
    working_set.add(
        "validation_result",
        ValidationResult(
            "validation_1",
            "chain_1",
            "meaning_1",
            "allow",
            "ready",
            "2026-05-23T00:00:00Z",
        ),
    )

    assert ReactionCube().coordinate(working_set).code == (
        ReactionCode.MEMORY_REQUEST_NORMAL_READY
    )
