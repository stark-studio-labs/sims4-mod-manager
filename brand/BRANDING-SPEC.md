# Stark Labs Mod Manager — Branding Specification
**Authored by:** Victor Nolan-Carter, CCO  
**Date:** 2026-03-30  
**Version:** 3.0 — APPROVED ✅  
**Status:** Production-locked. No deviations without CCO sign-off.

---

## Design Foundation

### Token System (from live codebase)
```
--bg-primary:    #0d1117   (near-black base)
--bg-secondary:  #161b22   (elevated surfaces)
--bg-tertiary:   #1c2128
--bg-elevated:   #21262d

--text-primary:  #e6edf3
--text-secondary:#8b949e
--text-muted:    #484f58

--accent:        #4ade80   (Plumbob green — PRIMARY BRAND COLOR)
--accent-dim:    #22c55e
--accent-bg:     rgba(74,222,128,0.08)

--danger:        #f85149
--warning:       #d29922
--info:          #58a6ff
```

### Brand Voice (Visual)
- Dark, premium, editorial
- Plumbob green as the single vivid signature
- Glassmorphism: `rgba(22, 27, 34, 0.75)` + `backdrop-filter: blur`
- No gradients except the Plumbob glow aura
- Typography: system sans-serif stack, tight tracking, clean hierarchy

---

## Mod Layer Color System

Each layer has a distinct color. These must be consistent across all surfaces.

| Mod | Layer | Color | Hex | Emoji |
|-----|-------|-------|-----|-------|
| Economy Sim | Economy | Green | `#2ea043` | 💰 |
| Social Sim | Social | Red/Coral | `#e05d44` | 💬 |
| QoL Pack | Quality of Life | Blue | `#0969da` | ⚡ |
| Drama Engine | Drama | Amber/Gold | `#d4a017` | 🎭 |
| Political Sim | Politics | Purple | `#8957e5` | 🏛️ |
| Smart Sims | Intelligence | Teal/Cyan | `#1f9ada` | 🧠 |

> **Rule:** Background tint at 12% opacity, border at 30% opacity. Never full-saturation fill on dark bg.

---

## Asset Deliverables

### 1. App Icon — Plumbob Diamond

**Concept:** The Plumbob diamond form, redrawn in Stark Labs aesthetic.
- Geometric diamond (not the Sims default shape — sharper, more editorial)
- Fill: Deep void (`#0d1117`) body
- Facets: Three-value split — `#0d1117` (shadow), `#1c2128` (mid), `#4ade80` glow edge
- Glow halo: `rgba(74, 222, 128, 0.35)` radial behind diamond
- "SL" monogram in center at small sizes (512px and below)
- No text at 32px and below — icon reads as pure diamond

**Sizes required:**
- `icon.png` — 1024×1024 (master)
- `icon-512.png` — 512×512
- `icon-256.png` — 256×256
- `icon-128.png` — 128×128
- `icon-64.png` — 64×64
- `icon-32.png` — 32×32
- `icon-16.png` — 16×16
- `icon.icns` — macOS (bundled from above pngs)
- `icon.ico` — Windows (bundled from above pngs)

**File:** `brand/icons/icon-master.svg` → rasterize at each size

---

### 2. Six Mod Card Thumbnails

**Dimensions:** 200×120px (card art) + 48×48px (icon badge)
**Format:** PNG with transparency for badge; solid dark bg for card

**Template pattern:**
```
┌─────────────────────────────────────────────┐
│  [LAYER COLOR gradient, 15° diagonal wash]  │
│  Large emoji center (72px)                  │
│  Mod name bottom-left, 12px, weight 600     │
│  "STARK LABS" top-right, 9px, muted         │
└─────────────────────────────────────────────┘
```

**Files:**
- `brand/mod-cards/economy-sim-card.png`
- `brand/mod-cards/social-sim-card.png`
- `brand/mod-cards/qol-pack-card.png`
- `brand/mod-cards/drama-engine-card.png`
- `brand/mod-cards/political-sim-card.png`
- `brand/mod-cards/smart-sims-card.png`

---

### 3. Mac DMG Background

**Dimensions:** 660×400px (standard macOS DMG canvas)
**Format:** PNG

**Layout:**
```
Left half:   App icon (256px) + arrow pointing right
Right half:  Applications folder alias icon (system)
Background:  Dark (#0d1117) with subtle grid pattern or Plumbob watermark at 8% opacity
Bottom:      "Stark Labs Mod Manager" wordmark, centered, `--text-secondary` color
Corner:      Version string (e.g., "v1.0.0"), bottom-right, muted
```

**File:** `brand/installer/dmg-background.png`

---

### 4. Windows NSIS Installer Graphics

**Sidebar image:** 164×314px (NSIS Wizard Left Panel)
- Vertical composition
- Plumbob icon top-center (128px)
- "STARK LABS" vertical text or stacked wordmark
- Accent green strip along left edge (4px)
- Dark bg `#0d1117`

**Header banner:** 497×58px (NSIS Wizard Header)  
- "Stark Labs" wordmark left-aligned
- Subtitle: "Mod Manager" right-aligned
- Thin accent green underline
- White text on dark bg

**Files:**
- `brand/installer/nsis-sidebar.bmp` (BMP required by NSIS)
- `brand/installer/nsis-header.bmp`

---

### 5. Splash / Welcome Screen Banner

**Dimensions:** 800×320px
**Format:** PNG

**Layout:**
```
Background: #0d1117 with subtle radial glow (Plumbob green, center-left, 30% opacity)
Left:        Plumbob icon (200px) with glow aura
Center:      "STARK LABS MOD MANAGER" — H1, large, tracked
             "Install once. Play forever." — tagline, --text-secondary
Right:       "v3 Forge Edition" badge (pill, green border)
```

> Note: Chairman references "v3 forge" — this banner should carry that edition badge.

**File:** `brand/installer/splash-banner.png`

---

## Typography Rules

| Use Case | Weight | Size | Color |
|----------|--------|------|-------|
| Brand wordmark | 700 | 18-24px | `#e6edf3` |
| Section headers | 600 | 14-16px | `#e6edf3` |
| Body copy | 400 | 13-14px | `#8b949e` |
| Labels / badges | 500 | 10-11px | `#4ade80` |
| Muted meta | 400 | 11px | `#484f58` |

Font stack: `-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif`

---

## Progress Bar & Loading States

**Progress bar:**
- Track: `rgba(74, 222, 128, 0.1)` on `#161b22`
- Fill: gradient `#22c55e → #4ade80`
- Glow: `box-shadow: 0 0 8px rgba(74,222,128,0.4)`
- Height: 4px, fully rounded (`border-radius: 2px`)

**Spinner:**  
- 20×20px circle stroke
- Color: `#4ade80`
- Rotation animation, 600ms linear infinite

---

## Toast Notification Style

- Background: `rgba(22, 27, 34, 0.95)` + `backdrop-filter: blur(12px)`
- Border: `1px solid rgba(48, 54, 61, 0.7)`
- Success icon: `#4ade80` checkmark
- Error icon: `#f85149` X
- Info icon: `#58a6ff` circle
- Typography: 13px / `#e6edf3`
- Width: max 360px, border-radius: 10px

---

## Brand Don'ts

1. **No rainbow gradients** — one accent color, used with discipline
2. **No white backgrounds** — this is a dark-native product
3. **No rounded blob shapes** — the Plumbob is geometric, editorial
4. **No generic gamer aesthetics** (hexagons, scanlines, neon trails)
5. **No compression artifacts** — all icons delivered at native resolution
6. **No off-brand fonts** — system stack only, no display fonts

---

## Edition & Version Naming

- **Release label:** `Beta v3*`  
- The asterisk denotes pre-release / active development  
- Do not use "Forge Edition" or any other subtitle — Beta v3* is canonical  
- Badge pattern: `● Beta v3*` (filled green dot + label, pill border)

## Custom Icon System (v3)

All mod icons are hand-authored SVG — no emoji, no stock glyphs, no icon libraries.

| Mod | Icon Concept | Stroke Color |
|-----|-------------|--------------|
| Economy Sim | Coin/cylinder stack | `#2ea043` |
| Social Sim | Network graph (nodes + edges) | `#e05d44` |
| QoL Pack | Three-point tuning sliders | `#388bfd` |
| Drama Engine | Narrative arc line to climax | `#d4a017` |
| Political Sim | Classical columns + pediment | `#8957e5` |
| Smart Sims | 3-layer neural network | `#1f9ada` |

Source: `brand/preview/render-v3.html` — Theo pulls components directly from this file.

## Icon Glow System (v3)

Triple-layer box-shadow stack on app icon:
```css
box-shadow:
  0 0 0 1.5px rgba(74,222,128,0.18),   /* tight border halo */
  0 0 40px  rgba(74,222,128,0.22),       /* near glow */
  0 0 100px rgba(74,222,128,0.14),       /* mid glow */
  0 0 200px rgba(74,222,128,0.07),       /* ambient bloom */
  0 30px 80px rgba(0,0,0,0.75),          /* drop shadow */
  inset 0 1px 0 rgba(255,255,255,0.04),
  inset 0 0 60px rgba(74,222,128,0.03);
```
Plus internal radial gradient glow + SVG filter on diamond edges.

## Production Checklist

- [x] `brand/icons/icon-master.svg` — Plumbob SVG vector
- [x] `brand/icons/icon-*.png` — All 7 rasterized sizes
- [x] `brand/icons/icon.icns` — macOS bundle
- [x] `brand/icons/icon.ico` — Windows bundle
- [x] `brand/mod-cards/*.png` — 6 card thumbnails
- [x] `brand/installer/dmg-background.png`
- [x] `brand/installer/nsis-sidebar.bmp`
- [x] `brand/installer/nsis-header.bmp`
- [x] `brand/installer/splash-banner.png`
- [x] `brand/preview/render-v3.html` — 4K CSS source, Chairman-approved 2026-03-30

---

**APPROVED by Chairman Aaron Stark — 2026-03-30**  
*All assets produced against this spec are CCO-approved for production use.*  
*Any deviations require written sign-off from Victor Nolan-Carter.*
