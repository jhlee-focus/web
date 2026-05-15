# 공룡 시계 이미지·설명 출처

이 디렉터리의 모든 이미지는 `build_dinosaur_data.py`로 받은 결과물입니다.
출처는 두 곳이며 모두 CC BY-SA 3.0 라이선스로 사용합니다.

## 1. dino.fandom.com (대부분, ~41종)

`https://dino.fandom.com/wiki/{Species}` 페이지의 인포박스 메인 이미지.
라이선스: **CC BY-SA 3.0**. 페이지 본문 첫 문단은 7세 친화 한국어로 가공해
`dinosaur_data.js`의 `blurb` 필드에 사용했습니다.

## 2. 대체 이미지 (3종 — 가까운 친척 종으로 비주얼 대체)

해당 종은 dino.fandom.com에 페이지가 없거나 Wikipedia의 이미지가 두개골/박물관 전시 같이
어린이용으로 부적절해, 같은 과/가까운 친척의 일러스트로 대체했습니다. blurb에 사촌임을 명시.

- **지공고사우루스 (`Zigongosaurus`)** — 같은 마멘치사우루스과(Mamenchisauridae)의
  **마멘치사우루스(Mamenchisaurus)** 이미지 (dino.fandom.com). 두 종은 같은 과의 중국 출신
  대형 용각류로 외형이 비슷합니다.
- **작사르토사우루스 (`Jaxartosaurus`)** — 같은 람베오사우루스과(Lambeosaurinae)의
  **코리토사우루스(Corythosaurus)** 이미지 (dino.fandom.com). 둘 다 머리에 볏을 가진
  하드로사우르과 친척입니다.
- **완나노사우루스 (`Wannanosaurus`)** — 같은 파키케팔로사우루스과(Pachycephalosauridae)의
  **파키케팔로사우루스(Pachycephalosaurus)** 이미지 (dino.fandom.com). 둘 다 두꺼운 머리로
  부딪치며 살았던 친척입니다.

## 재생성 방법

```sh
cd clock_twins/
python build_dinosaur_data.py
```

원본 PNG/JPG는 `img_dinosaur_src/`에 캐시되며 (gitignored), 변환 결과만
`img_dinosaur/`에 커밋됩니다.

## 종 목록 (44종)

핑크퐁 [공룡 ABC](https://www.youtube.com/watch?v=Eoxa_YxOpuo) A-Z 26종 + 보완 18종.
세부는 `dinosaur_data.js` 참조.
