// Supabase Realtime 래퍼.
// Supabase 가 설정되지 않은 경우(SUPABASE_URL/KEY 비어있음)는 offline 모드로 작동합니다.
// offline 모드에서는 모든 broadcast 가 no-op 이고, 솔로(=AI 봇만) 플레이만 가능합니다.

import { SUPABASE_URL, SUPABASE_ANON_KEY } from "../config.js";

const SUPABASE_CDN = "https://esm.sh/@supabase/supabase-js@2";

let _client = null;
let _clientPromise = null;

export function isOnlineMode() {
  return !!(SUPABASE_URL && SUPABASE_ANON_KEY);
}

async function getClient() {
  if (!isOnlineMode()) return null;
  if (_client) return _client;
  if (_clientPromise) return _clientPromise;
  _clientPromise = (async () => {
    const mod = await import(/* @vite-ignore */ SUPABASE_CDN);
    _client = mod.createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
      realtime: { params: { eventsPerSecond: 10 } },
    });
    return _client;
  })();
  return _clientPromise;
}

// 클라이언트 ID (브라우저 단위 고정).
export function getOrCreateClientId() {
  let id = localStorage.getItem("dalmuti.clientId");
  if (!id) {
    id = (crypto.randomUUID && crypto.randomUUID()) || `c-${Math.random().toString(36).slice(2, 12)}`;
    localStorage.setItem("dalmuti.clientId", id);
  }
  return id;
}

// 닉네임 영속.
export function loadNickname() {
  return localStorage.getItem("dalmuti.nickname") || "";
}
export function saveNickname(name) {
  localStorage.setItem("dalmuti.nickname", name || "");
}

// 익명 닉네임 자동 생성.
export function makeAnonNickname() {
  const num = String(Math.floor(Math.random() * 999999)).padStart(6, "0");
  return `Player-${num}`;
}

// 6자리 방 코드. 혼동되는 0/O/1/I/L 제외.
const ROOM_ALPHABET = "23456789ABCDEFGHJKMNPQRSTUVWXYZ";
export function generateRoomCode(len = 6) {
  let s = "";
  for (let i = 0; i < len; i++) {
    s += ROOM_ALPHABET[Math.floor(Math.random() * ROOM_ALPHABET.length)];
  }
  return s;
}

// 공개 룸 채널 입장. 인간 플레이어가 호스트/게스트로 입장할 때 사용.
//   handlers: { onPresenceSync, onBroadcast }
//   onBroadcast(event, payload) - event 이름 그대로
export async function joinPublicChannel(roomCode, handlers = {}) {
  const sb = await getClient();
  if (!sb) {
    // offline 모드: 더미 채널 (broadcast/presence 모두 no-op)
    return makeOfflineChannel();
  }

  const channel = sb.channel(`dalmuti-room-${roomCode}`, {
    config: {
      broadcast: { self: false, ack: false },
      presence: { key: getOrCreateClientId() },
    },
  });

  if (handlers.onPresenceSync) {
    channel.on("presence", { event: "sync" }, () => {
      handlers.onPresenceSync(channel.presenceState());
    });
    channel.on("presence", { event: "join" }, () => {
      handlers.onPresenceSync(channel.presenceState());
    });
    channel.on("presence", { event: "leave" }, () => {
      handlers.onPresenceSync(channel.presenceState());
    });
  }

  // 모든 broadcast 이벤트 수신
  if (handlers.onBroadcast) {
    const events = ["room_meta", "state_public", "action", "tax_done", "round_advance", "host_left"];
    for (const ev of events) {
      channel.on("broadcast", { event: ev }, (payload) => {
        handlers.onBroadcast(ev, payload.payload ?? payload);
      });
    }
  }

  await new Promise((resolve, reject) => {
    channel.subscribe((status) => {
      if (status === "SUBSCRIBED") resolve();
      else if (status === "CHANNEL_ERROR" || status === "TIMED_OUT") reject(new Error(status));
    });
  });

  return {
    online: true,
    track: (state) => channel.track(state),
    untrack: () => channel.untrack(),
    broadcast: (event, payload) =>
      channel.send({ type: "broadcast", event, payload }),
    leave: () => channel.unsubscribe(),
  };
}

// 호스트 → 특정 플레이어에게 비밀(손패) 전송용 채널. 호스트만 publish, 해당 플레이어만 subscribe.
export async function joinPrivateChannel(roomCode, playerId, handlers = {}) {
  const sb = await getClient();
  if (!sb) return makeOfflineChannel();

  const channel = sb.channel(`dalmuti-room-${roomCode}-player-${playerId}`, {
    config: { broadcast: { self: false, ack: false } },
  });

  if (handlers.onBroadcast) {
    const events = ["private_hand", "tax_request"];
    for (const ev of events) {
      channel.on("broadcast", { event: ev }, (payload) => {
        handlers.onBroadcast(ev, payload.payload ?? payload);
      });
    }
  }

  await new Promise((resolve, reject) => {
    channel.subscribe((status) => {
      if (status === "SUBSCRIBED") resolve();
      else if (status === "CHANNEL_ERROR" || status === "TIMED_OUT") reject(new Error(status));
    });
  });

  return {
    online: true,
    broadcast: (event, payload) =>
      channel.send({ type: "broadcast", event, payload }),
    leave: () => channel.unsubscribe(),
  };
}

function makeOfflineChannel() {
  return {
    online: false,
    track: () => Promise.resolve(),
    untrack: () => Promise.resolve(),
    broadcast: () => Promise.resolve(),
    leave: () => Promise.resolve(),
  };
}
