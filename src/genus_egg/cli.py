from __future__ import annotations

import argparse
from pathlib import Path

from genus_egg.habitat.environment_probe import EnvironmentProbe
from genus_egg.kernel.reaction_kernel import ReactionKernel
from genus_egg.maturation.maturation_seed import MaturationSeed
from genus_egg.memory.memory_store import MemoryStore
from genus_egg.truth.ledger import Ledger
from genus_egg.truth.sqlite_store import SQLiteStore


DEFAULT_DB = Path("data/genus_egg.sqlite")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="genus-egg")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="SQLite database path")

    subparsers = parser.add_subparsers(dest="command", required=True)

    remember = subparsers.add_parser("remember", help="Create a governed memory")
    remember.add_argument("text")

    subparsers.add_parser("memories", help="List stored memories")

    ledger = subparsers.add_parser("ledger", help="List ledger entries for a chain")
    ledger.add_argument("--chain", required=True)

    habitat = subparsers.add_parser("habitat", help="Probe and store the local habitat")
    habitat.add_argument("--db", default=argparse.SUPPRESS, help="SQLite database path")

    subparsers.add_parser("observations", help="List maturation observations")

    needs = subparsers.add_parser("needs", help="List or draft capability needs")
    needs.add_argument(
        "action",
        nargs="?",
        choices=["list", "draft-memory-indexing"],
        default="list",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    store = SQLiteStore(args.db)
    ledger = Ledger(store)

    try:
        if args.command == "remember":
            result = ReactionKernel(store, ledger).remember(args.text)
            if result.outcome != "completed":
                print(f"Outcome: {result.outcome}")
                print(f"Reason: {result.reason_code}")
                print(f"Chain: {result.chain_id}")
                print(f"Ledger entries: {result.ledger_entries}")
                return 1
            print(f"Memory created: {result.memory_content}")
            print(f"Chain: {result.chain_id}")
            print(f"Ledger entries: {result.ledger_entries}")
            print("Outcome: completed")
            return 0

        if args.command == "memories":
            memories = MemoryStore(store).list_memories()
            for memory in memories:
                print(f"{memory.memory_id}\t{memory.chain_id}\t{memory.content}")
            return 0

        if args.command == "ledger":
            entries = ledger.list_by_chain(args.chain)
            for entry in entries:
                print(
                    f"{entry.step}\t{entry.event_type}\t"
                    f"{entry.source_kind}:{entry.source_id}\t"
                    f"{entry.target_kind or '-'}:{entry.target_id or '-'}"
                )
            return 0

        if args.command == "habitat":
            manifest = EnvironmentProbe(args.db).probe()
            store.save_habitat_manifest(manifest)
            print(f"habitat_id: {manifest.habitat_id}")
            print(f"os_name: {manifest.os_name}")
            print(f"repo_path: {manifest.repo_path}")
            print(f"sqlite_path: {manifest.sqlite_path}")
            print(f"git_available: {str(manifest.git_available).lower()}")
            print(f"network_allowed: {str(manifest.network_allowed).lower()}")
            return 0

        if args.command == "observations":
            for observation in store.list_observation_records():
                print(
                    f"{observation.observation_id}\t{observation.chain_id}\t"
                    f"{observation.observation_type}"
                )
            return 0

        if args.command == "needs":
            if args.action == "draft-memory-indexing":
                observations = store.list_observation_records()
                source_observation_id = (
                    observations[-1].observation_id if observations else None
                )
                need = MaturationSeed(store).draft_memory_indexing_need(
                    source_observation_id=source_observation_id
                )
                print(f"CapabilityNeed drafted: {need.description}")
                print(f"Need: {need.need_id}")
                print(f"Status: {need.status}")
                print(f"Activation: none")
                return 0

            for need in store.list_capability_needs():
                print(f"{need.need_id}\t{need.status}\t{need.description}")
            return 0

        return 2
    finally:
        store.close()


if __name__ == "__main__":
    raise SystemExit(main())
