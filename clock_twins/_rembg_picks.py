"""Remove background from 6 ABC-song species so the white margin becomes transparent.

Uses rembg (U2Net/ISNet) on each picked source file in img_dinosaur_src/,
writes a *_nobg.png next to it, then re-runs to_webp_square to produce the
final 512x512 transparent WebP in img_dinosaur/.
"""
import sys
from pathlib import Path
from PIL import Image
from rembg import remove, new_session

sys.path.insert(0, '.')
import build_dinosaur_data as b  # reuse to_webp_square

SRC_DIR = Path("img_dinosaur_src")
OUT_DIR = Path("img_dinosaur")

# (no, ko, en) — files already exist in SRC_DIR as DN-NNN_ko.<ext>
TARGETS = [
    ("049", "니게르사우루스", "Nigersaurus"),
    ("050", "오르니토미무스", "Ornithomimus"),
    ("051", "쿠아에시토사우루스", "Quaesitosaurus"),
    ("052", "레바키사우루스", "Rebbachisaurus"),
    ("053", "우다노케라톱스", "Udanoceratops"),
    ("054", "우에르호사우루스", "Wuerhosaurus"),
]

# isnet-general-use gives the cleanest cutouts for paleoart / CGI renders.
session = new_session("isnet-general-use")


def find_src(no, ko):
    """Match DN-NNN_ko.* with any of the known extensions."""
    for ext in ("png", "jpg", "jpeg", "webp", "gif"):
        p = SRC_DIR / f"DN-{no}_{ko}.{ext}"
        if p.exists():
            return p
    return None


for no, ko, en in TARGETS:
    src = find_src(no, ko)
    if not src:
        print(f"[{no}] {ko}: source not found in {SRC_DIR}")
        continue
    print(f"[{no}] {ko} ({en}) <- {src.name}")
    with Image.open(src) as im:
        cleaned = remove(im, session=session)
    nobg_path = SRC_DIR / f"DN-{no}_{ko}_nobg.png"
    cleaned.save(nobg_path, "PNG")
    print(f"    nobg -> {nobg_path.name} ({nobg_path.stat().st_size // 1024} KB)")
    out_path = OUT_DIR / f"DN-{no}_{ko}.webp"
    b.to_webp_square(nobg_path, out_path)
    print(f"    webp -> {out_path.name} ({out_path.stat().st_size // 1024} KB)")

print("\nDONE")
