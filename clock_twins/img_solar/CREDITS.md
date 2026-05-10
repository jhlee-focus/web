# 태양계 시계 이미지 출처

이 디렉터리의 모든 이미지는 `build_solar_images.py`로 외부에서 받아 정사각 512×512 WebP로 변환한 결과물입니다. 1·2차 출처를 함께 기재합니다.

## 행성·태양·왜소행성 (1차: nineplanets.org 투명 배경 PNG)

| 파일 | 천체 | 원본 | 비고 |
|---|---|---|---|
| `SS-01_태양.webp` | 태양 | [sun.png](https://nineplanets.org/wp-content/uploads/2020/03/sun.png) | nineplanets.org / 교육 목적 사용 (저작자 표기 권장) |
| `SS-02_수성.webp` | 수성 | [mercury.png](https://nineplanets.org/wp-content/uploads/2020/03/mercury.png) | nineplanets.org |
| `SS-03_금성.webp` | 금성 | [venus.png](https://nineplanets.org/wp-content/uploads/2020/03/venus.png) | nineplanets.org |
| `SS-04_지구.webp` | 지구 | [earth.png](https://nineplanets.org/wp-content/uploads/2020/03/earth.png) | nineplanets.org |
| `SS-05_달.webp` | 달 | [moon.png](https://nineplanets.org/wp-content/uploads/2020/03/moon.png) | nineplanets.org |
| `SS-06_화성.webp` | 화성 | [mars.png](https://nineplanets.org/wp-content/uploads/2020/03/mars.png) | nineplanets.org |
| `SS-07_목성.webp` | 목성 | [jupiter.png](https://nineplanets.org/wp-content/uploads/2020/03/jupiter.png) | nineplanets.org |
| `SS-08_토성.webp` | 토성 | [saturn.png](https://nineplanets.org/wp-content/uploads/2020/03/saturn.png) | nineplanets.org |
| `SS-09_천왕성.webp` | 천왕성 | [uranus.png](https://nineplanets.org/wp-content/uploads/2020/03/uranus.png) | nineplanets.org |
| `SS-10_해왕성.webp` | 해왕성 | [neptune.png](https://nineplanets.org/wp-content/uploads/2020/03/neptune.png) | nineplanets.org |
| `SS-11_명왕성.webp` | 명왕성 | [pluto.png](https://nineplanets.org/wp-content/uploads/2020/03/pluto.png) | nineplanets.org |
| `SS-13_에리스.webp` | 에리스 | [eris.png](https://nineplanets.org/wp-content/uploads/2020/03/eris.png) | nineplanets.org |

## 혜성·탐사선 (사용자 제공 — 로컬 소스)

nineplanets.org에는 핼리혜성·보이저가 없어 사용자가 직접 제공한 이미지를 사용합니다. 원본 파일은 `img_solar_src/SS-12_핼리혜성.*`, `img_solar_src/SS-14_보이저1호.*`에 보관되며 (gitignored), 빌드 스크립트는 `URL=None`으로 설정해 가장 최근에 수정된 로컬 소스를 자동 선택합니다.

| 파일 | 천체 | 원본 파일명 | 비고 |
|---|---|---|---|
| `SS-12_핼리혜성.webp` | 핼리 혜성 | `Halley%27s_Comet_Icon.webp` | 사용자 제공 — 출처 표기는 사용자 측 책임 |
| `SS-14_보이저1호.webp` | 보이저 1호 | `Voyager_spacecraft_model.png` | 사용자 제공 — 출처 표기는 사용자 측 책임 |

## 재생성 방법

```sh
cd clock_twins/
python build_solar_images.py
```

원본은 `img_solar_src/`에 캐시되며 (gitignore), 변환 결과만 `img_solar/`에 커밋됩니다.

## 출처 표기

- **nineplanets.org**: 행성·태양·왜소행성 투명 배경 일러스트 — 무료 공개 이미지로 명시되어 있으며, 사용 시 출처 표기를 권장합니다. 본 페이지는 교육·취미 목적으로 사용합니다.
- **NASA / Wikimedia Commons**: 핼리혜성·보이저 1호 이미지 — 미국 정부 저작물로 Public Domain.
