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

def fetch_namu_image_url(pw_page, robot_name: str):
    """
    Playwright 브라우저 페이지 객체를 받아
    https://namu.wiki/w/카봇%20{name} 을 렌더링한 뒤
    og:image 메타 태그 URL을 반환. 없으면 None.

    나무위키는 SPA(React)라 requests HTML에는 og:image가 없음 →
    JS가 실행된 뒤 meta[property="og:image"]가 채워짐.
    """
    # 이름 정규화: "카봇 " / "그랜드 카봇 " 접두어 없으면 추가
    if robot_name.startswith("카봇 ") or robot_name.startswith("그랜드 카봇 "):
        query_name = robot_name
    else:
        query_name = "카봇 " + robot_name

    url = "https://namu.wiki/w/" + urllib.parse.quote(query_name)
    print(f"    fetch: {url}")

    try:
        pw_page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        # React 앱이 meta 태그를 채울 때까지 잠시 대기
        try:
            pw_page.wait_for_function(
                "() => !!document.querySelector('meta[property=\"og:image\"]')?.content",
                timeout=8_000,
            )
        except PWTimeout:
            pass  # 타임아웃이어도 있는 것으로 시도

        img_url = pw_page.evaluate(
            "document.querySelector('meta[property=\"og:image\"]')?.getAttribute('content') || ''"
        )
        if img_url:
            return "https:" + img_url if img_url.startswith("//") else img_url

        # 404 등 → 이름 그대로 재시도
        if query_name != robot_name:
            url2 = "https://namu.wiki/w/" + urllib.parse.quote(robot_name)
            print(f"    retry: {url2}")
            pw_page.goto(url2, wait_until="domcontentloaded", timeout=30_000)
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
            if img_url:
                return "https:" + img_url if img_url.startswith("//") else img_url

    except Exception as e:
        print(f"    Playwright 오류: {e}")

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
# 5. 메인
# ────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="카봇 이미지 크롤러")
    parser.add_argument("--all",   action="store_true", help="전체 카봇 크롤링 (미구현, 향후 확장)")
    parser.add_argument("--force", action="store_true", help="캐시 무시하고 재다운로드")
    args = parser.parse_args()

    if args.all:
        print("[info] --all 모드는 아직 미구현입니다. 합체 카봇만 처리합니다.\n")

    OUT_DIR.mkdir(exist_ok=True)
    SRC_DIR.mkdir(exist_ok=True)

    # 메타데이터 로드
    metadata: dict = {}
    if META_FILE.exists() and not args.force:
        try:
            metadata = json.loads(META_FILE.read_text(encoding="utf-8"))
        except Exception:
            metadata = {}

    # 합체 카봇 이름 목록
    robot_names = parse_combo_robots(MD_FILE)
    print(f"합체 카봇 {len(robot_names)}종 처리 시작\n")

    # 로컬 캐시 맵 구성
    cache_map: dict = {}
    if CACHE_HTML.exists():
        cache_map = build_cache_map(CACHE_HTML)
    else:
        print(f"[warn] 캐시 HTML 없음: {CACHE_HTML.name} — 모두 Playwright fetch로 처리합니다.")

    print()
    success = skipped = failed = 0
    failures = []

    # ── Playwright 브라우저 초기화 (전체 루프에서 재사용) ────────────────
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

        for idx, name in enumerate(robot_names, 1):
            print(f"[{idx:02d}/{len(robot_names)}] {name}")

            # 안전한 파일명 (경로 특수문자 제거)
            safe_name = re.sub(r'[\\/*?:"<>|()\[\]]', "", name).strip()
            src_file = SRC_DIR / f"{safe_name}.webp"
            out_file = OUT_DIR / f"{safe_name}.webp"

            # 이미 완성된 출력 파일 + 메타가 있으면 스킵
            if (out_file.exists() and out_file.stat().st_size > 0
                    and metadata.get(name, {}).get("url")
                    and not args.force):
                print(f"    skip (이미 완료)")
                skipped += 1
                continue

            # ── 이미지 URL 탐색 ──────────────────────────────────────
            img_url = None
            local_file = None
            source = "unknown"

            # 1) 로컬 캐시 HTML에서 alt 텍스트로 매칭
            img_url, local_file, matched_key = lookup_cache(name, cache_map)
            if img_url:
                source = "local" if (local_file and local_file.exists()) else "cache"
                print(f"    cache hit: alt='{matched_key}' [{source}]")

            # 2) fallback: Playwright로 개별 나무위키 페이지 렌더링
            if not img_url:
                img_url = fetch_namu_image_url(pw_page, name)
                if img_url:
                    source = "fetch"
                time.sleep(1.0)  # rate-limit 회피

            if not img_url:
                print(f"    FAIL: 이미지 URL을 찾지 못했습니다.")
                failed += 1
                failures.append(name)
                continue

            # ── 원본 파일 준비 ───────────────────────────────────────
            try:
                need_download = not (src_file.exists() and src_file.stat().st_size > 0)

                if not need_download and not args.force:
                    print(f"    src cached: {src_file.name}")
                elif source == "local" and local_file and local_file.exists():
                    # 로컬 캐시 파일 복사 (HTTP 요청 불필요)
                    shutil.copy2(local_file, src_file)
                    print(f"    copy local: {local_file.name}")
                else:
                    size_bytes = download_image(img_url, src_file)
                    print(f"    download: {size_bytes // 1024} KB  ← {img_url[:80]}")

                # ── WebP 512×512 변환 ────────────────────────────────
                to_webp_square(src_file, out_file)
                print(f"    → {out_file.name}  ({out_file.stat().st_size // 1024} KB)")

                # 메타데이터 저장 (매 항목마다 갱신해 중단 복구 가능)
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

        browser.close()

    # ── 결과 요약 ────────────────────────────────────────────────────────
    print(f"\n{'=' * 55}")
    print(f"완료: {success}개 성공  /  {skipped}개 스킵  /  {failed}개 실패")
    if failures:
        print(f"\n실패 목록:")
        for f in failures:
            print(f"  - {f}")
    print(f"\n출력 디렉터리 : {OUT_DIR}")
    print(f"메타데이터    : {META_FILE}")


if __name__ == "__main__":
    main()
