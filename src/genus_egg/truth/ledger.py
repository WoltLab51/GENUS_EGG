from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from genus_egg.ids import new_id
from genus_egg.time import utc_now
from genus_egg.truth.sqlite_store import SQLiteStore


@dataclass(frozen=True)
class LedgerEntry:
    ledger_id: str
    chain_id: str
    step: int
    event_type: str
    source_kind: str
    source_id: str
    target_kind: str | None
    target_id: str | None
    payload_json: str | None
    created_at: str


class Ledger:
    def __init__(self, store: SQLiteStore) -> None:
        self.store = store

    def record(
        self,
        chain_id: str,
        event_type: str,
        source_kind: str,
        source_id: str,
        target_kind: str | None = None,
        target_id: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> LedgerEntry:
        step = self._next_step(chain_id)
        entry = LedgerEntry(
            ledger_id=new_id("ledger"),
            chain_id=chain_id,
            step=step,
            event_type=event_type,
            source_kind=source_kind,
            source_id=source_id,
            target_kind=target_kind,
            target_id=target_id,
            payload_json=json.dumps(payload, sort_keys=True) if payload else None,
            created_at=utc_now(),
        )
        self.store.connection.execute(
            """
            INSERT INTO ledger_entries
            (ledger_id, chain_id, step, event_type, source_kind, source_id,
             target_kind, target_id, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entry.ledger_id,
                entry.chain_id,
                entry.step,
                entry.event_type,
                entry.source_kind,
                entry.source_id,
                entry.target_kind,
                entry.target_id,
                entry.payload_json,
                entry.created_at,
            ),
        )
        self.store.connection.commit()
        return entry

    def list_by_chain(self, chain_id: str) -> list[LedgerEntry]:
        rows = self.store.connection.execute(
            """
            SELECT ledger_id, chain_id, step, event_type, source_kind, source_id,
                   target_kind, target_id, payload_json, created_at
            FROM ledger_entries
            WHERE chain_id = ?
            ORDER BY step
            """,
            (chain_id,),
        ).fetchall()
        return [
            LedgerEntry(
                ledger_id=row["ledger_id"],
                chain_id=row["chain_id"],
                step=row["step"],
                event_type=row["event_type"],
                source_kind=row["source_kind"],
                source_id=row["source_id"],
                target_kind=row["target_kind"],
                target_id=row["target_id"],
                payload_json=row["payload_json"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def _next_step(self, chain_id: str) -> int:
        row = self.store.connection.execute(
            "SELECT COALESCE(MAX(step), 0) + 1 AS next_step FROM ledger_entries WHERE chain_id = ?",
            (chain_id,),
        ).fetchone()
        return int(row["next_step"])
