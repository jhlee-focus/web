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
var allSolar = [
  { no: 1,  name: '태양',     file: 'img_solar/SS-01_태양.webp',     kind: '항성',     tier: '항성',
    distance_au: 0,      blurb: '태양계 중심의 항성. 모든 천체가 태양을 중심으로 공전한다.' },
  { no: 2,  name: '수성',     file: 'img_solar/SS-02_수성.webp',     kind: '내행성',   tier: '행성',
    distance_au: 0.39,   blurb: '태양에서 가장 가까운 행성. 가장 작고 밤낮의 온도 차가 극단적이다.' },
  { no: 3,  name: '금성',     file: 'img_solar/SS-03_금성.webp',     kind: '내행성',   tier: '행성',
    distance_au: 0.72,   blurb: '가장 뜨거운 행성. 두꺼운 이산화탄소 대기로 표면이 460°C를 넘는다.' },
  { no: 4,  name: '지구',     file: 'img_solar/SS-04_지구.webp',     kind: '내행성',   tier: '행성',
    distance_au: 1.00,   blurb: '우리가 사는 행성. 태양계에서 표면에 액체 물이 풍부한 유일한 곳.' },
  { no: 5,  name: '달',       file: 'img_solar/SS-05_달.webp',       kind: '위성',     tier: '위성',
    distance_au: 1.00,   parent: '지구',
    blurb: '지구의 유일한 자연 위성. 지름이 지구의 약 1/4로 비교적 큰 위성.' },
  { no: 6,  name: '화성',     file: 'img_solar/SS-06_화성.webp',     kind: '내행성',   tier: '행성',
    distance_au: 1.52,   blurb: '붉은 행성. 표면의 산화철 때문에 붉게 보인다.' },
  { no: 7,  name: '목성',     file: 'img_solar/SS-07_목성.webp',     kind: '외행성',   tier: '행성',
    distance_au: 5.20,   blurb: '가장 큰 행성. 거대한 줄무늬와 수백 년째 부는 폭풍 대적반이 있다.' },
  { no: 8,  name: '토성',     file: 'img_solar/SS-08_토성.webp',     kind: '외행성',   tier: '행성',
    distance_au: 9.54,   blurb: '멋진 고리를 가진 가스행성. 고리는 주로 얼음과 암석 조각이다.' },
  { no: 9,  name: '천왕성',   file: 'img_solar/SS-09_천왕성.webp',   kind: '외행성',   tier: '행성',
    distance_au: 19.18,  blurb: '옆으로 누워 자전하는 얼음 거인. 대기의 메탄 때문에 청록색이다.' },
  { no: 10, name: '해왕성',   file: 'img_solar/SS-10_해왕성.webp',   kind: '외행성',   tier: '행성',
    distance_au: 30.07,  blurb: '가장 먼 행성. 강한 바람과 대흑점 폭풍이 있다.' },
  { no: 11, name: '핼리혜성', file: 'img_solar/SS-12_핼리혜성.webp', kind: '혜성',     tier: '혜성',
    distance_au: 17.8,   blurb: '약 76년 주기로 돌아오는 단주기 혜성. 마지막 방문은 1986년.' },
  { no: 12, name: '명왕성',   file: 'img_solar/SS-11_명왕성.webp',   kind: '왜소행성', tier: '왜소행성',
    distance_au: 39.48,  blurb: '카이퍼대의 왜소행성. 표면에 거대한 하트 모양 평원이 있다.' },
  { no: 13, name: '에리스',   file: 'img_solar/SS-13_에리스.webp',   kind: '왜소행성', tier: '왜소행성',
    distance_au: 67.78,  blurb: '명왕성보다 더 먼 왜소행성. 발견이 명왕성을 행성에서 왜소행성으로 강등시킨 계기.' },
  { no: 14, name: '보이저1호', file: 'img_solar/SS-14_보이저1호.webp', kind: '탐사선',   tier: '탐사선',
    distance_au: 167.0,  blurb: '1977년 발사된 NASA의 성간 탐사선. 인류가 만든 가장 먼 곳까지 도달한 물체로, 2012년 태양계 경계인 헬리오포즈를 통과했다.' }
];
