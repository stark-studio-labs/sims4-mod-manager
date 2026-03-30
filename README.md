<div align="center">

# Stark Labs Mod Manager

**The one-click installer for Stark Labs Sims 4 mods.**

[![Status](https://img.shields.io/badge/status-beta-blue)](https://github.com/stark-studio-labs/sims4-mod-manager)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Electron](https://img.shields.io/badge/electron-33-47848f)](https://www.electronjs.org/)
[![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey)]()
[![Made by Stark Labs](https://img.shields.io/badge/made%20by-Stark%20Labs-blueviolet)](https://github.com/stark-studio-labs)

</div>

---

## What This Is

A desktop app that installs, updates, and manages every Stark Labs mod for The Sims 4. Think Steam's game library but for mods. Download it, click Install, play.

- **Auto-detects** your Sims 4 Mods folder (Mac, Windows, Linux)
- **One-click install** for Economy Sim, Political Sim, Social Sim, QoL Pack, Drama Engine, Smart Sims
- **Auto-enables** script mods in Options.ini
- **Checks for updates** from GitHub Releases on launch
- **Clean uninstall** removes mod files without touching anything else

---

## Stark Labs Ecosystem

| Repo | What It Does | Status |
|------|-------------|--------|
| **[sims4-stark-framework](https://github.com/stark-studio-labs/sims4-stark-framework)** | Modern typed modding framework | Active |
| **[sims4-stark-devkit](https://github.com/stark-studio-labs/sims4-stark-devkit)** | CLI toolkit for mod development | Active |
| **[sims4-mod-manager](https://github.com/stark-studio-labs/sims4-mod-manager)** | One-click mod installer (this repo) | Beta |
| **[sims4-economy-sim](https://github.com/stark-studio-labs/sims4-economy-sim)** | Banking, bills, stock market | Pre-Alpha |
| **[sims4-political-sim](https://github.com/stark-studio-labs/sims4-political-sim)** | Elections, parties, policy | Pre-Alpha |
| **[sims4-social-sim](https://github.com/stark-studio-labs/sims4-social-sim)** | Reputation, social media, cliques | Pre-Alpha |
| **[sims4-drama-engine](https://github.com/stark-studio-labs/sims4-drama-engine)** | Emergent storylines and events | Pre-Alpha |
| **[sims4-smart-sims](https://github.com/stark-studio-labs/sims4-smart-sims)** | Better AI autonomy | Pre-Alpha |
| **[sims4-qol-pack](https://github.com/stark-studio-labs/sims4-qol-pack)** | 50+ quality-of-life fixes | Pre-Alpha |

---

## Quick Start

```bash
# Clone and install
git clone https://github.com/stark-studio-labs/sims4-mod-manager.git
cd sims4-mod-manager
npm install

# Run in dev mode
npm run dev

# Build for your platform
npm run build:mac    # macOS .dmg
npm run build:win    # Windows .exe installer
npm run build:linux  # Linux AppImage
```

---

## Architecture

```
src/
  main/
    main.js          # Electron main process, IPC handlers, window management
    mod-manager.js   # Mod catalog, path detection, install/uninstall, Options.ini
    updater.js       # Auto-updater via electron-updater (GitHub Releases)
  preload/
    preload.js       # Context bridge — secure IPC between main and renderer
  renderer/
    index.html       # App shell — titlebar, sidebar, views
    styles.css       # Dark theme, glassmorphism, Plumbob accents
    app.js           # View router, mod grid, settings, toast notifications
```

### How It Works

1. **First launch** — Welcome screen auto-detects `~/Documents/Electronic Arts/The Sims 4/Mods/`
2. **Mod catalog** — Cards for each Stark mod with name, version, size, tags, install status
3. **Install** — Downloads from GitHub Releases (or creates placeholders in dev mode), copies to Mods folder
4. **Script mods** — Automatically writes `scriptmodsenabled = 1` to Options.ini
5. **Updates** — Checks GitHub Releases API for newer versions of installed mods
6. **Uninstall** — Deletes only the files the manager installed

---

## Supported Mods

| Mod | Description | Script Mod |
|-----|-------------|:----------:|
| **Economy Sim** | Banking, bills, dynamic job market, stock market | Yes |
| **Political Sim** | Elections, parties, policy effects, government careers | Yes |
| **Social Sim** | Reputation, social media, cliques, relationship dynamics | Yes |
| **QoL Pack** | Faster loads, better autonomy, UI fixes, 50+ improvements | Yes |
| **Drama Engine** | Emergent storylines, neighborhood events, rivalries | Yes |
| **Smart Sims** | Better AI autonomy, smarter pathfinding, context-aware decisions | Yes |

---

## Building

Cross-platform packaging via electron-builder:

```bash
# macOS (DMG + ZIP)
npm run build:mac

# Windows (NSIS installer)
npm run build:win

# Linux (AppImage + deb)
npm run build:linux

# All platforms
npm run build
```

Output goes to `dist/`.

---

## Development

```bash
# Install dependencies
npm install

# Run with DevTools
npm run dev

# Package without full installer (for testing)
npm run pack
```

---

## ⚖️ How It Compares

| Feature | Manual (current reality) | Sims 4 Studio | sims4-mod-manager |
|---------|--------------------------|---------------|-------------------|
| Conflict detection | None — find out when game crashes | None | ✅ DBPF-level resource key collision scan |
| Conflict severity | Unknown | Unknown | ✅ High/Medium/Low by resource type |
| Enable/disable mods | Delete or move files manually | No | ✅ `s4mm disable` — moves to `_disabled/` |
| Install from ZIP | Unzip manually, drag files | Partial (for S4S assets) | ✅ `s4mm install mod.zip` |
| Scan mod collection | Open each file manually | Partial | ✅ `s4mm scan` — full table with metadata |
| Resource count per mod | Unknown | Visible in S4S | ✅ Shown in scan output |
| CLI workflow | None | None — GUI only | ✅ Full CLI with `--mods-dir` override |
| Conflict detail | None | None | ✅ Which mods conflict, which resource type |
| Batch operations | None | None | 📋 Planned |
| Dependency detection | None | None | 📋 Planned |
| Auto-update check | None | None | 📋 Planned |
| CAS / mesh editing | N/A | ✅ Primary feature | ❌ Out of scope |

> **Note:** Sims 4 Studio is the gold standard for asset editing and recoloring. sims4-mod-manager focuses exclusively on script and tuning mod management — conflict detection, install, enable/disable.

---

## 🗺️ Roadmap

| Feature | Status | Notes |
|---------|--------|-------|
| DBPF v2.0 binary parser | ✅ Shipped | Reads .package index tables at binary level |
| `s4mm scan` — full collection scan | ✅ Shipped | Rich table output with metadata |
| `s4mm list` — filtered/sorted listing | ✅ Shipped | Filter by type, sort by name/size/date |
| `s4mm enable/disable` — toggle mods | ✅ Shipped | Moves to/from `_disabled/` subfolder |
| `s4mm conflicts` — conflict report | ✅ Shipped | High/Medium/Low severity classification |
| `s4mm install` — install from ZIP | ✅ Shipped | Extracts and places mod files |
| `s4mm info` — detailed mod view | ✅ Shipped | Resources, path, size, status |
| 42 pytest tests | ✅ Shipped | Parser, manager, conflict, CLI coverage |
| `s4mm status` — quick overview | ✅ Shipped | Active count, total size, conflict summary |
| Mod profiles — switch mod sets | 🔨 In Progress | Save/restore named sets of enabled mods |
| Pre-install conflict scan | 📋 Planned | Warn about conflicts before installing |
| Dependency detection | 📋 Planned | Detect missing XML Injector, S4CL, etc. |
| Auto-update check | 📋 Planned | Poll mod sources for new versions |
| Web/TUI dashboard | 📋 Planned | Visual alternative to CLI |
| CurseForge API integration | 📋 Planned | One-click install from CurseForge |
| .package write support | ❌ Out of Scope | Read-only — use S4TK or S4S to create |
| CAS / mesh editing | ❌ Out of Scope | Use Sims 4 Studio |

---

<div align="center">

**Built by [Stark Labs](https://github.com/stark-studio-labs)**

*Making The Sims 4 modding less painful, one tool at a time.*

</div>
