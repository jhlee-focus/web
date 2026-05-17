// AI 봇의 의사결정 (순수 함수).
//
// chooseAction(state, playerId) → {type: 'play'|'pass', cards?: number[]}
//
// MVP 전략 (Normal 난이도):
// - 트릭 리드: 가장 큰 묶음 중 가장 약한(높은 숫자) 카드부터 송출. 광대는 최후 수단.
// - 추격: 트릭에 이길 수 있는 최저 비용(광대 적게, 약한 숫자) 묶음 선택. 못 이기면 패스.

import { JESTER } from "./cards.js";

function groupHand(hand) {
  const groups = {};
  for (const c of hand) {
    if (!groups[c]) groups[c] = [];
    groups[c].push(c);
  }
  return groups;
}

function jesterCount(groups) {
  return groups[JESTER]?.length ?? 0;
}

// 리드(첫 손) 선택.
function chooseLead(hand) {
  const groups = groupHand(hand);
  const numericRanks = Object.keys(groups)
    .map(Number)
    .filter((r) => r !== JESTER);

  if (numericRanks.length === 0) {
    // 전부 광대만 남은 경우
    const j = groups[JESTER] ?? [];
    return { type: "play", cards: [...j] };
  }

  // 후보: (숫자, 묶음 크기, 광대 결합 시 크기)
  const candidates = numericRanks.map((r) => ({
    rank: r,
    base: groups[r],
    sizeWithoutJester: groups[r].length,
    sizeWithJester: groups[r].length + jesterCount(groups),
  }));

  // 정렬: 묶음 크기(광대 미사용) 큰 순 → 같으면 숫자 큰(약한) 순
  candidates.sort((a, b) => {
    if (b.sizeWithoutJester !== a.sizeWithoutJester) {
      return b.sizeWithoutJester - a.sizeWithoutJester;
    }
    return b.rank - a.rank;
  });

  const pick = candidates[0];
  return { type: "play", cards: [...pick.base] };
}

// 추격(트릭에 이미 누가 냈음) 선택.
function chooseChase(hand, trick) {
  const groups = groupHand(hand);
  const needed = trick.leadCount;
  const maxRank = trick.leadRank - 1; // 이보다 같거나 낮은 숫자만 OK
  const jesters = groups[JESTER] ?? [];

  const candidates = [];

  // 숫자 카드만으로 needed 장 만들기
  for (const r of Object.keys(groups).map(Number)) {
    if (r === JESTER) continue;
    if (r > maxRank) continue;
    const base = groups[r];
    if (base.length >= needed) {
      candidates.push({
        rank: r,
        cards: base.slice(0, needed),
        jestersUsed: 0,
      });
    } else {
      const shortfall = needed - base.length;
      if (shortfall <= jesters.length) {
        candidates.push({
          rank: r,
          cards: [...base, ...jesters.slice(0, shortfall)],
          jestersUsed: shortfall,
        });
      }
    }
  }

  // 광대만으로 needed 장 (효과 랭크 1, leadRank > 1 이면 OK)
  if (jesters.length >= needed && trick.leadRank > 1) {
    candidates.push({
      rank: 1,
      cards: jesters.slice(0, needed),
      jestersUsed: needed,
    });
  }

  if (candidates.length === 0) {
    return { type: "pass" };
  }

  // 정렬: 광대 적게 → 숫자 큰(약한) 카드 사용
  candidates.sort((a, b) => {
    if (a.jestersUsed !== b.jestersUsed) return a.jestersUsed - b.jestersUsed;
    return b.rank - a.rank;
  });

  return { type: "play", cards: candidates[0].cards };
}

export function chooseAction(state, playerId) {
  const player = state.players.find((p) => p.id === playerId);
  if (!player) return { type: "pass" };
  const hand = player.hand;
  if (hand.length === 0) return { type: "pass" };

  const trick = state.currentTrick;
  if (trick.leadCount === null) {
    return chooseLead(hand);
  }
  return chooseChase(hand, trick);
}

// 세금 단계: dalmuti 가 peon 에게 줄 카드 자동 선택 (가장 약한 = 가장 높은 숫자 N장).
export function chooseDalmutiReturn(hand, count) {
  const sorted = [...hand].sort((a, b) => a - b);
  return sorted.slice(-count);
}
