"""카드 이미지의 둥근 모서리 바깥 크림 배경을 투명으로 변환.

방법:
1. 이미지를 RGBA 로 로드.
2. 4개의 모서리 픽셀 색을 샘플링 → 배경색으로 간주.
3. 4개의 모서리에서 flood-fill (BFS) 로 인접 + tolerance 내의 픽셀을 알파 0 으로.
4. PNG 로 저장.

플러드 필은 둥근 모서리를 따라 자연스럽게 카드 윤곽까지만 펼쳐짐.
카드 내부에 같은 크림색이 있어도 카드 테두리에 막혀서 영향 안 받음.
"""
from PIL import Image
from collections import deque
from pathlib import Path
import sys

TOLERANCE = 32  # RGB 각 채널 최대 허용 차이
HERE = Path(__file__).parent


def color_distance(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]), abs(a[2] - b[2]))


def make_transparent(in_path: Path, out_path: Path) -> dict:
    img = Image.open(in_path).convert("RGBA")
    w, h = img.size
    px = img.load()

    # 4 모서리 픽셀로 배경색 평균
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    samples = [px[x, y][:3] for x, y in corners]
    bg = tuple(sum(s[i] for s in samples) // len(samples) for i in range(3))

    # BFS flood-fill from each corner
    visited = bytearray(w * h)  # 1 = transparent already
    queue = deque()
    for cx, cy in corners:
        if not visited[cy * w + cx]:
            r, g, b, _ = px[cx, cy]
            if color_distance((r, g, b), bg) <= TOLERANCE:
                visited[cy * w + cx] = 1
                queue.append((cx, cy))

    changed = 0
    while queue:
        x, y = queue.popleft()
        px[x, y] = (px[x, y][0], px[x, y][1], px[x, y][2], 0)
        changed += 1
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h:
                idx = ny * w + nx
                if visited[idx]:
                    continue
                r, g, b, _ = px[nx, ny]
                if color_distance((r, g, b), bg) <= TOLERANCE:
                    visited[idx] = 1
                    queue.append((nx, ny))

    img.save(out_path, "PNG", optimize=True)
    return {"size": (w, h), "bg": bg, "transparent_px": changed, "total_px": w * h}


def main():
    files = sorted(HERE.glob("*.png"))
    for f in files:
        if f.name.startswith("_"):
            continue
        result = make_transparent(f, f)
        ratio = 100 * result["transparent_px"] / result["total_px"]
        print(f"{f.name}: bg={result['bg']} transparent {result['transparent_px']:>7,} px ({ratio:5.1f}%)")


if __name__ == "__main__":
    main()
