"""Scanning and management of Sims 4 mods (.package and .ts4script files)."""

from __future__ import annotations

import logging
import platform
import shutil
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable

from sims4_mod_manager.parser import parse_package

logger = logging.getLogger(__name__)

DISABLED_FOLDER = "_disabled"
MOD_EXTENSIONS = {".package", ".ts4script"}
# The Sims 4 only reads .ts4script from the Mods root or one subfolder deep.
TS4SCRIPT_MAX_DEPTH = 1


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ModInfo:
    """Metadata for a single mod file."""

    name: str
    path: Path
    mod_type: str  # "package" | "ts4script" | "unknown"
    size: int
    modified: datetime
    enabled: bool
    entry_count: int = 0
    error: str | None = None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def format_size(size_bytes: int) -> str:
    """Return a human-readable file size string."""
    if size_bytes < 0:
        raise ValueError("size_bytes must be non-negative")
    if size_bytes < 1024:
        return f"{size_bytes} B"
    for unit in ("KB", "MB", "GB", "TB"):
        size_bytes /= 1024.0
        if size_bytes < 1024.0 or unit == "TB":
            return f"{size_bytes:.1f} {unit}"
    # unreachable, but keeps mypy happy
    return f"{size_bytes:.1f} TB"  # pragma: no cover


def find_mods_folder() -> Path | None:
    """Try to auto-detect the Sims 4 Mods folder on the current platform.

    Returns the path if found, otherwise ``None``.
    """
    system = platform.system()

    candidates: list[Path] = []
    if system == "Darwin":
        candidates.append(
            Path.home() / "Documents" / "Electronic Arts" / "The Sims 4" / "Mods"
        )
    elif system == "Windows":
        candidates.append(
            Path.home() / "Documents" / "Electronic Arts" / "The Sims 4" / "Mods"
        )
    elif system == "Linux":
        # Proton / Lutris common location
        candidates.append(
            Path.home()
            / ".local"
            / "share"
            / "Steam"
            / "steamapps"
            / "compatdata"
            / "1222670"
            / "pfx"
            / "drive_c"
            / "users"
            / "steamuser"
            / "Documents"
            / "Electronic Arts"
            / "The Sims 4"
            / "Mods"
        )

    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    return None


def _mod_type_for(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".package":
        return "package"
    if suffix == ".ts4script":
        return "ts4script"
    return "unknown"


def _relative_depth(child: Path, root: Path) -> int:
    """Return how many directories deep *child* is relative to *root*."""
    return len(child.relative_to(root).parents) - 1


def _build_mod_info(path: Path, *, enabled: bool) -> ModInfo:
    """Build a ``ModInfo`` from a file path, parsing .package entries."""
    stat = path.stat()
    mod_type = _mod_type_for(path)
    entry_count = 0
    error: str | None = None

    if mod_type == "package":
        try:
            pkg = parse_package(path)
            entry_count = pkg.entry_count
        except Exception as exc:  # noqa: BLE001
            error = str(exc)
            logger.warning("Failed to parse %s: %s", path, exc)

    return ModInfo(
        name=path.stem,
        path=path,
        mod_type=mod_type,
        size=stat.st_size,
        modified=datetime.fromtimestamp(stat.st_mtime),
        enabled=enabled,
        entry_count=entry_count,
        error=error,
    )


# ---------------------------------------------------------------------------
# ModScanner
# ---------------------------------------------------------------------------

class ModScanner:
    """Recursively discover mod files inside a Sims 4 Mods folder."""

    def __init__(self, mods_path: Path) -> None:
        self.mods_path = mods_path

    # -- public API ---------------------------------------------------------

    def scan(self) -> list[ModInfo]:
        """Return ``ModInfo`` for every enabled mod.

        * ``.package`` files are found at any depth.
        * ``.ts4script`` files are found only at depth 0 or 1 (game
          limitation).
        * Files inside ``_disabled/`` are excluded.
        """
        if not self.mods_path.is_dir():
            logger.warning("Mods folder does not exist: %s", self.mods_path)
            return []

        results: list[ModInfo] = []
        disabled_dir = self.mods_path / DISABLED_FOLDER

        for path in self.mods_path.rglob("*"):
            if not path.is_file():
                continue
            # Skip anything inside the disabled folder.
            if _is_inside(path, disabled_dir):
                continue

            suffix = path.suffix.lower()
            if suffix == ".package":
                results.append(_build_mod_info(path, enabled=True))
            elif suffix == ".ts4script":
                depth = _relative_depth(path, self.mods_path)
                if depth <= TS4SCRIPT_MAX_DEPTH:
                    results.append(_build_mod_info(path, enabled=True))

        return results

    def scan_disabled(self) -> list[ModInfo]:
        """Return ``ModInfo`` for every mod inside ``_disabled/``."""
        disabled_dir = self.mods_path / DISABLED_FOLDER
        if not disabled_dir.is_dir():
            return []

        results: list[ModInfo] = []
        for path in disabled_dir.rglob("*"):
            if path.is_file() and path.suffix.lower() in MOD_EXTENSIONS:
                results.append(_build_mod_info(path, enabled=False))
        return results

    # -- class helpers ------------------------------------------------------

    @staticmethod
    def get_default_mods_path() -> Path:
        """Return the default Mods path for macOS / Windows."""
        return (
            Path.home() / "Documents" / "Electronic Arts" / "The Sims 4" / "Mods"
        )


# ---------------------------------------------------------------------------
# ModManager
# ---------------------------------------------------------------------------

class ModManager:
    """Enable, disable, install, and uninstall Sims 4 mods."""

    def __init__(self, mods_path: Path) -> None:
        self.mods_path = mods_path
        self._scanner = ModScanner(mods_path)

    # -- public API ---------------------------------------------------------

    def disable(self, mod_name: str) -> bool:
        """Move every file whose stem matches *mod_name* into ``_disabled/``.

        The relative path beneath ``Mods/`` is preserved so that
        :meth:`enable` can put it back.  Returns ``True`` if at least one
        file was moved.
        """
        disabled_dir = self.mods_path / DISABLED_FOLDER
        moved = False

        for mod in self._scanner.scan():
            if mod.name != mod_name:
                continue

            rel = mod.path.relative_to(self.mods_path)
            dest = disabled_dir / rel
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(mod.path), str(dest))
                moved = True
                logger.info("Disabled %s -> %s", mod.path, dest)
            except OSError as exc:
                logger.error("Could not disable %s: %s", mod.path, exc)

        return moved

    def enable(self, mod_name: str) -> bool:
        """Move every file whose stem matches *mod_name* from ``_disabled/``
        back to its original location.  Returns ``True`` on success.
        """
        disabled_dir = self.mods_path / DISABLED_FOLDER
        moved = False

        for mod in self._scanner.scan_disabled():
            if mod.name != mod_name:
                continue

            rel = mod.path.relative_to(disabled_dir)
            dest = self.mods_path / rel
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(mod.path), str(dest))
                moved = True
                logger.info("Enabled %s -> %s", mod.path, dest)
            except OSError as exc:
                logger.error("Could not enable %s: %s", mod.path, exc)

        return moved

    def install_from_zip(self, zip_path: Path) -> list[str]:
        """Extract mod files from a ZIP archive into ``Mods/<zip_stem>/``.

        Only ``.package`` and ``.ts4script`` files are extracted; everything
        else is silently skipped.  Returns the list of installed file names.
        """
        if not zip_path.is_file():
            raise FileNotFoundError(f"ZIP not found: {zip_path}")

        subfolder = self.mods_path / zip_path.stem
        subfolder.mkdir(parents=True, exist_ok=True)
        installed: list[str] = []

        with zipfile.ZipFile(zip_path, "r") as zf:
            for info in zf.infolist():
                if info.is_dir():
                    continue
                member_path = Path(info.filename)
                if member_path.suffix.lower() not in MOD_EXTENSIONS:
                    continue

                # Flatten nested directories -- place mod files directly in
                # the subfolder so they stay within the game's depth limit.
                dest = subfolder / member_path.name

                # Handle duplicate names by appending a counter.
                if dest.exists():
                    stem = dest.stem
                    suffix = dest.suffix
                    counter = 1
                    while dest.exists():
                        dest = subfolder / f"{stem}_{counter}{suffix}"
                        counter += 1

                with zf.open(info) as src, open(dest, "wb") as dst:
                    shutil.copyfileobj(src, dst)

                installed.append(dest.name)
                logger.info("Installed %s -> %s", info.filename, dest)

        return installed

    def uninstall(
        self,
        mod_name: str,
        *,
        confirm: Callable[[list[Path]], bool] | None = None,
    ) -> bool:
        """Delete all files whose stem matches *mod_name*.

        If *confirm* is provided it is called with the list of paths that
        will be deleted.  Deletion proceeds only if it returns ``True``.
        Returns ``True`` if at least one file was removed.
        """
        # Gather from both enabled and disabled locations.
        targets: list[Path] = []
        for mod in self._scanner.scan():
            if mod.name == mod_name:
                targets.append(mod.path)
        for mod in self._scanner.scan_disabled():
            if mod.name == mod_name:
                targets.append(mod.path)

        if not targets:
            return False

        if confirm is not None and not confirm(targets):
            return False

        deleted = False
        for path in targets:
            try:
                path.unlink()
                deleted = True
                logger.info("Uninstalled %s", path)
            except OSError as exc:
                logger.error("Could not delete %s: %s", path, exc)

        return deleted


# ---------------------------------------------------------------------------
# Private utilities
# ---------------------------------------------------------------------------

def _is_inside(child: Path, parent: Path) -> bool:
    """Return ``True`` if *child* is the same as or inside *parent*."""
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False
