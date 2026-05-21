from __future__ import annotations


class ApprovalBlockedError(RuntimeError):
    pass


class ApprovalGate:
    def can_modify_files(self, path: str | None = None) -> bool:
        return False

    def can_activate(self, proposal_id: str | None = None) -> bool:
        return False

    def assert_not_active(self) -> None:
        raise ApprovalBlockedError("Development activation is blocked in v0.5")
