"""Tests for the conflict detector."""
from __future__ import annotations

from pathlib import Path

import pytest

from sims4_mod_manager.conflicts import (
    ConflictDetector,
    ConflictReport,
    classify_severity,
    detect_conflicts,
)
from tests.conftest import make_package

# IDs that are in the conflict detector's _HIGH_SEVERITY_TYPE_IDS
HIGH_TYPE_ID = 0xE882D22F   # Interaction tuning
# IDs that are low severity (not in high or medium sets)
LOW_TYPE_ID = 0x545AC67A    # Geometry
# Medium severity
MEDIUM_TYPE_ID = 0x220557DA  # STBL


class TestClassifySeverity:
    def test_tuning_is_high(self) -> None:
        assert classify_severity(HIGH_TYPE_ID) == "high"

    def test_simdata_is_medium(self) -> None:
        assert classify_severity(0x0904DF10) == "medium"

    def test_stbl_is_medium(self) -> None:
        assert classify_severity(MEDIUM_TYPE_ID) == "medium"

    def test_geometry_is_low(self) -> None:
        assert classify_severity(LOW_TYPE_ID) == "low"

    def test_unknown_is_low(self) -> None:
        assert classify_severity(0xDEADBEEF) == "low"


class TestConflictDetector:
    def test_no_conflicts(self, tmp_mods: Path) -> None:
        make_package(
            tmp_mods / "mod_a.package",
            entries=[(HIGH_TYPE_ID, 0, 0x100)],
        )
        make_package(
            tmp_mods / "mod_b.package",
            entries=[(HIGH_TYPE_ID, 0, 0x200)],  # Different instance
        )
        detector = ConflictDetector(tmp_mods)
        report = detector.scan()
        assert report.total_conflicts == 0

    def test_detects_conflict(self, tmp_mods: Path) -> None:
        # Same type + group + instance = conflict
        make_package(
            tmp_mods / "mod_a.package",
            entries=[(HIGH_TYPE_ID, 0, 0x100)],
        )
        make_package(
            tmp_mods / "mod_b.package",
            entries=[(HIGH_TYPE_ID, 0, 0x100)],  # Same resource key
        )
        detector = ConflictDetector(tmp_mods)
        report = detector.scan()
        assert report.total_conflicts == 1
        assert report.high_severity == 1
        assert len(report.conflicts[0].mods) == 2

    def test_severity_classification(self, tmp_mods: Path) -> None:
        # High severity conflict (tuning)
        make_package(
            tmp_mods / "mod_a.package",
            entries=[(HIGH_TYPE_ID, 0, 0x100)],
        )
        make_package(
            tmp_mods / "mod_b.package",
            entries=[(HIGH_TYPE_ID, 0, 0x100)],
        )
        # Low severity conflict (geometry)
        make_package(
            tmp_mods / "mod_c.package",
            entries=[(LOW_TYPE_ID, 0, 0x999)],
        )
        make_package(
            tmp_mods / "mod_d.package",
            entries=[(LOW_TYPE_ID, 0, 0x999)],
        )

        detector = ConflictDetector(tmp_mods)
        report = detector.scan()
        assert report.total_conflicts == 2
        assert report.high_severity == 1
        assert report.low_severity == 1

    def test_scan_single(self, tmp_mods: Path, tmp_path: Path) -> None:
        existing = tmp_mods / "existing.package"
        make_package(existing, entries=[(HIGH_TYPE_ID, 0, 0x100)])

        new_mod = tmp_path / "new.package"
        make_package(new_mod, entries=[(HIGH_TYPE_ID, 0, 0x100)])

        detector = ConflictDetector(tmp_mods)
        report = detector.scan_single(new_mod, [existing])
        assert report.total_conflicts == 1

    def test_scan_single_no_conflict(self, tmp_mods: Path, tmp_path: Path) -> None:
        existing = tmp_mods / "existing.package"
        make_package(existing, entries=[(HIGH_TYPE_ID, 0, 0x100)])

        new_mod = tmp_path / "new.package"
        make_package(new_mod, entries=[(HIGH_TYPE_ID, 0, 0x999)])

        detector = ConflictDetector(tmp_mods)
        report = detector.scan_single(new_mod, [existing])
        assert report.total_conflicts == 0

    def test_empty_folder(self, tmp_mods: Path) -> None:
        detector = ConflictDetector(tmp_mods)
        report = detector.scan()
        assert report.total_conflicts == 0
        assert report.total_mods_scanned == 0


class TestDetectConflicts:
    def test_convenience_wrapper(self, tmp_mods: Path) -> None:
        make_package(tmp_mods / "a.package", entries=[(HIGH_TYPE_ID, 0, 0x1)])
        make_package(tmp_mods / "b.package", entries=[(HIGH_TYPE_ID, 0, 0x1)])
        report = detect_conflicts(tmp_mods)
        assert isinstance(report, ConflictReport)
        assert report.total_conflicts == 1
