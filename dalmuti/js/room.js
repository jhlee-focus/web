// 클라이언트 상태머신: 로비 ↔ 게임. 호스트와 게스트 양쪽 모두 처리.
// 호스트는 추가로 HostController 인스턴스를 보유함.

import {
  generateRoomCode,
  getOrCreateClientId,
  isOnlineMode,
  joinPublicChannel,
  joinPrivateChannel,
  loadNickname,
  makeAnonNickname,
  saveNickname,
} from "./realtime.js";
import { HostController } from "./hostController.js";
import { MIN_PLAYERS, MAX_PLAYERS } from "../config.js";

// 클라이언트 이벤트:
//   "lobby_changed", "game_started", "state_changed", "private_changed",
//   "host_left", "joined", "error"
export class GameClient extends EventTarget {
  constructor() {
    super();
    this.myId = getOrCreateClientId();
    this.nickname = "";
    this.roomCode = "";
    this.role = null; // 'host' | 'guest'
    this.publicChannel = null;
    this.privateChannel = null;
    this.host = null; // HostController (host only)

    // 로비 상태
    this.presentPlayers = []; // [{playerId, nickname, isHost}] (presence sync 결과)
    this.aiSlots = []; // host-only authoritative; broadcast to guests as room_meta

    // 게임 상태 (모든 클라이언트가 들고 있음)
    this.publicState = null; // server_public view
    this.myHand = [];
    this.myRank = "merchant";

    // 마지막 tax 모달 표시 여부 (UI 가 본인 액션이 필요한지 결정)
    this.taxModalShown = false;
  }

  emit(name, detail = {}) {
    this.dispatchEvent(new CustomEvent(name, { detail }));
  }

  setNickname(name) {
    this.nickname = (name || "").trim() || makeAnonNickname();
    saveNickname(this.nickname);
  }

  // ============================================================
  // 방 생성
  // ============================================================
  async createRoom() {
    this.role = "host";
    this.roomCode = generateRoomCode();
    await this._openPublicChannel();
    if (this.publicChannel.online) {
      await this.publicChannel.track({
        playerId: this.myId,
        nickname: this.nickname,
        isHost: true,
      });
    }
    // 호스트도 자기 자신은 presentPlayers 에 직접 추가 (offline / online 둘 다)
    this._refreshPresent([{ playerId: this.myId, nickname: this.nickname, isHost: true }]);
    this.emit("joined", { role: "host", roomCode: this.roomCode });
    this.emit("lobby_changed");
  }

  // ============================================================
  // 방 입장
  // ============================================================
  async joinRoom(code) {
    if (!isOnlineMode()) {
      this.emit("error", { message: "Supabase 가 설정되지 않아 방 입장이 불가합니다." });
      return false;
    }
    this.role = "guest";
    this.roomCode = (code || "").toUpperCase();
    await this._openPublicChannel();
    this.privateChannel = await joinPrivateChannel(this.roomCode, this.myId, {
      onBroadcast: (event, payload) => this._onPrivate(event, payload),
    });
    if (this.publicChannel.online) {
      await this.publicChannel.track({
        playerId: this.myId,
        nickname: this.nickname,
        isHost: false,
      });
    }
    this.emit("joined", { role: "guest", roomCode: this.roomCode });
    this.emit("lobby_changed");
    return true;
  }

  async _openPublicChannel() {
    this.publicChannel = await joinPublicChannel(this.roomCode, {
      onPresenceSync: (state) => {
        const flat = Object.values(state).flat();
        this._refreshPresent(flat);
      },
      onBroadcast: (event, payload) => this._onBroadcast(event, payload),
    });
  }

  _refreshPresent(list) {
    // 중복 제거 (한 클라이언트가 여러 presence 키로 잡힐 수 있음)
    const seen = new Set();
    const unique = [];
    for (const p of list) {
      if (!p || !p.playerId) continue;
      if (seen.has(p.playerId)) continue;
      seen.add(p.playerId);
      unique.push(p);
    }
    this.presentPlayers = unique;
    this.emit("lobby_changed");
  }

  _onBroadcast(event, payload) {
    if (event === "state_public") {
      this.publicState = payload;
      // 호스트의 경우엔 onLocalStateChange 가 이미 처리하므로 자기 자신의 broadcast 는 self:false 로 받지 않음.
      this.emit("state_changed");
    } else if (event === "room_meta") {
      // 호스트 → 게스트: AI 슬롯 갱신 등
      if (this.role === "guest") {
        this.aiSlots = payload.aiSlots ?? this.aiSlots;
        this.emit("lobby_changed");
      }
    } else if (event === "action") {
      // 호스트 → 게스트가 보낸 액션
      if (this.role === "host" && this.host) {
        this.host.receiveAction(payload.playerId, payload.action);
      }
    } else if (event === "tax_pick") {
      // 게스트가 dalmuti 픽을 보냄
      if (this.role === "host" && this.host) {
        this.host.submitDalmutiPick(payload.playerId, payload.cards);
      }
    } else if (event === "host_left") {
      this.emit("host_left");
    }
  }

  _onPrivate(event, payload) {
    if (event === "private_hand") {
      this.myHand = payload.hand ?? [];
      this.myRank = payload.rank ?? this.myRank;
      this.emit("private_changed");
    }
  }

  // ============================================================
  // 호스트 전용: AI 슬롯 / 게임 시작
  // ============================================================
  addAISlot() {
    if (this.role !== "host") return;
    if (this.totalSlotCount() >= MAX_PLAYERS) return;
    const idx = this.aiSlots.length + 1;
    const id = `ai-${idx}-${Math.random().toString(36).slice(2, 6)}`;
    this.aiSlots.push({ id, nickname: `AI Bot ${idx}`, isAI: true });
    this._broadcastRoomMeta();
    this.emit("lobby_changed");
  }

  removeAISlot() {
    if (this.role !== "host") return;
    this.aiSlots.pop();
    this._broadcastRoomMeta();
    this.emit("lobby_changed");
  }

  _broadcastRoomMeta() {
    if (!this.publicChannel?.online) return;
    this.publicChannel.broadcast("room_meta", { aiSlots: this.aiSlots });
  }

  totalSlotCount() {
    return this.presentPlayers.length + this.aiSlots.length;
  }

  canStartGame() {
    if (this.role !== "host") return false;
    const total = this.totalSlotCount();
    return total >= MIN_PLAYERS && total <= MAX_PLAYERS;
  }

  async startGame() {
    if (!this.canStartGame()) return;
    const players = [
      // 호스트(자기 자신)을 첫 자리로
      { id: this.myId, nickname: this.nickname, isAI: false },
      ...this.presentPlayers
        .filter((p) => p.playerId !== this.myId)
        .map((p) => ({ id: p.playerId, nickname: p.nickname, isAI: false })),
      ...this.aiSlots.map((p) => ({ id: p.id, nickname: p.nickname, isAI: true })),
    ];

    this.host = new HostController({
      roomCode: this.roomCode,
      players,
      publicChannel: this.publicChannel,
      onLocalStateChange: (state, pub) => {
        this.publicState = pub;
        // 호스트 본인의 손패 / 계급 갱신
        const me = state.players.find((p) => p.id === this.myId);
        if (me) {
          this.myHand = [...me.hand];
          this.myRank = me.rank;
        }
        this.emit("state_changed");
        this.emit("private_changed");
      },
    });

    this.emit("game_started");
    await this.host.startGame();
  }

  // ============================================================
  // 인간 플레이어 액션
  // ============================================================
  async submitAction(action) {
    if (this.role === "host") {
      await this.host?.receiveAction(this.myId, action);
    } else {
      await this.publicChannel?.broadcast("action", {
        playerId: this.myId,
        action,
      });
    }
  }

  async submitDalmutiPick(cards) {
    if (this.role === "host") {
      await this.host?.submitDalmutiPick(this.myId, cards);
    } else {
      await this.publicChannel?.broadcast("tax_pick", {
        playerId: this.myId,
        cards,
      });
    }
  }

  // ============================================================
  // 정리
  // ============================================================
  async leave() {
    try {
      if (this.host) await this.host.dispose();
    } catch {}
    try {
      if (this.publicChannel) await this.publicChannel.leave();
    } catch {}
    try {
      if (this.privateChannel) await this.privateChannel.leave();
    } catch {}
    this.host = null;
    this.publicChannel = null;
    this.privateChannel = null;
    this.publicState = null;
    this.myHand = [];
    this.role = null;
    this.roomCode = "";
    this.presentPlayers = [];
    this.aiSlots = [];
  }

  // 편의 헬퍼
  loadStoredNickname() {
    return loadNickname();
  }
}
