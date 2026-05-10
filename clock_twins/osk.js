// On-screen keyboard with Hangul IME
// Shared module for clock_twins/{teenieping,pokemon}.html dex search.
// Logic mirrors teenieping_dessert/index.html but generalized:
//   OnScreenKeyboard.attach({ input, oskRoot, onCommit, onChange })
(function(global) {
  'use strict';

  // ── Hangul IME (jamo composer) ────────────────────────────────────────────
  var HangulIME = (function() {
    var CHO  = ['ㄱ','ㄲ','ㄴ','ㄷ','ㄸ','ㄹ','ㅁ','ㅂ','ㅃ','ㅅ','ㅆ','ㅇ','ㅈ','ㅉ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ'];
    var JUNG = ['ㅏ','ㅐ','ㅑ','ㅒ','ㅓ','ㅔ','ㅕ','ㅖ','ㅗ','ㅘ','ㅙ','ㅚ','ㅛ','ㅜ','ㅝ','ㅞ','ㅟ','ㅠ','ㅡ','ㅢ','ㅣ'];
    var JONG = ['','ㄱ','ㄲ','ㄳ','ㄴ','ㄵ','ㄶ','ㄷ','ㄹ','ㄺ','ㄻ','ㄼ','ㄽ','ㄾ','ㄿ','ㅀ','ㅁ','ㅂ','ㅄ','ㅅ','ㅆ','ㅇ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ'];
    var VOWEL_COMBOS = {'ㅗㅏ':'ㅘ','ㅗㅐ':'ㅙ','ㅗㅣ':'ㅚ','ㅜㅓ':'ㅝ','ㅜㅔ':'ㅞ','ㅜㅣ':'ㅟ','ㅡㅣ':'ㅢ'};
    var JONG_COMBOS  = {'ㄱㅅ':'ㄳ','ㄴㅈ':'ㄵ','ㄴㅎ':'ㄶ','ㄹㄱ':'ㄺ','ㄹㅁ':'ㄻ','ㄹㅂ':'ㄼ','ㄹㅅ':'ㄽ','ㄹㅌ':'ㄾ','ㄹㅍ':'ㄿ','ㄹㅎ':'ㅀ','ㅂㅅ':'ㅄ'};
    var JONG_SPLIT   = {};
    Object.keys(JONG_COMBOS).forEach(function(k) { JONG_SPLIT[JONG_COMBOS[k]] = [k[0], k[1]]; });

    var buf = { cho: -1, jung: -1, jong: 0 };
    var baseValue = '';

    function isCho(j)  { return CHO.indexOf(j) !== -1; }
    function isJung(j) { return JUNG.indexOf(j) !== -1; }

    function compose() {
      if (buf.cho < 0) return '';
      if (buf.jung < 0) return CHO[buf.cho];
      return String.fromCharCode(0xAC00 + buf.cho * 588 + buf.jung * 28 + buf.jong);
    }

    function reset() {
      buf = { cho: -1, jung: -1, jong: 0 };
      baseValue = '';
    }

    function input(jamo, inputEl) {
      if (buf.cho < 0 && buf.jung < 0 && buf.jong === 0) {
        baseValue = inputEl.value;
      }
      if (isCho(jamo)) {
        if (buf.cho < 0) {
          buf.cho = CHO.indexOf(jamo);
        } else if (buf.jung < 0) {
          baseValue += CHO[buf.cho];
          buf = { cho: CHO.indexOf(jamo), jung: -1, jong: 0 };
        } else if (buf.jong === 0) {
          var idx = JONG.indexOf(jamo);
          if (idx > 0) {
            buf.jong = idx;
          } else {
            baseValue += compose();
            buf = { cho: CHO.indexOf(jamo), jung: -1, jong: 0 };
          }
        } else {
          var cur = JONG[buf.jong];
          var combo = JONG_COMBOS[cur + jamo];
          if (combo) {
            buf.jong = JONG.indexOf(combo);
          } else {
            baseValue += compose();
            buf = { cho: CHO.indexOf(jamo), jung: -1, jong: 0 };
          }
        }
      } else if (isJung(jamo)) {
        if (buf.cho < 0) {
          baseValue += jamo;
        } else if (buf.jung < 0) {
          buf.jung = JUNG.indexOf(jamo);
        } else if (buf.jong === 0) {
          var curV = JUNG[buf.jung];
          var comboV = VOWEL_COMBOS[curV + jamo];
          if (comboV) {
            buf.jung = JUNG.indexOf(comboV);
          } else {
            baseValue += compose();
            buf = { cho: -1, jung: -1, jong: 0 };
            baseValue += jamo;
          }
        } else {
          var jongChar = JONG[buf.jong];
          var split = JONG_SPLIT[jongChar];
          if (split) {
            buf.jong = JONG.indexOf(split[0]);
            baseValue += compose();
            buf = { cho: CHO.indexOf(split[1]), jung: JUNG.indexOf(jamo), jong: 0 };
          } else {
            var moveCho = jongChar;
            buf.jong = 0;
            baseValue += compose();
            buf = { cho: CHO.indexOf(moveCho), jung: JUNG.indexOf(jamo), jong: 0 };
          }
        }
      } else {
        baseValue += compose();
        buf = { cho: -1, jung: -1, jong: 0 };
        baseValue += jamo;
      }
      inputEl.value = baseValue + compose();
    }

    function backspace(inputEl) {
      if (buf.jong > 0) {
        var cur = JONG[buf.jong];
        var split = JONG_SPLIT[cur];
        buf.jong = split ? JONG.indexOf(split[0]) : 0;
      } else if (buf.jung >= 0) {
        var curV = JUNG[buf.jung];
        var rev = null;
        Object.keys(VOWEL_COMBOS).forEach(function(k) { if (VOWEL_COMBOS[k] === curV) rev = k; });
        if (rev) buf.jung = JUNG.indexOf(rev[0]);
        else buf.jung = -1;
      } else if (buf.cho >= 0) {
        buf.cho = -1;
      } else if (baseValue.length > 0) {
        baseValue = baseValue.slice(0, -1);
      }
      inputEl.value = baseValue + compose();
    }

    function commit(inputEl) {
      baseValue += compose();
      buf = { cho: -1, jung: -1, jong: 0 };
      inputEl.value = baseValue;
    }

    function syncFromInput(inputEl) {
      buf = { cho: -1, jung: -1, jong: 0 };
      baseValue = inputEl.value;
    }

    return { input: input, backspace: backspace, commit: commit, reset: reset, syncFromInput: syncFromInput };
  })();

  // ── Layouts ────────────────────────────────────────────────────────────────
  var OSK_LAYOUTS = {
    ko: [
      ['ㅂ','ㅈ','ㄷ','ㄱ','ㅅ','ㅛ','ㅕ','ㅑ','ㅐ','ㅔ'],
      ['ㅁ','ㄴ','ㅇ','ㄹ','ㅎ','ㅗ','ㅓ','ㅏ','ㅣ'],
      ['SHIFT','ㅋ','ㅌ','ㅊ','ㅍ','ㅠ','ㅜ','ㅡ','BACK'],
      ['MODE','SPACE','NEXT','CLEAR','OK']
    ],
    ko_shift: [
      ['ㅃ','ㅉ','ㄸ','ㄲ','ㅆ','ㅛ','ㅕ','ㅑ','ㅒ','ㅖ'],
      ['ㅁ','ㄴ','ㅇ','ㄹ','ㅎ','ㅗ','ㅓ','ㅏ','ㅣ'],
      ['SHIFT','ㅋ','ㅌ','ㅊ','ㅍ','ㅠ','ㅜ','ㅡ','BACK'],
      ['MODE','SPACE','NEXT','CLEAR','OK']
    ],
    en: [
      ['q','w','e','r','t','y','u','i','o','p'],
      ['a','s','d','f','g','h','j','k','l'],
      ['z','x','c','v','b','n','m','BACK'],
      ['MODE','SPACE','NEXT','CLEAR','OK']
    ]
  };

  function attach(opts) {
    var input     = opts.input;
    var oskRoot   = opts.oskRoot;
    var onCommit  = opts.onCommit  || function() {};
    var onChange  = opts.onChange  || function() {};
    var onDismiss = opts.onDismiss || null;

    var oskMode = 'ko';
    var oskShift = false;

    function buildOSK() {
      oskRoot.innerHTML = '';
      // 우상단 닫기 버튼 (onDismiss가 주어진 경우)
      if (onDismiss) {
        var dismissBtn = document.createElement('button');
        dismissBtn.type = 'button';
        dismissBtn.className = 'osk-dismiss';
        dismissBtn.textContent = '✕';
        dismissBtn.setAttribute('aria-label', '키보드 닫기');
        dismissBtn.addEventListener('mousedown', function(e) { e.preventDefault(); });
        dismissBtn.addEventListener('click', function(e) { e.preventDefault(); onDismiss(); });
        oskRoot.appendChild(dismissBtn);
      }
      var layoutKey = oskMode === 'ko' && oskShift ? 'ko_shift' : oskMode;
      var layout = OSK_LAYOUTS[layoutKey];
      layout.forEach(function(row) {
        var rowEl = document.createElement('div');
        rowEl.className = 'osk-row';
        row.forEach(function(k) {
          var btn = document.createElement('button');
          btn.type = 'button';
          btn.className = 'osk-key';
          if (k === 'SPACE')      { btn.classList.add('wide');           btn.textContent = '스페이스'; }
          else if (k === 'BACK')  { btn.classList.add('wide');           btn.textContent = '⌫'; }
          else if (k === 'OK')    { btn.classList.add('wide','action');  btn.textContent = '확인'; }
          else if (k === 'MODE')  { btn.classList.add('wide');           btn.textContent = oskMode === 'ko' ? '한/영' : 'KO/EN'; }
          else if (k === 'CLEAR') { btn.classList.add('wide');           btn.textContent = '지우기'; }
          else if (k === 'SHIFT') { btn.classList.add('wide');           btn.textContent = oskShift ? '⇧ ON' : '⇧'; }
          else if (k === 'NEXT')  { btn.classList.add('wide');           btn.textContent = '다음 ▶'; }
          else                    {                                       btn.textContent = k; }
          // input focus를 빼앗기지 않도록 mousedown에서 default 차단
          btn.addEventListener('mousedown', function(e) { e.preventDefault(); });
          btn.addEventListener('click', function(e) {
            e.preventDefault();
            handleKey(k);
          });
          rowEl.appendChild(btn);
        });
        oskRoot.appendChild(rowEl);
      });
    }

    function handleKey(k) {
      if (k === 'SPACE') { HangulIME.commit(input); input.value += ' '; HangulIME.syncFromInput(input); onChange(input.value); return; }
      if (k === 'BACK')  { HangulIME.backspace(input); onChange(input.value); return; }
      if (k === 'CLEAR') { HangulIME.reset(); input.value = ''; onChange(input.value); return; }
      if (k === 'OK')    { HangulIME.commit(input); onCommit(input.value); return; }
      if (k === 'MODE')  { oskMode = oskMode === 'ko' ? 'en' : 'ko'; oskShift = false; HangulIME.commit(input); buildOSK(); onChange(input.value); return; }
      if (k === 'SHIFT') { oskShift = !oskShift; buildOSK(); return; }
      if (k === 'NEXT')  { HangulIME.commit(input); onChange(input.value); return; }

      if (oskMode === 'ko') {
        HangulIME.input(k, input);
      } else {
        HangulIME.commit(input);
        input.value += k;
      }
      onChange(input.value);
      // 한 번 켠 SHIFT는 자모 한 글자 입력 후 자동 해제 (한국어 OSK 일반 동작)
      if (oskShift) {
        oskShift = false;
        buildOSK();
      }
    }

    // 외부(물리 키보드/시스템 IME/붙여넣기)에서 input이 바뀌면 IME 버퍼 동기화.
    // Enter 키는 의도적으로 처리하지 않는다 — 호출 측에서 자체 keydown으로 onCommit을 트리거.
    input.addEventListener('input', function() {
      HangulIME.syncFromInput(input);
      onChange(input.value);
    });

    buildOSK();

    return {
      reset: function() { HangulIME.reset(); input.value = ''; },
      sync: function() { HangulIME.syncFromInput(input); },
      rebuild: buildOSK
    };
  }

  global.OnScreenKeyboard = { attach: attach };
})(window);
