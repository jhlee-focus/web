# 둥둥이 시계 (clock_twins)

어린이를 위한 5개의 테마 아날로그 시계 모음 — **티니핑 · 포켓몬 · 태양계 · 공룡 · 스트레이키즈(SKZ)**.  
각 시계는 12시 자리에 12개의 캐릭터(또는 행성/공룡/멤버)가 배치되고, 도감 모드에서 전체 라인업을 탐색할 수 있다.

## 빠른 실행

이 디렉터리는 정적 HTML/JS/CSS만 사용한다. 빌드 단계 없음.

```sh
# 저장소 루트에서
python -m http.server --bind 127.0.0.1 8000
# 그 후 http://localhost:8000/clock_twins/ 열기
```

또는 `clock_twins/index.html`을 더블클릭해도 동작은 하지만, 일부 fetch 기반 기능(포켓몬 세대 로드 등)이 file:// 스킴에서 실패할 수 있어 로컬 서버 권장.

## 페이지 구성

| 파일 | 시계 | 자산 폴더 | 데이터 |
|---|---|---|---|
| `index.html` | 5개 시계 카드 허브 | — | — |
| `teenieping.html` | 티니핑 시계 | `img_teenieping/` | `teenieping_list.js` |
| `pokemon.html` | 포켓몬 시계 (9세대) | `img_pokemon/`, `img_pokemon/dot/` | `pokemon_data.js`, `pokemon_gen1.js` ~ `pokemon_gen9.js`, `pokemon_evolutions.js` |
| `solar.html` | 태양계 시계 | `img_solar/` | `solar_data.js` |
| `dinosaur.html` | 공룡 시계 (가사 ABC 26 + 시대별 56) | `img_dinosaur/` | `dinosaur_data.js` |
| `skz.html` | SKZ 시계 (멤버 8 + SKZOO 8 페어) | `img_skz/` | `skz_data.js` |

모든 페이지에 공통으로 들어가는 컴포넌트:
- `osk.css` + `osk.js` — 한글 화면 키보드 (모바일 검색용)
- 시계 페이스, 시침/분침/초침, 12 자리 마커
- 기본/전체/도감 3-모드 토글

## 모드

- **기본 모드**: 시계 12자리에 큐레이션된 12개 캐릭터
- **전체 모드**: 전체 라인업에서 무작위 12개 추첨 (새로고침 가능)
- **도감 모드**: 그리드로 전체 라인업 탐색
  - 공룡: `🦴 시대별 보기` ↔ `🎵 알파벳송 순서` (26공룡 + 영상)
  - 포켓몬: 9개 세대 탭, 진화 트리 표시
  - 태양계: 거리·궤도 정보 차트
  - 티니핑: 단일 그리드 + & 합체 핑 매칭

## 자산 정책

### 커밋되는 자산 (앱 실행에 필요)

`img_teenieping/`, `img_pokemon/`, `img_solar/`, `img_dinosaur/` — 512×512 WebP 또는 PNG로 통일된 최종 자산.

### `img_pokemon/dot/` (도트 그래픽)

별도 도트 픽셀 그래픽. 현재는 일부 페이지의 작은 썸네일/8비트 표현에만 사용 (정책: **메인 일러스트는 `img_pokemon/`, 작은 도트/픽셀 표현은 `img_pokemon/dot/`**).

### gitignored 자산 (재생성용 원본 캐시)

- `img_teenieping_src/` — `build_teenieping_list.py` 원본 입력 (현재 미사용)
- `img_solar_src/` — `build_solar_images.py` NASA/Wikipedia 다운로드 캐시
- `img_dinosaur_src/` — `build_dinosaur_data.py` dino.fandom 다운로드 캐시 + `_raw_descriptions.json` (47KB, 56종 메타데이터)
- `img_dinosaur_candidates/` — 종별 후보 이미지 (시각 검수 후 픽한 것만 src로 승격)

**현재 앱 실행에는 이 폴더들 없어도 정상 동작.** 자산 재생성/추가 시에만 필요.

## 자산 재생성

각 빌드 스크립트는 Python 3.10+ 환경 + `requirements.txt` 의존성 필요.

```sh
pip install -r clock_twins/requirements.txt
cd clock_twins/
```

### 공룡

```sh
python build_dinosaur_data.py            # dino.fandom 크롤링 (대부분의 종)
python _apply_picks.py                   # PR #78 수동 픽 4종 덮어쓰기
python _apply_abc_song_picks.py          # PR #81 신규 12종 (ABC 가사 종)
python _rembg_picks.py                   # PR #83 6종 배경 제거 (rembg + ISNet)
python _build_dinosaur_js.py             # dinosaur_data.js + img_dinosaur/CREDITS.md
```

전체 흐름은 `img_dinosaur/CREDITS.md`에 출처 + 라이선스 함께 정리.

### 태양계

```sh
python build_solar_images.py             # NASA/Wikipedia 이미지 다운로드 + 512x512 WebP
```

### 티니핑

```sh
python build_teenieping_list.py          # 엑셀 메타 → teenieping_list.js
```

`build_teenieping_list.py`의 `SRC_DIR`는 `img_teenieping_src/`(원본 PNG 모음)를 기대하지만, 현재 저장소는 변환 결과인 `img_teenieping/`만 커밋됨. 원본 다시 모으려면 namu 위키 기반 가공이 필요.

### 포켓몬

이미지 자산은 외부 다운로드 스크립트 없이 수동 큐레이션. 메타데이터는 `pokemon_pokedex_with_evolution.xlsx`(커밋됨)를 입력으로 ad-hoc 변환.

## 의존성

`requirements.txt` 참조. 핵심:
- `Pillow` — 512×512 WebP 변환 + RGBA 처리
- `openpyxl` — 엑셀 메타 파싱
- `rembg` — 자동 배경 제거 (ISNet-general-use 모델)

표준 라이브러리만 사용하는 스크립트(`_find_alternatives.py` 등)는 `urllib.request` + `http.cookiejar`로 fandom 위키 크롤링.

## 외부 의존

- **YouTube IFrame API** — 공룡 도감 알파벳송 영상 임베드 (자동 차단 + 커스텀 재생 버튼)
- **youtube-nocookie.com** — 임베드 도메인 (개인정보 강화)

## 파일 구조

```
clock_twins/
├── README.md               (이 파일)
├── requirements.txt
├── index.html              4개 시계 카드 허브
├── teenieping.html
├── pokemon.html
├── solar.html
├── dinosaur.html
├── osk.css osk.js          공통 화면 키보드
├── *_data.js *_list.js     각 시계 데이터
├── pokemon_gen{1..9}.js    포켓몬 세대별 라인업 (lazy load)
├── pokemon_evolutions.js   진화 트리
├── img_{teenieping,pokemon,solar,dinosaur}/   ← 커밋됨
└── build_*.py _*.py        재생성 스크립트 (실행 안 해도 앱은 동작)
```

## 머지된 PR 이력

티니핑/포켓몬/태양계 초기 구현 외에 공룡 시계 관련 누적 PR:

- #67 공룡 시계 초기 구현
- #77 이미지 감사·재크롤링 10종
- #78 4종 실사형 투명 교체
- #79 알파벳송 모드 + 한글·영문 병기
- #80 핑크퐁 ABC 영상 임베드 → #82에서 주니토니로 정정
- #81 알파벳송 가사 기준 26종 재구성 + 신규 12종
- #82 영상 출처 교체
- #83 6종 배경 제거 (rembg)
- #84 영상 터치 차단 (pointer-events shield + YT IFrame API)
