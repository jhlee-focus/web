"""Re-fetch problematic dinosaurs from Wikipedia (life-restoration preferred).

For the 5-6 species where dino.fandom gave us banner/header-only images.
Also handles Jaxartosaurus and Wannanosaurus (already on Wikipedia but the
original fetch picked skull/museum).
"""
import http.cookiejar, json, re, time, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image
import sys
sys.path.insert(0, '.')
import build_dinosaur_data as b  # reuse to_webp_square, BAD_PATTERNS via extract_infobox_image

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"),
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
opener.addheaders = list(HEADERS.items())

WIKI_API = "https://en.wikipedia.org/w/api.php"
WIKI_FILEPATH = "https://en.wikipedia.org/wiki/Special:FilePath/"

# (no, ko, en) — species to re-fetch from Wikipedia
TARGETS = [
    ("001", "안킬로사우루스", "Ankylosaurus"),
    ("007", "갈리미무스",   "Gallimimus"),
    ("020", "티라노사우루스", "Tyrannosaurus"),
    ("032", "스테고사우루스", "Stegosaurus"),
    ("034", "파라사우롤로푸스", "Parasaurolophus"),
    ("037", "모사사우루스", "Mosasaurus"),
    ("010", "작사르토사우루스", "Jaxartosaurus"),
    ("023", "완나노사우루스", "Wannanosaurus"),
]


def fetch_wiki(name):
    params = {"action": "parse", "page": name, "format": "json",
              "prop": "text|images", "redirects": "1"}
    url = WIKI_API + "?" + urllib.parse.urlencode(params)
    with opener.open(url, timeout=30) as r:
        return json.load(r)


# Wikipedia-specific bad patterns + dino.fandom ones
WIKI_BAD = [
    re.compile(r"\bcommons-logo", re.IGNORECASE),
    re.compile(r"\bquestion_book", re.IGNORECASE),
    re.compile(r"\bedit-ltr", re.IGNORECASE),
    re.compile(r"\bambox\b", re.IGNORECASE),
    re.compile(r"\bsymbol_", re.IGNORECASE),
    re.compile(r"^OOjs_", re.IGNORECASE),
    re.compile(r"\bskull\b", re.IGNORECASE),
    re.compile(r"\bskeleton\b", re.IGNORECASE),
    re.compile(r"fossil", re.IGNORECASE),
    re.compile(r"museum", re.IGNORECASE),
    re.compile(r"paleozoolog", re.IGNORECASE),
    re.compile(r"\bvenn\b", re.IGNORECASE),
    re.compile(r"\bmap\b", re.IGNORECASE),
    re.compile(r"diagram", re.IGNORECASE),
    re.compile(r"\bscale\b", re.IGNORECASE),
    re.compile(r"_size_", re.IGNORECASE),
    re.compile(r"^Wiki", re.IGNORECASE),
    re.compile(r"_locator", re.IGNORECASE),
    re.compile(r"infobox", re.IGNORECASE),
]


def is_wiki_bad(filename):
    return any(p.search(filename) for p in WIKI_BAD)


def extract_wiki_infobox_image(html):
    """Find main image in Wikipedia infobox (table.infobox)."""
    m = re.search(r'<table[^>]*\binfobox\b[^>]*>(.*?)</table>',
                  html, re.DOTALL | re.IGNORECASE)
    candidates = []
    if m:
        imgs = re.findall(r'<img[^>]+src="([^"]+)"', m.group(1))
        for u in imgs:
            fn_m = re.search(r"/([^/]+\.(?:png|jpg|jpeg|webp|gif|svg))",
                             u.replace("&amp;", "&"), re.IGNORECASE)
            if not fn_m:
                continue
            fn = urllib.parse.unquote(fn_m.group(1))
            if not is_wiki_bad(fn):
                candidates.append(fn)
    if candidates:
        return candidates[0]
    # Fallback: first non-bad image anywhere in page
    imgs = re.findall(r'<img[^>]+src="([^"]+)"', html)
    for u in imgs[:30]:
        fn_m = re.search(r"/([^/]+\.(?:png|jpg|jpeg|webp|gif))",
                         u.replace("&amp;", "&"), re.IGNORECASE)
        if not fn_m:
            continue
        fn = urllib.parse.unquote(fn_m.group(1))
        if not is_wiki_bad(fn):
            return fn
    return None


def download(filename, dest):
    url = WIKI_FILEPATH + urllib.parse.quote(filename)
    with opener.open(url, timeout=60) as r:
        data = r.read()
    dest.write_bytes(data)
    return len(data)


SRC_DIR = Path("img_dinosaur_src")
OUT_DIR = Path("img_dinosaur")
desc_file = SRC_DIR / "_raw_descriptions.json"
descriptions = json.loads(desc_file.read_text(encoding="utf-8"))

# Per-species metadata fallback (preserve from existing or default)
META_DEFAULT = {
    "Ankylosaurus":     (3, "공룡", "초식", "A"),
    "Gallimimus":       (3, "공룡", "잡식", "G"),
    "Tyrannosaurus":    (3, "공룡", "육식", "T"),
    "Stegosaurus":      (2, "공룡", "초식", None),
    "Parasaurolophus":  (3, "공룡", "초식", None),
    "Mosasaurus":       (3, "수장룡", "육식", None),
    "Jaxartosaurus":    (3, "공룡", "초식", "J"),
    "Wannanosaurus":    (3, "공룡", "초식", "W"),
}

failures = []
for no, ko, en in TARGETS:
    print(f"[{no}] {ko} ({en})")
    try:
        data = fetch_wiki(en)
        if "parse" not in data:
            err = data.get("error", {}).get("info", "?")
            raise RuntimeError(f"no parse: {err}")
        html = data["parse"]["text"]["*"]
        img_fn = extract_wiki_infobox_image(html)
        if not img_fn:
            raise RuntimeError("no clean image found in wikipedia page")
        print(f"  candidate: {img_fn}")
        ext = img_fn.rsplit(".", 1)[-1].lower()
        if ext == "svg":
            raise RuntimeError("SVG not supported; trying next would help")
        src_file = SRC_DIR / f"DN-{no}_{ko}.{ext}"
        size_kb = download(img_fn, src_file) // 1024
        print(f"  downloaded {size_kb} KB")
        out_file = OUT_DIR / f"DN-{no}_{ko}.webp"
        b.to_webp_square(src_file, out_file)
        print(f"  -> {out_file.name} ({out_file.stat().st_size // 1024} KB)")
        # Update descriptions
        gen, kind, tier, abc = META_DEFAULT[en]
        # Extract intro paragraph
        intro = None
        for p in re.findall(r"<p\b[^>]*>(.*?)</p>", html, re.DOTALL):
            t = re.sub(r"<[^>]+>", "", p)
            t = re.sub(r"&#?\w+;", " ", t)
            t = re.sub(r"\s+", " ", t).strip()
            if len(t) > 40:
                intro = t
                break
        descriptions[en] = {
            "ko": ko, "gen": gen, "kind": kind, "tier": tier, "abc": abc,
            "intro": intro, "infobox": {}, "image_filename": img_fn,
            "source": "wikipedia",
        }
        # Save after each success
        desc_file.write_text(json.dumps(descriptions, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        print(f"  FAIL: {e}")
        failures.append((no, ko, en, str(e)))
    time.sleep(2)

print(f"\ndone: {len(TARGETS) - len(failures)}/{len(TARGETS)} succeeded")
if failures:
    print("FAILED:")
    for no, ko, en, err in failures:
        print(f"  {no} {ko} ({en}): {err}")
