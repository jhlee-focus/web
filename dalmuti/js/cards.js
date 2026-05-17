// 달무티 카드 데이터 + 셔플.
// 카드 표현: 정수.
//   1~12  = 숫자 카드 (낮을수록 강함)
//   13    = 광대(Jester) 와일드카드
//
// 덱 구성: 1×1장, 2×2장, ..., 12×12장 = 78장. 광대 2장. 총 80장.

export const JESTER = 13;
export const RANK_NAMES = {
  1: "Greater Dalmuti",
  2: "Archbishop",
  3: "Mayor",
  4: "Knight",
  5: "Squire",
  6: "Mason",
  7: "Cook",
  8: "Shepherd",
  9: "Stonecutter",
  10: "Peasant",
  11: "Peon",
  12: "Serf",
  13: "Jester",
};

export function rankLabel(r) {
  if (r === JESTER) return "광대";
  return String(r);
}

export function buildDeck() {
  const cards = [];
  for (let r = 1; r <= 12; r++) {
    for (let i = 0; i < r; i++) cards.push(r);
  }
  cards.push(JESTER, JESTER);
  return cards;
}

// Fisher-Yates 셔플 (원본 미변경, 새 배열 반환)
export function shuffle(arr, rng = Math.random) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

// 80장을 N명에게 균등 분배. 나머지가 있으면 처음부터 한 장씩 더 받음.
export function dealHands(deck, playerCount) {
  const hands = Array.from({ length: playerCount }, () => []);
  for (let i = 0; i < deck.length; i++) {
    hands[i % playerCount].push(deck[i]);
  }
  return hands.map(sortHand);
}

// 손패는 항상 오름차순으로 정렬해 보관 (광대는 맨 뒤).
export function sortHand(hand) {
  return [...hand].sort((a, b) => a - b);
}
