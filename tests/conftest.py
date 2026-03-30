"""Shared test fixtures for sims4-mod-manager tests."""
from __future__ import annotations

import struct
from pathlib import Path

import pytest


@pytest.fixture
def tmp_mods(tmp_path: Path) -> Path:
    """Create a temporary Mods directory structure."""
    mods = tmp_path / "Mods"
    mods.mkdir()
    return mods


def make_package(path: Path, entries: list[tuple[int, int, int]] | None = None) -> Path:
    """Create a minimal valid .package (DBPF v2.0) file.

    entries: list of (type_id, group_id, instance_id) tuples.
    Each entry gets a dummy 16-byte data block.
    """
    if entries is None:
        entries = []

    n = len(entries)
    data_start = 96  # header size
    entry_data_size = 16
    total_data = n * entry_data_size
    index_offset = data_start + total_data

    # Index: 4-byte flags + n * 32-byte entry records
    # With flags=0 (no constant fields), each record is the full 32 bytes
    index_size = 4 + n * 32

    # DBPF header: 96 bytes, matching parser's _HEADER_STRUCT = "<4s I I 12s I I I I I I I I I I I I 24s"
    # fields[0]  = magic (4s)
    # fields[1]  = major version (I)
    # fields[2]  = minor version (I)
    # fields[3]  = unknown 12 bytes (12s)
    # fields[4]  = creation date (I)
    # fields[5]  = modified date (I)
    # fields[6]  = index major version (I)
    # fields[7]  = index entry count (I)     <-- n
    # fields[8]  = index position low (I)    <-- 0 (unused)
    # fields[9]  = index size (I)            <-- index_size
    # fields[10] = unused (I)
    # fields[11] = unused (I)
    # fields[12] = unused (I)
    # fields[13] = index version (I)         <-- 3
    # fields[14] = index position (I)        <-- index_offset
    # fields[15] = unused (I)
    # fields[16] = reserved (24s)
    header = struct.pack(
        "<4s I I 12s I I I I I I I I I I I I 24s",
        b"DBPF",         # magic
        2,               # major version
        0,               # minor version
        b"\x00" * 12,    # unknown
        0,               # creation date
        0,               # modified date
        0,               # index major version
        n,               # index entry count
        0,               # index position low (unused)
        index_size,      # index size
        0,               # unused
        0,               # unused
        0,               # unused
        3,               # index version
        index_offset,    # index position
        0,               # unused
        b"\x00" * 24,    # reserved
    )
    assert len(header) == 96

    # Dummy data blocks
    data_blocks = b"\x00" * total_data

    # Index: flags (no constant fields) + entry records
    index = struct.pack("<I", 0)  # flags = 0
    for i, (type_id, group_id, instance_id) in enumerate(entries):
        instance_hi = (instance_id >> 32) & 0xFFFFFFFF
        instance_lo = instance_id & 0xFFFFFFFF
        offset = data_start + i * entry_data_size
        index += struct.pack(
            "<I I I I I I I H H",
            type_id,
            group_id,
            instance_hi,
            instance_lo,
            offset,
            entry_data_size,   # size
            entry_data_size,   # compressed_size
            0,                 # compression_type (0 = uncompressed)
            0,                 # unknown
        )

    content = header + data_blocks + index
    path.write_bytes(content)
    return path
