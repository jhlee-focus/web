// 렌더링 함수 모음. DOM 의존성 있음.

import { JESTER, rankLabel } from "./cards.js";
import { RANK_TITLE, effectiveRank, isUniformPlay } from "./game.js";

// ===== 카드 표현 모드 =====
// "simple" : 빈 카드 + 숫자/J 텍스트 (기본)
// "image"  : assets/card_imgs_1st/NN.png 이미지
let _cardStyle = "simple";
export function setCardStyle(style) {
  _cardStyle = style === "image" ? "image" : "simple";
}
export function getCardStyle() {
  return _cardStyle;
}

// ===== 카드 엘리먼트 =====
export function makeCardEl(cardValue, opts = {}) {
  const div = document.createElement("div");
  const isJester = cardValue === JESTER;
  div.className = "card" + (isJester ? " jester" : ` rank-${cardValue}`);

  if (_cardStyle === "image") {
    div.classList.add("card-image");
    const img = document.createElement("img");
    img.src = isJester
      ? "assets/card_imgs_1st/joker.png"
      : `assets/card_imgs_1st/${String(cardValue).padStart(2, "0")}.png`;
    img.alt = isJester ? "Joker" : String(cardValue);
    img.draggable = false;
    img.loading = "lazy";
    div.appendChild(img);
  } else if (!isJester) {
    div.textContent = String(cardValue);
  }

  if (opts.disabled) div.classList.add("disabled");
  if (opts.locked) div.classList.add("locked");
  if (opts.selected) div.classList.add("selected");
  div.dataset.value = String(cardValue);
  if (opts.dataIndex !== undefined) div.dataset.index = String(opts.dataIndex);
  return div;
}

// ===== 로비 =====
export function renderLobbyRoom(client, els) {
  els.roomCodeDisplay.textContent = client.roomCode;
  els.copyLinkBtn.hidden = !client.publicChannel?.online;

  // 플레이어 목록
  els.lobbyPlayers.innerHTML = "";
  const allPlayers = [
    ...client.presentPlayers.map((p) => ({
      id: p.playerId,
      nickname: p.nickname,
      isHost: p.isHost,
      isAI: false,
    })),
    ...client.aiSlots.map((p) => ({ id: p.id, nickname: p.nickname, isAI: true })),
  ];
  for (const p of allPlayers) {
    const li = document.createElement("li");
    if (p.isHost) li.classList.add("host");
    if (p.isAI) li.classList.add("is-ai");
    const name = document.createElement("span");
    name.textContent = p.nickname + (p.id === client.myId ? " (나)" : "");
    li.appendChild(name);
    els.lobbyPlayers.appendChild(li);
  }
  els.playerCount.textContent = String(allPlayers.length);

  if (client.role === "host") {
    els.hostControls.hidden = false;
    els.guestWaiting.hidden = true;
    els.aiCount.textContent = String(client.aiSlots.length);
    els.startGameBtn.disabled = !client.canStartGame();
    els.startGameBtn.textContent = client.canStartGame()
      ? "게임 시작"
      : `게임 시작 (${4 - allPlayers.length > 0 ? `${4 - allPlayers.length}명 더 필요` : "8명 초과"})`;
  } else {
    els.hostControls.hidden = true;
    els.guestWaiting.hidden = false;
  }
}

// ===== 게임 =====
export function renderGame(client, els, selection) {
  const state = client.publicState;
  if (!state) return;

  // 플레이어 패널
  renderPlayersPanel(state, client, els.playersPanel);

  // 트릭
  renderTrick(state, els.trickCards, els.trickInfo);

  // 상태 라인
  els.statusLine.innerHTML = renderStatusLine(state, client);

  // 손패
  renderHand(client, els.handCards, selection);

  // 액션 버튼 가시성
  const myTurn = state.phase === "play" && state.currentTurn === client.myId;
  const trick = state.currentTrick;
  const canPlaySelection = myTurn && validateSelection(client.myHand, selection, trick);
  els.playBtn.disabled = !myTurn || !canPlaySelection.ok;
  els.passBtn.disabled = !myTurn || trick.leadCount === null;
  els.clearSelectionBtn.disabled = selection.size === 0;
}

function renderPlayersPanel(state, client, container) {
  container.innerHTML = "";
  for (const p of state.players) {
    const tile = document.createElement("div");
    tile.className = "player-tile";
    if (state.currentTurn === p.id && state.phase === "play") tile.classList.add("is-turn");
    if (state.finishedOrder.includes(p.id)) tile.classList.add("is-finished");

    const nameRow = document.createElement("div");
    nameRow.className = "name-row";
    const name = document.createElement("span");
    name.className = "nickname";
    name.textContent = (p.id === client.myId ? "★ " : "") + p.nickname + (p.isAI ? " 🤖" : "");
    nameRow.appendChild(name);
    if (p.rank && p.rank !== "merchant") {
      const badge = document.createElement("span");
      badge.className = `badge ${p.rank}`;
      badge.textContent = RANK_TITLE[p.rank] || p.rank;
      nameRow.appendChild(badge);
    }
    tile.appendChild(nameRow);

    const meta = document.createElement("div");
    meta.className = "meta";
    const finIdx = state.finishedOrder.indexOf(p.id);
    meta.innerHTML = `
      <span>카드 ${p.cardCount}장</span>
      <span>${finIdx === -1 ? "" : `${finIdx + 1}등`}</span>
    `;
    tile.appendChild(meta);

    container.appendChild(tile);
  }
}

function renderTrick(state, cardsEl, infoEl) {
  cardsEl.innerHTML = "";
  const trick = state.currentTrick;
  if (trick.lastPlay && trick.lastPlay.length > 0) {
    for (const v of trick.lastPlay) {
      cardsEl.appendChild(makeCardEl(v, { locked: true }));
    }
    const player = state.players.find((p) => p.id === trick.lastPlayerId);
    infoEl.textContent = `${player?.nickname ?? "?"} 가 ${rankLabel(trick.leadRank)} ${trick.leadCount}장 냄`;
  } else {
    infoEl.textContent = state.phase === "play" ? "리드 자리: 카드를 내세요" : "";
  }
}

function renderStatusLine(state, client) {
  if (state.phase === "tax") return "<strong>세금/조공 단계</strong>";
  if (state.phase === "roundEnd") return `<strong>라운드 ${state.round}</strong> 종료`;
  if (state.phase === "play") {
    const turnPlayer = state.players.find((p) => p.id === state.currentTurn);
    if (!turnPlayer) return "";
    if (state.currentTurn === client.myId) {
      return "<strong>당신 차례</strong>";
    }
    return `${turnPlayer.nickname} 차례` + (turnPlayer.isAI ? " (AI)" : "");
  }
  return "";
}

function renderHand(client, container, selection) {
  container.innerHTML = "";
  const hand = client.myHand;
  hand.forEach((card, idx) => {
    const el = makeCardEl(card, {
      selected: selection.has(idx),
      dataIndex: idx,
    });
    container.appendChild(el);
  });
}

// 선택된 카드가 현재 트릭에 낼 수 있는지 검증.
function validateSelection(hand, selectionSet, trick) {
  if (selectionSet.size === 0) return { ok: false };
  const cards = [...selectionSet].map((i) => hand[i]);
  if (!isUniformPlay(cards)) return { ok: false };
  if (trick.leadCount !== null) {
    if (cards.length !== trick.leadCount) return { ok: false };
    const eff = effectiveRank(cards);
    if (eff >= trick.leadRank) return { ok: false };
  }
  return { ok: true, cards };
}

// 외부에서 쓸 수 있게 노출
export { validateSelection };

// ===== 세금 모달 =====
export function renderTaxModal(client, els, taxSelection) {
  const state = client.publicState;
  if (!state || state.phase !== "tax") {
    els.taxModal.hidden = true;
    return;
  }

  const ranks = state.taxState?.ranks || {};
  const myRank = ranks[client.myId];
  const isGreaterDal = myRank === "greaterDalmuti";
  const isLesserDal = myRank === "lesserDalmuti";

  if (!isGreaterDal && !isLesserDal) {
    // 페온은 자동 송출. 모달 띄우지 않음 (안내 문구만 status-line 에)
    els.taxModal.hidden = true;
    return;
  }

  const need = isGreaterDal ? 2 : 1;
  els.taxInstruction.textContent = isGreaterDal
    ? "Greater Peon 에게 줄 카드 2장을 고르세요. (보통 가장 약한 카드를 보냅니다)"
    : "Lesser Peon 에게 줄 카드 1장을 고르세요.";

  els.taxHand.innerHTML = "";
  client.myHand.forEach((card, idx) => {
    const el = makeCardEl(card, {
      selected: taxSelection.has(idx),
      dataIndex: idx,
    });
    els.taxHand.appendChild(el);
  });

  els.taxSubmitBtn.disabled = taxSelection.size !== need;
  els.taxSubmitBtn.textContent = `${need}장 보내기`;
  els.taxModal.hidden = false;
}

// ===== 라운드 종료 모달 =====
export function renderRoundEndModal(client, els) {
  const state = client.publicState;
  if (!state || state.phase !== "roundEnd") {
    els.roundEndModal.hidden = true;
    return;
  }
  els.roundEndTitle.textContent = `라운드 ${state.round} 결과`;
  els.roundEndList.innerHTML = "";
  state.finishedOrder.forEach((pid, idx) => {
    const player = state.players.find((p) => p.id === pid);
    const li = document.createElement("li");
    const left = document.createElement("span");
    const pos = document.createElement("span");
    pos.className = `rank-pos pos-${idx + 1}`;
    pos.textContent = `${idx + 1}등`;
    left.appendChild(pos);
    const name = document.createElement("span");
    name.textContent = " " + (player?.nickname ?? "?") + (player?.isAI ? " (AI)" : "");
    left.appendChild(name);
    li.appendChild(left);
    const right = document.createElement("span");
    right.className = "muted small";
    const newRank =
      idx === 0
        ? "Greater Dalmuti"
        : idx === 1
        ? "Lesser Dalmuti"
        : idx === state.finishedOrder.length - 1
        ? "Greater Peon"
        : idx === state.finishedOrder.length - 2
        ? "Lesser Peon"
        : "Merchant";
    right.textContent = newRank;
    li.appendChild(right);
    els.roundEndList.appendChild(li);
  });
  els.roundEndModal.hidden = false;
}

// ===== 토스트 =====
let toastTimer = null;
export function showToast(els, msg, ms = 2400) {
  els.toast.textContent = msg;
  els.toast.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    els.toast.hidden = true;
  }, ms);
}
