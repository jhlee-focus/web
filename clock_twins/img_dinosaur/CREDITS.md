# 공룡 시계 이미지·설명 출처

이 디렉터리의 모든 이미지는 `build_dinosaur_data.py` + 수동 픽으로 받은 결과물입니다.
출처는 두 곳(dino.fandom + jurassicpark.fandom)이며 모두 CC BY-SA 3.0 라이선스로 사용합니다.

## 1. dino.fandom.com (대부분, ~37종)

`https://dino.fandom.com/wiki/{Species}` 페이지의 인포박스 메인 이미지.
라이선스: **CC BY-SA 3.0**. 페이지 본문 첫 문단은 7세 친화 한국어로 가공해
`dinosaur_data.js`의 `blurb` 필드에 사용했습니다.

## 2. jurassicpark.fandom.com (2종 — 영화 리얼리스틱 렌더)

도감 인상을 더 실사형으로 보강하기 위해 Jurassic World Rebirth 영화 공식 투명 PNG 렌더로 교체:

- **스피노사우루스 (`Spinosaurus`)** — `Spinosaurus_Rebirth_Render.webp` (jurassicpark.fandom.com).
  주황 줄무늬 돛 + 입을 벌린 포즈의 실사형 CGI 렌더.
- **벨로키랍토르 (`Velociraptor`)** — `Velociraptor_Rebirth.webp` (jurassicpark.fandom.com).
  깃털 없는 영화판 무지개 눈 디자인의 실사형 CGI 렌더.

## 3. 대체 이미지 (5종 — 가까운 친척 종으로 비주얼 대체)

해당 종은 wiki 이미지가 두개골/박물관 전시/사이즈 차트같이 어린이용으로 부적절하거나,
2D 일러스트만 존재해 실사형 인상을 주지 못했습니다. 같은 과/가까운 친척의 일러스트로
대체했고 blurb에 친척 관계를 명시했습니다.

- **파브로사우루스 (`Fabrosaurus`)** — 동의어로 추정되는 **레소토사우루스(Lesothosaurus)**
  실사형 CGI 렌더 (dino.fandom.com). Fabrosaurus는 *nomen dubium*이며 같은 동물일 가능성이 큽니다.
- **지공고사우루스 (`Zigongosaurus`)** — 같은 마멘치사우루스과(Mamenchisauridae)의
  **마멘치사우루스(Mamenchisaurus)** 이미지 (dino.fandom.com). 두 종은 같은 과의 중국 출신
  대형 용각류로 외형이 비슷합니다.
- **작사르토사우루스 (`Jaxartosaurus`)** — 같은 람베오사우루스과(Lambeosaurinae)의
  **코리토사우루스(Corythosaurus)** 이미지 (dino.fandom.com). 둘 다 머리에 볏을 가진
  하드로사우르과 친척입니다.
- **완나노사우루스 (`Wannanosaurus`)** — 같은 파키케팔로사우루스과(Pachycephalosauridae)의
  **파키케팔로사우루스(Pachycephalosaurus)** 이미지 (dino.fandom.com). 둘 다 두꺼운 머리로
  부딪치며 살았던 친척입니다.
- **제노타르소사우루스 (`Xenotarsosaurus`)** — 같은 아벨리사우루스과(Abelisauridae)의
  **카르노타우루스(Carnotaurus)** 실사형 CGI 렌더 (dino.fandom.com / Jurassic World).
  둘 다 짧은 앞다리와 작은 머리 뿔을 가진 남미 수각류입니다.

## 재생성 방법

```sh
cd clock_twins/
python build_dinosaur_data.py
# 그 후 4종(006/019/022/024)은 수동 픽 → _apply_picks.py 로 덮어쓰기
```

원본 PNG/JPG는 `img_dinosaur_src/`에 캐시되며 (gitignored), 변환 결과만
`img_dinosaur/`에 커밋됩니다.

## 종 목록 (44종)

핑크퐁 [공룡 ABC](https://www.youtube.com/watch?v=Eoxa_YxOpuo) A-Z 26종 + 보완 18종.
세부는 `dinosaur_data.js` 참조.
