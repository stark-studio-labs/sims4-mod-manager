"""Tests for the DBPF package parser."""
from __future__ import annotations

from pathlib import Path

import pytest

from sims4_mod_manager.parser import (
    PackageInfo,
    PackageParseError,
    ResourceEntry,
    get_resource_type_name,
    is_tuning_type,
    parse_package,
)
from tests.conftest import make_package


class TestGetResourceTypeName:
    def test_known_types(self) -> None:
        assert get_resource_type_name(0x0904DF10) == "SimData"
        assert "String Table" in get_resource_type_name(0x220557DA)
        assert "Geometry" in get_resource_type_name(0x545AC67A)

    def test_tuning_types(self) -> None:
        assert "Tuning" in get_resource_type_name(0x6FA49E3A)  # Buff
        assert "Tuning" in get_resource_type_name(0xA8D58BE3)  # Interaction
        assert "Tuning" in get_resource_type_name(0x4F739CEE)  # Trait

    def test_unknown_type(self) -> None:
        result = get_resource_type_name(0xDEADBEEF)
        assert "Unknown" in result


class TestIsTuningType:
    def test_known_tuning(self) -> None:
        assert is_tuning_type(0x6FA49E3A) is True  # Buff
        assert is_tuning_type(0xA8D58BE3) is True  # Interaction

    def test_non_tuning(self) -> None:
        assert is_tuning_type(0x545AC67A) is False  # Geometry (above 0x0FFFFFFF range)
        assert is_tuning_type(0xDEADBEEF) is False  # Random high ID


class TestParsePackage:
    def test_empty_package(self, tmp_path: Path) -> None:
        pkg = make_package(tmp_path / "empty.package", entries=[])
        info = parse_package(pkg)
        assert isinstance(info, PackageInfo)
        assert info.entry_count == 0
        assert info.entries == []

    def test_single_entry(self, tmp_path: Path) -> None:
        pkg = make_package(
            tmp_path / "single.package",
            entries=[(0x6FA49E3A, 0, 0x00000001)],  # Buff tuning
        )
        info = parse_package(pkg)
        assert info.entry_count == 1
        assert len(info.entries) == 1
        entry = info.entries[0]
        assert entry.type_id == 0x6FA49E3A
        assert entry.instance_id == 0x00000001

    def test_multiple_entries(self, tmp_path: Path) -> None:
        entries = [
            (0x6FA49E3A, 0, 0x100),  # Buff
            (0xA8D58BE3, 0, 0x200),  # Interaction
            (0x545AC67A, 0, 0x300),  # Geometry
        ]
        pkg = make_package(tmp_path / "multi.package", entries=entries)
        info = parse_package(pkg)
        assert info.entry_count == 3
        assert len(info.entries) == 3

    def test_tuning_entries_property(self, tmp_path: Path) -> None:
        entries = [
            (0x6FA49E3A, 0, 0x100),  # Buff tuning (should be in tuning_entries)
            (0x545AC67A, 0, 0x200),  # Geometry (should NOT be in tuning_entries)
        ]
        pkg = make_package(tmp_path / "mixed.package", entries=entries)
        info = parse_package(pkg)
        tuning = info.tuning_entries
        assert len(tuning) == 1
        assert tuning[0].type_id == 0x6FA49E3A

    def test_invalid_magic(self, tmp_path: Path) -> None:
        bad = tmp_path / "bad.package"
        bad.write_bytes(b"NOPE" + b"\x00" * 92)
        with pytest.raises(PackageParseError, match="magic"):
            parse_package(bad)

    def test_truncated_file(self, tmp_path: Path) -> None:
        short = tmp_path / "short.package"
        short.write_bytes(b"DBPF" + b"\x00" * 10)
        with pytest.raises(PackageParseError):
            parse_package(short)

    def test_file_not_found(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            parse_package(tmp_path / "nonexistent.package")


class TestResourceEntry:
    def test_type_name_property(self) -> None:
        entry = ResourceEntry(
            type_id=0x6FA49E3A,
            group_id=0,
            instance_id=1,
            offset=0,
            size=16,
            compressed=False,
        )
        assert "Tuning" in entry.type_name

    def test_is_tuning_property(self) -> None:
        tuning = ResourceEntry(0x6FA49E3A, 0, 1, 0, 16, False)
        geom = ResourceEntry(0x545AC67A, 0, 1, 0, 16, False)
        assert tuning.is_tuning is True
        assert geom.is_tuning is False
