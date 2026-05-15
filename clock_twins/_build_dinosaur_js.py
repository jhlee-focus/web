"""Helper: generate dinosaur_data.js + img_dinosaur/CREDITS.md from inline metadata."""
import json
from pathlib import Path

# (no, name_ko, en, gen, kind, tier, period, length_m, weight_t_or_null, abc, blurb)
DATA = [
    ("001","안킬로사우루스","Ankylosaurus",3,"공룡","초식","백악기 후기",8,6,"A",
     "온몸이 두꺼운 갑옷으로 덮였어요. 꼬리 끝에 망치 같은 큰 뼈가 달려 있었어요."),
    ("002","브라키오사우루스","Brachiosaurus",2,"공룡","초식","쥐라기 후기",22,35,"B",
     "목이 정말정말 길어서 4층 건물보다 키가 컸어요. 나무 꼭대기 잎을 먹었어요."),
    ("003","콤프소그나투스","Compsognathus",2,"공룡","육식","쥐라기 후기",1,0.003,"C",
     "닭만큼 작은 공룡이에요. 작은 도마뱀이나 곤충을 빠르게 잡아먹었어요."),
    ("004","데이노니쿠스","Deinonychus",3,"공룡","육식","백악기 전기",3,0.1,"D",
     "발에 큰 갈고리 발톱이 있어서 사냥할 때 휘둘렀어요. 똑똑하고 빨랐어요."),
    ("005","엘라스모사우루스","Elasmosaurus",3,"수장룡","육식","백악기 후기",14,2,"E",
     "목이 몸보다 더 긴 바다 공룡이에요. 긴 목으로 물고기를 쑥 잡았어요."),
    ("006","파브로사우루스","Fabrosaurus",2,"공룡","초식","쥐라기 전기",1,0.02,"F",
     "강아지만큼 작은 초식 공룡이에요. 그림은 같은 공룡일지도 모르는 친척 레소토사우루스에서 빌려왔어요."),
    ("007","갈리미무스","Gallimimus",3,"공룡","잡식","백악기 후기",6,0.4,"G",
     "타조처럼 길고 가는 다리로 빠르게 달렸어요. 이빨 없는 부리가 있었어요."),
    ("008","하드로사우루스","Hadrosaurus",3,"공룡","초식","백악기 후기",10,4,"H",
     "오리주둥이 같은 입을 가진 큰 공룡이에요. 나뭇잎을 한꺼번에 많이 먹었어요."),
    ("009","이구아노돈","Iguanodon",3,"공룡","초식","백악기 전기",10,3.5,"I",
     "엄지손가락에 뾰족한 가시가 있어서 적을 찔렀어요. 두 발이나 네 발 모두 걸었어요."),
    ("010","작사르토사우루스","Jaxartosaurus",3,"공룡","초식","백악기 후기",7,2,"J",
     "머리 위에 작은 볏이 있었어요. 그림은 람베오사우루스 사촌인 코리토사우루스를 빌려왔어요."),
    ("011","켄트로사우루스","Kentrosaurus",2,"공룡","초식","쥐라기 후기",5,1.5,"K",
     "등과 꼬리에 길고 뾰족한 가시가 줄지어 났어요. 가시로 적을 막았어요."),
    ("012","람베오사우루스","Lambeosaurus",3,"공룡","초식","백악기 후기",9,4,"L",
     "머리 위에 도끼 모양의 멋진 볏이 있어요. 볏으로 큰 나팔 소리를 냈어요."),
    ("013","메갈로사우루스","Megalosaurus",2,"공룡","육식","쥐라기 중기",9,1,"M",
     "세상에서 가장 먼저 발견된 공룡이에요. 큰 이빨과 발톱으로 다른 공룡을 잡았어요."),
    ("014","노도사우루스","Nodosaurus",3,"공룡","초식","백악기 후기",6,3,"N",
     "꼬리에 망치는 없지만 등이 골판으로 가득해요. 적이 와도 몸을 낮춰 버텼어요."),
    ("015","오비랍토르","Oviraptor",3,"공룡","잡식","백악기 후기",2,0.04,"O",
     "이름은 '알 도둑'이지만 사실 자기 알을 지킨 좋은 부모였어요."),
    ("016","프로토케라톱스","Protoceratops",3,"공룡","초식","백악기 후기",2,0.18,"P",
     "양만한 크기에 작은 뿔과 목 둘레의 작은 방패가 있어요. 트리케라톱스의 옛 친척."),
    ("017","케찰코아틀루스","Quetzalcoatlus",3,"익룡","육식","백악기 후기",10,0.25,"Q",
     "날개를 펴면 작은 비행기만큼 컸어요. 하늘을 나는 동물 중에서 가장 컸어요."),
    ("018","람포린쿠스","Rhamphorhynchus",2,"익룡","육식","쥐라기 후기",1.3,0.005,"R",
     "긴 꼬리 끝에 마름모 모양 깃발이 달린 작은 익룡이에요. 물고기를 잡아먹었어요."),
    ("019","스피노사우루스","Spinosaurus",3,"공룡","육식","백악기 후기",15,8,"S",
     "등에 큰 돛이 달렸어요. 티라노사우루스보다 더 길고, 물고기도 잘 잡았어요."),
    ("020","티라노사우루스","Tyrannosaurus",3,"공룡","육식","백악기 후기",12,7,"T",
     "이빨이 바나나만큼 컸어요. 스쿨버스보다 길고 정말정말 무서운 사냥꾼이었어요."),
    ("021","유타랍토르","Utahraptor",3,"공룡","육식","백악기 전기",7,0.5,"U",
     "벨로키랍토르의 형 같은 큰 사냥꾼이에요. 발톱이 사람 손만큼 컸어요."),
    ("022","벨로키랍토르","Velociraptor",3,"공룡","육식","백악기 후기",2,0.015,"V",
     "닭처럼 작지만 깃털이 있고 매우 빨랐어요. 똑똑하게 무리지어 사냥했어요."),
    ("023","완나노사우루스","Wannanosaurus",3,"공룡","초식","백악기 후기",0.6,0.005,"W",
     "고양이만큼 작은 공룡이에요. 그림은 큰 사촌 파키케팔로사우루스인데, 단단한 머리로 부딪치는 모습은 비슷해요."),
    ("024","제노타르소사우루스","Xenotarsosaurus",3,"공룡","육식","백악기 후기",6,1,"X",
     "남아메리카에서 살던 사냥꾼이에요. 그림은 가까운 친척 카르노타우루스에서 빌려왔어요. 머리 위 작은 뿔이 닮았어요."),
    ("025","양추아노사우루스","Yangchuanosaurus",2,"공룡","육식","쥐라기 후기",10,3,"Y",
     "중국에서 살던 큰 육식 공룡이에요. 알로사우루스랑 친척이고 비슷하게 생겼어요."),
    ("026","지공고사우루스","Zigongosaurus",2,"공룡","초식","쥐라기 후기",20,15,"Z",
     "중국 자공시에서 발견된 큰 용각류예요. 마멘치사우루스랑 사촌이에요."),
    ("027","에오랍토르","Eoraptor",1,"공룡","잡식","트라이아스기 후기",1,0.01,None,
     "맨 처음 등장한 공룡 중 하나예요. 강아지만큼 작고 잎과 작은 동물을 함께 먹었어요."),
    ("028","코엘로피시스","Coelophysis",1,"공룡","육식","트라이아스기 후기",3,0.03,None,
     "긴 꼬리와 가는 다리로 빠르게 달리던 작은 사냥꾼이에요."),
    ("029","플라테오사우루스","Plateosaurus",1,"공룡","초식","트라이아스기 후기",9,4,None,
     "초기에 등장한 큰 초식 공룡이에요. 보통은 네 발로 걷고 잎을 먹을 땐 두 발로 섰어요."),
    ("030","헤레라사우루스","Herrerasaurus",1,"공룡","육식","트라이아스기 후기",5,0.3,None,
     "아주 옛날 트라이아스기에 살던 사냥꾼 공룡이에요. 빠르게 달리며 작은 동물을 잡았어요."),
    ("031","트리케라톱스","Triceratops",3,"공룡","초식","백악기 후기",9,6,None,
     "얼굴에 큰 뿔이 세 개! 머리만 트럭만큼 컸어요. 풀과 잎을 먹고 살았어요."),
    ("032","스테고사우루스","Stegosaurus",2,"공룡","초식","쥐라기 후기",9,5,None,
     "등에 큰 골판이 두 줄로 줄지어 났어요. 꼬리 끝엔 뾰족한 가시 네 개가 있었어요."),
    ("033","디플로도쿠스","Diplodocus",2,"공룡","초식","쥐라기 후기",27,15,None,
     "코끝부터 꼬리 끝까지 버스 두 대만큼 길어요. 채찍 같은 꼬리를 휘둘렀어요."),
    ("034","파라사우롤로푸스","Parasaurolophus",3,"공룡","초식","백악기 후기",10,4,None,
     "머리 뒤에 긴 관 모양 볏이 있었어요. 그 볏으로 큰 나팔 소리를 냈을 거예요."),
    ("035","알로사우루스","Allosaurus",2,"공룡","육식","쥐라기 후기",9,2,None,
     "쥐라기의 무서운 사냥꾼이에요. 큰 이빨과 발톱으로 스테고사우루스 같은 큰 공룡도 잡았어요."),
    ("036","프테라노돈","Pteranodon",3,"익룡","육식","백악기 후기",7,0.025,None,
     "날개를 펴면 7미터! 머리 뒤에 길쭉한 볏이 있고, 바다 위를 날며 물고기를 잡았어요."),
    ("037","모사사우루스","Mosasaurus",3,"수장룡","육식","백악기 후기",17,14,None,
     "바다의 폭군이에요. 큰 도마뱀처럼 생겼고 이빨이 두 줄로 나 있었어요."),
    ("038","스티라코사우루스","Styracosaurus",3,"공룡","초식","백악기 후기",5,3,None,
     "코에 큰 뿔 하나, 머리 둘레에 뾰족한 뿔 여러 개가 있어요. 왕관을 쓴 공룡 같아요."),
    ("039","파키리노사우루스","Pachyrhinosaurus",3,"공룡","초식","백악기 후기",8,4,None,
     "뿔 대신 코 위에 두꺼운 둥근 뼈가 있어요. 그 뼈로 친구들과 머리를 부딪쳤어요."),
    ("040","에드몬토니아","Edmontonia",3,"공룡","초식","백악기 후기",7,4,None,
     "안킬로사우루스의 사촌이에요. 어깨에 긴 가시가 양쪽으로 뻗어 있었어요."),
    ("041","디모르포돈","Dimorphodon",2,"익룡","육식","쥐라기 전기",1,0.005,None,
     "머리가 크고 이가 두 가지 모양인 작은 익룡이에요. 강가에서 작은 동물을 잡았어요."),
    ("042","크로노사우루스","Kronosaurus",3,"수장룡","육식","백악기 전기",10,11,None,
     "큰 입과 짧은 목을 가진 바다 사냥꾼이에요. 이빨이 바나나만큼 컸어요."),
    ("043","리오플레우로돈","Liopleurodon",2,"수장룡","육식","쥐라기 후기",7,2,None,
     "쥐라기 바다의 강한 사냥꾼이에요. 큰 머리와 네 개의 노 같은 지느러미가 있었어요."),
    ("044","이크티오사우루스","Ichthyosaurus",2,"어룡","육식","쥐라기 전기",2,0.09,None,
     "돌고래처럼 생긴 바다 파충류예요. 큰 눈으로 물속에서도 잘 봤어요."),
]

basic_hours = {
    1:  "Tyrannosaurus", 2:  "Triceratops", 3:  "Brachiosaurus", 4:  "Stegosaurus",
    5:  "Velociraptor",  6:  "Ankylosaurus", 7:  "Spinosaurus",  8:  "Diplodocus",
    9:  "Parasaurolophus", 10: "Pteranodon", 11: "Mosasaurus",   12: "Allosaurus",
}
by_en = {row[2]: row for row in DATA}

basic_lines = []
for hour in range(1, 13):
    en = basic_hours[hour]
    no, ko, _, gen, kind, tier, period, length_m, weight_t, abc, blurb = by_en[en]
    f = f"img_dinosaur/DN-{no}_{ko}.webp"
    basic_lines.append(f'  {{ hour: {hour}, name: "{ko}", file: "{f}", tier: "{tier}" }}')
basic_js = ",\n".join(basic_lines)

all_lines = []
for row in DATA:
    no, ko, en, gen, kind, tier, period, length_m, weight_t, abc, blurb = row
    no_int = int(no)
    f = f"img_dinosaur/DN-{no}_{ko}.webp"
    abc_part = f'"{abc}"' if abc else "null"
    weight_part = str(weight_t) if weight_t is not None else "null"
    # Escape quotes in blurb
    safe_blurb = blurb.replace('"', '\\"')
    all_lines.append(
        f'  {{ no: {no_int}, name: "{ko}", file: "{f}",\n'
        f'    en: "{en}", abc: {abc_part},\n'
        f'    gen: {gen}, kind: "{kind}", tier: "{tier}",\n'
        f'    period: "{period}", length_m: {length_m}, weight_t: {weight_part},\n'
        f'    blurb: "{safe_blurb}" }}'
    )
all_js = ",\n".join(all_lines)

content = (
    "// auto-generated by _build_dinosaur_js.py — basic 12 + all 44\n"
    "// gen: 1=트라이아스기, 2=쥐라기, 3=백악기.  kind: 공룡/익룡/수장룡/어룡.  tier: 육식/초식/잡식.\n"
    "var basicDinosaur = [\n" + basic_js + "\n];\n\n"
    "var allDinosaur = [\n" + all_js + "\n];\n"
)
Path("dinosaur_data.js").write_text(content, encoding="utf-8")
print(f"dinosaur_data.js written: basic 12 + all {len(DATA)}")

credits = """# 공룡 시계 이미지·설명 출처

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
"""
Path("img_dinosaur/CREDITS.md").write_text(credits, encoding="utf-8")
print("CREDITS.md written")
