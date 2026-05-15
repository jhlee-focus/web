"""Restore dino.fandom main illustrations for species where Wikipedia replacements went bad.
Uses Special:FilePath direct download — bypasses API rate-limiting since static.wikia.nocookie.net
is a CDN that allows direct image fetches.
"""
import http.cookiejar, json, time, urllib.parse, urllib.request
from pathlib import Path
import sys
sys.path.insert(0, '.')
import build_dinosaur_data as b

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"),
    "Accept": "image/webp,image/png,image/*,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
opener.addheaders = list(HEADERS.items())

FILEPATH = "https://dino.fandom.com/wiki/Special:FilePath/"

# (no, ko, en, image_filename) — known good dino.fandom main illustrations
TARGETS = [
    ("001", "안킬로사우루스",   "Ankylosaurus",    "Anklyosaurus_header_copia.png"),
    ("007", "갈리미무스",       "Gallimimus",      "Gallimimus-detail-header.png"),
    ("020", "티라노사우루스",   "Tyrannosaurus",   "Jurassic_Park_Tyrannosaurus_Rex_(1).png"),
    ("032", "스테고사우루스",   "Stegosaurus",     "Stegosaurus-detail-header.png"),
    ("034", "파라사우롤로푸스", "Parasaurolophus", "Parasaurolophus-detail-header.png"),
    ("037", "모사사우루스",     "Mosasaurus",      "Mosasaurus-detail-header.png"),
]

SRC_DIR = Path("img_dinosaur_src")
OUT_DIR = Path("img_dinosaur")
desc_file = SRC_DIR / "_raw_descriptions.json"
descriptions = json.loads(desc_file.read_text(encoding="utf-8"))

META_DEFAULT = {
    "Ankylosaurus":     (3, "공룡", "초식", "A"),
    "Gallimimus":       (3, "공룡", "잡식", "G"),
    "Tyrannosaurus":    (3, "공룡", "육식", "T"),
    "Stegosaurus":      (2, "공룡", "초식", None),
    "Parasaurolophus":  (3, "공룡", "초식", None),
    "Mosasaurus":       (3, "수장룡", "육식", None),
}

failures = []
for no, ko, en, filename in TARGETS:
    print(f"[{no}] {ko} ({en}) <- {filename}")
    try:
        url = FILEPATH + urllib.parse.quote(filename)
        with opener.open(url, timeout=60) as r:
            data = r.read()
        ext = filename.rsplit(".", 1)[-1].lower()
        if ext not in ("png", "jpg", "jpeg", "webp", "gif"):
            ext = "png"
        src_file = SRC_DIR / f"DN-{no}_{ko}.{ext}"
        src_file.write_bytes(data)
        print(f"  downloaded {len(data) // 1024} KB")
        out_file = OUT_DIR / f"DN-{no}_{ko}.webp"
        b.to_webp_square(src_file, out_file)
        print(f"  -> {out_file.name} ({out_file.stat().st_size // 1024} KB)")
        gen, kind, tier, abc = META_DEFAULT[en]
        # Preserve existing intro if any
        existing = descriptions.get(en, {})
        descriptions[en] = {
            "ko": ko, "gen": gen, "kind": kind, "tier": tier, "abc": abc,
            "intro": existing.get("intro"),
            "infobox": existing.get("infobox", {}),
            "image_filename": filename,
            "source": "dino.fandom (manual restore via Chrome verification)",
        }
        desc_file.write_text(json.dumps(descriptions, ensure_ascii=False, indent=2), encoding="utf-8")
        time.sleep(1)
    except Exception as e:
        print(f"  FAIL: {e}")
        failures.append((no, ko, en, str(e)))

print(f"\ndone: {len(TARGETS) - len(failures)}/{len(TARGETS)} succeeded")
if failures:
    print("FAILED:")
    for f in failures:
        print(f"  {f}")
