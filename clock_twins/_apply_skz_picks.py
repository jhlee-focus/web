"""SKZ 시계 — 16 캐릭터(8 멤버 + 8 SKZOO) 자산 가공.

각 후보 이미지를:
  1) img_skz_src/ 에 복사 (DN-NN_식별자.확장자)
  2) (SKZOO만) 우상단 SKZOO 로고를 잘라낸 뒤
  3) rembg(ISNet-general-use) 로 배경 제거 → transparent PNG
  4) to_webp_square 로 512×512 WebP → img_skz/

멤버 사진은 일본 JYP 프로필(데님 톤, 캐주얼) 우선 — 한국 dominATE 프로필은
6-7세 어린이에게 너무 강렬해서 제외.
"""
import shutil
import sys
from pathlib import Path
from PIL import Image
from rembg import remove, new_session

sys.path.insert(0, '.')
import build_dinosaur_data as b  # to_webp_square 재사용 (이미 RGBA 처리됨)

CANDIDATES = Path("img_skz_candidates")
SRC_DIR = Path("img_skz_src")
OUT_DIR = Path("img_skz")
SRC_DIR.mkdir(exist_ok=True)
OUT_DIR.mkdir(exist_ok=True)

# (no, slug_ko, kind, candidate_relpath, source_note)
PICKS = [
    # 멤버 8명 — 일본 프로필 (캐주얼 데님 톤)
    ("01", "방찬",     "member",
     "01_BangChan/01_Bang_Chan_Profile_Picture_-_Japan.jpg",
     "JYP Japan official profile (denim, dominATE era)"),
    ("02", "리노",     "member",
     "02_LeeKnow/01_Lee_Know_Profile_Picture_-_Japan.jpg",
     "JYP Japan official profile"),
    ("03", "창빈",     "member",
     "03_Changbin/01_Changbin_Profile_Picture_-_Japan.jpg",
     "JYP Japan official profile"),
    ("04", "현진",     "member",
     "04_Hyunjin/01_Hyunjin_Profile_Picture_-_Japan.jpg",
     "JYP Japan official profile"),
    ("05", "한",       "member",
     "05_HAN/01_HAN_Profile_Picture_-_Japan.jpg",
     "JYP Japan official profile"),
    ("06", "필릭스",   "member",
     "06_Felix/01_Felix_Profile_Picture_-_Japan.jpg",
     "JYP Japan official profile"),
    ("07", "승민",     "member",
     "07_Seungmin/01_Seungmin_Profile_Picture_-_Japan.jpg",
     "JYP Japan official profile"),
    ("08", "아이엔",   "member",
     "08_IN/01_I.N_Profile_Picture_-_Japan.jpg",
     "JYP Japan official profile"),
    # SKZOO 8마리 — 공식 2D 일러스트
    ("09", "울프찬",   "skzoo",
     "09_WolfChan/01_Wolf_Chan_SKZOO_2D.jpg",
     "SKZOO official 2D art (JYP/SKZOO)"),
    ("10", "리빗",     "skzoo",
     "10_Leebit/01_Leebit_SKZOO_2D.jpg",
     "SKZOO official 2D art"),
    ("11", "돼끼",     "skzoo",
     "11_DWAEKKI/01_DWAEKKI_SKZOO_2D.jpg",
     "SKZOO official 2D art"),
    ("12", "지니렛",   "skzoo",
     "12_Jiniret/01_Jiniret_SKZOO_2D.jpg",
     "SKZOO official 2D art"),
    ("13", "한쿼카",   "skzoo",
     "13_HANQUOKKA/01_HAN_QUOKKA_SKZOO_2D.jpg",
     "SKZOO official 2D art"),
    ("14", "뽁아리",   "skzoo",
     "14_BbokAri/01_Bbokari_SKZOO_2D.jpg",
     "SKZOO official 2D art"),
    ("15", "퍼핌",     "skzoo",
     "15_PuppyM/01_PuppyM_SKZOO_2D.jpg",
     "SKZOO official 2D art"),
    ("16", "폭시니",   "skzoo",
     "16_FoxINy/01_FoxI.Ny_SKZOO_2D.jpg",
     "SKZOO official 2D art"),
]


def crop_top_right_logo(img: Image.Image, kind: str) -> Image.Image:
    """SKZOO 2D 일러스트는 우상단에 'SKZOO' 로고가 박혀 있어 rembg가 잡아둠.
    위쪽 12% 행 + 오른쪽 25% 열의 교차 영역을 배경색으로 덮어 가린다."""
    if kind != "skzoo":
        return img
    img = img.convert("RGB")
    w, h = img.size
    # 배경 색 추정 — 좌상단 코너 픽셀
    bg = img.getpixel((2, 2))
    from PIL import ImageDraw
    canvas = img.copy()
    draw = ImageDraw.Draw(canvas)
    # rect: x0=w*0.72, y0=0, x1=w, y1=h*0.13
    draw.rectangle([int(w * 0.70), 0, w, int(h * 0.14)], fill=bg)
    return canvas


print("rembg 모델 로드 중 (첫 실행 시 ~150MB 다운로드)...")
session = new_session("isnet-general-use")

failures = []
for no, ko, kind, rel, source in PICKS:
    src_cand = CANDIDATES / rel
    if not src_cand.exists():
        print(f"[{no}] {ko}: candidate not found: {src_cand}")
        failures.append((no, ko))
        continue
    ext = src_cand.suffix.lstrip(".").lower()
    src_file = SRC_DIR / f"SKZ-{no}_{ko}.{ext}"
    shutil.copy(src_cand, src_file)
    print(f"[{no}] {ko} ({kind})  <- {src_cand.name}")
    # 1) SKZOO 로고 가리기
    with Image.open(src_file) as im:
        im2 = crop_top_right_logo(im, kind)
        # 2) rembg
        cleaned = remove(im2, session=session)
    nobg = SRC_DIR / f"SKZ-{no}_{ko}_nobg.png"
    cleaned.save(nobg, "PNG")
    print(f"     nobg -> {nobg.name} ({nobg.stat().st_size // 1024} KB)")
    # 3) 512x512 WebP
    out = OUT_DIR / f"SKZ-{no}_{ko}.webp"
    b.to_webp_square(nobg, out)
    print(f"     webp -> {out.name} ({out.stat().st_size // 1024} KB)")

print()
print(f"DONE — {len(PICKS) - len(failures)}/{len(PICKS)} succeeded")
if failures:
    print("FAILED:", failures)
