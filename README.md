<div align="center">

<img src="https://raw.githubusercontent.com/stark-studio-labs/.github/main/assets/stark-labs-banner.svg" alt="Stark Studio Labs" width="100%">

# sims4-mod-manager

**The mod manager The Sims 4 has always needed — but never had.**

[![Status](https://img.shields.io/badge/status-in%20development-orange)](https://github.com/stark-studio-labs/sims4-mod-manager)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Made by Stark Studio Labs](https://img.shields.io/badge/made%20by-Stark%20Studio%20Labs-blueviolet)](https://github.com/stark-studio-labs)

*Built by [Stark Studio Labs](https://github.com/stark-studio-labs)*

</div>

---

## What Is This?

**sims4-mod-manager** is a desktop application for managing your Sims 4 mod collection. Install mods from a URL, track updates automatically, detect conflicts before they crash your game, and switch between curated mod profiles without moving files around by hand.

The Sims 4 modding community is massive — tens of thousands of mods, spread across Patreon, itch.io, CurseForge, ModTheSims, and personal creator sites. There has never been a single tool that handles installation, updates, and conflict detection across all of those sources. That's what this is.

---

## Why This Exists

Every existing Sims 4 mod management solution has the same problem: it doesn't actually manage mods.

| Tool | What It Does | What It Misses |
|------|-------------|----------------|
| Manual file management | Copy `.package` files into `Mods/` | No update tracking, no conflict detection |
| Mod Organizer 2 | Excellent for Bethesda games | Not built for Sims 4's XML/Python mod structure |
| Vortex (Nexus) | Handles NexusMods releases | Most Sims 4 mods aren't on Nexus |
| CurseForge app | Works for CurseForge-hosted mods | Covers ~5% of Sims 4 mods |
| TS4 Mod Conflict Detector | Detects conflicts post-install | Read-only, no management features |

sims4-mod-manager is built specifically for The Sims 4's ecosystem — multiple distribution sources, `.package`/`.ts4script` structure, EA patch-driven breakage cycles, and the community's Patreon-first distribution model.

---

## Features (Coming)

### Core Management
- **Install from URL** — paste any download link (itch.io, Patreon, CurseForge, personal sites) and the manager handles the rest: download, extract, move to `Mods/`, register
- **Auto-update detection** — monitors mod sources and notifies you when creators release updates; one-click update without manual re-download
- **Mod profiles** — create named mod sets (e.g., "Storytelling Build", "Minimal Gameplay", "Full Install") and switch between them without moving files; great for testing or different playstyles
- **One-click backup** — snapshot your entire mod folder before an EA patch drops, restore with one click if something breaks

### Conflict Detection
- **Pre-install conflict scan** — before installing a new mod, check whether it overwrites tuning files already modified by an installed mod
- **Batch conflict audit** — scan your entire `Mods/` folder and surface all conflicts with explanations of what each conflict affects
- **Dependency resolution** — identifies when a mod requires XML Injector, Sims4CommunityLibrary, or another framework, and installs the dependency if missing
- **Post-patch impact report** — after an EA update, show which installed mods are likely affected based on the patch notes

### Organization
- **Tag-based filtering** — tag mods by category (gameplay, CC, QoL, NSFW, etc.) and filter your library instantly
- **Creator tracking** — follow creators and see all their mods in one place; get notified when they release something new
- **Mod notes** — attach personal notes to mods ("breaks with Slice of Life", "need to configure on first run")
- **Bulk enable/disable** — toggle mods without deleting them, useful for isolating issues

### Intelligence
- **Community status feed** — pulls from SimsVIP and community patch trackers to surface which of your installed mods are broken after the latest EA patch
- **Load time estimator** — estimates game load time impact as you add mods
- **Duplicate detector** — flags when you have two copies of the same mod (common after re-downloads)

---

## How It Differs From Manual Management

If you've been managing mods by hand, here's what changes:

**Before (manual):**
1. Find a mod on Patreon or itch.io
2. Download a `.zip` file
3. Open the zip, find the `.package` files
4. Navigate to `Documents/Electronic Arts/The Sims 4/Mods/`
5. Create a subfolder
6. Move the files
7. Repeat for each update, forever
8. If something breaks after a patch, guess which of your 200+ mods is the problem

**After (sims4-mod-manager):**
1. Paste the download URL
2. Done
3. When there's an update, click Update
4. When something breaks, run the conflict scan

---

## Technical Approach

- **Platform:** Electron + React (cross-platform desktop: Windows, Mac)
- **Mod parsing:** Direct `.package` file parsing to extract tuning XML — no reliance on game files
- **Source connectors:** Pluggable source adapters for each distribution platform (Patreon, itch.io, CurseForge, ModTheSims, direct URL)
- **Storage:** Local SQLite database for mod registry, no cloud dependency
- **Conflict detection:** XML tuning file comparison at the instance/resource key level — the same approach used by TS4 Mod Conflict Detector, extended with resolution suggestions

---

## Status

In active development. No release date yet.

Follow [Stark Studio Labs](https://github.com/stark-studio-labs) for updates. If you want to contribute or have feature requests, open an issue.

---

## Related Projects

- [awesome-sims4-mods](https://github.com/stark-studio-labs/awesome-sims4-mods) — Curated mod directory
- [sims4-mod-builder](https://github.com/stark-studio-labs/sims4-mod-builder) — Visual mod creation tool

---

<div align="center">

**Built with 💚 by [Stark Studio Labs](https://github.com/stark-studio-labs)**

</div>
