from __future__ import annotations

import ctypes
import json
import os
import platform
import shutil
from pathlib import Path

from genus_egg.habitat.habitat_manifest import HabitatManifest
from genus_egg.habitat.habitat_readiness_report import HabitatReadinessReport
from genus_egg.habitat.resource_snapshot import ResourceSnapshot
from genus_egg.ids import new_id
from genus_egg.time import utc_now


class HabitatContract:
    def snapshot_resources(self, manifest: HabitatManifest) -> ResourceSnapshot:
        disk_path = Path(manifest.repo_path or ".")
        if not disk_path.exists():
            disk_path = Path(".")
        disk = shutil.disk_usage(disk_path)
        total_mb, available_mb = _memory_mb()
        cpu_label = platform.processor() or platform.machine() or "unknown"
        return ResourceSnapshot(
            snapshot_id=new_id("resources"),
            habitat_id=manifest.habitat_id,
            cpu_count=os.cpu_count(),
            cpu_label=cpu_label,
            memory_total_mb=total_mb,
            memory_available_mb=available_mb,
            disk_total_mb=_bytes_to_mb(disk.total),
            disk_free_mb=_bytes_to_mb(disk.free),
            temperature_celsius=None,
            payload_json=json.dumps({"temperature": "unknown"}, sort_keys=True),
            created_at=utc_now(),
        )

    def assess(
        self, manifest: HabitatManifest, snapshot: ResourceSnapshot
    ) -> HabitatReadinessReport:
        checks = {
            "repo_path_present": bool(manifest.repo_path),
            "sqlite_path_present": bool(manifest.sqlite_path),
            "disk_available": snapshot.disk_free_mb > 0,
            "cpu_known": snapshot.cpu_count is not None and snapshot.cpu_count > 0,
            "memory_known": snapshot.memory_total_mb is not None,
            "github_closed_by_default": manifest.github_allowed is False,
        }
        if not checks["repo_path_present"] or not checks["sqlite_path_present"]:
            status = "blocked"
            reason_code = "missing_required_paths"
        elif not checks["disk_available"]:
            status = "blocked"
            reason_code = "disk_unavailable"
        elif not checks["cpu_known"] or not checks["memory_known"] or not manifest.git_available:
            status = "limited"
            reason_code = "limited_tool_or_resource_visibility"
        else:
            status = "ready"
            reason_code = "habitat_ready"

        return HabitatReadinessReport(
            report_id=new_id("readiness"),
            habitat_id=manifest.habitat_id,
            snapshot_id=snapshot.snapshot_id,
            status=status,
            reason_code=reason_code,
            checks_json=json.dumps(checks, sort_keys=True),
            payload_json=json.dumps({"activation": "blocked"}, sort_keys=True),
            created_at=utc_now(),
        )


def _bytes_to_mb(value: int) -> int:
    return round(value / (1024 * 1024))


def _memory_mb() -> tuple[int | None, int | None]:
    if os.name == "nt":
        return _windows_memory_mb()
    total_pages = _sysconf_value("SC_PHYS_PAGES")
    available_pages = _sysconf_value("SC_AVPHYS_PAGES")
    page_size = _sysconf_value("SC_PAGE_SIZE")
    if total_pages is None or page_size is None:
        return None, None
    total = _bytes_to_mb(total_pages * page_size)
    available = (
        _bytes_to_mb(available_pages * page_size)
        if available_pages is not None
        else None
    )
    return total, available


def _sysconf_value(name: str) -> int | None:
    if not hasattr(os, "sysconf") or name not in os.sysconf_names:
        return None
    value = os.sysconf(name)
    return int(value) if value > 0 else None


def _windows_memory_mb() -> tuple[int | None, int | None]:
    class MemoryStatus(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_ulong),
            ("dwMemoryLoad", ctypes.c_ulong),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]

    status = MemoryStatus()
    status.dwLength = ctypes.sizeof(MemoryStatus)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        return None, None
    return _bytes_to_mb(status.ullTotalPhys), _bytes_to_mb(status.ullAvailPhys)
