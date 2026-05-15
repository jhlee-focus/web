"""Apply 4 hand-picked replacement images: convert to 512x512 webp + update JSON.

Picks (after visual review):
- DN-006 Fabrosaurus    -> Lesothosaurus realistic CGI (dino.fandom 9018592_orig.png) — senior synonym
- DN-019 Spinosaurus    -> JW Rebirth render (jurassicpark.fandom Spinosaurus_Rebirth_Render.webp)
- DN-022 Velociraptor   -> JW Rebirth render (jurassicpark.fandom Velociraptor_Rebirth.webp)
- DN-024 Xenotarsosaurus -> Carnotaurus JW render (dino.fandom Jurassic_world_carnotaurus.png) — close relative
"""
import json
import shutil
from pathlib import Path
import sys
sys.path.insert(0, '.')
import build_dinosaur_data as b  # reuse to_webp_square

CANDIDATES = Path("img_dinosaur_candidates")
SRC_DIR = Path("img_dinosaur_src")
OUT_DIR = Path("img_dinosaur")
desc_file = SRC_DIR / "_raw_descriptions.json"
descriptions = json.loads(desc_file.read_text(encoding="utf-8"))

# (no, ko, en, source_candidate_relpath, image_filename_for_credits, source_note)
PICKS = [
    ("006", "파브로사우루스", "Fabrosaurus",
     "Lesothosaurus/dino_00_9018592_orig.png",
     "9018592_orig.png",
     "dino.fandom (substitute — Lesothosaurus, senior synonym of Fabrosaurus)"),
    ("019", "스피노사우루스", "Spinosaurus",
     "Spinosaurus/jpfilms_04_Spinosaurus_Rebirth_Render.webp",
     "Spinosaurus_Rebirth_Render.webp",
     "jurassicpark.fandom (Jurassic World Rebirth render)"),
    ("022", "벨로키랍토르", "Velociraptor",
     "Velociraptor/jpfilms_00_Velociraptor_Rebirth.webp",
     "Velociraptor_Rebirth.webp",
     "jurassicpark.fandom (Jurassic World Rebirth render)"),
    ("024", "제노타르소사우루스", "Xenotarsosaurus",
     "Carnotaurus/dino_00_Jurassic_world_carnotaurus.png",
     "Jurassic_world_carnotaurus.png",
     "dino.fandom (substitute — Carnotaurus, close relative in Abelisauridae)"),
]

for no, ko, en, candidate_rel, img_fn, source_note in PICKS:
    src_candidate = CANDIDATES / candidate_rel
    if not src_candidate.exists():
        print(f"[{no}] {en}: candidate not found: {src_candidate}")
        continue
    ext = src_candidate.suffix.lstrip(".").lower()
    src_file = SRC_DIR / f"DN-{no}_{ko}.{ext}"
    shutil.copy(src_candidate, src_file)
    print(f"[{no}] {ko} ({en}) <- {candidate_rel}")
    print(f"    saved src: {src_file.name} ({src_file.stat().st_size // 1024} KB)")
    out_file = OUT_DIR / f"DN-{no}_{ko}.webp"
    b.to_webp_square(src_file, out_file)
    print(f"    -> {out_file.name} ({out_file.stat().st_size // 1024} KB)")
    # Update descriptions
    existing = descriptions.get(en, {})
    descriptions[en] = {
        **existing,
        "image_filename": img_fn,
        "source": source_note,
    }
    desc_file.write_text(json.dumps(descriptions, ensure_ascii=False, indent=2),
                         encoding="utf-8")

print("\nDONE")
