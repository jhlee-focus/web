// 달무티 핵심 게임 로직 (UI / 통신 의존성 0).
// 모든 함수는 순수 함수: 입력 상태를 변형하지 않고 새 상태를 반환합니다.

import { JESTER, buildDeck, shuffle, dealHands, sortHand } from "./cards.js";

// ============================================================
// 카드 그룹/효과치
// ============================================================

// 카드 묶음의 "효과 랭크": 광대는 같이 낸 숫자 카드의 랭크를 따름.
// 모두 광대인 경우 1로 취급(가장 강함).
export function effectiveRank(cards) {
  const non = cards.filter((c) => c !== JESTER);
  if (non.length === 0) return 1;
  return non[0];
}

// 같은 묶음으로 인정되는가? (광대는 어떤 숫자와도 OK, 단 숫자끼리는 모두 같아야 함)
export function isUniformPlay(cards) {
  if (cards.length === 0) return false;
  const non = cards.filter((c) => c !== JESTER);
  if (non.length === 0) return true;
  return non.every((c) => c === non[0]);
}

// 손에 cards 가 모두 들어 있는가?
export function handHasAll(hand, cards) {
  const remaining = [...hand];
  for (const c of cards) {
    const idx = remaining.indexOf(c);
    if (idx === -1) return false;
    remaining.splice(idx, 1);
  }
  return true;
}

// 손패에서 cards 를 빼서 새 손패를 반환.
export function removeFromHand(hand, cards) {
  const remaining = [...hand];
  for (const c of cards) {
    const idx = remaining.indexOf(c);
    if (idx === -1) throw new Error("removeFromHand: card not in hand");
    remaining.splice(idx, 1);
  }
  return remaining;
}

// ============================================================
// 검증
// ============================================================

export function validatePlay(state, playerId, cards) {
  if (state.phase !== "play") return { ok: false, reason: "wrong_phase" };
  if (state.currentTurn !== playerId) return { ok: false, reason: "not_your_turn" };
  if (!Array.isArray(cards) || cards.length === 0) return { ok: false, reason: "empty_play" };

  const player = state.players.find((p) => p.id === playerId);
  if (!player) return { ok: false, reason: "no_such_player" };
  if (!handHasAll(player.hand, cards)) return { ok: false, reason: "card_not_in_hand" };
  if (!isUniformPlay(cards)) return { ok: false, reason: "mixed_ranks" };

  const trick = state.currentTrick;
  if (trick.leadCount !== null) {
    if (cards.length !== trick.leadCount) return { ok: false, reason: "count_mismatch" };
    const eff = effectiveRank(cards);
    if (eff >= trick.leadRank) return { ok: false, reason: "rank_not_lower" };
  }

  return { ok: true, effectiveRank: effectiveRank(cards) };
}

// ============================================================
// 액션 적용
// ============================================================

// 다음 차례를 좌석 순서대로 한 칸 진행. (이미 손패가 0이거나 트릭에서 패스한 사람은 건너뜀)
function nextActiveTurn(state, fromId) {
  const order = state.seatOrder;
  const startIdx = order.indexOf(fromId);
  for (let step = 1; step <= order.length; step++) {
    const idx = (startIdx + step) % order.length;
    const candidate = order[idx];
    if (state.finishedOrder.includes(candidate)) continue;
    if (state.currentTrick.passedThisTrick.includes(candidate)) continue;
    return candidate;
  }
  return null;
}

// 트릭 종료 후 다음 트릭의 리더 결정:
//   - 우승자(winnerId)가 아직 활성이면 그 사람
//   - 아니면 좌석 순서에서 winnerId 다음의 활성(=finished 아님) 플레이어
function leaderAfterTrickEnd(state, winnerId) {
  if (winnerId && !state.finishedOrder.includes(winnerId)) {
    return winnerId;
  }
  const order = state.seatOrder;
  const fromId = winnerId ?? state.currentTurn ?? order[0];
  const idx = Math.max(0, order.indexOf(fromId));
  for (let step = 1; step <= order.length; step++) {
    const candidate = order[(idx + step) % order.length];
    if (!state.finishedOrder.includes(candidate)) return candidate;
  }
  return null;
}

function freshTrick() {
  return {
    leadCount: null,
    leadRank: null,
    lastPlayerId: null,
    lastPlay: null,
    passedThisTrick: [],
  };
}

export function applyPlay(state, playerId, cards) {
  const next = cloneState(state);
  const player = next.players.find((p) => p.id === playerId);
  player.hand = removeFromHand(player.hand, cards);
  player.cardCount = player.hand.length;

  const eff = effectiveRank(cards);
  next.currentTrick.leadCount = cards.length;
  next.currentTrick.leadRank = eff;
  next.currentTrick.lastPlayerId = playerId;
  next.currentTrick.lastPlay = [...cards];
  next.lastEvent = { type: "play", playerId, cards: [...cards], effectiveRank: eff };

  // 손패 0이면 finishedOrder에 추가
  if (player.hand.length === 0 && !next.finishedOrder.includes(playerId)) {
    next.finishedOrder.push(playerId);
  }

  // 모든 사람이 손패를 비웠으면 라운드 종료
  if (next.finishedOrder.length >= next.players.length - 1) {
    // 마지막 한 명도 자동 finishedOrder 추가
    for (const p of next.players) {
      if (!next.finishedOrder.includes(p.id)) {
        next.finishedOrder.push(p.id);
      }
    }
    next.phase = "roundEnd";
    next.currentTurn = null;
    return next;
  }

  // 다음 차례 결정
  const candidate = nextActiveTurn(next, playerId);
  if (candidate === null) {
    // 다른 모두 패스/finished. 방금 낸 사람이 트릭 우승.
    next.currentTrick = freshTrick();
    next.currentTurn = leaderAfterTrickEnd(next, playerId);
  } else if (candidate === playerId) {
    // 자기 자신뿐. 본인이 다음 트릭 리드.
    next.currentTrick = freshTrick();
    next.currentTurn = playerId;
  } else {
    next.currentTurn = candidate;
  }
  return next;
}

export function applyPass(state, playerId) {
  if (state.currentTrick.leadCount === null) {
    // 리드 자리에서는 패스 불가 (반드시 카드 내야 함)
    return { ok: false, reason: "lead_must_play" };
  }
  const next = cloneState(state);
  next.currentTrick.passedThisTrick.push(playerId);
  next.lastEvent = { type: "pass", playerId };

  // 트릭 종료 검사: 아직 패스하지 않은 활성 플레이어가 1명 이하면 종료
  const stillIn = next.seatOrder.filter(
    (id) =>
      !next.finishedOrder.includes(id) &&
      !next.currentTrick.passedThisTrick.includes(id),
  );
  if (stillIn.length <= 1) {
    const winner = next.currentTrick.lastPlayerId;
    next.currentTrick = freshTrick();
    next.currentTurn = leaderAfterTrickEnd(next, winner);
  } else {
    next.currentTurn = nextActiveTurn(next, playerId);
  }
  return { ok: true, state: next };
}

// ============================================================
// 라운드/계급
// ============================================================

// 끝난 순서(1등→꼴등)에서 새 계급 계산. 4명 기준:
//   1등 = Greater Dalmuti, 2등 = Lesser Dalmuti, 3등 = Lesser Peon, 4등 = Greater Peon
// 5명 이상이면 중간은 Merchant(세금 없음).
export function computeRanks(finishedOrder) {
  const n = finishedOrder.length;
  const result = {};
  finishedOrder.forEach((pid, idx) => {
    if (idx === 0) result[pid] = "greaterDalmuti";
    else if (idx === 1) result[pid] = "lesserDalmuti";
    else if (idx === n - 1) result[pid] = "greaterPeon";
    else if (idx === n - 2) result[pid] = "lesserPeon";
    else result[pid] = "merchant";
  });
  return result;
}

export const RANK_TITLE = {
  greaterDalmuti: "Greater Dalmuti",
  lesserDalmuti: "Lesser Dalmuti",
  merchant: "Merchant",
  lesserPeon: "Lesser Peon",
  greaterPeon: "Greater Peon",
};

// 자리 순서: 첫 라운드는 입장 순. 이후 라운드는 finishedOrder(=새 계급 순)을 그대로 사용.
export function nextSeatOrder(prevFinishedOrder) {
  return [...prevFinishedOrder];
}

// ============================================================
// 세금/조공
// ============================================================
// peon 이 dalmuti 에게 보내는 카드: 손패에서 가장 낮은(=가장 강한) N장.
export function peonTribute(hand, count) {
  const sorted = sortHand(hand);
  return sorted.slice(0, count);
}

// dalmuti 가 peon 에게 보내는 카드: AI/자동 선택은 가장 높은(=가장 약한) N장.
export function dalmutiAutoReturn(hand, count) {
  const sorted = sortHand(hand);
  return sorted.slice(-count);
}

// 세금 단계용 교환 계획. 손패 변동을 적용해 새 손패 맵 반환.
export function applyTaxExchange(handsMap, ranks, dalmutiPicks) {
  const result = {};
  for (const [pid, hand] of Object.entries(handsMap)) result[pid] = [...hand];

  const greaterPeon = Object.keys(ranks).find((id) => ranks[id] === "greaterPeon");
  const lesserPeon = Object.keys(ranks).find((id) => ranks[id] === "lesserPeon");
  const greaterDal = Object.keys(ranks).find((id) => ranks[id] === "greaterDalmuti");
  const lesserDal = Object.keys(ranks).find((id) => ranks[id] === "lesserDalmuti");

  function exchange(peonId, dalId, count) {
    if (!peonId || !dalId) return;
    const peonGives = peonTribute(result[peonId], count);
    const picks = dalmutiPicks?.[dalId] ?? dalmutiAutoReturn(result[dalId], count);
    const dalGives = picks.slice(0, count);
    result[peonId] = removeFromHand(result[peonId], peonGives);
    result[dalId] = removeFromHand(result[dalId], dalGives);
    result[peonId] = sortHand([...result[peonId], ...dalGives]);
    result[dalId] = sortHand([...result[dalId], ...peonGives]);
  }

  exchange(greaterPeon, greaterDal, 2);
  exchange(lesserPeon, lesserDal, 1);
  return result;
}

// ============================================================
// 라운드 시작 / 게임 시작
// ============================================================

export function startNewRound(prevState) {
  const next = cloneState(prevState);
  const playerCount = next.players.length;
  const deck = shuffle(buildDeck());
  const hands = dealHands(deck, playerCount);

  // 좌석 순서: 이전 라운드의 finishedOrder 사용 (없으면 입장 순서 유지)
  const seatOrder = next.round === 0
    ? next.players.map((p) => p.id)
    : nextSeatOrder(next.finishedOrder);

  // 새 계급 (이전 라운드 종료 시점)
  const ranks = next.round === 0
    ? Object.fromEntries(seatOrder.map((id) => [id, "merchant"]))
    : computeRanks(next.finishedOrder);

  next.players = seatOrder.map((id, idx) => {
    const prev = next.players.find((p) => p.id === id);
    return {
      ...prev,
      hand: hands[idx],
      cardCount: hands[idx].length,
      rank: ranks[id] ?? "merchant",
    };
  });

  next.seatOrder = seatOrder;
  next.finishedOrder = [];
  next.currentTrick = freshTrick();
  next.round = (next.round || 0) + 1;
  next.lastEvent = null;

  if (next.round === 1) {
    // 첫 라운드: 세금 단계 건너뛰고 광대(13) 가진 사람이 시작 (없으면 첫 좌석)
    next.phase = "play";
    const starter = seatOrder.find((id) =>
      next.players.find((p) => p.id === id).hand.includes(JESTER),
    ) ?? seatOrder[0];
    next.currentTurn = starter;
  } else {
    // 2라운드부터: 세금 단계 먼저
    next.phase = "tax";
    next.currentTurn = null;
    next.taxState = {
      ranks,
      // dalmutiPicks: dalmuti 가 peon 에게 줄 카드를 픽 한 결과. 비어 있으면 자동 처리.
      dalmutiPicks: {},
      done: { greater: false, lesser: false },
    };
  }
  return next;
}

// 세금 단계가 끝나면 play 단계로 진입. (호스트가 호출)
export function finishTaxPhase(state) {
  const next = cloneState(state);
  const handsMap = Object.fromEntries(next.players.map((p) => [p.id, p.hand]));
  const newHands = applyTaxExchange(handsMap, next.taxState.ranks, next.taxState.dalmutiPicks);
  for (const p of next.players) {
    p.hand = newHands[p.id];
    p.cardCount = p.hand.length;
  }
  // Greater Dalmuti 가 시작
  const starter = Object.keys(next.taxState.ranks).find(
    (id) => next.taxState.ranks[id] === "greaterDalmuti",
  );
  next.currentTurn = starter ?? next.seatOrder[0];
  next.phase = "play";
  next.taxState = null;
  return next;
}

// ============================================================
// 초기 상태 만들기
// ============================================================

export function createInitialState(players) {
  // players: [{id, nickname, isAI?}]
  const seatOrder = players.map((p) => p.id);
  return {
    phase: "lobby",
    round: 0,
    players: players.map((p) => ({
      id: p.id,
      nickname: p.nickname,
      isAI: !!p.isAI,
      hand: [],
      cardCount: 0,
      rank: "merchant",
    })),
    seatOrder,
    finishedOrder: [],
    leftPlayers: [],        // 도중에 방을 나간 playerId 들
    currentTurn: null,
    currentTrick: freshTrick(),
    taxState: null,
    lastEvent: null,
    turnStartedAt: 0,       // 현재 턴이 시작된 시각 (ms epoch) — 카운트다운용
  };
}

// 깊은 복사가 아니라 얕은 복사 + 중첩 객체 카피. 손패 등 배열은 새 배열로 만든다.
export function cloneState(state) {
  return {
    ...state,
    players: state.players.map((p) => ({ ...p, hand: [...p.hand] })),
    seatOrder: [...state.seatOrder],
    finishedOrder: [...state.finishedOrder],
    leftPlayers: state.leftPlayers ? [...state.leftPlayers] : [],
    currentTrick: {
      ...state.currentTrick,
      passedThisTrick: [...state.currentTrick.passedThisTrick],
      lastPlay: state.currentTrick.lastPlay ? [...state.currentTrick.lastPlay] : null,
    },
    taxState: state.taxState
      ? {
          ranks: { ...state.taxState.ranks },
          dalmutiPicks: Object.fromEntries(
            Object.entries(state.taxState.dalmutiPicks).map(([k, v]) => [k, [...v]]),
          ),
          done: { ...state.taxState.done },
        }
      : null,
    lastEvent: state.lastEvent ? { ...state.lastEvent } : null,
  };
}

// 공개 상태(다른 사람들에게 broadcast 할 때 손패 빼고 전달).
export function publicView(state) {
  const view = cloneState(state);
  view.players = view.players.map((p) => ({
    id: p.id,
    nickname: p.nickname,
    isAI: p.isAI,
    cardCount: p.cardCount,
    rank: p.rank,
  }));
  return view;
}

// 강제 액션(나간 사람 또는 타임아웃)이 트릭 리드 위치에서 내야 할 카드.
// 가장 약한(=숫자가 가장 높은) 카드 1장을 단독으로 낸다.
export function pickForcedLeadCard(hand) {
  if (!hand || hand.length === 0) return null;
  const sorted = [...hand].sort((a, b) => a - b);
  return sorted[sorted.length - 1];
}
