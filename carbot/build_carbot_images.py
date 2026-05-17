"""
합체 카봇 이미지 크롤러.
나무위키(namu.wiki)에서 각 합체 카봇의 대표 이미지를 가져와
512×512 WebP로 변환해 img_carbot/에 저장한다.
원본은 img_carbot_src/에, 메타데이터는 img_carbot_src/_raw_metadata.json에 둔다.

run:  python build_carbot_images.py          (carbot/ 디렉터리에서, 합체 카봇만)
      python build_carbot_images.py --force   (캐시 무시, 재다운로드)
      python build_carbot_images.py --all     (향후: 전체 카봇 확장 예정)

deps: playwright requests beautifulsoup4 pillow
      (playwright install chromium  도 필요)

나무위키는 SPA(React)라 requests로는 og:image를 가져올 수 없으므로
Playwright 헤드리스 브라우저로 페이지를 렌더링한 뒤 og:image를 추출한다.
CDN 이미지 다운로드는 requests로 수행한다.
"""

import argparse
import json
import re
import shutil
import sys
import time
import urllib.parse
from datetime import datetime
from pathlib import Path

# ── 의존성 체크 ──────────────────────────────────────────────────────────
try:
    import requests
except ImportError:
    print("requests is required. Install with: pip install requests", file=sys.stderr)
    sys.exit(1)

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("beautifulsoup4 is required. Install with: pip install beautifulsoup4", file=sys.stderr)
    sys.exit(1)

try:
    from PIL import Image
except ImportError:
    print("Pillow is required. Install with: pip install Pillow", file=sys.stderr)
    sys.exit(1)

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
except ImportError:
    print("playwright is required. Install with: pip install playwright && python -m playwright install chromium", file=sys.stderr)
    sys.exit(1)

# ── 경로 설정 ─────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent
MD_FILE    = BASE_DIR / "hello_carbot_robots.md"
CACHE_HTML = BASE_DIR / "카봇(헬로카봇) - 나무위키.html"
CACHE_FILES_DIR = BASE_DIR / "carbot_namu_wiki_files"
OUT_DIR    = BASE_DIR / "img_carbot"
SRC_DIR    = BASE_DIR / "img_carbot_src"
META_FILE  = SRC_DIR / "_raw_metadata.json"

SIZE = 512

# ────────────────────────────────────────────────────────────────────────
# 합체 카봇 → 구성 멤버 맵
# ────────────────────────────────────────────────────────────────────────
# 값: 짧은 이름 그대로 (검색 시 "카봇 {이름}" 으로 자동 완성됨)
# 이미 "카봇 " 접두어가 붙어야 하는 경우에만 명시
# 중복 멤버(퓨처버스, 바우, 파이트라 등)는 dedup 처리됨

COMBO_COMPONENTS = {
    # 시즌 1
    "펜타스톰":                       ["에이스", "프론", "댄디", "스카이", "스톰"],
    "펜타스톰 X":                      ["라이프 X"],
    # 시즌 2
    "카봇 로드세이버":                  ["아티", "마이스터", "세이버"],
    "카봇 삼총사":                      ["나이트", "루크", "폰"],
    # 시즌 3
    "카봇 마이티가드":                  ["레디", "큐어", "가드", "헬프"],
    "카봇 K-캅스":                     ["썬더", "스피드", "터보", "캅스"],
    # 시즌 4
    "카봇 슈퍼패트론":                  ["패트론", "스키드", "다이어", "리프"],
    "카봇 패트론S":                     ["패트론", "스키드"],
    "카봇 다이어EX":                    ["다이어", "리프"],
    # 시즌 5 (하이퍼빌디언 구성원은 콤보 리스트에 이미 있음)
    "카봇 프라우드제트":                 ["프라우드", "제스티"],
    "카봇 스타블래스터":                 ["블래스터", "스타비"],
    "카봇 아머다이저":                   ["킹다이저", "아머포스"],
    # 시즌 6
    "카봇 럭키펀치":                    ["럭키", "펀치"],
    # 시즌 10 – 가디언트 / 자이언트 로더
    "카봇 가디언트":                    ["덤피", "브로피"],
    "카봇 자이언트 로더":               ["페이저", "소닉붐", "로더"],
    # 시즌 10 – 뱅 시리즈 (퓨처버스·파이트라·바우는 공유 부품)
    "잭슈트뱅":                        ["잭슈트", "타우", "퓨처버스"],
    "페로뱅":                          ["페로", "파우", "퓨처버스"],
    "나노티스뱅":                       ["나노티스", "도우", "퓨처버스"],
    "썬런뱅":                          ["썬런", "미우", "파이트라"],
    "호스퍼스뱅":                       ["호스퍼스", "바우", "파이트라"],
    "자크뱅":                          ["자크", "바우", "파이트라"],
    "자크레인뱅":                       ["자크", "자크레인"],
    # 시즌 11
    "카봇 킹가이더":                    ["핫가이더", "쿨가이더"],
    # 시즌 12
    "카봇 하이퍼캅스":                  ["드로캅", "이그리붐", "푸르디붐", "서포티붐"],
    # 시즌 13
    "카봇 사파리세이버":                 ["드럼킹", "호크하이", "하울러", "타이거붐", "스터번"],
    # 시즌 15
    "카봇 스타가디언":                  ["폴리스타", "스카이스타", "아이언스타", "파이어스타"],
    # 시즌 16
    "그랜드 카봇 X":                   ["카봇 X", "엑스 파이터", "엑스 트레인"],
    "카봇 패트롤가이즈":                 ["히트가이", "코드가이"],
    # 시즌 17
    "카봇 스카이 트리오":               ["제트밴더", "에어밴더", "헬리밴더"],
    # 크로스 콤비네이션 (마하+피스·로드 / 브레이브+피스·로드)
    "카봇 마하피스":                    ["마하", "피스"],
    "카봇 브레이피스":                  ["브레이브", "피스"],
    "카봇 마하로드":                    ["마하", "로드"],
    "카봇 브레이로드":                  ["브레이브", "로드"],
}

# ────────────────────────────────────────────────────────────────────────
# 개별 나무위키 페이지가 없는 구성원 → 해당 합체 로봇 페이지에서 이미지 탐색
# ────────────────────────────────────────────────────────────────────────
FALLBACK_PAGE_MAP = {
    # 뱅 시리즈 (시즌 10)
    "카봇 잭슈트":   "카봇 잭슈트뱅",
    "카봇 타우":     "카봇 잭슈트뱅",
    "카봇 퓨처버스": "카봇 잭슈트뱅",
    "카봇 페로":     "카봇 페로뱅",
    "카봇 파우":     "카봇 페로뱅",
    "카봇 나노티스": "카봇 나노티스뱅",
    "카봇 도우":     "카봇 나노티스뱅",
    "카봇 썬런":     "카봇 썬런뱅",
    "카봇 미우":     "카봇 썬런뱅",
    "카봇 파이트라": "카봇 썬런뱅",
    "카봇 호스퍼스": "카봇 호스퍼스뱅",
    "카봇 바우":     "카봇 호스퍼스뱅",
    "카봇 자크":     "카봇 자크뱅",
    "카봇 자크레인": "카봇 자크레인뱅",
}


def get_component_robots(already_in_dir: set) -> list:
    """
    COMBO_COMPONENTS에서 유일한 구성원 로봇 이름 목록을 반환.
    - 중복 제거 (순서 유지)
    - already_in_dir: OUT_DIR에 이미 있는 safe_name 집합
    - 반환값: 아직 다운로드되지 않은 구성원 이름 list (전체도 함께 반환)
    """
    seen = {}  # name → True (ordered dedup)
    for members in COMBO_COMPONENTS.values():
        for m in members:
            # "카봇 " 접두어 없으면 붙여 표준 이름 생성
            full = m if (m.startswith("카봇 ") or m.startswith("그랜드 카봇 ")) else f"카봇 {m}"
            seen[full] = True

    all_components = list(seen.keys())

    # 이미 img_carbot/ 에 있는 것 스킵 표시
    pending = []
    for name in all_components:
        safe = re.sub(r'[\\/*?:"<>|()\[\]]', "", name).strip()
        if safe not in already_in_dir:
            pending.append(name)

    return all_components, pending


# ── HTTP 설정 (나무위키 403 회피용 브라우저 유사 헤더) ──────────────────
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://namu.wiki/",
    "Connection": "keep-alive",
}

_session = requests.Session()
_session.headers.update(HEADERS)


# ────────────────────────────────────────────────────────────────────────
# 1. 합체 카봇 이름 파싱
# ────────────────────────────────────────────────────────────────────────

def parse_combo_robots(md_path: Path) -> list:
    """
    hello_carbot_robots.md의 '합체 카봇 표' 섹션 테이블에서
    첫 번째 열(합체 카봇 이름)을 모두 추출한다.
    """
    text = md_path.read_text(encoding="utf-8")
    # 표 섹션 추출: "## 합체 카봇 표" 이후 다음 "---" 또는 "## " 섹션까지
    m = re.search(r"## 합체 카봇 표\s*\n(.*?)(?:\n---|\n## |\Z)", text, re.DOTALL)
    if not m:
        raise ValueError("hello_carbot_robots.md에서 '합체 카봇 표' 섹션을 찾을 수 없습니다.")

    table_text = m.group(1)
    names = []
    for line in table_text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cols = [c.strip() for c in line.split("|") if c.strip()]
        if not cols:
            continue
        name = cols[0]
        # 헤더행·구분선 스킵
        if name in ("합체 카봇 이름", "") or re.match(r"^-+$", name):
            continue
        names.append(name)

    return names


# ────────────────────────────────────────────────────────────────────────
# 2. 로컬 캐시 HTML 파싱
# ────────────────────────────────────────────────────────────────────────

def build_cache_map(html_path: Path) -> dict:
    """
    카봇(헬로카봇) 나무위키 캐시 HTML에서
    {alt_키워드 → {"url": CDN_URL, "local": 로컬파일_또는_None}} 딕셔너리를 만든다.
    data-src="//i.namu.wiki/..." 이미지만 대상.
    로컬 캐시 파일(carbot_namu_wiki_files/)이 존재하면 local에 Path를 담는다.
    """
    print(f"[cache] {html_path.name} 파싱 중...")
    soup = BeautifulSoup(
        html_path.read_text(encoding="utf-8", errors="ignore"), "html.parser"
    )
    cache = {}
    for img in soup.find_all("img"):
        data_src = img.get("data-src") or ""
        local_src = img.get("src") or ""
        alt = (img.get("alt") or "").strip()

        if "i.namu.wiki" not in data_src or not alt:
            continue

        cdn_url = "https:" + data_src if data_src.startswith("//") else data_src

        # 로컬 파일 존재 여부 확인 (./carbot_namu_wiki_files/xxx.webp 형식)
        local_file = None
        if local_src.startswith("./"):
            candidate = html_path.parent / local_src[2:]
            if candidate.exists() and candidate.stat().st_size > 0:
                local_file = candidate

        entry = {"url": cdn_url, "local": local_file}
        cache[alt] = entry
        # "카봇 펜타스톰" → "펜타스톰" 단축키도 등록
        if alt.startswith("카봇 "):
            cache[alt[3:]] = entry

    print(f"[cache] {len(cache)}개 이미지 엔트리 로드 완료")
    return cache


def lookup_cache(name: str, cache_map: dict):
    """
    로봇 이름으로 cache_map 탐색.
    부분 매칭: name의 핵심 단어가 alt 키에 포함되거나 반대.
    (url, local_path_or_None, matched_key) 반환, 없으면 (None, None, None).
    """
    # 정규화: "카봇 " / "그랜드 카봇 " 제거해 핵심어 추출
    short = name
    for prefix in ("그랜드 카봇 ", "카봇 "):
        if short.startswith(prefix):
            short = short[len(prefix):]
            break

    candidates = [name, short, "카봇 " + short]
    for candidate in candidates:
        if candidate in cache_map:
            e = cache_map[candidate]
            return e["url"], e["local"], candidate

    # 부분 포함 탐색 (짧은 핵심어가 alt에 들어있는 경우)
    for key, e in cache_map.items():
        if short and (short in key or key in short):
            return e["url"], e["local"], key

    return None, None, None


# ────────────────────────────────────────────────────────────────────────
# 3. 개별 나무위키 페이지에서 이미지 URL 추출 (Playwright 헤드리스)
# ────────────────────────────────────────────────────────────────────────

def _get_og_image(pw_page) -> str:
    """현재 pw_page에서 og:image URL을 추출. 없으면 빈 문자열."""
    try:
        pw_page.wait_for_function(
            "() => !!document.querySelector('meta[property=\"og:image\"]')?.content",
            timeout=8_000,
        )
    except PWTimeout:
        pass
    img_url = pw_page.evaluate(
        "document.querySelector('meta[property=\"og:image\"]')?.getAttribute('content') || ''"
    )
    return ("https:" + img_url if img_url.startswith("//") else img_url) if img_url else ""


def _find_img_by_alt(pw_page, keyword: str) -> str:
    """
    페이지 내 <img> 중 alt 텍스트에 keyword가 포함되고
    i.namu.wiki CDN URL을 갖는 첫 번째 이미지 src 반환. 없으면 빈 문자열.
    """
    try:
        result = pw_page.evaluate(
            """(kw) => {
                for (const img of document.querySelectorAll('img')) {
                    const alt = (img.alt || '').toLowerCase();
                    const src = img.src || img.getAttribute('data-src') || '';
                    if (alt.includes(kw.toLowerCase()) && src.includes('namu.wiki')) {
                        return src.startsWith('//') ? 'https:' + src : src;
                    }
                }
                return '';
            }""",
            keyword,
        )
        return result or ""
    except Exception:
        return ""


def fetch_namu_image_url(pw_page, robot_name: str):
    """
    Playwright 브라우저 페이지 객체를 받아 나무위키에서 로봇 이미지 URL을 반환.
    없으면 None.

    1차: https://namu.wiki/w/카봇%20{name} — og:image 추출
    2차: FALLBACK_PAGE_MAP에 등록된 경우 합체 로봇 페이지에서 탐색
         → alt 텍스트 매칭 우선, 없으면 og:image
    """
    # 이름 정규화
    if robot_name.startswith("카봇 ") or robot_name.startswith("그랜드 카봇 "):
        query_name = robot_name
    else:
        query_name = "카봇 " + robot_name

    # ── 1차: 개별 페이지 ─────────────────────────────────────────────────
    url = "https://namu.wiki/w/" + urllib.parse.quote(query_name)
    print(f"    fetch: {url}")
    try:
        pw_page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        img_url = _get_og_image(pw_page)
        if img_url:
            return img_url

        # "카봇 " 접두어 없이 재시도
        if query_name != robot_name:
            url2 = "https://namu.wiki/w/" + urllib.parse.quote(robot_name)
            print(f"    retry: {url2}")
            pw_page.goto(url2, wait_until="domcontentloaded", timeout=30_000)
            img_url = _get_og_image(pw_page)
            if img_url:
                return img_url
    except Exception as e:
        print(f"    Playwright 오류(1차): {e}")

    # ── 2차: 폴백 페이지 (합체 로봇 페이지에서 alt 텍스트 매칭) ──────────
    fallback_name = FALLBACK_PAGE_MAP.get(query_name)
    if fallback_name:
        fb_url = "https://namu.wiki/w/" + urllib.parse.quote(fallback_name)
        print(f"    fallback: {fb_url}")
        try:
            pw_page.goto(fb_url, wait_until="domcontentloaded", timeout=30_000)
            # 핵심어(접두어 제거): "카봇 썬런" → "썬런"
            short = query_name
            for pfx in ("그랜드 카봇 ", "카봇 "):
                if short.startswith(pfx):
                    short = short[len(pfx):]
                    break
            img_url = _find_img_by_alt(pw_page, short)
            if img_url:
                print(f"    alt-match: '{short}'")
                return img_url
            # alt 매칭 실패 → 폴백 페이지 og:image
            img_url = _get_og_image(pw_page)
            if img_url:
                print(f"    fallback og:image")
                return img_url
        except Exception as e:
            print(f"    Playwright 오류(fallback): {e}")

    return None


# ────────────────────────────────────────────────────────────────────────
# 4. 이미지 다운로드 / WebP 변환
# ────────────────────────────────────────────────────────────────────────

def download_image(url: str, dest: Path) -> int:
    """URL에서 이미지를 다운로드하고 저장. 바이트 수 반환."""
    resp = _session.get(url, timeout=60)
    resp.raise_for_status()
    dest.write_bytes(resp.content)
    return len(resp.content)


def to_webp_square(src: Path, dest: Path, size: int = SIZE):
    """원본 이미지를 투명 패딩 정사각형 후 512×512 WebP(quality=88)로 변환."""
    with Image.open(src) as im:
        im = im.convert("RGBA")
        w, h = im.size
        side = max(w, h)
        canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
        canvas.paste(im, ((side - w) // 2, (side - h) // 2))
        canvas = canvas.resize((size, size), Image.LANCZOS)
        canvas.save(dest, "WEBP", quality=88, method=6)


# ────────────────────────────────────────────────────────────────────────
# 5. 공통 처리 루프
# ────────────────────────────────────────────────────────────────────────

def process_robot_list(robot_names: list, pw_page, cache_map: dict,
                       metadata: dict, force: bool) -> tuple:
    """
    robot_names 리스트를 순회하며 이미지 수집·변환.
    (success, skipped, failed, failures) 반환.
    """
    success = skipped = failed = 0
    failures = []

    for idx, name in enumerate(robot_names, 1):
        print(f"[{idx:02d}/{len(robot_names)}] {name}")

        safe_name = re.sub(r'[\\/*?:"<>|()\[\]]', "", name).strip()
        src_file = SRC_DIR / f"{safe_name}.webp"
        out_file = OUT_DIR / f"{safe_name}.webp"

        # 이미 완성 + 메타 있으면 스킵 (수동 추가 파일도 포함)
        already_done = out_file.exists() and out_file.stat().st_size > 0
        has_meta = bool(metadata.get(name, {}).get("url"))
        if already_done and (has_meta or not force):
            if not force:
                print(f"    skip (이미 완료)")
                skipped += 1
                continue

        # ── 이미지 URL 탐색 ──────────────────────────────────────────
        img_url = local_file = None
        source = "unknown"

        img_url, local_file, matched_key = lookup_cache(name, cache_map)
        if img_url:
            source = "local" if (local_file and local_file.exists()) else "cache"
            print(f"    cache hit: alt='{matched_key}' [{source}]")

        if not img_url:
            img_url = fetch_namu_image_url(pw_page, name)
            if img_url:
                source = "fetch"
            time.sleep(1.0)

        if not img_url:
            print(f"    FAIL: 이미지 URL을 찾지 못했습니다.")
            failed += 1
            failures.append(name)
            continue

        # ── 원본 준비 → WebP 변환 ────────────────────────────────────
        try:
            need_dl = not (src_file.exists() and src_file.stat().st_size > 0) or force
            if not need_dl:
                print(f"    src cached: {src_file.name}")
            elif source == "local" and local_file and local_file.exists():
                shutil.copy2(local_file, src_file)
                print(f"    copy local: {local_file.name}")
            else:
                size_bytes = download_image(img_url, src_file)
                print(f"    download: {size_bytes // 1024} KB  ← {img_url[:80]}")

            to_webp_square(src_file, out_file)
            print(f"    → {out_file.name}  ({out_file.stat().st_size // 1024} KB)")

            metadata[name] = {
                "url": img_url,
                "source": source,
                "safe_name": safe_name,
                "fetched_at": datetime.now().isoformat(timespec="seconds"),
            }
            META_FILE.write_text(
                json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            success += 1

        except Exception as e:
            print(f"    FAIL: {e}")
            failed += 1
            failures.append(name)

    return success, skipped, failed, failures


# ────────────────────────────────────────────────────────────────────────
# 6. 메인
# ────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="카봇 이미지 크롤러")
    parser.add_argument("--components", action="store_true",
                        help="합체 카봇 구성원 로봇 이미지 수집 (img_carbot에 없는 것만)")
    parser.add_argument("--all",   action="store_true",
                        help="전체 카봇 크롤링 (미구현, 향후 확장)")
    parser.add_argument("--force", action="store_true",
                        help="캐시 무시하고 재다운로드")
    args = parser.parse_args()

    OUT_DIR.mkdir(exist_ok=True)
    SRC_DIR.mkdir(exist_ok=True)

    metadata: dict = {}
    if META_FILE.exists() and not args.force:
        try:
            metadata = json.loads(META_FILE.read_text(encoding="utf-8"))
        except Exception:
            metadata = {}

    # ── 처리 대상 결정 ───────────────────────────────────────────────────
    if args.components:
        # 이미 img_carbot/ 에 있는 파일명(확장자 제외) 집합
        existing = {f.stem for f in OUT_DIR.glob("*.webp")}
        all_comp, pending = get_component_robots(existing)
        print(f"구성원 로봇 전체 {len(all_comp)}종 중 미수집 {len(pending)}종 처리 시작")
        print(f"(이미 있는 {len(all_comp) - len(pending)}종은 스킵)\n")
        robot_names = pending
        section_label = "구성원 로봇"
    else:
        robot_names = parse_combo_robots(MD_FILE)
        print(f"합체 카봇 {len(robot_names)}종 처리 시작\n")
        section_label = "합체 카봇"

    if args.all:
        print("[info] --all 모드는 아직 미구현입니다.\n")

    cache_map: dict = {}
    if CACHE_HTML.exists():
        cache_map = build_cache_map(CACHE_HTML)
    else:
        print(f"[warn] 캐시 HTML 없음 — Playwright fetch만 사용합니다.")
    print()

    # ── Playwright 브라우저 (전체 루프 재사용) ───────────────────────────
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="ko-KR",
            extra_http_headers={"Referer": "https://namu.wiki/"},
        )
        pw_page = context.new_page()
        success, skipped, failed, failures = process_robot_list(
            robot_names, pw_page, cache_map, metadata, args.force
        )
        browser.close()

    # ── 결과 요약 ────────────────────────────────────────────────────────
    print(f"\n{'=' * 55}")
    print(f"[{section_label}] 완료: {success}개 성공  /  {skipped}개 스킵  /  {failed}개 실패")
    if failures:
        print(f"\n실패 목록:")
        for f in failures:
            print(f"  - {f}")
    print(f"\n출력 디렉터리 : {OUT_DIR}")
    print(f"메타데이터    : {META_FILE}")


if __name__ == "__main__":
    main()
