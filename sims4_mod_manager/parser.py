"""DBPF v2.0 package file parser for The Sims 4.

Reads .package files (DBPF format), extracts the index table, and identifies
resource types for conflict detection and mod analysis.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


# ---------------------------------------------------------------------------
# Known resource type IDs
# ---------------------------------------------------------------------------

# Core non-tuning resource types
RESOURCE_TYPES: dict[int, str] = {
    0x0904DF10: "SimData",
    0x220557DA: "String Table (STBL)",
    0x545AC67A: "Geometry (GEOM)",
    0x034AEECB: "CAS Part",
    0xC0DB5AE7: "Combined Tuning",
    0x6017E896: "CLIP (Animation)",
    0x00B2D882: "DDS Image",
}

# Known tuning type IDs (XML-based resources that are most important for
# conflict detection).  The generic XML Tuning bucket 0x03B33009 is included.
TUNING_TYPES: dict[int, str] = {
    0x03B33009: "XML Tuning (Interaction)",
    0xCB5FDDC7: "Action Tuning",
    0xE882D22F: "Animation Tuning",
    0x0C772E27: "Aspiration Tuning",
    0x6FA49E3A: "Buff Tuning",
    0x339BC0AB: "Career Tuning",
    0xA8D58BE3: "Interaction Tuning",
    0xC6B72B88: "Lot Tuning",
    0x0069453E: "Object Tuning",
    0x48A8B92B: "Reward Tuning",
    0x02D5DF13: "Situation Tuning",
    0xE5F6C9BC: "Snippet Tuning",
    0x0B0BBE56: "Test Set Tuning",
    0x4F739CEE: "Trait Tuning",
    0x04FE5C6B: "Loot Tuning",
}

# Merge both dicts for quick lookup
_ALL_KNOWN_TYPES: dict[int, str] = {**RESOURCE_TYPES, **TUNING_TYPES}


def get_resource_type_name(type_id: int) -> str:
    """Return a human-readable name for a resource *type_id*.

    Known tuning and resource IDs are returned directly.  IDs in the range
    0x00000000-0x0FFFFFFF that are not in the known list are labelled
    "Unknown Tuning" because EA uses many unlisted tuning type IDs in that
    range.  Everything else is "Unknown".
    """
    name = _ALL_KNOWN_TYPES.get(type_id)
    if name is not None:
        return name
    if 0x00000000 <= type_id <= 0x0FFFFFFF:
        return "Unknown Tuning"
    return "Unknown"


def is_tuning_type(type_id: int) -> bool:
    """Return True if *type_id* represents an XML / tuning resource."""
    if type_id in TUNING_TYPES:
        return True
    # EA allocates many tuning type IDs in this range
    if 0x00000000 <= type_id <= 0x0FFFFFFF:
        return True
    return False


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class ResourceEntry:
    """A single resource entry from the DBPF index table."""

    type_id: int
    group_id: int
    instance_id: int
    offset: int
    size: int
    compressed: bool

    @property
    def type_name(self) -> str:
        return get_resource_type_name(self.type_id)

    @property
    def is_tuning(self) -> bool:
        return is_tuning_type(self.type_id)

    @property
    def resource_key(self) -> str:
        """Return the canonical Type-Group-Instance key string."""
        return f"{self.type_id:08X}:{self.group_id:08X}:{self.instance_id:016X}"


@dataclass(frozen=True, slots=True)
class PackageInfo:
    """Parsed summary of a .package file."""

    path: Path
    entry_count: int
    entries: List[ResourceEntry]

    @property
    def tuning_entries(self) -> List[ResourceEntry]:
        """Return only XML / tuning resource entries."""
        return [e for e in self.entries if e.is_tuning]

    @property
    def type_summary(self) -> dict[str, int]:
        """Return a {type_name: count} mapping across all entries."""
        counts: dict[str, int] = {}
        for entry in self.entries:
            name = entry.type_name
            counts[name] = counts.get(name, 0) + 1
        return counts


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class PackageParseError(Exception):
    """Raised when a .package file cannot be parsed."""


# ---------------------------------------------------------------------------
# Binary parsing helpers
# ---------------------------------------------------------------------------

_DBPF_MAGIC = b"DBPF"

# DBPF v2.0 header layout (96 bytes total):
#   0-3   : magic "DBPF"
#   4-7   : major version (u32 LE) — expect 2
#   8-11  : minor version (u32 LE) — expect 0
#  12-23  : unknown / reserved (12 bytes)
#  24-27  : creation date (u32, often 0)
#  28-31  : modified date (u32, often 0)
#  32-35  : index major version (u32)
#  36-39  : index entry count (u32)
#  40-43  : index position low (u32) — first index offset / unused in v2
#  44-47  : index size (u32)
#  48-51  : unused (u32)
#  52-55  : unused (u32)
#  56-59  : unused (u32)
#  60-63  : index version (u32) — 3 for Sims 4
#  64-67  : index position (u32) — actual byte offset of the index
#  68-71  : unused (u32)
#  72-95  : reserved / padding (24 bytes)
#
# The header is 96 bytes.  We only need a subset of fields.

_HEADER_SIZE = 96
_HEADER_STRUCT = struct.Struct("<4s I I 12s I I I I I I I I I I I I 24s")

# Index entry (32 bytes each):
#   type_id          u32
#   group_id         u32
#   instance_id_high u32  (combined into u64 instance_id)
#   instance_id_low  u32
#   offset           u32
#   size             u32  — file size OR compressed size (see flags)
#   compressed_size  u32
#   compression_type u16
#   unknown          u16
_INDEX_ENTRY_SIZE = 32
_INDEX_ENTRY_STRUCT = struct.Struct("<I I I I I I I H H")


def _read_header(data: bytes) -> tuple[int, int, int]:
    """Parse the DBPF header and return (entry_count, index_position, index_size).

    Raises PackageParseError on invalid data.
    """
    if len(data) < _HEADER_SIZE:
        raise PackageParseError(
            f"File too small for DBPF header (got {len(data)} bytes, need {_HEADER_SIZE})"
        )

    fields = _HEADER_STRUCT.unpack_from(data, 0)

    magic = fields[0]
    if magic != _DBPF_MAGIC:
        raise PackageParseError(
            f"Invalid magic number: expected {_DBPF_MAGIC!r}, got {magic!r}"
        )

    major_version = fields[1]
    minor_version = fields[2]
    if major_version != 2:
        raise PackageParseError(
            f"Unsupported DBPF version {major_version}.{minor_version} (expected 2.0)"
        )

    entry_count = fields[7]   # index entry count at offset 36
    index_size = fields[9]    # index size at offset 44
    index_position = fields[14]  # index position at offset 64

    return entry_count, index_position, index_size


def _read_index_entries(
    data: bytes,
    index_position: int,
    entry_count: int,
    index_size: int,
) -> List[ResourceEntry]:
    """Parse the index table and return a list of ResourceEntry objects."""
    # Sims 4 DBPF v2.0 uses a "flags" header at the start of the index block.
    # The first 4 bytes of the index are a flags/index_type field that controls
    # which TGI fields are constant across all entries:
    #   bit 0 (0x01) — type_id is constant (4 bytes follow flags)
    #   bit 1 (0x02) — group_id is constant (4 bytes follow)
    #   bit 2 (0x04) — instance_id high is constant (4 bytes follow)
    #
    # After the constant fields, each entry stores only the variable fields
    # plus offset, sizes, and compression info.

    if index_position + index_size > len(data):
        raise PackageParseError(
            f"Index table extends beyond file "
            f"(position={index_position}, size={index_size}, file_len={len(data)})"
        )

    if entry_count == 0:
        return []

    pos = index_position

    # Read the index flags
    if pos + 4 > len(data):
        raise PackageParseError("Truncated index: cannot read flags")
    (index_flags,) = struct.unpack_from("<I", data, pos)
    pos += 4

    # Read constant fields based on flags
    const_type_id: Optional[int] = None
    const_group_id: Optional[int] = None
    const_instance_id_high: Optional[int] = None

    if index_flags & 0x01:
        if pos + 4 > len(data):
            raise PackageParseError("Truncated index: cannot read constant type_id")
        (const_type_id,) = struct.unpack_from("<I", data, pos)
        pos += 4

    if index_flags & 0x02:
        if pos + 4 > len(data):
            raise PackageParseError("Truncated index: cannot read constant group_id")
        (const_group_id,) = struct.unpack_from("<I", data, pos)
        pos += 4

    if index_flags & 0x04:
        if pos + 4 > len(data):
            raise PackageParseError("Truncated index: cannot read constant instance_id high")
        (const_instance_id_high,) = struct.unpack_from("<I", data, pos)
        pos += 4

    entries: List[ResourceEntry] = []

    for i in range(entry_count):
        # Read type_id
        if const_type_id is not None:
            type_id = const_type_id
        else:
            if pos + 4 > len(data):
                raise PackageParseError(f"Truncated index at entry {i}: cannot read type_id")
            (type_id,) = struct.unpack_from("<I", data, pos)
            pos += 4

        # Read group_id
        if const_group_id is not None:
            group_id = const_group_id
        else:
            if pos + 4 > len(data):
                raise PackageParseError(f"Truncated index at entry {i}: cannot read group_id")
            (group_id,) = struct.unpack_from("<I", data, pos)
            pos += 4

        # Read instance_id (high + low u32 → u64)
        if const_instance_id_high is not None:
            instance_hi = const_instance_id_high
        else:
            if pos + 4 > len(data):
                raise PackageParseError(f"Truncated index at entry {i}: cannot read instance_id high")
            (instance_hi,) = struct.unpack_from("<I", data, pos)
            pos += 4

        if pos + 4 > len(data):
            raise PackageParseError(f"Truncated index at entry {i}: cannot read instance_id low")
        (instance_lo,) = struct.unpack_from("<I", data, pos)
        pos += 4

        instance_id = (instance_hi << 32) | instance_lo

        # Read offset, compressed_size, decompressed_size, compression_type, committed
        if pos + 16 > len(data):
            raise PackageParseError(f"Truncated index at entry {i}: cannot read offset/size fields")

        (offset, size_and_flags) = struct.unpack_from("<I I", data, pos)
        pos += 8

        (decompressed_size, compression_type, committed) = struct.unpack_from("<I H H", data, pos)
        pos += 8

        # The high bit of size_and_flags is the "compressed" flag in some
        # implementations. The actual compressed size is the lower 31 bits.
        compressed_size = size_and_flags & 0x7FFFFFFF
        extended_compress_flag = bool(size_and_flags & 0x80000000)

        # Determine if the resource is compressed:
        # compression_type != 0 means some form of compression is used.
        # Common values: 0x5A42 = ZLIB, 0xFFFF = internal ref, 0 = none.
        compressed = compression_type != 0 or extended_compress_flag

        # For the "size" we report the decompressed size when available,
        # otherwise the compressed size.
        reported_size = decompressed_size if decompressed_size != 0 else compressed_size

        entries.append(
            ResourceEntry(
                type_id=type_id,
                group_id=group_id,
                instance_id=instance_id,
                offset=offset,
                size=reported_size,
                compressed=compressed,
            )
        )

    return entries


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse_package(path: Path | str) -> PackageInfo:
    """Parse a Sims 4 .package file and return a PackageInfo summary.

    Parameters
    ----------
    path:
        Path to the .package file.

    Returns
    -------
    PackageInfo with all index entries parsed.

    Raises
    ------
    PackageParseError
        On invalid magic, unsupported version, or truncated data.
    FileNotFoundError
        If *path* does not exist.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Package file not found: {path}")

    data = path.read_bytes()

    entry_count, index_position, index_size = _read_header(data)

    entries = _read_index_entries(data, index_position, entry_count, index_size)

    return PackageInfo(
        path=path,
        entry_count=entry_count,
        entries=entries,
    )


# ---------------------------------------------------------------------------
# CLI convenience — run directly to inspect a package
# ---------------------------------------------------------------------------

def _cli_main() -> None:
    """Quick CLI: ``python -m sims4_mod_manager.parser path/to/file.package``"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m sims4_mod_manager.parser <file.package>", file=sys.stderr)
        sys.exit(1)

    pkg_path = Path(sys.argv[1])
    try:
        info = parse_package(pkg_path)
    except (PackageParseError, FileNotFoundError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Package : {info.path}")
    print(f"Entries : {info.entry_count}")
    print(f"Tuning  : {len(info.tuning_entries)}")
    print()
    print("Type summary:")
    for name, count in sorted(info.type_summary.items(), key=lambda kv: -kv[1]):
        print(f"  {name:40s} {count:>6d}")
    print()
    print("First 20 entries:")
    for entry in info.entries[:20]:
        flag = "C" if entry.compressed else " "
        print(f"  [{flag}] {entry.resource_key}  {entry.type_name:30s}  {entry.size:>10,d} bytes")
    if len(info.entries) > 20:
        print(f"  ... and {len(info.entries) - 20} more")


if __name__ == "__main__":
    _cli_main()
