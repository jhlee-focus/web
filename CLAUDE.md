# CLAUDE.md — jhlee-focus/web

이 레포는 사용자가 직접 만든 웹 프로젝트들을 모은 정적 사이트(GitHub Pages, 커스텀 도메인 `CNAME`)로,
대부분의 프로젝트는 **iOS 홈 화면 바로가기로 추가되어 어린이(주로 6–7세)가 사용하는 환경**입니다.
이 컨텍스트가 모든 작업의 전제입니다.

## 🔒 필수 규칙: iOS 홈 화면 풀스크린 메타태그

새로운 `index.html`을 추가하거나 기존 페이지의 `<head>`를 손볼 때 **반드시**
아래 메타태그가 `<head>` 안에 포함되어야 합니다 (`<meta name="viewport" ...>` 바로 다음 줄 권장):

```html
<meta name="apple-mobile-web-app-capable" content="yes">
```

### 왜 필요한가
이 태그가 있어야 iOS Safari → "홈 화면에 추가"로 만든 바로가기가
**standalone(주소창·탭바 없는 풀스크린)** 으로 열립니다.
없으면 Safari 탭 안에서 열려 다른 탭들·주소창이 보이는 UX가 됩니다.

### 파일별 스타일 일관성
들여쓰기와 셀프클로징(`>` vs ` />`)은 **그 파일의 기존 viewport 라인 스타일을 그대로** 따라가세요.
예:
- `avengers_game` / `draft-compare` → 2-space 들여쓰기 + ` />`
- `clock_twins` / `hand_tracking6` → 0 들여쓰기 + (파일별로 다름)
- `git/` → 4-space 들여쓰기 + `>`
- 루트 `index.html` → 2-space 들여쓰기 + `>`

### 의도적으로 제외하는 페이지 (메타태그 추가 금지)
- `chat/index.html`
- `pgr21_manwoo_2026/index.html`

이 외 모든 `*/index.html`(루트 포함)은 위 태그를 가져야 합니다.

### 이미 적용된 페이지 (참고)
- 루트 `index.html`, `avengers_game/`, `clock_twins/`, `draft-compare/`, `git/`,
  `hand_tracking6/`, `teenieping/`, `teenieping_dessert/`

### iOS 캐싱 주의 (사용자 안내 필수)
사용자가 **이미 홈에 추가한 바로가기는 메타태그가 새로 들어가도 자동으로 풀스크린이 안 바뀝니다.**
신규 페이지를 배포한 뒤 사용자에게 반드시 다음을 안내하세요:
1. 기존 바로가기 삭제
2. Safari로 URL 재방문
3. 공유 → "홈 화면에 추가" 다시 실행

### Out of scope (이 규칙에 포함 안 됨)
- 안드로이드 PWA (`manifest.json` + `display: standalone` + 아이콘 PNG) — 필요해지면 별도 작업
- 다른 풍부한 메타태그(`apple-mobile-web-app-status-bar-style`, `apple-touch-icon`, `apple-mobile-web-app-title` 등) — 필요해지면 별도 작업

## 👶 콘텐츠 톤 가이드 (어린이 사용자)

이 레포의 프로젝트는 주로 6–7세 어린이가 직접 사용합니다.
콘텐츠(텍스트·설명·라벨·에러 메시지 등)를 작성할 때:

- 짧은 문장, 쉬운 동사·명사 (한자어 줄이기)
- 어두운 개념 피하기: 살해/암살/세뇌/복수/스파이/혈청 같은 단어 ❌
- 시각적 단서 강조: "초록색 피부", "동그란 방패", "은빛 쇠팔" 등 화면에서 바로 알아볼 단서
- 친근한 호칭: 누나/형아/아저씨/친구
- 의성어·의태어 적극 사용: 슝슝, 쾅쾅, 휙
- 밝고 긍정적인 결말

성인 위키 스타일(MCU 정식 명칭·복잡한 설정) ❌ → 또래 그림책 톤 ✅

## 🛠 작업 시 일반 원칙

- 한 파일을 고칠 때 그 파일의 기존 들여쓰기·따옴표·셀프클로징 스타일을 그대로 보존
- HTML/CSS/JS 모두 vanilla 위주, 빌드 도구 없음 — 새 파일도 가급적 의존성 없는 단일 HTML로
- 이미지는 각 프로젝트의 `images/` 또는 폴더 내 어셋 폴더에 둠
- 변경 후엔 작은 PR 단위로 분리 (예: "메타태그 일괄 추가"와 "어벤져스 도감 텍스트 다듬기"는 별도 커밋)

## 🗂 폴더 구조 요약

| 폴더 | 설명 |
|---|---|
| `avengers_game/` | 마블 어벤져스 미니게임 모음 (drag-puzzle, hero-run, memory-game, puzzle-game) |
| `teenieping/`, `teenieping_dessert/` | 티니핑 테마 페이지 (이미 풀스크린 정상) |
| `clock_twins/` | 시계 골라봐 |
| `hand_tracking6/` | Cat's Cradle 네온 핸드 트래킹 |
| `draft-compare/` | MD 초안 비교 도구 |
| `git/` | SweetK 멀티LLM 인터페이스 |
| `chat/`, `pgr21_manwoo_2026/` | 풀스크린 메타태그 제외 페이지 |
| `backup/` | 이전 버전 백업 — 일반적으로 수정 대상 아님 |
