#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Stark Labs Mod Manager — Brand Asset Rasterization
# Requires: rsvg-convert (brew install librsvg) + imagemagick (brew install imagemagick)
# ─────────────────────────────────────────────────────────────────────────────

set -e

BRAND="$(cd "$(dirname "$0")" && pwd)"

echo "🎨 Stark Labs Brand — Rasterizing assets..."

# ── App Icon ─────────────────────────────────────────────────────────────────
echo "  → App icon (all sizes)..."
for SIZE in 1024 512 256 128 64 32 16; do
  rsvg-convert -w $SIZE -h $SIZE \
    "$BRAND/icons/icon-master.svg" \
    -o "$BRAND/icons/icon-${SIZE}.png"
done

# macOS .icns
if command -v iconutil &>/dev/null; then
  echo "  → macOS .icns..."
  ICONSET="$BRAND/icons/AppIcon.iconset"
  mkdir -p "$ICONSET"
  cp "$BRAND/icons/icon-16.png"   "$ICONSET/icon_16x16.png"
  cp "$BRAND/icons/icon-32.png"   "$ICONSET/icon_16x16@2x.png"
  cp "$BRAND/icons/icon-32.png"   "$ICONSET/icon_32x32.png"
  cp "$BRAND/icons/icon-64.png"   "$ICONSET/icon_32x32@2x.png"
  cp "$BRAND/icons/icon-128.png"  "$ICONSET/icon_128x128.png"
  cp "$BRAND/icons/icon-256.png"  "$ICONSET/icon_128x128@2x.png"
  cp "$BRAND/icons/icon-256.png"  "$ICONSET/icon_256x256.png"
  cp "$BRAND/icons/icon-512.png"  "$ICONSET/icon_256x256@2x.png"
  cp "$BRAND/icons/icon-512.png"  "$ICONSET/icon_512x512.png"
  cp "$BRAND/icons/icon-1024.png" "$ICONSET/icon_512x512@2x.png"
  iconutil -c icns "$ICONSET" -o "$BRAND/icons/icon.icns"
  rm -rf "$ICONSET"
  echo "     ✓ icon.icns"
fi

# Windows .ico (multi-size)
if command -v convert &>/dev/null; then
  echo "  → Windows .ico..."
  convert \
    "$BRAND/icons/icon-16.png" \
    "$BRAND/icons/icon-32.png" \
    "$BRAND/icons/icon-64.png" \
    "$BRAND/icons/icon-128.png" \
    "$BRAND/icons/icon-256.png" \
    "$BRAND/icons/icon.ico"
  echo "     ✓ icon.ico"
fi

# ── Mod Cards ─────────────────────────────────────────────────────────────────
echo "  → Mod card thumbnails..."
# The master SVG contains all 6 at x-offsets of 0, 220, 440, 660, 880, 1100
# Extract each as individual 200×120 PNGs
CARDS=("economy-sim" "social-sim" "qol-pack" "drama-engine" "political-sim" "smart-sims")
X_OFFSETS=(0 220 440 660 880 1100)

for i in "${!CARDS[@]}"; do
  X="${X_OFFSETS[$i]}"
  NAME="${CARDS[$i]}"
  # Full sheet render then crop
  rsvg-convert -w 1400 -h 160 \
    "$BRAND/mod-cards/cards-master.svg" \
    -o "/tmp/cards-sheet.png"
  convert "/tmp/cards-sheet.png" \
    -crop "200x120+${X}+20" +repage \
    "$BRAND/mod-cards/${NAME}-card.png"
  echo "     ✓ ${NAME}-card.png"
done
rm -f /tmp/cards-sheet.png

# ── Installer Assets ──────────────────────────────────────────────────────────
echo "  → Installer assets..."

# Splash banner
rsvg-convert -w 800 -h 320 \
  "$BRAND/installer/splash-banner.svg" \
  -o "$BRAND/installer/splash-banner.png"
echo "     ✓ splash-banner.png"

# DMG background
rsvg-convert -w 660 -h 400 \
  "$BRAND/installer/dmg-background.svg" \
  -o "$BRAND/installer/dmg-background.png"
echo "     ✓ dmg-background.png"

# NSIS sidebar (BMP required by NSIS — 164×314)
rsvg-convert -w 164 -h 314 \
  "$BRAND/installer/nsis-sidebar.svg" \
  -o "/tmp/nsis-sidebar.png"
convert "/tmp/nsis-sidebar.png" \
  -type Palette \
  "BMP3:$BRAND/installer/nsis-sidebar.bmp"
echo "     ✓ nsis-sidebar.bmp"

# NSIS header (BMP — 497×58)
rsvg-convert -w 497 -h 58 \
  "$BRAND/installer/nsis-header.svg" \
  -o "/tmp/nsis-header.png"
convert "/tmp/nsis-header.png" \
  -type Palette \
  "BMP3:$BRAND/installer/nsis-header.bmp"
echo "     ✓ nsis-header.bmp"
rm -f /tmp/nsis-sidebar.png /tmp/nsis-header.png

echo ""
echo "✅ All brand assets rasterized."
echo ""
echo "Output summary:"
echo "  brand/icons/icon-{1024,512,256,128,64,32,16}.png"
echo "  brand/icons/icon.icns  (macOS)"
echo "  brand/icons/icon.ico   (Windows)"
echo "  brand/mod-cards/{economy-sim,social-sim,qol-pack,drama-engine,political-sim,smart-sims}-card.png"
echo "  brand/installer/splash-banner.png"
echo "  brand/installer/dmg-background.png"
echo "  brand/installer/nsis-sidebar.bmp"
echo "  brand/installer/nsis-header.bmp"
