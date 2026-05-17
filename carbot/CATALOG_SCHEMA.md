# 카봇 카탈로그 스키마

> 헬로카봇 이미지 수집/관리를 위한 분류·모드·변종 정의서.
> 최종 갱신: 2026-05-18

---

## 1. 역할 분류 (Role)

| 역할 | 정의 | 예시 |
|---|---|---|
| **standalone** (개별) | 합체와 무관, 단독 활약 | 카봇 호크, 카봇 빅터, 카봇 라란자, 카봇 팔로, 카봇 베어하이더, 알카봇 시리즈, 카봇 트루 |
| **member** (멤버) | 합체의 구성요소 | 카봇 에이스, 카봇 스카이, 카봇 가드, 카봇 자크, 카봇 마이스터 |
| **combined** (합체) | 멤버들이 합쳐진 거대 로봇 | 카봇 펜타스톰, 카봇 마이티가드, 카봇 로드세이버 |

**비직교 (Non-orthogonal)**: 한 카봇이 여러 역할을 동시에 가짐.
→ 데이터 모델에서는 `roles: ["member", "standalone"]`처럼 set으로 표현.

---

## 2. 모드 (Mode) — 한 카봇이 가질 수 있는 형태

| 모드 키 | 설명 | 예시 |
|---|---|---|
| `robot` | 인간형/휴머노이드 로봇 | 거의 모든 카봇 |
| `vehicle` | 자동차/항공기/선박 등 탈것 | 카봇 스카이의 해치백, 카봇 에이스의 SUV |
| `beast` | 동물 형태 (전신 또는 하체) | 카봇 팔로 (아프리카물소 하체), 카봇 베어하이더 (곰), 카봇 디고베어, 카봇 이글하이더 |
| `animal_full` | 완전한 진짜 동물 모드 (트리플 체인저용) | 카봇 팔로 (완전 물소 모드) |
| `power` | 합체 로봇의 분노형/강화형 | 로어세이버 파워 모드 (= 로드세이버의 곰형) |
| `armed` | 특정 무장 장착 형태 (변형은 아님) | 펜타스톰 X 빅큐브, 새니타이저 캐논만 장비형 |
| `combined_only` | 단독 변형 없이 합체 시에만 변형 | 마이스터/아티 (작중에선 합체용으로만 변형) |

핵심: **한 카봇 인스턴스에 모드는 1개가 아닌 N개**. 모드별로 이미지가 따로 있음.

---

## 3. 변종 차원 (Variation Axis)

| 변종 축 | 변종 키 | 예시 | 변경 내용 |
|---|---|---|---|
| 시즌 진화 | `x` | 스카이 → 스카이 S.W.A.T X (시즌 9) | 디자인 강화, 새 비클, 새 기술 |
| 컬러/소재 | `crystal` | 크리스탈 카봇 스카이 S.W.A.T X (시즌 13) | 반투명 재질, 빨간 포인트 |
| 컬러/소재 | `gold` | 카봇 펜타스톰 황금특공대 (시즌 10) | 황금 맥기, 블랙+골드 투톤 |
| 컬러/소재 | `allstar` | 카봇 로드세이버 올스타 (시즌 15) | 반투명 어레인지 |
| 컬러/소재 | `refine` / `facelift` | 카봇 펜타스톰 리파인 (시즌 16) | 페이스리프트 디자인 |
| 무장 추가 | `bigcube` | 카봇 펜타스톰 X 빅큐브 (시즌 14) | 빅큐브 무장 장착 |
| 무장 추가 | `lifecannon` | 카봇 펜타스톰 X 라이프 캐논 모드 (시즌 14) | 새니타이저 캐논 + 콰트로 클로 |
| 합체 방식 변경 | `power_mode` / `rage` | 로드세이버 → 로어세이버 파워 모드 | 같은 멤버, **다른 합체 결과** (인간형 ↔ 곰형) |
| 멤버 추가/교체 | `+life_x` | 펜타스톰 X (5단) → 펜타스톰 X 라이프 캐논 모드 (6단) | 멤버 1개 추가로 그레이트 합체 |
| 크로스 콤비네이션 | `_cross` | 마하피스 / 브레이피스 / 마하로드 / 브레이로드 | 상체-하체 멤버 교차로 4가지 합체 |
| 비클 변종 | `_taxi`, `_swat`, `_police`, `_ambulance` | 스카이 (기본) / 스카이 S.W.A.T / 댄디 (구급차) | 같은 멤버의 다른 비클 모드 |

---

## 4. 데이터 모델 (JSON Schema)

### 4.1 멤버/개별 로봇

```jsonc
{
  "id": "carbot_sky",
  "korean_name": "카봇 스카이",
  "english_name": "Carbot Sky",
  "namu_url": "https://namu.wiki/w/카봇 스카이",
  "roles": ["member", "standalone"],
  "season_first": 1,
  "gender": "여성",
  "voice_actor": "사문영",
  "combines_to": [
    "carbot_pentastorm",
    "carbot_pentastorm_x",
    "carbot_pentastorm_x_bigcube",
    "carbot_pentastorm_x_lifecannon"
  ],
  "variations": [
    {
      "id": "basic",
      "korean_name": "카봇 스카이",
      "season_range": [1, 16],
      "vehicle_type": "해치백",
      "car_model": "현대 벨로스터 1세대",
      "color": "주황색",
      "modes": {
        "robot":   { "image_url": "...", "alt": "..." },
        "vehicle": { "image_url": "...", "alt": "..." }
      }
    },
    {
      "id": "swat",
      "korean_name": "카봇 스카이 S.W.A.T",
      "season_range": [1, null],
      "vehicle_type": "해치백 S.W.A.T 경찰차",
      "color": "검은색",
      "modes": { "robot": {...}, "vehicle": {...} }
    },
    {
      "id": "swat_x",
      "korean_name": "카봇 스카이 S.W.A.T X",
      "season_range": [9, 15],
      "variation_axis": "x",
      "modes": { "robot": {...}, "vehicle": {...} }
    },
    {
      "id": "swat_x_crystal",
      "korean_name": "크리스탈 카봇 스카이 S.W.A.T X",
      "season_range": [13, 13],
      "base_variation": "swat_x",
      "variation_axis": "crystal",
      "modes": { "robot": {...} }
    }
  ]
}
```

### 4.2 합체 로봇

```jsonc
{
  "id": "carbot_pentastorm_x_lifecannon",
  "korean_name": "카봇 펜타스톰 X 라이프 캐논 모드",
  "roles": ["combined"],
  "composed_of": [
    "carbot_storm/swat_x",
    "carbot_ace/swat_x",
    "carbot_phron/swat_x",
    "carbot_dandy/swat_x",
    "carbot_sky/swat_x",
    "carbot_life_x/basic"
  ],
  "season_first": 14,
  "combination_type": "great_combine",
  "weapons": ["새니타이저 캐논", "콰트로 클로"],
  "merge_call": "펜타스톰, 라이프 X 플러스!",
  "modes": {
    "robot": { "image_url": "..." }
  },
  "compatible_with": ["carbot_pentastorm_x_bigcube"]
}
```

---

## 5. 파일명 규칙

```
<한국어이름>__<변종키>__<모드>.webp
```

이중 언더스코어로 필드 구분 (이름에 단일 `_`가 들어갈 수 있어서).

### 5.1 예시

| 파일명 | 의미 |
|---|---|
| `카봇 스카이__basic__robot.webp` | 기본 스카이 로봇 모드 |
| `카봇 스카이__basic__vehicle.webp` | 기본 스카이 비클 모드 (벨로스터 자가용) |
| `카봇 스카이__swat__robot.webp` | S.W.A.T 변종 로봇 |
| `카봇 스카이__swat__vehicle.webp` | S.W.A.T 변종 경찰차 |
| `카봇 스카이__swat_x__robot.webp` | X 강화판 로봇 |
| `카봇 스카이__swat_x__vehicle.webp` | X 강화판 비클 |
| `카봇 스카이__swat_x_crystal__robot.webp` | 크리스탈 변종 |
| `카봇 팔로__basic__robot.webp` | 팔로 로봇 모드 |
| `카봇 팔로__basic__beast.webp` | 팔로 비스트(하체 물소) |
| `카봇 팔로__basic__animal_full.webp` | 팔로 완전 물소 (트리플 체인저) |
| `카봇 로드세이버__basic__robot.webp` | 로드세이버 인간형 |
| `카봇 로드세이버__basic__power.webp` | 로어세이버 파워 모드 (곰형) |
| `카봇 로드세이버__allstar__robot.webp` | 올스타 인간형 |
| `카봇 로드세이버__allstar__power.webp` | 올스타 곰형 |
| `카봇 펜타스톰__basic__robot.webp` | 기본 펜타스톰 |
| `카봇 펜타스톰__gold__robot.webp` | 황금특공대 |
| `카봇 펜타스톰__refine__robot.webp` | 리파인 |
| `카봇 펜타스톰 X__basic__robot.webp` | 펜타스톰 X 기본 |
| `카봇 펜타스톰 X__crystal__robot.webp` | 크리스탈 펜타스톰 X |
| `카봇 펜타스톰 X__bigcube__robot.webp` | 빅큐브 장착 |
| `카봇 펜타스톰 X__lifecannon__robot.webp` | 라이프 캐논 (6단) |
| `카봇 마하피스__cross__robot.webp` | 마하+피스 교차 합체 |

---

## 6. 크롤러 보완 사항

| 차원 | 현재 (`build_carbot_images.py`) | 보완 후 |
|---|---|---|
| 이미지 수 | `og:image` 1장 | 페이지 내 모든 `i.namu.wiki` `<img>` 추출 |
| (변종, 모드) 라벨링 | 없음 | 섹션 헤더 `### 3.x` + 인접 표 라벨 ("로봇 모드"/"비클 모드"/"비스트 모드"/"파워 모드") 매칭 |
| 역할 자동 판정 | 없음 | infobox `합체` 필드 → member, `구성원` 필드 → combined |
| 합체-멤버 그래프 | `COMBO_COMPONENTS` 수동 사전 | infobox `구성원` 자동 파싱 + 역참조로 양방향 자동 구축 |
| 시즌 정보 | 없음 | infobox `첫 등장` / `시즌 N ~ 시즌 M` 파싱 |
| 차종 정보 | 없음 | infobox `차량 모델` 파싱 |
| 저장 구조 | flat `_raw_metadata.json` | 계층형 JSON (§4 스키마) |

---

## 7. 검증된 변종 (Verified Variations)

나무위키에서 실제 확인을 마친 페이지:

### 카봇 스카이 (member + standalone)
- `basic` (시즌 1~16) — robot / vehicle (해치백, 현대 벨로스터 1세대, 주황)
- `swat` (시즌 1~) — robot / vehicle (해치백 SWAT 경찰차, 검정)
- `swat_x` (시즌 9~10, 14~15) — robot / vehicle (SWAT 기동차량, 검정)
- `swat_x_crystal` (시즌 13) — robot

### 카봇 팔로 (standalone, 극장판)
- `basic` (옴파로스 섬의 비밀) — robot / beast (하체 물소) / animal_full (완전 물소, 트리플 체인저)

### 카봇 로드세이버 (combined)
- `basic` (시즌 2~) — robot (인간형) / power (로어세이버 곰형)
- `allstar` (시즌 15~) — robot / power

### 카봇 펜타스톰 (combined, 시즌 1 최초 합체)
- `basic` (시즌 1~3, 16) — robot
- `gold` 황금특공대 (시즌 10~11) — robot
- `refine` 리파인 (시즌 16) — robot
- (X 시리즈는 별도 패밀리)

### 카봇 펜타스톰 X (combined, X 강화판)
- `basic` (시즌 9~10, 14~15) — robot
- `crystal` 크리스탈 (시즌 13) — robot
- `bigcube` 빅큐브 (시즌 14~) — robot (+ 빅큐브 무장 부스터/기어 모드)
- `lifecannon` 라이프 캐논 모드 (시즌 14~) — robot (6단 그레이트 합체)
