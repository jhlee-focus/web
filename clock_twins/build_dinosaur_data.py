"""
공룡 시계용 데이터 빌더.
dino.fandom.com 위키에서 각 공룡의 인포박스 메인 이미지 + 본문 첫 문단 + 인포박스 스펙을 가져와
512×512 WebP로 변환해 img_dinosaur/에 저장하고, 원시 설명은 img_dinosaur_src/_raw_descriptions.json에 둔다.

run:  python build_dinosaur_data.py    (clock_twins/ 디렉터리에서)
deps: pillow
"""

import http.cookiejar
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("PIL/Pillow is required. Install with: pip install Pillow", file=sys.stderr)
    sys.exit(1)

OUT_DIR = Path("img_dinosaur")
SRC_DIR = Path("img_dinosaur_src")
SIZE = 512

API = "https://dino.fandom.com/api.php"
FILEPATH_BASE = "https://dino.fandom.com/wiki/Special:FilePath/"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,ko;q=0.7",
    "Accept-Encoding": "identity",
}

# Cloudflare 세션 추적 회피 — 쿠키 유지 + 같은 opener 재사용
_cookie_jar = http.cookiejar.CookieJar()
_opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(_cookie_jar))
_opener.addheaders = list(HEADERS.items())

# (no, ko, en, gen [1=Tri 2=Jur 3=Cret], kind, tier, abc_letter or None)
SPECIES = [
    # 핑크퐁 공룡 ABC 26
    ("001", "안킬로사우루스",      "Ankylosaurus",     3, "공룡",   "초식", "A"),
    ("002", "브라키오사우루스",    "Brachiosaurus",    2, "공룡",   "초식", "B"),
    ("003", "콤프소그나투스",      "Compsognathus",    2, "공룡",   "육식", "C"),
    ("004", "데이노니쿠스",        "Deinonychus",      3, "공룡",   "육식", "D"),
    ("005", "엘라스모사우루스",    "Elasmosaurus",     3, "수장룡", "육식", "E"),
    ("006", "파브로사우루스",      "Fabrosaurus",      2, "공룡",   "초식", "F"),
    ("007", "갈리미무스",          "Gallimimus",       3, "공룡",   "잡식", "G"),
    ("008", "하드로사우루스",      "Hadrosaurus",      3, "공룡",   "초식", "H"),
    ("009", "이구아노돈",          "Iguanodon",        3, "공룡",   "초식", "I"),
    ("010", "작사르토사우루스",    "Jaxartosaurus",    3, "공룡",   "초식", "J"),
    ("011", "켄트로사우루스",      "Kentrosaurus",     2, "공룡",   "초식", "K"),
    ("012", "람베오사우루스",      "Lambeosaurus",     3, "공룡",   "초식", "L"),
    ("013", "메갈로사우루스",      "Megalosaurus",     2, "공룡",   "육식", "M"),
    ("014", "노도사우루스",        "Nodosaurus",       3, "공룡",   "초식", "N"),
    ("015", "오비랍토르",          "Oviraptor",        3, "공룡",   "잡식", "O"),
    ("016", "프로토케라톱스",      "Protoceratops",    3, "공룡",   "초식", "P"),
    ("017", "케찰코아틀루스",      "Quetzalcoatlus",   3, "익룡",   "육식", "Q"),
    ("018", "람포린쿠스",          "Rhamphorhynchus",  2, "익룡",   "육식", "R"),
    ("019", "스피노사우루스",      "Spinosaurus",      3, "공룡",   "육식", "S"),
    ("020", "티라노사우루스",      "Tyrannosaurus",    3, "공룡",   "육식", "T"),
    ("021", "유타랍토르",          "Utahraptor",       3, "공룡",   "육식", "U"),
    ("022", "벨로키랍토르",        "Velociraptor",     3, "공룡",   "육식", "V"),
    ("023", "완나노사우루스",      "Wannanosaurus",    3, "공룡",   "초식", "W"),
    ("024", "제노타르소사우루스",  "Xenotarsosaurus",  3, "공룡",   "육식", "X"),
    ("025", "양추아노사우루스",    "Yangchuanosaurus", 2, "공룡",   "육식", "Y"),
    ("026", "지공고사우루스",      "Zigongosaurus",    2, "공룡",   "초식", "Z"),
    # 보완종 18
    ("027", "에오랍토르",          "Eoraptor",         1, "공룡",   "잡식", None),
    ("028", "코엘로피시스",        "Coelophysis",      1, "공룡",   "육식", None),
    ("029", "플라테오사우루스",    "Plateosaurus",     1, "공룡",   "초식", None),
    ("030", "헤레라사우루스",      "Herrerasaurus",    1, "공룡",   "육식", None),
    ("031", "트리케라톱스",        "Triceratops",      3, "공룡",   "초식", None),
    ("032", "스테고사우루스",      "Stegosaurus",      2, "공룡",   "초식", None),
    ("033", "디플로도쿠스",        "Diplodocus",       2, "공룡",   "초식", None),
    ("034", "파라사우롤로푸스",    "Parasaurolophus",  3, "공룡",   "초식", None),
    ("035", "알로사우루스",        "Allosaurus",       2, "공룡",   "육식", None),
    ("036", "프테라노돈",          "Pteranodon",       3, "익룡",   "육식", None),
    ("037", "모사사우루스",        "Mosasaurus",       3, "수장룡", "육식", None),
    ("038", "스티라코사우루스",    "Styracosaurus",    3, "공룡",   "초식", None),
    ("039", "파키리노사우루스",    "Pachyrhinosaurus", 3, "공룡",   "초식", None),
    ("040", "에드몬토니아",        "Edmontonia",       3, "공룡",   "초식", None),
    ("041", "디모르포돈",          "Dimorphodon",      2, "익룡",   "육식", None),
    ("042", "크로노사우루스",      "Kronosaurus",      3, "수장룡", "육식", None),
    ("043", "리오플레우로돈",      "Liopleurodon",     2, "수장룡", "육식", None),
    ("044", "이크티오사우루스",    "Ichthyosaurus",    2, "어룡",   "육식", None),
]


def fetch_page(en_name):
    """MediaWiki parse API. Returns dict, may raise."""
    params = {
        "action": "parse",
        "page": en_name,
        "format": "json",
        "prop": "text|images",
        "redirects": "1",
    }
    url = API + "?" + urllib.parse.urlencode(params)
    with _opener.open(url, timeout=30) as r:
        return json.load(r)


def extract_infobox_image(html):
    """Find the main <img> inside the infobox table.
    dino.fandom uses classic <table class="infobox"> markup:
      <th><img>name-banner.png</img></th>     <- skip
      <td><img>actual_photo.png</img></td>    <- want this
    Strategy: collect imgs inside the infobox table, reject obviously bad ones
    (name banners, scale charts, skull-only, museum exhibits, etc.), return first usable.
    """
    # 파일명 거부 패턴 (정규식). 다음 중 하나라도 매칭되면 스킵.
    BAD_PATTERNS = [
        re.compile(r"name\.\w+$", re.IGNORECASE),         # *name.png
        re.compile(r"\bname\b", re.IGNORECASE),
        re.compile(r"\b(logo|wordmark|icon|edit[-_]ltr|edit[-_]rtl)\b", re.IGNORECASE),
        re.compile(r"\b(scale|size|sizes|comparison)\b", re.IGNORECASE),
        re.compile(r"\b(skull|skeleton|fossil|fossils|bones|tooth|teeth)\b", re.IGNORECASE),
        re.compile(r"\b(graph|chart|map|diagram)\b", re.IGNORECASE),
        re.compile(r"paleozoological|paleontolog", re.IGNORECASE),
        re.compile(r"\bmuseum\b", re.IGNORECASE),
        re.compile(r"\bquestion[-_]book", re.IGNORECASE),
        re.compile(r"\bcommons[-_]logo", re.IGNORECASE),
        # JW detail page hero banner — 가로 길고 텍스트 오버레이 들어있을 가능성 ↑
        re.compile(r"-detail-header", re.IGNORECASE),
        re.compile(r"_header_copia", re.IGNORECASE),
        re.compile(r"\bheader\b", re.IGNORECASE),
    ]

    def is_bad(filename):
        # filename only (no path)
        for pat in BAD_PATTERNS:
            if pat.search(filename):
                return True
        return False

    def extract_fn(url):
        url_clean = url.replace("&amp;", "&")
        fn = re.search(r"/([^/]+\.(?:png|jpg|jpeg|webp|gif))", url_clean, re.IGNORECASE)
        if not fn:
            return None
        # URL-decode (e.g., %281%29 → (1)) so Special:FilePath redirect works correctly.
        return urllib.parse.unquote(fn.group(1))

    def candidate_from_imgs(imgs):
        # Pass 1: skip bad filenames
        for url in imgs:
            file_part = extract_fn(url)
            if not file_part:
                continue
            if is_bad(file_part):
                continue
            return file_part
        # Pass 2: accept any image (last resort)
        for url in imgs:
            file_part = extract_fn(url)
            if file_part:
                return file_part
        return None

    # 1) Try classic <table class="infobox">
    m = re.search(r'<table[^>]*\binfobox\b[^>]*>(.*?)</table>', html, re.DOTALL | re.IGNORECASE)
    if m:
        box = m.group(1)
        imgs = re.findall(r'<img[^>]+(?:data-src|src)="([^"]+)"', box)
        result = candidate_from_imgs(imgs)
        if result:
            return result

    # 2) Fallback: portable-infobox aside (modern fandom)
    m2 = re.search(r'<aside[^>]*portable-infobox[^>]*>(.*?)</aside>', html, re.DOTALL | re.IGNORECASE)
    if m2:
        box = m2.group(1)
        imgs = re.findall(r'<img[^>]+(?:data-src|src)="([^"]+)"', box)
        result = candidate_from_imgs(imgs)
        if result:
            return result

    # 3) 마지막 폴백: 페이지 본문 전체에서 첫 적합 이미지
    # — dino.fandom의 일부 페이지(Diplodocus 등)는 infobox 없이 <figure class="thumb">만 있음.
    # 첫 figure는 이름 배너인 경우가 많아 필터로 거른 뒤 다음을 선택.
    all_imgs = re.findall(r'<img[^>]+(?:data-src|src)="([^"]+)"', html)
    return candidate_from_imgs(all_imgs)


def extract_intro_paragraph(html):
    """First substantial <p> in the rendered HTML."""
    for p in re.findall(r"<p\b[^>]*>(.*?)</p>", html, re.DOTALL | re.IGNORECASE):
        # Strip HTML tags
        text = re.sub(r"<[^>]+>", "", p)
        # Decode common entities (rough but good enough)
        text = (
            text.replace("&amp;", "&")
            .replace("&lt;", "<")
            .replace("&gt;", ">")
            .replace("&quot;", '"')
            .replace("&#39;", "'")
            .replace("&nbsp;", " ")
        )
        text = re.sub(r"\s+", " ", text).strip()
        if len(text) > 40:
            return text
    return None


def extract_infobox_specs(html):
    """Pull label/value pairs out of the portable-infobox aside."""
    m = re.search(r"<aside[^>]*portable-infobox[^>]*>(.*?)</aside>", html, re.DOTALL | re.IGNORECASE)
    if not m:
        return {}
    box = m.group(1)
    specs = {}
    # Each data row has: data-source="key" ... pi-data-value">value</div>
    for row in re.finditer(
        r'data-source="([^"]+)"[^>]*>.*?pi-data-value[^>]*>(.*?)</div>',
        box,
        re.DOTALL | re.IGNORECASE,
    ):
        key = row.group(1)
        val_html = row.group(2)
        val = re.sub(r"<[^>]+>", "", val_html)
        val = (
            val.replace("&amp;", "&")
            .replace("&#160;", " ")
            .replace("&nbsp;", " ")
            .replace("&#39;", "'")
        )
        val = re.sub(r"\s+", " ", val).strip()
        if val:
            specs[key] = val
    return specs


def download_image(filename, dest):
    url = FILEPATH_BASE + urllib.parse.quote(filename)
    with _opener.open(url, timeout=60) as r:
        data = r.read()
    dest.write_bytes(data)
    return len(data)


def to_webp_square(src, dest, size=SIZE):
    with Image.open(src) as im:
        im = im.convert("RGBA")
        w, h = im.size
        side = max(w, h)
        canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
        canvas.paste(im, ((side - w) // 2, (side - h) // 2))
        canvas = canvas.resize((size, size), Image.LANCZOS)
        canvas.save(dest, "WEBP", quality=88, method=6)


def main():
    OUT_DIR.mkdir(exist_ok=True)
    SRC_DIR.mkdir(exist_ok=True)

    desc_file = SRC_DIR / "_raw_descriptions.json"
    descriptions = {}
    if desc_file.exists():
        try:
            descriptions = json.loads(desc_file.read_text(encoding="utf-8"))
        except Exception:
            descriptions = {}

    failures = []
    for no, ko, en, gen, kind, tier, abc in SPECIES:
        print(f"[{no}] {ko}  ({en})")
        try:
            # 이미 캐시된 설명에 image_filename이 있으면 API 호출 스킵
            cached = descriptions.get(en)
            if cached and cached.get("image_filename"):
                img_filename = cached["image_filename"]
                print(f"    using cached metadata for {en}")
            else:
                data = fetch_page(en)
                if "parse" not in data:
                    err = data.get("error", {}).get("info", "unknown")
                    raise RuntimeError(f"no parse: {err}")
                html = data["parse"]["text"]["*"]

                img_filename = extract_infobox_image(html)
                if not img_filename:
                    imgs = data["parse"].get("images") or []
                    if imgs:
                        img_filename = imgs[0]
                if not img_filename:
                    raise RuntimeError("no image found")

                intro = extract_intro_paragraph(html)
                specs = extract_infobox_specs(html)
                descriptions[en] = {
                    "ko": ko,
                    "gen": gen,
                    "kind": kind,
                    "tier": tier,
                    "abc": abc,
                    "intro": intro,
                    "infobox": specs,
                    "image_filename": img_filename,
                }

            ext = img_filename.rsplit(".", 1)[-1].lower()
            if ext not in ("png", "jpg", "jpeg", "webp", "gif"):
                ext = "png"
            src_file = SRC_DIR / f"DN-{no}_{ko}.{ext}"
            if not (src_file.exists() and src_file.stat().st_size > 0):
                size_kb = download_image(img_filename, src_file) // 1024
                print(f"    download: {img_filename}  ({size_kb} KB)")
            else:
                print(f"    cached:   {src_file.name}")
            time.sleep(4.0)  # Cloudflare rate-limit 회피 — 큰 폭으로 늘려 ~3분 짜리 안전 진행

            out_file = OUT_DIR / f"DN-{no}_{ko}.webp"
            to_webp_square(src_file, out_file)
            print(f"    -> {out_file.name}  ({out_file.stat().st_size // 1024} KB)")
            # 종별로 즉시 저장 — Cloudflare 차단되더라도 진행분 보존
            desc_file.write_text(json.dumps(descriptions, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            print(f"    FAIL: {e}")
            failures.append((no, ko, en, str(e)))

    desc_file.write_text(json.dumps(descriptions, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\ndescriptions saved: {desc_file}")

    print(f"\ndone: {len(SPECIES) - len(failures)}/{len(SPECIES)} succeeded")
    if failures:
        print("FAILED:")
        for f in failures:
            print(f"  {f[0]} {f[1]} ({f[2]}): {f[3]}")


if __name__ == "__main__":
    main()
