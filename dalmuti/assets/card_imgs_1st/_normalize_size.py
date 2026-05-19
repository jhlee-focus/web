"""투명 PNG 카드들을 동일한 크기 + 종횡비로 정규화.

- 각 카드의 alpha>0 영역 bbox 로 타이트 크롭
- 모두 동일 (TARGET_W, TARGET_H) 로 리사이즈 (LANCZOS)
- 게임 애셋으로 즉시 사용 가능

종횡비 0.683 (=820/1200) 은 13장 측정치의 중앙값. 평균 왜곡 ~3%, 최대 ~5%.
"""
from PIL import Image
from pathlib import Path

TARGET_W = 820
TARGET_H = 1200
HERE = Path(__file__).parent


def normalize(in_path: Path) -> dict:
    img = Image.open(in_path).convert("RGBA")
    bbox = img.getbbox()
    if not bbox:
        return {"name": in_path.name, "skipped": True}
    cropped = img.crop(bbox)
    bw, bh = cropped.size
    resized = cropped.resize((TARGET_W, TARGET_H), Image.LANCZOS)
    resized.save(in_path, "PNG", optimize=True)
    return {
        "name": in_path.name,
        "src": (bw, bh),
        "src_aspect": bw / bh,
        "dst": (TARGET_W, TARGET_H),
        "stretch_w": TARGET_W / bw - 1,
        "stretch_h": TARGET_H / bh - 1,
    }


def main():
    files = sorted(p for p in HERE.glob("*.png") if not p.name.startswith("_"))
    print(f"target: {TARGET_W}x{TARGET_H} (aspect {TARGET_W/TARGET_H:.3f})")
    for f in files:
        r = normalize(f)
        if r.get("skipped"):
            print(f"{r['name']:12s} SKIPPED (no opaque pixels)")
            continue
        print(
            f"{r['name']:12s} {r['src'][0]:4d}x{r['src'][1]:4d}"
            f" (asp {r['src_aspect']:.3f}) → {TARGET_W}x{TARGET_H}"
            f"  stretch w{r['stretch_w']*100:+5.1f}% h{r['stretch_h']*100:+5.1f}%"
        )


if __name__ == "__main__":
    main()
