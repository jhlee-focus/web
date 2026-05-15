"""Apply 12 hand-picked replacement images for new ABC-song species.

After this runs, all 12 species have DN-NNN_한국어.webp under img_dinosaur/ and
img_dinosaur_src/_raw_descriptions.json has an entry for each.
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

# (no, ko, en, source_relpath, image_filename_for_credits, source_note,
#  gen, kind, tier, abc, ko_intro_for_blurb_gen)
PICKS = [
    ("045", "디메트로돈", "Dimetrodon",
     "Dimetrodon/jpfilms_01_JWD_Dimetrodon_render.png",
     "JWD_Dimetrodon_render.png",
     "jurassicpark.fandom (Jurassic World Dominion render)"),
    ("046", "기가노토사우루스", "Giganotosaurus",
     "Giganotosaurus/jpfilms_01_Giganotasaurus_Jurassic_World_Dominion.png",
     "Giganotasaurus_Jurassic_World_Dominion.png",
     "jurassicpark.fandom (Jurassic World Dominion render)"),
    ("047", "힙실로포돈", "Hypsilophodon",
     "Hypsilophodon/dino_00_7084751_orig.png",
     "7084751_orig.png",
     "dino.fandom (3D CGI render)"),
    ("048", "마이아사우라", "Maiasaura",
     "Maiasaura/dino_00_77084_orig.png",
     "77084_orig.png",
     "dino.fandom (3D CGI render — adult with hatchling)"),
    ("049", "니게르사우루스", "Nigersaurus",
     "Nigersaurus/dinopedia_00_Nigersaurus-alive.jpg",
     "Nigersaurus-alive.jpg",
     "dinopedia.fandom (life reconstruction CGI)"),
    ("050", "오르니토미무스", "Ornithomimus",
     "Ornithomimus/jpfilms_00_JPI_Ornithomimus.png",
     "JPI_Ornithomimus.png",
     "jurassicpark.fandom (Jurassic Park I-style illustration)"),
    ("051", "쿠아에시토사우루스", "Quaesitosaurus",
     "Quaesitosaurus/jpfilms_00_JPI_Quaesitosaurus.png",
     "JPI_Quaesitosaurus.png",
     "jurassicpark.fandom (Jurassic Park I-style illustration)"),
    ("052", "레바키사우루스", "Rebbachisaurus",
     "Rebbachisaurus/jpfilms_00_JPI_Rebbachisaurus.png",
     "JPI_Rebbachisaurus.png",
     "jurassicpark.fandom (Jurassic Park I-style illustration)"),
    ("053", "우다노케라톱스", "Udanoceratops",
     "Udanoceratops/dinopedia_02_Static-assets-upload2305109101503932972.jpg",
     "Udanoceratops_life_reconstruction.jpg",
     "dinopedia.fandom (life reconstruction illustration)"),
    ("054", "우에르호사우루스", "Wuerhosaurus",
     "Wuerhosaurus/jpfilms_01_JPI_Wuerhosaurus.png",
     "JPI_Wuerhosaurus.png",
     "jurassicpark.fandom (Jurassic Park I-style illustration)"),
    ("055", "제노케라톱스", "Xenoceratops",
     "Xenoceratops/dino_00_Tumblr_ouiks9asxB1s5f2yxo1_1280.png",
     "Xenoceratops_Saurian.png",
     "dino.fandom (Saurian-game style CGI render)"),
    ("056", "주니케라톱스", "Zuniceratops",
     "Zuniceratops/dino_00_Zuniceratops_01_by_2ndecho-d5369p7.png",
     "Zuniceratops_01_by_2ndecho.png",
     "dino.fandom (3D CGI render)"),
]

for no, ko, en, candidate_rel, img_fn, source_note in PICKS:
    src_candidate = CANDIDATES / candidate_rel
    if not src_candidate.exists():
        print(f"[{no}] {en}: candidate not found: {src_candidate}")
        continue
    ext = src_candidate.suffix.lstrip(".").lower()
    src_file = SRC_DIR / f"DN-{no}_{ko}.{ext}"
    shutil.copy(src_candidate, src_file)
    print(f"[{no}] {ko} ({en})")
    out_file = OUT_DIR / f"DN-{no}_{ko}.webp"
    b.to_webp_square(src_file, out_file)
    print(f"    -> {out_file.name} ({out_file.stat().st_size // 1024} KB)")
    descriptions[en] = {
        "ko": ko,
        "image_filename": img_fn,
        "source": source_note,
        "intro": None,
        "infobox": {},
    }

desc_file.write_text(json.dumps(descriptions, ensure_ascii=False, indent=2),
                     encoding="utf-8")
print("\nDONE")
