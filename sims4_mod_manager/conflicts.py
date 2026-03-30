"""Conflict detection for Sims 4 .package mods.

Scans .package files for overlapping resource entries (same type_id,
group_id, instance_id tuple claimed by two or more mods).  Conflicts are
classified by severity so the user can focus on gameplay-breaking
collisions first.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from sims4_mod_manager.parser import (
    PackageInfo,
    ResourceEntry,
    get_resource_type_name,
    parse_package,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Type-ID sets used for severity classification
# ---------------------------------------------------------------------------

# Tuning types -- overrides here change game behaviour directly.
_HIGH_SEVERITY_TYPE_IDS: frozenset[int] = frozenset(
    {
        # Interaction tuning
        0x03B33DDF,  # TUNING (generic tuning)
        0xE882D22F,  # Interaction tuning
        # Trait / buff tuning
        0xCB5FDDC7,  # Trait
        0x6017E896,  # Buff
        # Object / recipe / career tuning
        0xC0DB5AE7,  # Object tuning
        0xEB97F823,  # Recipe
        0xCB40B2A6,  # Career
        # Situation / aspiration / reward
        0x5BCA3B2D,  # Situation
        0x0EB7D138,  # Aspiration
        0xE4F5242C,  # Reward
        # Lot tuning
        0xB3C438F0,  # Lot tuning
        # Relationship / statistic
        0x0069453E,  # Relationship bit
        0x339BC3BD,  # Statistic
        # Skill
        0xD86028E7,  # Skill
        # Mood
        0xBA7B60B8,  # Mood
        # Test set / loot / action
        0x205E4A90,  # Loot actions
        0x1F0B3B77,  # Test set
        # Snippet / objective / whim
        0x7DF2169C,  # Snippet
        0x0C772E27,  # Objective
        0x178CB946,  # Whim set
        # CAS part tuning
        0x034AEECB,  # CAS Part
    }
)

# Medium -- text tables and SimData.  Errors manifest as missing strings
# or garbled metadata, not broken gameplay.
_MEDIUM_SEVERITY_TYPE_IDS: frozenset[int] = frozenset(
    {
        0x220557DA,  # STBL  (String Table)
        0x0904DF10,  # SimData
    }
)

# Everything not listed above is considered low severity (meshes,
# textures, images, animations).


# ---------------------------------------------------------------------------
# Public severity classifier
# ---------------------------------------------------------------------------


def classify_severity(type_id: int) -> str:
    """Return ``"high"``, ``"medium"``, or ``"low"`` for *type_id*."""
    if type_id in _HIGH_SEVERITY_TYPE_IDS:
        return "high"
    if type_id in _MEDIUM_SEVERITY_TYPE_IDS:
        return "medium"
    return "low"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class Conflict:
    """A single resource key claimed by multiple mods."""

    resource_type: str
    type_id: int
    group_id: int
    instance_id: int
    mods: list[str]
    severity: str  # "high" | "medium" | "low"


@dataclass
class ConflictReport:
    """Aggregated result of a conflict scan."""

    total_mods_scanned: int
    total_conflicts: int
    high_severity: int
    medium_severity: int
    low_severity: int
    conflicts: list[Conflict]
    scan_time: float  # seconds


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

ResourceKey = Tuple[int, int, int]  # (type_id, group_id, instance_id)


def _build_resource_index(
    packages: Dict[str, PackageInfo],
) -> Dict[ResourceKey, List[str]]:
    """Map each resource key to the list of mod filenames that contain it."""
    index: Dict[ResourceKey, List[str]] = {}
    for mod_name, pkg in packages.items():
        for entry in pkg.entries:
            key: ResourceKey = (entry.type_id, entry.group_id, entry.instance_id)
            index.setdefault(key, []).append(mod_name)
    return index


def _build_report(
    index: Dict[ResourceKey, List[str]],
    total_mods: int,
    elapsed: float,
) -> ConflictReport:
    """Turn a resource index into a :class:`ConflictReport`."""
    conflicts: list[Conflict] = []
    high = medium = low = 0

    for (type_id, group_id, instance_id), mods in index.items():
        if len(mods) < 2:
            continue
        severity = classify_severity(type_id)
        conflicts.append(
            Conflict(
                resource_type=get_resource_type_name(type_id),
                type_id=type_id,
                group_id=group_id,
                instance_id=instance_id,
                mods=sorted(mods),
                severity=severity,
            )
        )
        if severity == "high":
            high += 1
        elif severity == "medium":
            medium += 1
        else:
            low += 1

    # Sort conflicts: high first, then medium, then low, then by resource type
    _severity_order = {"high": 0, "medium": 1, "low": 2}
    conflicts.sort(key=lambda c: (_severity_order[c.severity], c.resource_type))

    return ConflictReport(
        total_mods_scanned=total_mods,
        total_conflicts=len(conflicts),
        high_severity=high,
        medium_severity=medium,
        low_severity=low,
        conflicts=conflicts,
        scan_time=round(elapsed, 3),
    )


def _parse_packages(paths: list[Path]) -> Dict[str, PackageInfo]:
    """Parse a list of .package files, skipping any that fail."""
    packages: Dict[str, PackageInfo] = {}
    for path in paths:
        try:
            pkg = parse_package(path)
            packages[path.name] = pkg
        except Exception:
            logger.warning("Failed to parse %s — skipping", path, exc_info=True)
    return packages


# ---------------------------------------------------------------------------
# ConflictDetector
# ---------------------------------------------------------------------------


class ConflictDetector:
    """Detect resource-key conflicts among Sims 4 .package mods.

    Parameters
    ----------
    mods_path:
        Directory that contains ``.package`` files (typically the EA
        Mods folder).
    """

    def __init__(self, mods_path: Path) -> None:
        self.mods_path = mods_path

    # -- full scan ----------------------------------------------------------

    def scan(self, mod_paths: Optional[list[Path]] = None) -> ConflictReport:
        """Scan mods for conflicts.

        Parameters
        ----------
        mod_paths:
            Explicit list of ``.package`` files to scan.  When *None*,
            every ``.package`` file under :attr:`mods_path` is scanned.

        Returns
        -------
        ConflictReport
        """
        start = time.monotonic()

        if mod_paths is None:
            mod_paths = sorted(self.mods_path.rglob("*.package"))

        packages = _parse_packages(mod_paths)
        index = _build_resource_index(packages)
        elapsed = time.monotonic() - start
        return _build_report(index, total_mods=len(packages), elapsed=elapsed)

    # -- single-mod pre-install check ---------------------------------------

    def scan_single(
        self,
        new_mod: Path,
        existing_mods: list[Path],
    ) -> ConflictReport:
        """Check whether *new_mod* conflicts with *existing_mods*.

        Only conflicts that involve *new_mod* are reported — conflicts
        among the existing mods themselves are ignored so the result
        focuses on what the new mod would introduce.

        Parameters
        ----------
        new_mod:
            Path to the ``.package`` file being evaluated.
        existing_mods:
            Paths to the mods already installed.

        Returns
        -------
        ConflictReport
        """
        start = time.monotonic()

        # Parse the new mod first — fail loudly if it's broken.
        try:
            new_pkg = parse_package(new_mod)
        except Exception:
            logger.error("Cannot parse new mod %s", new_mod, exc_info=True)
            elapsed = time.monotonic() - start
            return ConflictReport(
                total_mods_scanned=0,
                total_conflicts=0,
                high_severity=0,
                medium_severity=0,
                low_severity=0,
                conflicts=[],
                scan_time=round(elapsed, 3),
            )

        new_mod_name = new_mod.name

        # Build a set of resource keys in the new mod for fast lookup.
        new_keys: set[ResourceKey] = {
            (e.type_id, e.group_id, e.instance_id) for e in new_pkg.entries
        }

        # Parse existing mods and collect only the entries that overlap
        # with the new mod's keys.
        packages: Dict[str, PackageInfo] = {new_mod_name: new_pkg}
        for path in existing_mods:
            try:
                pkg = parse_package(path)
            except Exception:
                logger.warning("Failed to parse %s — skipping", path, exc_info=True)
                continue

            # Filter to entries that share a key with the new mod.
            overlapping = [
                e
                for e in pkg.entries
                if (e.type_id, e.group_id, e.instance_id) in new_keys
            ]
            if overlapping:
                # Create a lightweight PackageInfo with only the
                # relevant entries so the index builder works as-is.
                filtered = PackageInfo(
                    path=path,
                    entry_count=len(overlapping),
                    entries=overlapping,
                )
                packages[path.name] = filtered

        index = _build_resource_index(packages)

        # Drop any index entries that do NOT include the new mod — we only
        # care about conflicts the new mod participates in.
        filtered_index: Dict[ResourceKey, List[str]] = {
            k: v for k, v in index.items() if new_mod_name in v and len(v) >= 2
        }

        elapsed = time.monotonic() - start
        return _build_report(
            filtered_index,
            total_mods=len(packages),
            elapsed=elapsed,
        )


# ---------------------------------------------------------------------------
# Convenience wrapper
# ---------------------------------------------------------------------------


def detect_conflicts(mods_path: Path) -> ConflictReport:
    """Scan all ``.package`` files in *mods_path* and return a conflict report.

    This is a one-call convenience wrapper around :class:`ConflictDetector`.
    """
    detector = ConflictDetector(mods_path)
    return detector.scan()
