"""Fetch candidate images for SKZ 시계 — 8 멤버 + 8 SKZOO.

stray-kids.fandom.com 의 각 캐릭터/멤버 페이지에서 메인 이미지 후보를 수집한다.
- 멤버 8명: 공식 프로필 사진 우선
- SKZOO 8마리: 2D 일러스트 우선

수집 결과는 img_skz_candidates/{Name}/ 아래에 저장. 시각 검수 후 픽한 것만
img_skz_src/ 로 승격, rembg + to_webp_square 거쳐 img_skz/ 에 최종 자산.
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
    re.compile(r"\b(logo|wordmark|icon|favicon)\b", re.IGNORECASE),
    re.compile(r"\b(commons|wiki)[-_]?logo\b", re.IGNORECASE),
    re.compile(r"^Wikia[-_]visualization", re.IGNORECASE),
    re.compile(r"\.svg$", re.IGNORECASE),
    re.compile(r"Smallwikipedialogo", re.IGNORECASE),
    re.compile(r"\bvideo[-_]thumb\b", re.IGNORECASE),
    re.compile(r"^X[-_]Icon", re.IGNORECASE),
    re.compile(r"^Ko\.", re.IGNORECASE),  # 가격 표시용 'Ko.png'
    re.compile(r"^Spoiler", re.IGNORECASE),
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


WIKI = {
    "name": "stray-kids",
    "api": "https://stray-kids.fandom.com/api.php",
    "filepath": "https://stray-kids.fandom.com/wiki/Special:FilePath/",
}

# (page_name, folder_name, kind)
TARGETS = [
    # 멤버 8명 (fandom 페이지 영문명 그대로)
    ("Bang_Chan",   "01_BangChan",  "member"),
    ("Lee_Know",    "02_LeeKnow",   "member"),
    ("Changbin",    "03_Changbin",  "member"),
    ("Hyunjin",     "04_Hyunjin",   "member"),
    ("HAN",         "05_HAN",       "member"),
    ("Felix",       "06_Felix",     "member"),
    ("Seungmin",    "07_Seungmin",  "member"),
    ("I.N",         "08_IN",        "member"),
    # SKZOO 8마리 (fandom 페이지명)
    ("Wolf_Chan",   "09_WolfChan",  "skzoo"),
    ("Leebit",      "10_Leebit",    "skzoo"),
    ("DWAEKKI",     "11_DWAEKKI",   "skzoo"),
    ("Jiniret",     "12_Jiniret",   "skzoo"),
    ("HAN_QUOKKA",  "13_HANQUOKKA", "skzoo"),
    ("BbokAri",     "14_BbokAri",   "skzoo"),
    ("PuppyM",      "15_PuppyM",    "skzoo"),
    ("FoxI.Ny",     "16_FoxINy",    "skzoo"),
]

OUT = Path("img_skz_candidates")
OUT.mkdir(exist_ok=True)


for page, folder, kind in TARGETS:
    print(f"\n==== {folder} ({kind}) page={page} ====")
    sp_dir = OUT / folder
    sp_dir.mkdir(exist_ok=True)
    data = fetch_html(WIKI["api"], page)
    if "_error" in data:
        print(f"  fetch error: {data['_error']}")
        continue
    if "parse" not in data:
        err = data.get("error", {}).get("info", "?")
        print(f"  no parse: {err}")
        continue
    html = data["parse"]["text"]["*"]
    candidates = extract_images_from_html(html)
    good = [c for c in candidates if not is_bad(c)]
    print(f"  {len(candidates)} imgs, {len(good)} after filter")
    # 상위 8장만 후보로 다운로드 (메인 이미지가 보통 상단에 있음)
    for i, fn in enumerate(good[:8]):
        local = sp_dir / f"{i:02d}_{fn}"[:200]
        if local.exists():
            continue
        try:
            size = download(WIKI["filepath"], fn, local)
            print(f"    [{i}] {fn[:60]:60s}  {size//1024}KB")
            time.sleep(0.6)
        except Exception as e:
            print(f"    [{i}] FAIL {fn[:60]}: {e}")
    time.sleep(1.5)

print("\nDONE")
