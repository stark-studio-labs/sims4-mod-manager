"""Tests for the mod scanner and manager."""
from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from sims4_mod_manager.manager import ModScanner, ModManager, ModInfo, format_size
from tests.conftest import make_package


class TestFormatSize:
    def test_bytes(self) -> None:
        assert format_size(500) == "500 B"

    def test_kilobytes(self) -> None:
        assert format_size(1536) == "1.5 KB"

    def test_megabytes(self) -> None:
        result = format_size(5 * 1024 * 1024)
        assert "MB" in result

    def test_zero(self) -> None:
        assert format_size(0) == "0 B"


class TestModScanner:
    def test_scan_empty_folder(self, tmp_mods: Path) -> None:
        scanner = ModScanner(tmp_mods)
        mods = scanner.scan()
        assert mods == []

    def test_scan_finds_packages(self, tmp_mods: Path) -> None:
        make_package(tmp_mods / "test_mod.package", entries=[])
        scanner = ModScanner(tmp_mods)
        mods = scanner.scan()
        assert len(mods) == 1
        assert mods[0].name == "test_mod"
        assert mods[0].mod_type == "package"
        assert mods[0].enabled is True

    def test_scan_finds_ts4scripts(self, tmp_mods: Path) -> None:
        # .ts4script is just a zip file
        script = tmp_mods / "test_script.ts4script"
        with zipfile.ZipFile(script, "w") as zf:
            zf.writestr("test.pyc", b"\x00" * 20)
        scanner = ModScanner(tmp_mods)
        mods = scanner.scan()
        assert len(mods) == 1
        assert mods[0].name == "test_script"
        assert mods[0].mod_type == "ts4script"

    def test_scan_subfolder(self, tmp_mods: Path) -> None:
        sub = tmp_mods / "SubFolder"
        sub.mkdir()
        make_package(sub / "nested.package", entries=[])
        scanner = ModScanner(tmp_mods)
        mods = scanner.scan()
        assert len(mods) == 1
        assert mods[0].name == "nested"

    def test_scan_skips_disabled(self, tmp_mods: Path) -> None:
        disabled = tmp_mods / "_disabled"
        disabled.mkdir()
        make_package(disabled / "off.package", entries=[])
        make_package(tmp_mods / "on.package", entries=[])

        scanner = ModScanner(tmp_mods)
        active = scanner.scan()
        assert len(active) == 1
        assert active[0].name == "on"

    def test_scan_disabled(self, tmp_mods: Path) -> None:
        disabled = tmp_mods / "_disabled"
        disabled.mkdir()
        make_package(disabled / "off.package", entries=[])

        scanner = ModScanner(tmp_mods)
        mods = scanner.scan_disabled()
        assert len(mods) == 1
        assert mods[0].name == "off"
        assert mods[0].enabled is False


class TestModManager:
    def test_disable_mod(self, tmp_mods: Path) -> None:
        make_package(tmp_mods / "target.package", entries=[])
        manager = ModManager(tmp_mods)
        assert manager.disable("target") is True
        assert not (tmp_mods / "target.package").exists()
        assert (tmp_mods / "_disabled" / "target.package").exists()

    def test_enable_mod(self, tmp_mods: Path) -> None:
        disabled = tmp_mods / "_disabled"
        disabled.mkdir()
        make_package(disabled / "target.package", entries=[])
        manager = ModManager(tmp_mods)
        assert manager.enable("target") is True
        assert (tmp_mods / "target.package").exists()
        assert not (disabled / "target.package").exists()

    def test_disable_nonexistent(self, tmp_mods: Path) -> None:
        manager = ModManager(tmp_mods)
        assert manager.disable("ghost_mod") is False

    def test_enable_nonexistent(self, tmp_mods: Path) -> None:
        manager = ModManager(tmp_mods)
        assert manager.enable("ghost_mod") is False

    def test_install_from_zip(self, tmp_mods: Path, tmp_path: Path) -> None:
        # Create a zip with a .package inside
        zip_path = tmp_path / "new_mod.zip"
        pkg_path = tmp_path / "inner.package"
        make_package(pkg_path, entries=[])

        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.write(pkg_path, "inner.package")

        manager = ModManager(tmp_mods)
        installed = manager.install_from_zip(zip_path)
        assert len(installed) == 1
        assert "inner.package" in installed[0]

    def test_install_skips_non_mod_files(self, tmp_mods: Path, tmp_path: Path) -> None:
        zip_path = tmp_path / "mixed.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("readme.txt", "hello")
            zf.writestr("mod.package", b"\x00" * 100)

        manager = ModManager(tmp_mods)
        installed = manager.install_from_zip(zip_path)
        assert len(installed) == 1
        assert installed[0].endswith(".package")
