// 4명 AI 자동 시뮬레이션. game.js + aiPlayer.js 검증용.
// 실행: node dalmuti/test/sim.mjs

import {
  createInitialState,
  startNewRound,
  validatePlay,
  applyPlay,
  applyPass,
  finishTaxPhase,
  computeRanks,
  RANK_TITLE,
} from "../js/game.js";
import { chooseAction } from "../js/aiPlayer.js";
import { rankLabel, JESTER } from "../js/cards.js";

function fmtCards(cards) {
  return cards.map((c) => (c === JESTER ? "J" : String(c))).join(",");
}

function sim(playerCount = 4, rounds = 3, verbose = false) {
  const players = Array.from({ length: playerCount }, (_, i) => ({
    id: `ai-${i + 1}`,
    nickname: `AI-${i + 1}`,
    isAI: true,
  }));

  let state = createInitialState(players);

  for (let r = 0; r < rounds; r++) {
    state = startNewRound(state);

    // 세금 단계 자동 처리 (2라운드부터)
    if (state.phase === "tax") {
      // dalmutiPicks 비워두면 자동
      state = finishTaxPhase(state);
    }

    // 플레이 단계 — 모두 finished 가 될 때까지
    let safety = 0;
    while (state.phase === "play") {
      safety++;
      if (safety > 5000) {
        throw new Error("infinite loop in play phase");
      }
      const turn = state.currentTurn;
      if (!turn) {
        console.error(`R${state.round} step ${safety}: currentTurn is null/undefined`);
        console.error(`finishedOrder=${state.finishedOrder.join(",")}`);
        console.error(`seatOrder=${state.seatOrder.join(",")}`);
        console.error(`trick=`, state.currentTrick);
        for (const p of state.players) {
          console.error(`  ${p.id}: hand=[${fmtCards(p.hand)}] (${p.hand.length} cards)`);
        }
        throw new Error("null currentTurn");
      }
      const action = chooseAction(state, turn);
      if (action.type === "play") {
        const v = validatePlay(state, turn, action.cards);
        if (!v.ok) {
          console.error(
            `INVALID PLAY by ${turn}: cards=[${fmtCards(action.cards)}] reason=${v.reason}`,
          );
          console.error(`hand=[${fmtCards(state.players.find((p) => p.id === turn).hand)}]`);
          console.error(`trick=`, state.currentTrick);
          throw new Error("invalid AI play");
        }
        if (verbose) {
          console.log(`R${state.round}: ${turn} plays [${fmtCards(action.cards)}]`);
        }
        state = applyPlay(state, turn, action.cards);
      } else {
        const result = applyPass(state, turn);
        if (!result.ok) {
          // 리드인데 패스 시도 → 강제로 한 장 내기 (AI 버그 방지)
          const player = state.players.find((p) => p.id === turn);
          const fallback = [player.hand[player.hand.length - 1]];
          if (verbose) console.log(`R${state.round}: ${turn} forced play [${fmtCards(fallback)}]`);
          state = applyPlay(state, turn, fallback);
        } else {
          if (verbose) console.log(`R${state.round}: ${turn} passes`);
          state = result.state;
        }
      }
    }

    // 라운드 종료 결과
    const ranks = computeRanks(state.finishedOrder);
    console.log(`Round ${state.round} finished:`);
    state.finishedOrder.forEach((pid, idx) => {
      console.log(`  ${idx + 1}. ${pid} → ${RANK_TITLE[ranks[pid]] ?? "Merchant"}`);
    });
  }
  console.log("\n✓ simulation completed without errors");
}

const args = process.argv.slice(2);
const playerCount = parseInt(args[0]) || 4;
const rounds = parseInt(args[1]) || 3;
const verbose = args.includes("-v");
sim(playerCount, rounds, verbose);
