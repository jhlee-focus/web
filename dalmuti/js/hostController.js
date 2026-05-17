// 호스트 컨트롤러: 방을 만든 사람의 클라이언트가 게임 상태의 진실 공급원이 됩니다.
// - public 채널 broadcast (state_public, room_meta)
// - 인간 플레이어 각자의 private 채널 broadcast (private_hand)
// - AI 차례 자동 진행

import {
  createInitialState,
  startNewRound,
  validatePlay,
  applyPlay,
  applyPass,
  finishTaxPhase,
  publicView,
  RANK_TITLE,
} from "./game.js";
import { chooseAction, chooseDalmutiReturn } from "./aiPlayer.js";
import { joinPrivateChannel } from "./realtime.js";

const AI_TURN_DELAY_MIN = 700;
const AI_TURN_DELAY_MAX = 1500;
const ROUND_END_DELAY_MS = 4500;
const TAX_AUTO_DELAY_MS = 1500;

export class HostController {
  constructor({ roomCode, players, publicChannel, onLocalStateChange }) {
    this.roomCode = roomCode;
    this.publicChannel = publicChannel; // 공개 채널 (online 또는 offline 더미)
    this.onLocalStateChange = onLocalStateChange;

    this.state = createInitialState(players);
    this.privateChannels = {}; // { [playerId]: channel }
    this.aiTimer = null;
    this.advanceTimer = null;
    this.taxTimer = null;
    this.disposed = false;
  }

  // 인간 플레이어가 입장하면 private 채널을 연다(호스트가 손패 송신용).
  async ensurePrivateChannel(playerId) {
    if (this.privateChannels[playerId]) return;
    if (!this.publicChannel.online) return; // offline: 호스트 자기 자신만 → private 불필요
    try {
      this.privateChannels[playerId] = await joinPrivateChannel(this.roomCode, playerId, {});
    } catch (err) {
      console.warn("private channel open failed", playerId, err);
    }
  }

  async startGame() {
    if (this.disposed) return;
    this.clearTimers();
    // 모든 인간 플레이어 private 채널 확보
    for (const p of this.state.players) {
      if (!p.isAI) await this.ensurePrivateChannel(p.id);
    }
    this.state = startNewRound(this.state);
    await this.broadcastAll();
    this.maybeAutoTax();
    this.scheduleAITurn();
  }

  // tax 단계 진입 시: AI dalmuti 가 자동 픽 → finishTaxPhase 호출
  // (인간 dalmuti 가 있다면 입력 대기 — UI 가 호스트에 메시지 보내야 함)
  maybeAutoTax() {
    if (this.disposed) return;
    if (this.state.phase !== "tax") return;
    const ranks = this.state.taxState.ranks;
    const greaterDal = Object.keys(ranks).find((id) => ranks[id] === "greaterDalmuti");
    const lesserDal = Object.keys(ranks).find((id) => ranks[id] === "lesserDalmuti");
    const greaterDalPlayer = this.state.players.find((p) => p.id === greaterDal);
    const lesserDalPlayer = this.state.players.find((p) => p.id === lesserDal);

    const picks = { ...this.state.taxState.dalmutiPicks };
    let humansWaiting = false;

    if (greaterDal) {
      if (greaterDalPlayer.isAI) {
        picks[greaterDal] = chooseDalmutiReturn(greaterDalPlayer.hand, 2);
      } else if (!picks[greaterDal]) {
        humansWaiting = true;
      }
    }
    if (lesserDal) {
      if (lesserDalPlayer.isAI) {
        picks[lesserDal] = chooseDalmutiReturn(lesserDalPlayer.hand, 1);
      } else if (!picks[lesserDal]) {
        humansWaiting = true;
      }
    }

    this.state = { ...this.state, taxState: { ...this.state.taxState, dalmutiPicks: picks } };

    if (humansWaiting) {
      // UI 가 호스트에게 submitDalmutiPick(playerId, cards) 호출하길 대기
      this.broadcastAll();
      return;
    }

    // 모두 자동 → 약간의 딜레이 후 tax 종료
    this.taxTimer = setTimeout(async () => {
      this.state = finishTaxPhase(this.state);
      await this.broadcastAll();
      this.scheduleAITurn();
    }, TAX_AUTO_DELAY_MS);
  }

  // UI(인간 dalmuti)가 자기 카드를 선택해 보내옴
  async submitDalmutiPick(playerId, cards) {
    if (this.state.phase !== "tax") return;
    const ranks = this.state.taxState.ranks;
    if (ranks[playerId] !== "greaterDalmuti" && ranks[playerId] !== "lesserDalmuti") return;
    const expected = ranks[playerId] === "greaterDalmuti" ? 2 : 1;
    if (cards.length !== expected) return;
    const picks = { ...this.state.taxState.dalmutiPicks, [playerId]: [...cards] };
    this.state = { ...this.state, taxState: { ...this.state.taxState, dalmutiPicks: picks } };

    // 두 dalmuti 모두 픽 끝났는가?
    const dalmutis = Object.keys(ranks).filter(
      (id) => ranks[id] === "greaterDalmuti" || ranks[id] === "lesserDalmuti",
    );
    const allDone = dalmutis.every((id) => picks[id]);
    if (allDone) {
      this.state = finishTaxPhase(this.state);
      await this.broadcastAll();
      this.scheduleAITurn();
    } else {
      await this.broadcastAll();
    }
  }

  // 인간 플레이어에게서 들어오는 action (또는 AI 가 직접 주입)
  async receiveAction(playerId, action) {
    if (this.disposed) return;
    if (this.state.phase !== "play") return;
    if (this.state.currentTurn !== playerId) return;

    if (action.type === "play") {
      const v = validatePlay(this.state, playerId, action.cards);
      if (!v.ok) {
        // 잘못된 액션은 무시 (UI 측에서 검증해야 함)
        console.warn("invalid play", playerId, v.reason, action.cards);
        return;
      }
      this.state = applyPlay(this.state, playerId, action.cards);
    } else if (action.type === "pass") {
      const r = applyPass(this.state, playerId);
      if (!r.ok) {
        console.warn("invalid pass", playerId, r.reason);
        return;
      }
      this.state = r.state;
    } else {
      return;
    }

    if (this.state.phase === "roundEnd") {
      await this.broadcastAll();
      this.advanceTimer = setTimeout(() => this.advanceRound(), ROUND_END_DELAY_MS);
      return;
    }

    await this.broadcastAll();
    this.scheduleAITurn();
  }

  scheduleAITurn() {
    if (this.disposed) return;
    clearTimeout(this.aiTimer);
    if (this.state.phase !== "play") return;
    const turn = this.state.currentTurn;
    if (!turn) return;
    const p = this.state.players.find((pp) => pp.id === turn);
    if (!p || !p.isAI) return;

    const delay =
      AI_TURN_DELAY_MIN + Math.floor(Math.random() * (AI_TURN_DELAY_MAX - AI_TURN_DELAY_MIN));
    this.aiTimer = setTimeout(() => {
      if (this.disposed) return;
      const currentTurn = this.state.currentTurn;
      if (currentTurn !== turn) return; // 상태가 바뀌었으면 재예약된 다른 타이머가 처리
      const action = chooseAction(this.state, turn);
      this.receiveAction(turn, action);
    }, delay);
  }

  async advanceRound() {
    if (this.disposed) return;
    this.clearTimers();
    this.state = startNewRound(this.state);
    await this.broadcastAll();
    this.maybeAutoTax();
    this.scheduleAITurn();
  }

  async broadcastAll() {
    if (this.disposed) return;
    const pub = publicView(this.state);
    this.onLocalStateChange?.(this.state, pub);
    if (this.publicChannel.online) {
      try {
        await this.publicChannel.broadcast("state_public", pub);
      } catch (e) {
        console.warn("public broadcast failed", e);
      }
    }
    // private hands → 인간 플레이어에게만
    for (const player of this.state.players) {
      if (player.isAI) continue;
      const ch = this.privateChannels[player.id];
      if (!ch || !ch.online) continue;
      try {
        await ch.broadcast("private_hand", {
          hand: [...player.hand],
          rank: player.rank,
        });
      } catch (e) {
        console.warn("private broadcast failed", player.id, e);
      }
    }
  }

  clearTimers() {
    clearTimeout(this.aiTimer);
    clearTimeout(this.advanceTimer);
    clearTimeout(this.taxTimer);
    this.aiTimer = null;
    this.advanceTimer = null;
    this.taxTimer = null;
  }

  async dispose() {
    this.disposed = true;
    this.clearTimers();
    if (this.publicChannel.online) {
      try {
        await this.publicChannel.broadcast("host_left", {});
      } catch {}
    }
    for (const ch of Object.values(this.privateChannels)) {
      try {
        await ch.leave();
      } catch {}
    }
  }
}
