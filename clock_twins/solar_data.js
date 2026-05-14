// 태양계 시계 데이터 — 손수 작성 (build_data.mjs와 별개)
// 태양은 시계 중심에 위치하므로 basicSolar에는 들어가지 않고, 1~12시는 거리순 12천체.
var basicSolar = [
  { hour: 1,  name: '수성',     file: 'img_solar/SS-02_수성.webp',     kind: '내행성',   tier: '행성' },
  { hour: 2,  name: '금성',     file: 'img_solar/SS-03_금성.webp',     kind: '내행성',   tier: '행성' },
  { hour: 3,  name: '지구',     file: 'img_solar/SS-04_지구.webp',     kind: '내행성',   tier: '행성' },
  { hour: 4,  name: '달',       file: 'img_solar/SS-05_달.webp',       kind: '위성',     tier: '위성' },
  { hour: 5,  name: '화성',     file: 'img_solar/SS-06_화성.webp',     kind: '내행성',   tier: '행성' },
  { hour: 6,  name: '목성',     file: 'img_solar/SS-07_목성.webp',     kind: '외행성',   tier: '행성' },
  { hour: 7,  name: '토성',     file: 'img_solar/SS-08_토성.webp',     kind: '외행성',   tier: '행성' },
  { hour: 8,  name: '천왕성',   file: 'img_solar/SS-09_천왕성.webp',   kind: '외행성',   tier: '행성' },
  { hour: 9,  name: '해왕성',   file: 'img_solar/SS-10_해왕성.webp',   kind: '외행성',   tier: '행성' },
  { hour: 10, name: '명왕성',   file: 'img_solar/SS-11_명왕성.webp',   kind: '왜소행성', tier: '왜소행성' },
  { hour: 11, name: '핼리혜성', file: 'img_solar/SS-12_핼리혜성.webp', kind: '혜성',     tier: '혜성' },
  { hour: 12, name: '보이저1호', file: 'img_solar/SS-14_보이저1호.webp', kind: '탐사선',   tier: '탐사선' }
];

// 도감용 — 태양 포함 13개. 거리순 정렬(태양=0 AU 첫 번째).
// blurb는 7세(만 6세) 어린이 눈높이로 쉬운 말로 작성.
var allSolar = [
  { no: 1,  name: '태양',     file: 'img_solar/SS-01_태양.webp',     kind: '항성',     tier: '항성',
    distance_au: 0,      blurb: '태양계 한가운데에서 환하게 빛나는 별이에요. 아주아주 뜨거워서 우리를 따뜻하게 해 줘요.' },
  { no: 2,  name: '수성',     file: 'img_solar/SS-02_수성.webp',     kind: '내행성',   tier: '행성',
    distance_au: 0.39,   blurb: '태양과 가장 가까운 행성이에요. 행성 중에 제일 작고, 낮엔 엄청 뜨겁고 밤엔 엄청 추워요.' },
  { no: 3,  name: '금성',     file: 'img_solar/SS-03_금성.webp',     kind: '내행성',   tier: '행성',
    distance_au: 0.72,   blurb: '태양계에서 가장 뜨거운 행성이에요. 두꺼운 구름이 이불처럼 덮고 있어서 펄펄 끓어요.' },
  { no: 4,  name: '지구',     file: 'img_solar/SS-04_지구.webp',     kind: '내행성',   tier: '행성',
    distance_au: 1.00,   blurb: '우리가 사는 곳이에요. 물도 있고 공기도 있어서 사람도 동물도 식물도 살 수 있어요.' },
  { no: 5,  name: '달',       file: 'img_solar/SS-05_달.webp',       kind: '위성',     tier: '위성',
    distance_au: 1.00,   parent: '지구',
    blurb: '지구 옆을 빙글빙글 도는 친구예요. 밤하늘에서 반짝반짝 빛나요.' },
  { no: 6,  name: '화성',     file: 'img_solar/SS-06_화성.webp',     kind: '내행성',   tier: '행성',
    distance_au: 1.52,   blurb: '흙이 빨개서 "붉은 행성"이라고 불러요. 지구랑 조금 닮았어요.' },
  { no: 7,  name: '목성',     file: 'img_solar/SS-07_목성.webp',     kind: '외행성',   tier: '행성',
    distance_au: 5.20,   blurb: '태양계에서 가장 큰 행성이에요. 줄무늬 옷을 입었고, 커다란 빨간 점도 있어요.' },
  { no: 8,  name: '토성',     file: 'img_solar/SS-08_토성.webp',     kind: '외행성',   tier: '행성',
    distance_au: 9.54,   blurb: '예쁜 고리를 두르고 있어요. 고리는 작은 얼음과 돌멩이로 되어 있어요.' },
  { no: 9,  name: '천왕성',   file: 'img_solar/SS-09_천왕성.webp',   kind: '외행성',   tier: '행성',
    distance_au: 19.18,  blurb: '옆으로 누운 채로 데굴데굴 굴러가듯 도는 행성이에요. 예쁜 하늘색이에요.' },
  { no: 10, name: '해왕성',   file: 'img_solar/SS-10_해왕성.webp',   kind: '외행성',   tier: '행성',
    distance_au: 30.07,  blurb: '태양에서 가장 먼 행성이에요. 바람이 아주아주 세게 불어요.' },
  { no: 11, name: '핼리혜성', file: 'img_solar/SS-12_핼리혜성.webp', kind: '혜성',     tier: '혜성',
    distance_au: 17.8,   blurb: '76년에 한 번씩 우리를 보러 오는 혜성이에요. 긴 꼬리를 달고 날아다녀요.' },
  { no: 12, name: '명왕성',   file: 'img_solar/SS-11_명왕성.webp',   kind: '왜소행성', tier: '왜소행성',
    distance_au: 39.48,  blurb: '작고 차가운 얼음 행성이에요. 표면에 커다란 하트 모양이 있어요.' },
  { no: 13, name: '에리스',   file: 'img_solar/SS-13_에리스.webp',   kind: '왜소행성', tier: '왜소행성',
    distance_au: 67.78,  blurb: '명왕성보다 더 멀리 있는 작은 친구예요. 아주아주 추운 곳에 살아요.' },
  { no: 14, name: '보이저1호', file: 'img_solar/SS-14_보이저1호.webp', kind: '탐사선',   tier: '탐사선',
    distance_au: 167.0,  blurb: '사람이 만들어서 우주로 보낸 작은 탐험가예요. 지금도 가장 먼 우주를 여행하고 있어요.' }
];
