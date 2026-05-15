# 공룡 시계 이미지·설명 출처

이 디렉터리의 모든 이미지는 `build_dinosaur_data.py` + 수동 픽으로 받은 결과물입니다.
출처는 두 곳(dino.fandom + jurassicpark.fandom)이며 모두 CC BY-SA 3.0 라이선스로 사용합니다.

## 1. dino.fandom.com (대부분, ~40종)

`https://dino.fandom.com/wiki/{Species}` 페이지의 인포박스 메인 이미지.
라이선스: **CC BY-SA 3.0**. 페이지 본문 첫 문단은 7세 친화 한국어로 가공해
`dinosaur_data.js`의 `blurb` 필드에 사용했습니다.

## 2. jurassicpark.fandom.com (영화 리얼리스틱 렌더)

도감 인상을 더 실사형으로 보강하기 위해 영화 공식 투명 PNG 렌더 사용:

- **스피노사우루스 (`Spinosaurus`)** — `Spinosaurus_Rebirth_Render.webp`
- **벨로키랍토르 (`Velociraptor`)** — `Velociraptor_Rebirth.webp`
- **디메트로돈 (`Dimetrodon`)** — `JWD_Dimetrodon_render.png`
- **기가노토사우루스 (`Giganotosaurus`)** — `Giganotasaurus_Jurassic_World_Dominion.png`
- **마이아사우라·힙실로포돈·오르니토미무스·쿠아에시토사우루스·레바키사우루스·우에르호사우루스** — JPI 시리즈 일러스트

## 3. 대체 이미지 (5종 — 가까운 친척 종으로 비주얼 대체)

해당 종은 wiki 이미지가 두개골/박물관 전시/사이즈 차트같이 어린이용으로 부적절하거나,
2D 일러스트만 존재해 실사형 인상을 주지 못했습니다. 같은 과/가까운 친척의 일러스트로
대체했고 blurb에 친척 관계를 명시했습니다.

- **파브로사우루스 (`Fabrosaurus`)** — 동의어로 추정되는 **레소토사우루스(Lesothosaurus)**
  실사형 CGI 렌더 (dino.fandom.com). Fabrosaurus는 *nomen dubium*이며 같은 동물일 가능성이 큽니다.
- **지공고사우루스 (`Zigongosaurus`)** — 같은 마멘치사우루스과(Mamenchisauridae)의
  **마멘치사우루스(Mamenchisaurus)** 이미지 (dino.fandom.com).
- **작사르토사우루스 (`Jaxartosaurus`)** — 같은 람베오사우루스과(Lambeosaurinae)의
  **코리토사우루스(Corythosaurus)** 이미지 (dino.fandom.com).
- **완나노사우루스 (`Wannanosaurus`)** — 같은 파키케팔로사우루스과(Pachycephalosauridae)의
  **파키케팔로사우루스(Pachycephalosaurus)** 이미지 (dino.fandom.com).
- **제노타르소사우루스 (`Xenotarsosaurus`)** — 같은 아벨리사우루스과(Abelisauridae)의
  **카르노타우루스(Carnotaurus)** 실사형 CGI 렌더 (dino.fandom.com / Jurassic World).

## 알파벳송 매핑 (26종)

주니토니 [알파벳 공룡](https://www.youtube.com/watch?v=wA5penhto5s) 가사 순서:

A 알로사우루스 · B 브라키오사우루스 · C 콤프소그나투스 · D 디메트로돈 · E 에드몬토니아 ·
F 파브로사우루스 · G 기가노토사우루스 · H 힙실로포돈 · I 이구아노돈 · J 작사르토사우루스 ·
K 켄트로사우루스 · L 람베오사우루스 · M 마이아사우라 · N 니게르사우루스 · O 오르니토미무스 ·
P 파라사우롤로푸스 · Q 쿠아에시토사우루스 · R 레바키사우루스 · S 스피노사우루스 · T 티라노사우루스 ·
U 우다노케라톱스 · V 벨로키랍토르 · W 우에르호사우루스 · X 제노케라톱스 · Y 양추아노사우루스 · Z 주니케라톱스

## 재생성 방법

```sh
cd clock_twins/
python build_dinosaur_data.py        # 기존 fandom 크롤링 (대부분의 종)
python _apply_picks.py               # PR #78 수동 4종
python _apply_abc_song_picks.py      # PR #81 신규 12종
python _build_dinosaur_js.py         # dinosaur_data.js + CREDITS.md 재생성
```

원본 PNG/JPG는 `img_dinosaur_src/`에 캐시되며 (gitignored), 변환 결과만
`img_dinosaur/`에 커밋됩니다.
