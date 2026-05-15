"""Fetch ALL non-bad images for 4 species so we can pick a different realistic transparent one.

Targets: Fabrosaurus (DN-006), Spinosaurus (DN-019), Velociraptor (DN-022), Xenotarsosaurus (DN-024).

For each species we try multiple fandom wikis:
- dino.fandom.com (primary)
- jurassicpark.fandom.com (Jurassic Park franchise)
- dinopedia.fandom.com
And we list every <img> on the page, run BAD_PATTERNS filter, and keep the top N candidates
as separate files for human visual review.
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
    re.compile(r"\bname\b", re.IGNORECASE),
    re.compile(r"\b(logo|wordmark|icon|edit[-_]ltr|edit[-_]rtl)\b", re.IGNORECASE),
    re.compile(r"\b(scale|size|sizes|comparison|chart)\b", re.IGNORECASE),
    re.compile(r"\b(skull|skeleton|fossil|fossils|bones|tooth|teeth|holotype)\b", re.IGNORECASE),
    re.compile(r"\b(graph|map|diagram|chronology|timeline)\b", re.IGNORECASE),
    re.compile(r"paleozoological|paleontolog|paleogeog", re.IGNORECASE),
    re.compile(r"\bmuseum\b", re.IGNORECASE),
    re.compile(r"^Wikia[-_]visualization", re.IGNORECASE),
    re.compile(r"^Site[-_]?navigation", re.IGNORECASE),
    re.compile(r"\bquestion[-_]book\b", re.IGNORECASE),
    re.compile(r"\bambox\b", re.IGNORECASE),
    re.compile(r"-(thumb|small|favicon)\.", re.IGNORECASE),
    re.compile(r"^Spoiler", re.IGNORECASE),
    re.compile(r"\bcommons[-_]logo\b", re.IGNORECASE),
    re.compile(r"^OOjs_", re.IGNORECASE),
    re.compile(r"^Achievement", re.IGNORECASE),
    re.compile(r"\bvideo[-_]thumb\b", re.IGNORECASE),
    re.compile(r"\.svg$", re.IGNORECASE),
    re.compile(r"^Background[_-]", re.IGNORECASE),
]


def is_bad(filename):
    return any(p.search(filename) for p in BAD_PATTERNS)


def fetch_html(api_url, page):
    params = {"action": "parse", "page": page, "format": "json",
              "prop": "text|images", "redirects": "1"}
    url = api_url + "?" + urllib.parse.urlencode(params)
    try:
        with opener.open(url, timeout=30) as r:
            data = json.load(r)
        return data
    except Exception as e:
        return {"_error": str(e)}


def extract_images_from_html(html):
    """Return de-duped list of image filenames in page order."""
    seen = set()
    out = []
    # Find all <img src=...> in the parsed HTML
    imgs = re.findall(r'<img[^>]+(?:src|data-src)="([^"]+)"', html)
    for u in imgs:
        u = u.replace("&amp;", "&")
        m = re.search(r"/([^/]+\.(?:png|jpg|jpeg|webp|gif))",
                      u, re.IGNORECASE)
        if not m:
            continue
        fn = urllib.parse.unquote(m.group(1))
        # Strip thumbnail params like .png/revision/...?
        fn = fn.split("/revision/")[0]
        if fn in seen:
            continue
        seen.add(fn)
        out.append(fn)
    return out


def download(filepath_url_base, filename, dest):
    """filepath_url_base is e.g. https://dino.fandom.com/wiki/Special:FilePath/"""
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

TARGETS = ["Fabrosaurus", "Spinosaurus", "Velociraptor", "Xenotarsosaurus"]

OUT = Path("img_dinosaur_candidates")
OUT.mkdir(exist_ok=True)


for species in TARGETS:
    print(f"\n==== {species} ====")
    sp_dir = OUT / species
    sp_dir.mkdir(exist_ok=True)
    saved = 0
    for wiki in WIKIS:
        print(f"  wiki: {wiki['name']}")
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
        # Filter
        good = [c for c in candidates if not is_bad(c)]
        print(f"    {len(candidates)} imgs, {len(good)} after filter")
        # Save top 5
        for i, fn in enumerate(good[:5]):
            ext = fn.rsplit(".", 1)[-1].lower()
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
    print(f"  total saved: {saved}")

print("\nDONE")
