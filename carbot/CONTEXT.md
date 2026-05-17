# carbot 이미지 수집 — 컨텍스트 문서

> 새 세션에서 이 폴더를 이어받을 때 가장 먼저 읽을 문서.  
> 마지막 업데이트: 2026-05-18

---

## 폴더 구조

```
carbot/
├── build_carbot_images.py          ← 메인 크롤러 스크립트
├── hello_carbot_robots.md          ← 카봇 로봇 전체 목록 (합체 카봇 표 포함)
├── 카봇(헬로카봇) - 나무위키.html  ← 로컬 캐시 HTML (이미지 1차 탐색용)
├── carbot_namu_wiki_files/         ← 캐시 HTML 연결 로컬 이미지 파일들
├── img_carbot/                     ← 최종 512×512 WebP (앱에서 실제 사용)
├── img_carbot_src/                 ← 원본 다운로드 보관 (재변환 대비)
│   └── _raw_metadata.json          ← 수집 메타데이터 (URL, 소스, 날짜)
└── CONTEXT.md                      ← 이 파일
```

---

## 수집 현황 (2026-05-18 기준)

| 분류 | 종수 | 비고 |
|------|------|------|
| 합체 카봇 | 36 | 3종 실패 (나무위키 페이지 없음) |
| 크로스 콤비네이션 합체형 | 4 | 마하피스·브레이피스·마하로드·브레이로드 (수동 추가) |
| 크로스 콤비네이션 구성원 | 4 | 마하·피스·브레이브·로드 (수동 추가) |
| 구성원 로봇 (자동 수집) | 60 | --components 플래그로 수집 |
| 뱅 시리즈 구성원 (폴백) | 14 | 개별 페이지 없음 → 합체 페이지 og:image 사용 |
| **합계** | **118** | img_carbot/ 기준 |

### 합체 카봇 수집 실패 3종
나무위키에 개별 페이지가 없어 확인 필요:
- 카봇 하이퍼빌디언
- (나머지 2종은 _raw_metadata.json 및 실행 로그 확인)

---

## 스크립트 사용법

```bash
# carbot/ 디렉터리에서 실행

# 합체 카봇 이미지 수집
python build_carbot_images.py

# 구성원 로봇 이미지 수집 (img_carbot/에 없는 것만)
python build_carbot_images.py --components

# 강제 재다운로드 (캐시 무시)
python build_carbot_images.py --force
python build_carbot_images.py --components --force
```

### 의존성
```
pip install playwright requests beautifulsoup4 Pillow
python -m playwright install chromium
```

---

## 핵심 기술 사항

### 나무위키 SPA 문제
나무위키는 React SPA라 `requests`로 HTML을 받으면 3KB짜리 JS 셸만 옴.
og:image가 없으므로 **Playwright 헤드리스 브라우저**로 JS 렌더링 후 추출.

```python
pw_page.goto(url, wait_until="domcontentloaded")
pw_page.wait_for_function("() => !!document.querySelector('meta[property=\"og:image\"]')?.content")
img_url = pw_page.evaluate("document.querySelector('meta[property=\"og:image\"]')?.getAttribute('content')")
```

### 이미지 탐색 우선순위
1. **로컬 캐시 HTML** (`카봇(헬로카봇) - 나무위키.html`) — `data-src` + alt 매칭
2. **개별 나무위키 페이지** — Playwright → og:image
3. **FALLBACK_PAGE_MAP** (개별 페이지 없는 구성원) — 합체 로봇 페이지 → alt 텍스트 매칭 → og:image

### FALLBACK_PAGE_MAP (뱅 시리즈)
시즌 10 뱅 시리즈 구성원은 나무위키에 개별 페이지가 없음.
합체 로봇 페이지에서 이미지를 가져오므로, **같은 합체를 공유하는 구성원들은 동일한 이미지**를 갖고 있음.
예: 잭슈트·타우·퓨처버스 모두 잭슈트뱅 og:image

### 이미지 변환
- 원본 → RGBA 투명 패딩으로 정사각형 → 512×512 리사이즈 (LANCZOS)
- WebP quality=88, method=6

---

## 데이터 구조

### COMBO_COMPONENTS
합체 카봇 → 구성원 이름 매핑. `--components` 실행 시 이 딕셔너리에서 대상 로봇 목록 생성.
구성원 이름은 짧은 이름으로 저장되며, "카봇 " 접두어는 자동 추가됨.
(`"카봇 " / "그랜드 카봇 "` 으로 시작하는 이름은 그대로 사용)

### _raw_metadata.json
```json
{
  "카봇 펜타스톰": {
    "url": "https://i.namu.wiki/i/...",
    "source": "fetch",          // "cache" | "local" | "fetch"
    "safe_name": "카봇 펜타스톰",
    "fetched_at": "2026-05-18T..."
  }
}
```

---

## 알려진 이슈 / 향후 과제

- **합체 카봇 실패 3종**: 나무위키 페이지 URL이 다르거나 리다이렉트 이슈. 수동 확인 필요.
- **뱅 시리즈 구성원 이미지**: 합체형 og:image 사용 중. 각 구성원의 개별 이미지가 필요하다면 합체 로봇 페이지 본문에서 alt 텍스트 매칭으로 추출하는 로직 개선 필요.
- **전체 카봇 수집**: `--all` 플래그 미구현. `hello_carbot_robots.md`의 전체 카봇 목록을 파싱해 확장 예정.
- **이미지 중복**: 같은 합체 페이지를 공유하는 구성원들(예: 레디·큐어·가드·헬프 모두 마이티가드 이미지)은 동일 이미지. 용도에 따라 허용 여부 판단 필요.
