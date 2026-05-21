from __future__ import annotations

import argparse
from pathlib import Path

from genus_egg.kernel.reaction_kernel import ReactionKernel
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

        return 2
    finally:
        store.close()


if __name__ == "__main__":
    raise SystemExit(main())
