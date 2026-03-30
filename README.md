<div align="center">

# 📦 sims4-mod-manager

**The mod manager The Sims 4 has always needed.**

[![Status](https://img.shields.io/badge/status-alpha-orange)](https://github.com/stark-studio-labs/sims4-mod-manager)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-42%20passed-brightgreen)]()
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)]()
[![Made by Stark Studio Labs](https://img.shields.io/badge/made%20by-Stark%20Studio%20Labs-blueviolet)](https://github.com/stark-studio-labs)

</div>

---

## 🌐 Stark Labs Ecosystem

> Everything we build for The Sims 4 modding community — open source, interconnected, and community-driven.

| Repo | What It Does | Status |
|------|-------------|--------|
| 📚 **[awesome-sims4-mods](https://github.com/stark-studio-labs/awesome-sims4-mods)** | Curated mod directory with compatibility tracking | ![Active](https://img.shields.io/badge/-active-brightgreen) |
| 🧱 **[sims4-stark-framework](https://github.com/stark-studio-labs/sims4-stark-framework)** | Modern typed modding framework (replaces S4CL patterns) | ![Active](https://img.shields.io/badge/-active-brightgreen) |
| 🔧 **[sims4-stark-devkit](https://github.com/stark-studio-labs/sims4-stark-devkit)** | CLI toolkit — decompile, package, scaffold, test | ![Active](https://img.shields.io/badge/-active-brightgreen) |
| 📦 **[sims4-mod-manager](https://github.com/stark-studio-labs/sims4-mod-manager)** | Scan, organize, and detect conflicts in your mod collection | ![Alpha](https://img.shields.io/badge/-alpha-orange) |
| 🎨 **[sims4-mod-builder](https://github.com/stark-studio-labs/sims4-mod-builder)** | Visual mod creation tool — no XML knowledge needed | ![In Dev](https://img.shields.io/badge/-in%20dev-yellow) |
| 🔬 **[sims4-mod-revival](https://github.com/stark-studio-labs/sims4-mod-revival)** | Decompile and revive abandoned community mods | ![Active](https://img.shields.io/badge/-active-brightgreen) |
| 💰 **[sims4-economy-sim](https://github.com/stark-studio-labs/sims4-economy-sim)** | Banking, bills, jobs, and stock market overhaul mod | ![Pre-Alpha](https://img.shields.io/badge/-pre--alpha-red) |

---

## 📖 Table of Contents

- [😤 The Problem](#-the-problem)
- [🔍 What It Does](#-what-it-does)
- [🚀 Quick Start](#-quick-start)
- [📋 Features](#-features)
- [📥 Install](#-install)
- [⚡ Commands](#-commands)
- [🏗️ Architecture](#️-architecture)
- [💥 How Conflict Detection Works](#-how-conflict-detection-works)
- [🔬 Development](#-development)
- [🗺️ Roadmap](#️-roadmap)

---

## 😤 The Problem

- You have **200+ mods** and the game just crashes. Which one broke? 🤷
- Two mods override the **same interaction** — but you only find out when behavior is wrong
- Unzipping mods into the right folder is **tedious and error-prone**
- After a game update, you need to **check every mod manually** for compatibility
- There's no good way to **disable a mod temporarily** without deleting it

This tool fixes all of that.

---

## 🔍 What It Does

A Python CLI tool that scans, organizes, and manages your Sims 4 mod collection. Built on a real DBPF v2.0 parser that reads `.package` files at the binary level to detect conflicts before they crash your game.

```
$ s4mm scan

 ____  _                _  _    __  __           _
/ ___|(_)_ __ ___  ___ | || |  |  \/  | ___   __| |
\___ \| | '_ ` _ \/ __|| || |_ | |\/| |/ _ \ / _` |
 ___) | | | | | | \__ \|__   _|| |  | | (_) | (_| |
|____/|_|_| |_| |_|___/   |_|  |_|  |_|\___/ \__,_|
                                    Manager v0.1.0

Scanning: ~/Documents/Electronic Arts/The Sims 4/Mods/

            Active Mods (47)
 Name                  Type        Size  Resources  Modified
 basemental_drugs      .package    85 MB     3,412  2026-03-15
 mc_cmd_center         .ts4script  12 MB         -  2026-03-20
 ui_cheats_extension   .package     2 MB       156  2026-03-18
 ...

Summary: 47 active, 3 disabled, 412 MB total
```

---

## 🚀 Quick Start

```bash
# Install
pip install -e .

# See what's in your Mods folder
s4mm scan

# Check for conflicts between mods
s4mm conflicts

# Disable a broken mod without deleting it
s4mm disable "BrokenMod"
```

---

## 📋 Features

- **🔍 Scan** -- recursively finds all `.package` and `.ts4script` mods with resource counts and metadata
- **📃 List** -- filter by type, sort by name/size/date
- **🔀 Enable/Disable** -- toggle mods without deleting them (moves to `_disabled/` subfolder)
- **💥 Conflict Detection** -- parses DBPF index tables to find resource key collisions (same type+group+instance ID across multiple mods), classified by severity (high/medium/low)
- **📥 Install** -- extract mods from `.zip` files directly into your Mods folder
- **ℹ️ Info** -- detailed view of any mod (resources, path, size, status)

---

## 📥 Install

```bash
pip install -e .

# Or just run directly:
python -m sims4_mod_manager.cli scan
```

---

## ⚡ Commands

| Command | Description |
|---------|-------------|
| `s4mm scan` | Full scan with rich table output |
| `s4mm list --type package --sort size` | Filtered, sorted list |
| `s4mm disable ModName` | Move mod to `_disabled/` |
| `s4mm enable ModName` | Restore from `_disabled/` |
| `s4mm conflicts` | Scan for resource conflicts with severity report |
| `s4mm install path/to/mod.zip` | Extract and install from ZIP |
| `s4mm info ModName` | Detailed mod info |
| `s4mm status` | Quick overview |

All commands accept `--mods-dir /path/to/Mods` to override auto-detection.

---

## 🏗️ Architecture

```
sims4_mod_manager/
  parser.py     -- DBPF v2.0 binary parser (reads .package index tables)
  manager.py    -- Mod scanner, enable/disable, ZIP installer
  conflicts.py  -- Resource conflict detection with severity classification
  cli.py        -- Rich TUI CLI (click + rich)
```

---

### 💥 How Conflict Detection Works

Every `.package` file is a DBPF container with an index table mapping resources by `(type_id, group_id, instance_id)`. When two mods contain entries with the same key, the game loads the last one -- silently overriding the first. This tool detects those collisions and classifies them:

- 🔴 **High** -- tuning overrides (interactions, traits, buffs, objects, careers) that change gameplay
- 🟡 **Medium** -- string tables and SimData that may cause text glitches
- 🟢 **Low** -- meshes, textures, animations (visual only, last-loaded wins)

---

## 🔬 Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests (42 tests)
pytest tests/ -v

# Run a specific test module
pytest tests/test_parser.py -v
```

---

## 🗺️ Roadmap

- [ ] 🔄 Auto-update detection (check mod sources for new versions)
- [ ] 🎭 Mod profiles (switch between mod sets)
- [ ] 🛡️ Pre-install conflict scan
- [ ] 🔗 Dependency resolution (detect missing XML Injector, S4CL, etc.)
- [ ] 🖥️ Web/TUI dashboard
- [ ] 🌐 CurseForge API integration

---

<div align="center">

**Built with 💜 by [Stark Studio Labs](https://github.com/stark-studio-labs)**

*Making The Sims 4 modding less painful, one tool at a time.*

</div>
