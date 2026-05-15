/* ═══════════════════════════════════════════════════════════════
   horses.js — 숨은 유니콘 찾기 게임용 SVG 생성 모듈
   ─────────────────────────────────────────────────────────────
   • 외부 자산 의존 0개. 전부 SVG path로 동적 생성.
   • 향후 자산 교체 시 createHorse() 반환 형태(<g> 노드)만 유지하면 됨.
   • 좌표계: 각 말은 내부 60×40 단위로 그려짐. 외부에서 transform 적용.
   ═══════════════════════════════════════════════════════════════ */

(function () {
  'use strict';

  const SVG_NS = 'http://www.w3.org/2000/svg';

  // 말 몸체에 쓰이는 팔레트 (다크 배경 #2d2620 위에서 식별 가능한 밝은 톤만)
  // 어두운 색(밤색/갈색/검정/짙은 회색)은 배경과 동화되어 제외
  const PALETTES = [
    '#e8e0d0', // 백마 (크림)
    '#cfc1a8', // 옅은 베이지
    '#c9a063', // 황금색 (팔로미노)
    '#a89888', // 옅은 회색 (실버)
    '#d49560', // 살구 (밝은 소렐)
    '#d8a8b0', // 로제 (스트로베리)
    '#b8c0c8', // 라벤더 그레이
    '#eccc80'  // 연노랑
  ];

  // 갈기/꼬리 색 — 모든 body가 light 톤이므로 일률적으로 어두운 카카오 톤
  function maneColor(_body) {
    return '#5a4632';
  }

  // 유니콘 뿔 색 — 옅은 카키. 몸체와 살짝 대비되도록 (난이도 유지)
  function hornColor(_body) {
    return '#a89868';
  }

  function el(name, attrs) {
    const node = document.createElementNS(SVG_NS, name);
    if (attrs) {
      for (const k in attrs) {
        node.setAttribute(k, attrs[k]);
      }
    }
    return node;
  }

  /* ─────────────────────────────────────────────
     말 한 마리 생성
     반환: <g class="horse"> 노드 (transform 미적용)
     내부 좌표계: 0~60 가로, 0~40 세로
     ───────────────────────────────────────────── */
  function createHorse({ id, color, isUnicorn = false } = {}) {
    const body = color || PALETTES[0];
    const mane = maneColor(body);

    const g = el('g', {
      class: isUnicorn ? 'horse horse--unicorn' : 'horse',
      'data-id': String(id ?? ''),
      'data-unicorn': isUnicorn ? '1' : '0'
    });

    // 1) 투명 hit-zone — 모바일 터치 타깃 (시각 영역보다 넉넉히)
    g.appendChild(el('rect', {
      x: '0', y: '0', width: '60', height: '40',
      fill: 'transparent', class: 'hit-zone'
    }));

    // 2) 뒷다리 2개 (뒤가 먼저 그려져야 앞다리에 가려짐)
    g.appendChild(el('rect', { x: '10', y: '22', width: '4', height: '14', fill: body, rx: '1' }));
    g.appendChild(el('rect', { x: '17', y: '22', width: '4', height: '14', fill: body, rx: '1' }));

    // 3) 앞다리 2개
    g.appendChild(el('rect', { x: '36', y: '22', width: '4', height: '14', fill: body, rx: '1' }));
    g.appendChild(el('rect', { x: '43', y: '22', width: '4', height: '14', fill: body, rx: '1' }));

    // 4) 몸통 (타원)
    g.appendChild(el('ellipse', {
      cx: '28', cy: '20', rx: '20', ry: '9', fill: body
    }));

    // 5) 꼬리 (뒤쪽)
    g.appendChild(el('path', {
      d: 'M 8 18 Q 2 18 0 26 Q 4 22 8 22 Z',
      fill: mane
    }));

    // 6) 목 (몸통과 머리 연결)
    g.appendChild(el('path', {
      d: 'M 44 18 L 50 8 L 54 10 L 48 22 Z',
      fill: body
    }));

    // 7) 갈기 (목 위)
    g.appendChild(el('path', {
      d: 'M 44 14 Q 46 8 50 6 L 52 10 Q 48 14 46 18 Z',
      fill: mane
    }));

    // 8) 머리
    g.appendChild(el('ellipse', {
      cx: '53', cy: '10', rx: '6', ry: '4', fill: body
    }));

    // 9) 주둥이 (코끝, 약간 더 어둡게)
    g.appendChild(el('ellipse', {
      cx: '58', cy: '11', rx: '2.5', ry: '2', fill: body, opacity: '0.85'
    }));

    // 10) 귀 1개 — 머리 뒤쪽(왼쪽 윗부분)
    g.appendChild(el('path', {
      d: 'M 48 6 L 50 1 L 52 6 Z',
      fill: body
    }));

    // 11) 눈
    g.appendChild(el('circle', {
      cx: '55', cy: '9.5', r: '0.7', fill: '#000'
    }));

    // 12) 유니콘 뿔 — 앞쪽(이마 쪽)으로 이동, 더 크게
    if (isUnicorn) {
      g.appendChild(el('path', {
        d: 'M 53.5 5 L 54.8 -3 L 56 5 Z',
        fill: hornColor(body),
        stroke: '#a89668',
        'stroke-width': '0.25',
        class: 'horn'
      }));
    }

    return g;
  }

  /* ─────────────────────────────────────────────
     반짝이 효과 — 정답 클릭 시 부착
     반환: <g class="sparkle"> (animate 자동 시작)
     ───────────────────────────────────────────── */
  function createSparkle({ cx = 0, cy = 0, count = 8, duration = 1200 } = {}) {
    const g = el('g', { class: 'sparkle', transform: `translate(${cx}, ${cy})` });
    const dur = (duration / 1000).toFixed(2) + 's';

    // 중앙 빛
    const center = el('circle', { cx: '0', cy: '0', r: '0', fill: '#fff8c8' });
    center.appendChild(el('animate', {
      attributeName: 'r', values: '0;14;6', dur, fill: 'freeze'
    }));
    center.appendChild(el('animate', {
      attributeName: 'opacity', values: '1;1;0', dur, fill: 'freeze'
    }));
    g.appendChild(center);

    // 방사형 별 입자들
    for (let i = 0; i < count; i++) {
      const ang = (Math.PI * 2 * i) / count;
      const r = 18 + Math.random() * 6;
      const tx = (Math.cos(ang) * r).toFixed(1);
      const ty = (Math.sin(ang) * r).toFixed(1);

      // 4점 별 모양 path
      const star = el('path', {
        d: 'M 0 -2.5 L 0.8 -0.8 L 2.5 0 L 0.8 0.8 L 0 2.5 L -0.8 0.8 L -2.5 0 L -0.8 -0.8 Z',
        fill: i % 2 ? '#ffe66b' : '#fff8c8',
        transform: 'translate(0,0) scale(0)'
      });
      star.appendChild(el('animateTransform', {
        attributeName: 'transform',
        type: 'translate',
        values: `0 0; ${tx} ${ty}`,
        dur,
        additive: 'sum',
        fill: 'freeze'
      }));
      star.appendChild(el('animateTransform', {
        attributeName: 'transform',
        type: 'scale',
        values: '0; 1.4; 0',
        dur,
        additive: 'sum',
        fill: 'freeze'
      }));
      star.appendChild(el('animate', {
        attributeName: 'opacity',
        values: '1; 1; 0',
        dur,
        fill: 'freeze'
      }));
      g.appendChild(star);
    }

    return g;
  }

  window.HorsesArt = {
    PALETTES,
    createHorse,
    createSparkle,
    HORSE_W: 60,
    HORSE_H: 40
  };
})();
