"""Fetch realistic transparent candidate images for the 12 new ABC-song species.

Species (12 species needed to match the actual lyrics of 핑크퐁 공룡 ABC):
D Dimetrodon
G Giganotosaurus
H Hypsilophodon
M Maiasaura (also try Maiasaurus)
N Nigersaurus
O Ornithomimus
Q Quaesitosaurus
R Rebbachisaurus
U Udanoceratops
W Wuerhosaurus
X Xenoceratops
Z Zuniceratops

For each species, query 3 fandom wikis and store up to 6 non-bad images per wiki
for visual review.
"""
import http.cookiejar
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"),
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
opener.addheaders = list(HEADERS.items())

BAD_PATTERNS = [
    re.compile(r"name\.\w+$", re.IGNORECASE),
    re.compile(r"\b(logo|wordmark|icon)\b", re.IGNORECASE),
    re.compile(r"\b(scale|size|comparison|chart)\b", re.IGNORECASE),
    re.compile(r"\b(skull|skeleton|fossil|bones|tooth|teeth|holotype)\b", re.IGNORECASE),
    re.compile(r"\b(graph|map|diagram|chronology|timeline)\b", re.IGNORECASE),
    re.compile(r"paleozoological|paleontolog|paleogeog", re.IGNORECASE),
    re.compile(r"\bmuseum\b", re.IGNORECASE),
    re.compile(r"^Wikia[-_]visualization", re.IGNORECASE),
    re.compile(r"\bcommons[-_]logo\b", re.IGNORECASE),
    re.compile(r"\.svg$", re.IGNORECASE),
    re.compile(r"Smallwikipedialogo", re.IGNORECASE),
    re.compile(r"Herbivore_Icon|Carnivore_Icon|Omnivore_Icon", re.IGNORECASE),
    re.compile(r"Spoiler", re.IGNORECASE),
    re.compile(r"\bvideo[-_]thumb\b", re.IGNORECASE),
]


def is_bad(filename):
    return any(p.search(filename) for p in BAD_PATTERNS)


def fetch_html(api_url, page):
    params = {"action": "parse", "page": page, "format": "json",
              "prop": "text|images", "redirects": "1"}
    url = api_url + "?" + urllib.parse.urlencode(params)
    try:
        with opener.open(url, timeout=30) as r:
            return json.load(r)
    except Exception as e:
        return {"_error": str(e)}


def extract_images_from_html(html):
    seen = set()
    out = []
    imgs = re.findall(r'<img[^>]+(?:src|data-src)="([^"]+)"', html)
    for u in imgs:
        u = u.replace("&amp;", "&")
        m = re.search(r"/([^/]+\.(?:png|jpg|jpeg|webp|gif))", u, re.IGNORECASE)
        if not m:
            continue
        fn = urllib.parse.unquote(m.group(1))
        fn = fn.split("/revision/")[0]
        if fn in seen:
            continue
        seen.add(fn)
        out.append(fn)
    return out


def download(filepath_url_base, filename, dest):
    url = filepath_url_base + urllib.parse.quote(filename)
    with opener.open(url, timeout=60) as r:
        data = r.read()
    dest.write_bytes(data)
    return len(data)


WIKIS = [
    {"name": "dino", "api": "https://dino.fandom.com/api.php",
     "filepath": "https://dino.fandom.com/wiki/Special:FilePath/"},
    {"name": "jpfilms", "api": "https://jurassicpark.fandom.com/api.php",
     "filepath": "https://jurassicpark.fandom.com/wiki/Special:FilePath/"},
    {"name": "dinopedia", "api": "https://dinopedia.fandom.com/api.php",
     "filepath": "https://dinopedia.fandom.com/wiki/Special:FilePath/"},
]

# (canonical query, alt_queries[])
TARGETS = [
    ("Dimetrodon", []),
    ("Giganotosaurus", []),
    ("Hypsilophodon", []),
    ("Maiasaura", ["Maiasaurus"]),
    ("Nigersaurus", []),
    ("Ornithomimus", []),
    ("Quaesitosaurus", []),
    ("Rebbachisaurus", []),
    ("Udanoceratops", []),
    ("Wuerhosaurus", []),
    ("Xenoceratops", []),
    ("Zuniceratops", []),
]

OUT = Path("img_dinosaur_candidates")
OUT.mkdir(exist_ok=True)


def process_species(species, sp_dir):
    saved = 0
    for wiki in WIKIS:
        print(f"  wiki: {wiki['name']} -> {species}")
        data = fetch_html(wiki["api"], species)
        if "_error" in data:
            print(f"    fetch error: {data['_error']}")
            continue
        if "parse" not in data:
            err = data.get("error", {}).get("info", "?")
            print(f"    no parse: {err}")
            continue
        html = data["parse"]["text"]["*"]
        candidates = extract_images_from_html(html)
        good = [c for c in candidates if not is_bad(c)]
        print(f"    {len(candidates)} imgs, {len(good)} after filter")
        for i, fn in enumerate(good[:6]):
            local = sp_dir / f"{wiki['name']}_{i:02d}_{fn}"[:200]
            if local.exists():
                continue
            try:
                size = download(wiki["filepath"], fn, local)
                print(f"      [{i}] {fn[:60]:60s}  {size//1024}KB")
                saved += 1
                time.sleep(0.8)
            except Exception as e:
                print(f"      [{i}] FAIL {fn[:60]}: {e}")
        time.sleep(2.0)
    return saved


for canon, alts in TARGETS:
    print(f"\n==== {canon} ====")
    sp_dir = OUT / canon
    sp_dir.mkdir(exist_ok=True)
    saved = process_species(canon, sp_dir)
    if saved == 0:
        for alt in alts:
            print(f"  fallback alt name: {alt}")
            saved = process_species(alt, sp_dir)
            if saved > 0:
                break
    print(f"  total saved: {saved}")

print("\nDONE")
