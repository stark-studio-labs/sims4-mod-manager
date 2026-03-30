#!/usr/bin/env python3
"""
Stark Labs Mod Manager — Brand Asset Rasterization
Uses cairosvg to convert SVG → PNG, then struct to build .ico
Requires: cairosvg (pip install cairosvg)
"""
import os
import struct
import subprocess
from pathlib import Path

try:
    import cairosvg
except ImportError:
    print("❌ cairosvg not found. Run: pip3 install cairosvg")
    exit(1)

BRAND = Path(__file__).parent
ICONS_DIR = BRAND / "icons"
CARDS_DIR = BRAND / "mod-cards"
INSTALL_DIR = BRAND / "installer"

for d in [ICONS_DIR, CARDS_DIR, INSTALL_DIR]:
    d.mkdir(exist_ok=True)

print("🎨 Stark Labs Brand — Rasterizing assets...")

# ── App Icons ──────────────────────────────────────────────────────────────────
print("  → App icon (all sizes)...")
icon_svg = ICONS_DIR / "icon-master.svg"
icon_sizes = [1024, 512, 256, 128, 64, 32, 16]

for size in icon_sizes:
    out = ICONS_DIR / f"icon-{size}.png"
    cairosvg.svg2png(url=str(icon_svg), write_to=str(out), output_width=size, output_height=size)
    print(f"     ✓ icon-{size}.png")

# Windows .ico (multi-size embedded)
print("  → Windows .ico...")
def build_ico(png_paths, output_path):
    """Build a multi-size .ico from PNG files."""
    images = []
    for p in png_paths:
        with open(p, 'rb') as f:
            data = f.read()
        images.append(data)

    # ICO header
    num_images = len(images)
    header = struct.pack('<HHH', 0, 1, num_images)  # reserved, type=1 (ICO), count

    # Directory entries + image data
    offset = 6 + num_images * 16  # header + all directory entries
    directory = b''
    image_data = b''

    for i, (png_path, data) in enumerate(zip(png_paths, images)):
        from PIL import Image
        import io
        img = Image.open(io.BytesIO(data))
        w, h = img.size
        w_byte = w if w < 256 else 0
        h_byte = h if h < 256 else 0
        size_bytes = len(data)
        directory += struct.pack('<BBBBHHII',
            w_byte, h_byte,  # width, height (0 = 256)
            0,               # color count
            0,               # reserved
            1,               # color planes
            32,              # bits per pixel
            size_bytes,
            offset
        )
        image_data += data
        offset += size_bytes

    with open(output_path, 'wb') as f:
        f.write(header + directory + image_data)

try:
    from PIL import Image
    # Build .ico from 256, 128, 64, 32, 16
    ico_sources = [ICONS_DIR / f"icon-{s}.png" for s in [256, 128, 64, 32, 16]]
    build_ico(ico_sources, ICONS_DIR / "icon.ico")
    print("     ✓ icon.ico")
except ImportError:
    print("     ⚠️  Pillow not installed — skipping .ico (pip3 install pillow)")

# macOS .icns (using iconutil if available)
print("  → macOS .icns...")
iconset_dir = ICONS_DIR / "AppIcon.iconset"
iconset_dir.mkdir(exist_ok=True)
iconset_map = {
    "icon_16x16.png": 16,
    "icon_16x16@2x.png": 32,
    "icon_32x32.png": 32,
    "icon_32x32@2x.png": 64,
    "icon_128x128.png": 128,
    "icon_128x128@2x.png": 256,
    "icon_256x256.png": 256,
    "icon_256x256@2x.png": 512,
    "icon_512x512.png": 512,
    "icon_512x512@2x.png": 1024,
}
for name, size in iconset_map.items():
    src = ICONS_DIR / f"icon-{size}.png"
    dst = iconset_dir / name
    import shutil
    shutil.copy(src, dst)

result = subprocess.run(
    ["iconutil", "-c", "icns", str(iconset_dir), "-o", str(ICONS_DIR / "icon.icns")],
    capture_output=True
)
if result.returncode == 0:
    print("     ✓ icon.icns")
    import shutil
    shutil.rmtree(iconset_dir)
else:
    print(f"     ⚠️  iconutil failed: {result.stderr.decode()}")

# ── Mod Cards ──────────────────────────────────────────────────────────────────
print("  → Mod card thumbnails...")
cards_svg = CARDS_DIR / "cards-master.svg"

# Render full sheet then crop each card
sheet_path = CARDS_DIR / "_sheet.png"
cairosvg.svg2png(url=str(cards_svg), write_to=str(sheet_path), output_width=1400, output_height=160)

try:
    from PIL import Image
    sheet = Image.open(sheet_path)
    cards = [
        ("economy-sim", 0),
        ("social-sim", 220),
        ("qol-pack", 440),
        ("drama-engine", 660),
        ("political-sim", 880),
        ("smart-sims", 1100),
    ]
    for name, x in cards:
        # Each card: 200×120 at y=20
        card = sheet.crop((x, 20, x + 200, 140))
        card.save(CARDS_DIR / f"{name}-card.png")
        print(f"     ✓ {name}-card.png")
    sheet_path.unlink()
except ImportError:
    print("     ⚠️  Pillow not installed — card cropping skipped (pip3 install pillow)")
    print("     ℹ️  Full sheet saved at brand/mod-cards/_sheet.png — crop manually")

# ── Installer Assets ────────────────────────────────────────────────────────────
print("  → Installer assets...")

# Splash banner
cairosvg.svg2png(
    url=str(INSTALL_DIR / "splash-banner.svg"),
    write_to=str(INSTALL_DIR / "splash-banner.png"),
    output_width=800, output_height=320
)
print("     ✓ splash-banner.png")

# DMG background
cairosvg.svg2png(
    url=str(INSTALL_DIR / "dmg-background.svg"),
    write_to=str(INSTALL_DIR / "dmg-background.png"),
    output_width=660, output_height=400
)
print("     ✓ dmg-background.png")

# NSIS sidebar
cairosvg.svg2png(
    url=str(INSTALL_DIR / "nsis-sidebar.svg"),
    write_to=str(INSTALL_DIR / "nsis-sidebar.png"),
    output_width=164, output_height=314
)
# Convert PNG → BMP (24-bit, no alpha, required by NSIS)
try:
    from PIL import Image
    img = Image.open(INSTALL_DIR / "nsis-sidebar.png").convert("RGB")
    img.save(INSTALL_DIR / "nsis-sidebar.bmp")
    print("     ✓ nsis-sidebar.bmp")
except ImportError:
    print("     ⚠️  Pillow not installed — .bmp conversion skipped (pip3 install pillow)")

# NSIS header
cairosvg.svg2png(
    url=str(INSTALL_DIR / "nsis-header.svg"),
    write_to=str(INSTALL_DIR / "nsis-header.png"),
    output_width=497, output_height=58
)
try:
    from PIL import Image
    img = Image.open(INSTALL_DIR / "nsis-header.png").convert("RGB")
    img.save(INSTALL_DIR / "nsis-header.bmp")
    print("     ✓ nsis-header.bmp")
except ImportError:
    pass

print("")
print("✅ All brand assets rasterized.")
