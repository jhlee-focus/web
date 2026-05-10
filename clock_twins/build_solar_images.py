"""
태양계 시계용 이미지 빌더.
Wikimedia Commons에서 NASA(또는 동등한 공개 라이선스) 이미지를 받아
정사각형 512×512 WebP로 변환해 img_solar/ 에 저장한다.

run:  python build_solar_images.py   (clock_twins/ 디렉터리에서)
deps: pillow (already installed)
"""

import os
import io
import sys
import urllib.request
import urllib.error
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("PIL/Pillow is required. Install with: pip install Pillow", file=sys.stderr)
    sys.exit(1)

# (no, 이름, 위키미디어 직접 URL, 출처 라이선스 메모)
# 거리순 1~12 + 항성(no=13 마지막에 두고 파일명만 SS-01_태양으로 저장)
TARGETS = [
    # 1~11, 13: nineplanets.org 투명 배경 PNG (배경 제거되어 정사각 캔버스에 합성 시 깔끔함)
    ("01", "태양",     "https://nineplanets.org/wp-content/uploads/2020/03/sun.png"),
    ("02", "수성",     "https://nineplanets.org/wp-content/uploads/2020/03/mercury.png"),
    ("03", "금성",     "https://nineplanets.org/wp-content/uploads/2020/03/venus.png"),
    ("04", "지구",     "https://nineplanets.org/wp-content/uploads/2020/03/earth.png"),
    ("05", "달",       "https://nineplanets.org/wp-content/uploads/2020/03/moon.png"),
    ("06", "화성",     "https://nineplanets.org/wp-content/uploads/2020/03/mars.png"),
    ("07", "목성",     "https://nineplanets.org/wp-content/uploads/2020/03/jupiter.png"),
    ("08", "토성",     "https://nineplanets.org/wp-content/uploads/2020/03/saturn.png"),
    ("09", "천왕성",   "https://nineplanets.org/wp-content/uploads/2020/03/uranus.png"),
    ("10", "해왕성",   "https://nineplanets.org/wp-content/uploads/2020/03/neptune.png"),
    ("11", "명왕성",   "https://nineplanets.org/wp-content/uploads/2020/03/pluto.png"),
    # 12, 14: 외부 URL이 마땅치 않아 사용자가 직접 제공한 로컬 소스 사용
    # (img_solar_src/SS-12_핼리혜성.webp, SS-14_보이저1호.png)
    ("12", "핼리혜성", None),
    ("13", "에리스",   "https://nineplanets.org/wp-content/uploads/2020/03/eris.png"),
    ("14", "보이저1호", None),
]

OUT_DIR = Path("img_solar")
SRC_DIR = Path("img_solar_src")
SIZE = 512

# Wikimedia는 의미있는 User-Agent를 요구함 (정책)
HEADERS = {
    "User-Agent": "clock-twins-bot/1.0 (https://github.com/jhlee-focus/web; jhlee.focus@gmail.com) Python-urllib"
}


def download(url: str, dest: Path) -> bool:
    """Wikimedia에서 이미지를 받아 dest에 원본 그대로 저장."""
    if dest.exists() and dest.stat().st_size > 0:
        print(f"    cached: {dest.name}")
        return True
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
        dest.write_bytes(data)
        print(f"    downloaded: {dest.name}  ({len(data) // 1024} KB)")
        return True
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
        print(f"    FAILED {url}: {e}")
        return False


def to_webp_square(src: Path, dest: Path, size: int = SIZE) -> bool:
    """원본 이미지를 정사각형 RGBA로 패드 + 리사이즈 → WebP."""
    try:
        with Image.open(src) as im:
            im = im.convert("RGBA")
            w, h = im.size
            side = max(w, h)
            # 투명 배경 정사각형 캔버스
            canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
            canvas.paste(im, ((side - w) // 2, (side - h) // 2))
            canvas = canvas.resize((size, size), Image.LANCZOS)
            canvas.save(dest, "WEBP", quality=90, method=6)
        print(f"    -> {dest.name}  ({dest.stat().st_size // 1024} KB)")
        return True
    except Exception as e:
        print(f"    CONVERT FAILED {src.name}: {e}")
        return False


def main():
    OUT_DIR.mkdir(exist_ok=True)
    SRC_DIR.mkdir(exist_ok=True)

    ok = 0
    fail = []
    for no, name, url in TARGETS:
        print(f"[{no}] {name}")
        if url is None:
            # 로컬 소스 모드: 가장 최근에 수정된 SS-NN_이름.* 파일을 사용
            # (사용자가 새 이미지 추가/교체 시 자동으로 최신 파일이 선택되도록)
            existing = list(SRC_DIR.glob(f"SS-{no}_{name}.*"))
            if not existing:
                print(f"    MISSING local source for SS-{no}_{name}")
                fail.append((no, name, "<local>"))
                continue
            src_file = max(existing, key=lambda p: p.stat().st_mtime)
            print(f"    using local: {src_file.name}")
        else:
            ext = url.rsplit(".", 1)[-1].split("?")[0].lower()
            if ext not in ("jpg", "jpeg", "png", "gif", "tif", "tiff", "webp"):
                ext = "jpg"
            src_file = SRC_DIR / f"SS-{no}_{name}.{ext}"
            if not download(url, src_file):
                fail.append((no, name, url))
                continue
        out_file = OUT_DIR / f"SS-{no}_{name}.webp"
        if to_webp_square(src_file, out_file):
            ok += 1
        else:
            fail.append((no, name, url or "<local>"))

    print()
    print(f"done: {ok}/{len(TARGETS)} succeeded")
    if fail:
        print("FAILED:")
        for no, name, url in fail:
            print(f"  SS-{no} {name}: {url}")
        sys.exit(1)


if __name__ == "__main__":
    main()
