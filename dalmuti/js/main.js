// 진입점 — DOM 과 GameClient 를 연결.

import { GameClient } from "./room.js";
import { isOnlineMode, makeAnonNickname } from "./realtime.js";
import {
  renderLobbyRoom,
  renderGame,
  renderTaxModal,
  renderRoundEndModal,
  showToast,
  validateSelection,
} from "./ui.js";

// ================ DOM 헬퍼 ================
const $ = (id) => document.getElementById(id);
const els = {
  lobby: $("lobby"),
  game: $("game"),

  // 닉네임 화면
  nicknameScreen: $("nickname-screen"),
  nicknameInput: $("nickname-input"),
  continueBtn: $("continue-btn"),
  onlineStatusValue: $("online-status-value"),

  // 입장 선택 화면
  entryScreen: $("entry-screen"),
  entryNickname: $("entry-nickname"),
  createRoomBtn: $("create-room-btn"),
  roomCodeInput: $("room-code-input"),
  joinRoomBtn: $("join-room-btn"),
  joinWarning: $("join-warning"),

  // 룸 화면
  roomScreen: $("room-screen"),
  roomCodeDisplay: $("room-code-display"),
  copyLinkBtn: $("copy-link-btn"),
  lobbyPlayers: $("lobby-players"),
  playerCount: $("player-count"),
  hostControls: $("host-controls"),
  guestWaiting: $("guest-waiting"),
  addAiBtn: $("add-ai-btn"),
  removeAiBtn: $("remove-ai-btn"),
  aiCount: $("ai-count"),
  startGameBtn: $("start-game-btn"),

  // 게임 화면
  playersPanel: $("players-panel"),
  trickCards: $("trick-cards"),
  trickInfo: $("trick-info"),
  statusLine: $("status-line"),
  handCards: $("hand-cards"),
  playBtn: $("play-btn"),
  passBtn: $("pass-btn"),
  clearSelectionBtn: $("clear-selection-btn"),

  // 모달
  taxModal: $("tax-modal"),
  taxInstruction: $("tax-instruction"),
  taxHand: $("tax-hand"),
  taxSubmitBtn: $("tax-submit-btn"),
  roundEndModal: $("round-end-modal"),
  roundEndTitle: $("round-end-title"),
  roundEndList: $("round-end-list"),

  toast: $("toast"),
};

// ================ 상태 ================
const client = new GameClient();
let selection = new Set(); // 손패에서 선택한 카드 인덱스
let taxSelection = new Set();

// 디버그: localhost 에서는 client 를 window 에 노출
if (location.hostname === "localhost" || location.hostname === "127.0.0.1") {
  window.__dalmuti = { client, getSelection: () => selection };
}

// ================ 초기 화면 ================
function init() {
  // online 상태 표시
  if (isOnlineMode()) {
    els.onlineStatusValue.textContent = "Supabase 연결됨 ✓";
    els.onlineStatusValue.style.color = "var(--accent)";
  } else {
    els.onlineStatusValue.textContent = "오프라인 (솔로 + AI 만 가능)";
    els.onlineStatusValue.style.color = "var(--text-dim)";
    els.joinWarning.hidden = false;
    els.joinRoomBtn.disabled = true;
    els.roomCodeInput.disabled = true;
  }

  // 닉네임 복원
  const stored = client.loadStoredNickname();
  if (stored) els.nicknameInput.value = stored;
  els.nicknameInput.focus();

  // URL 해시에 방 코드 있으면 자동 채움 (#room=AB23CD)
  const m = location.hash.match(/room=([A-Z0-9]+)/i);
  if (m) {
    els.roomCodeInput.value = m[1].toUpperCase();
  }
}

// ================ 화면 전환 ================
function showLobbySection(name) {
  els.nicknameScreen.hidden = name !== "nickname";
  els.entryScreen.hidden = name !== "entry";
  els.roomScreen.hidden = name !== "room";
}

function showGame() {
  els.lobby.hidden = true;
  els.game.hidden = false;
}

function showLobby() {
  els.lobby.hidden = false;
  els.game.hidden = true;
}

// ================ 이벤트: 닉네임 ================
els.continueBtn.addEventListener("click", () => {
  const raw = els.nicknameInput.value.trim();
  client.setNickname(raw);
  els.entryNickname.textContent = client.nickname;
  showLobbySection("entry");
});
els.nicknameInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") els.continueBtn.click();
});

// ================ 이벤트: 방 생성/입장 ================
els.createRoomBtn.addEventListener("click", async () => {
  els.createRoomBtn.disabled = true;
  try {
    await client.createRoom();
    showLobbySection("room");
    if (client.publicChannel?.online) {
      // 공유 가능한 링크 만들기
      els.copyLinkBtn.hidden = false;
    }
  } catch (e) {
    showToast(els, "방 생성 실패: " + (e.message || e));
  } finally {
    els.createRoomBtn.disabled = false;
  }
});

els.joinRoomBtn.addEventListener("click", async () => {
  const code = els.roomCodeInput.value.trim().toUpperCase();
  if (!code) {
    showToast(els, "방 코드를 입력하세요.");
    return;
  }
  els.joinRoomBtn.disabled = true;
  try {
    const ok = await client.joinRoom(code);
    if (ok) showLobbySection("room");
  } catch (e) {
    showToast(els, "입장 실패: " + (e.message || e));
  } finally {
    els.joinRoomBtn.disabled = false;
  }
});

els.roomCodeInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") els.joinRoomBtn.click();
});

els.copyLinkBtn?.addEventListener("click", () => {
  const link = `${location.origin}${location.pathname}#room=${client.roomCode}`;
  navigator.clipboard?.writeText(link).then(
    () => showToast(els, "링크가 복사됐어요"),
    () => showToast(els, "복사 실패: " + link),
  );
});

// ================ 이벤트: 호스트 컨트롤 ================
els.addAiBtn.addEventListener("click", () => client.addAISlot());
els.removeAiBtn.addEventListener("click", () => client.removeAISlot());
els.startGameBtn.addEventListener("click", async () => {
  els.startGameBtn.disabled = true;
  await client.startGame();
});

// ================ 이벤트: 게임 액션 ================
els.handCards.addEventListener("click", (e) => {
  const card = e.target.closest(".card");
  if (!card) return;
  if (card.classList.contains("disabled") || card.classList.contains("locked")) return;
  const idx = parseInt(card.dataset.index);
  if (Number.isNaN(idx)) return;
  if (selection.has(idx)) selection.delete(idx);
  else selection.add(idx);
  renderAll();
});

els.clearSelectionBtn.addEventListener("click", () => {
  selection.clear();
  renderAll();
});

els.playBtn.addEventListener("click", async () => {
  if (!client.publicState) return;
  const trick = client.publicState.currentTrick;
  const sel = validateSelection(client.myHand, selection, trick);
  if (!sel.ok) {
    showToast(els, "낼 수 없는 조합입니다.");
    return;
  }
  await client.submitAction({ type: "play", cards: sel.cards });
  selection.clear();
});

els.passBtn.addEventListener("click", async () => {
  await client.submitAction({ type: "pass" });
  selection.clear();
});

// ================ 이벤트: 세금 모달 ================
els.taxHand.addEventListener("click", (e) => {
  const card = e.target.closest(".card");
  if (!card) return;
  const idx = parseInt(card.dataset.index);
  if (Number.isNaN(idx)) return;

  const myRank = client.publicState?.taxState?.ranks?.[client.myId];
  const need = myRank === "greaterDalmuti" ? 2 : myRank === "lesserDalmuti" ? 1 : 0;
  if (need === 0) return;

  if (taxSelection.has(idx)) {
    taxSelection.delete(idx);
  } else {
    if (taxSelection.size >= need) {
      // 가장 오래된 선택을 제거
      const first = taxSelection.values().next().value;
      taxSelection.delete(first);
    }
    taxSelection.add(idx);
  }
  renderTaxModal(client, els, taxSelection);
});

els.taxSubmitBtn.addEventListener("click", async () => {
  const cards = [...taxSelection].map((i) => client.myHand[i]);
  await client.submitDalmutiPick(cards);
  taxSelection.clear();
});

// ================ 이벤트: GameClient → 렌더 ================
client.addEventListener("lobby_changed", () => {
  if (els.roomScreen.hidden && els.entryScreen.hidden) return;
  renderLobbyRoom(client, els);
});

client.addEventListener("joined", () => {
  showLobbySection("room");
  renderLobbyRoom(client, els);
});

client.addEventListener("game_started", () => {
  showGame();
});

client.addEventListener("state_changed", () => {
  // 게임이 시작되면 자동으로 게임 화면 전환
  if (client.publicState && els.game.hidden) showGame();
  renderAll();
});

client.addEventListener("private_changed", () => {
  renderAll();
});

client.addEventListener("host_left", () => {
  showToast(els, "호스트가 방을 떠나 게임이 종료되었습니다.", 5000);
  setTimeout(async () => {
    await client.leave();
    location.hash = "";
    showLobby();
    showLobbySection("entry");
  }, 1200);
});

client.addEventListener("error", (e) => {
  showToast(els, e.detail.message);
});

// ================ 통합 렌더 ================
function renderAll() {
  if (!client.publicState) return;
  renderGame(client, els, selection);
  renderTaxModal(client, els, taxSelection);
  renderRoundEndModal(client, els);
}

// 페이지 떠날 때 호스트라면 host_left broadcast
window.addEventListener("beforeunload", () => {
  if (client.host) {
    client.host.dispose();
  }
});

// ================ 시작 ================
init();
