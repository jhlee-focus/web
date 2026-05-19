"""SKZ 시계 색 팔레트 교체: Nachimbong 다크 → 5-STAR Cream.

기존: 다크 와인/네이비 배경 + 형광 빨강/노랑 — 6-7세에게 부담스러움.
신규: 따뜻한 크림·피치 배경 + 깊은 와인레드(#c62828) + 실버 시계 페이스 +
       앰버 액센트(#f9a825). SKZ 시그니처 빨강은 유지하되 가독성·친화성↑.
"""
from pathlib import Path

# (old, new, expected_min, description)
# 각 치환은 unique한 컨텍스트를 가지므로 단순 문자열 replace로 충분.
REPLACEMENTS = [
    # ===== 본문 배경 + 기본 색 =====
    (
        "    /* Nachimbong: 검정/네이비/와인 다크 그라디언트 */\n"
        "    background: linear-gradient(135deg, #0d0d1a 0%, #1a1a2e 30%, #2d1a2e 70%, #1a0d14 100%);\n"
        "    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;\n"
        "    color: #fff;",
        "    /* 5-STAR Cream: 따뜻한 크림·피치 그라디언트 (어린이 친화 + SKZ 빨강 유지) */\n"
        "    background: linear-gradient(135deg, #fff8f0 0%, #ffe9d6 25%, #ffd6b8 60%, #fce0d6 100%);\n"
        "    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;\n"
        "    color: #3d2010;",
        1, "body bg + text color"
    ),
    # ===== h1 (제목) =====
    (
        "  h1 {\n"
        "    color: #ff1744;\n"
        "    text-shadow: 0 0 12px rgba(255,23,68,0.45), 0 1px 3px rgba(0,0,0,0.6);\n"
        "    letter-spacing: 0.18em;\n"
        "  }",
        "  h1 {\n"
        "    color: #c62828;\n"
        "    text-shadow: 0 1px 2px rgba(255,255,255,0.6), 0 0 14px rgba(198,40,40,0.18);\n"
        "    letter-spacing: 0.18em;\n"
        "  }",
        1, "h1 title color"
    ),
    # ===== 시계 페이스 (Nachimbong 손잡이는 그대로 silver/white 유지 — light bg와 잘 어울림) =====
    (
        "    /* Nachimbong: 흰·실버 손잡이 */\n"
        "    background: radial-gradient(circle at 35% 35%, #ffffff 0%, #f5f5f5 30%, #cfd8dc 65%, #78909c 100%);\n"
        "    box-shadow:\n"
        "      0 0 0 calc(var(--s) * 0.013) rgba(213,0,0,0.55),\n"
        "      0 0 0 calc(var(--s) * 0.026) rgba(255,213,0,0.25),\n"
        "      0 calc(var(--s) * 0.013) calc(var(--s) * 0.053) rgba(0,0,0,0.5),\n"
        "      inset 0 0 calc(var(--s) * 0.1) rgba(120,144,156,0.25);",
        "    /* Nachimbong V2 흰·실버 손잡이 — 크림 배경 위에서 또렷한 대비 */\n"
        "    background: radial-gradient(circle at 35% 35%, #ffffff 0%, #fafafa 30%, #e8e8e8 65%, #c0c0c0 100%);\n"
        "    box-shadow:\n"
        "      0 0 0 calc(var(--s) * 0.013) rgba(198,40,40,0.5),\n"
        "      0 0 0 calc(var(--s) * 0.026) rgba(249,168,37,0.25),\n"
        "      0 calc(var(--s) * 0.013) calc(var(--s) * 0.053) rgba(0,0,0,0.15),\n"
        "      inset 0 0 calc(var(--s) * 0.1) rgba(80,80,80,0.18);",
        1, "clock-face gradient + ring shadow"
    ),
    # ===== hour-marker hover =====
    (
        "    filter: drop-shadow(0 4px 12px rgba(255,23,68,0.55));",
        "    filter: drop-shadow(0 4px 12px rgba(198,40,40,0.45));",
        1, "hour-marker hover glow"
    ),
    # ===== char-name (마커 호버 시 표시되는 라벨) =====
    (
        "    font-weight: 700; color: #ff1744;\n"
        "    white-space: nowrap; opacity: 0;\n"
        "    transition: opacity 0.3s ease;\n"
        "    text-shadow: 0 0 4px rgba(0,0,0,0.9), 0 0 8px rgba(0,0,0,0.7), 0 1px 2px rgba(0,0,0,0.8);",
        "    font-weight: 700; color: #c62828;\n"
        "    white-space: nowrap; opacity: 0;\n"
        "    transition: opacity 0.3s ease;\n"
        "    text-shadow: 0 0 4px #fff, 0 0 8px #fff, 0 0 14px rgba(255,255,255,0.85), 0 1px 2px rgba(80,40,20,0.3);",
        1, "char-name color + halo (light bg에 맞춰 흰색 글로우)"
    ),
    # ===== hour-number (시계 12자리 숫자) =====
    (
        "    color: rgba(33, 33, 33, 0.75);",
        "    color: rgba(80, 40, 20, 0.7);",
        1, "hour-number warm dark"
    ),
    # ===== hour-marker img drop-shadow =====
    (
        "    width: 100%; height: 100%; object-fit: contain;\n"
        "    filter: drop-shadow(0 2px 6px rgba(0,0,0,0.45));",
        "    width: 100%; height: 100%; object-fit: contain;\n"
        "    filter: drop-shadow(0 2px 6px rgba(80,40,20,0.25));",
        1, "marker image shadow (light bg)"
    ),
    # ===== hand-hour (시침: 깊은 빨강) =====
    (
        "  .hand-hour {\n"
        "    height: 22%;\n"
        "    background: linear-gradient(to top, #d50000, #ff5252);\n"
        "    box-shadow: 0 0 8px rgba(213,0,0,0.5);\n"
        "  }",
        "  .hand-hour {\n"
        "    height: 22%;\n"
        "    background: linear-gradient(to top, #c62828, #ef5350);\n"
        "    box-shadow: 0 0 8px rgba(198,40,40,0.4);\n"
        "  }",
        1, "hand-hour"
    ),
    # ===== hand-minute (분침: 따뜻한 차콜) =====
    (
        "  .hand-minute {\n"
        "    height: 30%;\n"
        "    background: linear-gradient(to top, #1a1a1a, #424242);\n"
        "    box-shadow: 0 0 6px rgba(0,0,0,0.5);\n"
        "  }",
        "  .hand-minute {\n"
        "    height: 30%;\n"
        "    background: linear-gradient(to top, #4a4a4a, #8a8a8a);\n"
        "    box-shadow: 0 0 6px rgba(74,74,74,0.35);\n"
        "  }",
        1, "hand-minute"
    ),
    # ===== hand-second (초침: 앰버, 네온 노랑 아님) =====
    (
        "  .hand-second {\n"
        "    height: 35%;\n"
        "    background: linear-gradient(to top, #ffd600, #ffeb3b);\n"
        "    box-shadow: 0 0 4px rgba(255,214,0,0.6);\n"
        "  }",
        "  .hand-second {\n"
        "    height: 35%;\n"
        "    background: linear-gradient(to top, #f9a825, #ffc107);\n"
        "    box-shadow: 0 0 4px rgba(249,168,37,0.5);\n"
        "  }",
        1, "hand-second amber"
    ),
    # ===== center-dot =====
    (
        "    background: radial-gradient(circle, #fff, #d50000);\n"
        "    box-shadow: 0 0 12px rgba(213,0,0,0.7);",
        "    background: radial-gradient(circle, #fff, #c62828);\n"
        "    box-shadow: 0 0 12px rgba(198,40,40,0.55);",
        1, "center-dot"
    ),
    # ===== digital-time =====
    (
        "  .digital-time {\n"
        "    font-weight: 700; color: #ff1744;\n"
        "    letter-spacing: 0.2em;\n"
        "    background: rgba(255,255,255,0.06);\n"
        "    border-radius: 999px;\n"
        "    backdrop-filter: blur(10px);\n"
        "    box-shadow: 0 2px 12px rgba(0,0,0,0.4), inset 0 0 0 1px rgba(255,23,68,0.3);\n"
        "  }",
        "  .digital-time {\n"
        "    font-weight: 700; color: #c62828;\n"
        "    letter-spacing: 0.2em;\n"
        "    background: rgba(255,255,255,0.55);\n"
        "    border-radius: 999px;\n"
        "    backdrop-filter: blur(10px);\n"
        "    box-shadow: 0 2px 12px rgba(80,40,20,0.12), inset 0 0 0 1px rgba(198,40,40,0.3);\n"
        "  }",
        1, "digital-time"
    ),
    # ===== credit (Stray Kids 라벨) =====
    (
        "    color: #ff1744; font-weight: 700; letter-spacing: 0.02em;\n"
        "    pointer-events: none; white-space: nowrap;\n"
        "    text-shadow: 0 1px 3px rgba(0,0,0,0.6);",
        "    color: #c62828; font-weight: 700; letter-spacing: 0.02em;\n"
        "    pointer-events: none; white-space: nowrap;\n"
        "    text-shadow: 0 1px 3px rgba(255,255,255,0.65);",
        1, "credit label"
    ),
    # ===== sparkle (작은 반짝임) =====
    (
        "    background: rgba(255,214,0,0.85);",
        "    background: rgba(255,180,90,0.8);",
        1, "sparkle warm"
    ),
    # ===== floating-heart opacity =====
    (
        "  .floating-heart {\n"
        "    position: fixed; opacity: 0.2;",
        "  .floating-heart {\n"
        "    position: fixed; opacity: 0.28;",
        1, "floating decoration opacity (light bg에서 살짝 강조)"
    ),
    (
        "    10% { opacity: 0.2; }\n"
        "    90% { opacity: 0.2; }",
        "    10% { opacity: 0.28; }\n"
        "    90% { opacity: 0.28; }",
        1, "floatUp keyframe opacity"
    ),
    # ===== hour-marker.active img glow =====
    (
        "    filter: drop-shadow(0 0 10px rgba(255,23,68,0.7)) drop-shadow(0 2px 6px rgba(0,0,0,0.45));",
        "    filter: drop-shadow(0 0 10px rgba(198,40,40,0.6)) drop-shadow(0 2px 6px rgba(80,40,20,0.25));",
        1, "active marker glow"
    ),
    # ===== heart-pulse ring =====
    (
        "    border: 2px solid rgba(255,23,68,0.55);",
        "    border: 2px solid rgba(198,40,40,0.45);",
        1, "heart-pulse ring"
    ),
    # ===== tick (시계 눈금) =====
    (
        "    background: rgba(33,33,33,0.4);",
        "    background: rgba(80,40,20,0.35);",
        1, "tick marks"
    ),
    # ===== mode-btn (normal + hover + active) =====
    (
        "  .mode-btn {\n"
        "    border: 2px solid rgba(255,23,68,0.4);\n"
        "    background: rgba(255,255,255,0.06);\n"
        "    color: #ff1744; font-weight: 700;",
        "  .mode-btn {\n"
        "    border: 2px solid rgba(198,40,40,0.4);\n"
        "    background: rgba(255,255,255,0.55);\n"
        "    color: #c62828; font-weight: 700;",
        1, "mode-btn"
    ),
    (
        "  .mode-btn:hover { background: rgba(255,23,68,0.15); }\n"
        "  .mode-btn.mode-active {\n"
        "    background: linear-gradient(135deg, #d50000, #ff5252);\n"
        "    color: #fff;\n"
        "    border-color: transparent;\n"
        "    box-shadow: 0 2px 12px rgba(213,0,0,0.55);\n"
        "  }",
        "  .mode-btn:hover { background: rgba(198,40,40,0.12); }\n"
        "  .mode-btn.mode-active {\n"
        "    background: linear-gradient(135deg, #c62828, #ef5350);\n"
        "    color: #fff;\n"
        "    border-color: transparent;\n"
        "    box-shadow: 0 4px 14px rgba(198,40,40,0.4);\n"
        "  }",
        1, "mode-btn hover + active"
    ),
    # ===== refresh-btn =====
    (
        "  .refresh-btn {\n"
        "    border: 2px solid rgba(255,214,0,0.4);\n"
        "    background: rgba(255,255,255,0.06);\n"
        "    color: #ffd600;",
        "  .refresh-btn {\n"
        "    border: 2px solid rgba(249,168,37,0.5);\n"
        "    background: rgba(255,255,255,0.55);\n"
        "    color: #f9a825;",
        1, "refresh-btn"
    ),
    (
        "  .refresh-btn:hover { background: rgba(255,214,0,0.18); transform: rotate(180deg); }",
        "  .refresh-btn:hover { background: rgba(249,168,37,0.18); transform: rotate(180deg); }",
        1, "refresh-btn hover"
    ),
    # ===== sort-tab (도감 sub-mode 토글) =====
    (
        "  .sort-tab {\n"
        "    border: 2px solid rgba(255,23,68,0.35);\n"
        "    background: rgba(255,255,255,0.06);\n"
        "    color: #ff1744;",
        "  .sort-tab {\n"
        "    border: 2px solid rgba(198,40,40,0.4);\n"
        "    background: rgba(255,255,255,0.6);\n"
        "    color: #c62828;",
        1, "sort-tab"
    ),
    (
        "  .sort-tab:hover { background: rgba(255,23,68,0.18); }\n"
        "  .sort-tab.active {\n"
        "    background: linear-gradient(135deg, #d50000, #ff5252);\n"
        "    color: #fff;\n"
        "    border-color: transparent;\n"
        "    box-shadow: 0 2px 8px rgba(213,0,0,0.55);\n"
        "  }",
        "  .sort-tab:hover { background: rgba(198,40,40,0.14); }\n"
        "  .sort-tab.active {\n"
        "    background: linear-gradient(135deg, #c62828, #ef5350);\n"
        "    color: #fff;\n"
        "    border-color: transparent;\n"
        "    box-shadow: 0 4px 12px rgba(198,40,40,0.4);\n"
        "  }",
        1, "sort-tab hover + active"
    ),
    # ===== dex-section-title =====
    (
        "  .dex-section-title {\n"
        "    font-weight: 800;\n"
        "    color: #ff1744;\n"
        "    font-size: 18px;\n"
        "    letter-spacing: 0.04em;\n"
        "    padding: 8px 12px 6px;\n"
        "    border-bottom: 2px solid rgba(255,23,68,0.35);\n"
        "    margin-bottom: 10px;\n"
        "    background: rgba(0,0,0,0.35);\n"
        "    backdrop-filter: blur(6px);\n"
        "    border-radius: 8px 8px 0 0;\n"
        "  }",
        "  .dex-section-title {\n"
        "    font-weight: 800;\n"
        "    color: #c62828;\n"
        "    font-size: 18px;\n"
        "    letter-spacing: 0.04em;\n"
        "    padding: 8px 12px 6px;\n"
        "    border-bottom: 2px solid rgba(198,40,40,0.4);\n"
        "    margin-bottom: 10px;\n"
        "    background: rgba(255,255,255,0.6);\n"
        "    backdrop-filter: blur(6px);\n"
        "    border-radius: 8px 8px 0 0;\n"
        "  }",
        1, "dex-section-title"
    ),
    # ===== dex-section-title .count =====
    (
        "  .dex-section-title .count {\n"
        "    color: #ffd600; font-weight: 600; font-size: 13px;\n"
        "    margin-left: 8px; opacity: 0.9;",
        "  .dex-section-title .count {\n"
        "    color: #b35900; font-weight: 600; font-size: 13px;\n"
        "    margin-left: 8px; opacity: 0.85;",
        1, "count text"
    ),
    # ===== dex-container scrollbar =====
    (
        "    scrollbar-color: rgba(255,23,68,0.3) transparent;\n"
        "  }\n"
        "  .dex-container::-webkit-scrollbar { width: 6px; }\n"
        "  .dex-container::-webkit-scrollbar-thumb { background: rgba(255,23,68,0.3); border-radius: 3px; }",
        "    scrollbar-color: rgba(198,40,40,0.35) transparent;\n"
        "  }\n"
        "  .dex-container::-webkit-scrollbar { width: 6px; }\n"
        "  .dex-container::-webkit-scrollbar-thumb { background: rgba(198,40,40,0.35); border-radius: 3px; }",
        1, "scrollbar"
    ),
    # ===== pair-card =====
    (
        "  .pair-card {\n"
        "    display: flex; align-items: center; gap: 8px;\n"
        "    padding: 10px;\n"
        "    background: rgba(0,0,0,0.35);\n"
        "    border: 1.5px solid rgba(255,23,68,0.28);\n"
        "    border-radius: 14px;\n"
        "    backdrop-filter: blur(6px);\n"
        "  }",
        "  .pair-card {\n"
        "    display: flex; align-items: center; gap: 8px;\n"
        "    padding: 10px;\n"
        "    background: rgba(255,255,255,0.55);\n"
        "    border: 1.5px solid rgba(198,40,40,0.3);\n"
        "    border-radius: 14px;\n"
        "    backdrop-filter: blur(6px);\n"
        "    box-shadow: 0 4px 14px rgba(80,40,20,0.08);\n"
        "  }",
        1, "pair-card"
    ),
    # ===== pair-side img shadow =====
    (
        "  .pair-card .pair-side img {\n"
        "    width: 96px; height: 96px; object-fit: contain;\n"
        "    filter: drop-shadow(0 2px 8px rgba(0,0,0,0.5));\n"
        "  }",
        "  .pair-card .pair-side img {\n"
        "    width: 96px; height: 96px; object-fit: contain;\n"
        "    filter: drop-shadow(0 2px 8px rgba(80,40,20,0.18));\n"
        "  }",
        1, "pair-side image shadow"
    ),
    # ===== pair-name =====
    (
        "  .pair-card .pair-side .pair-name {\n"
        "    font-weight: 700; color: #ffe5b3;\n"
        "    font-size: 13px; margin-top: 4px;",
        "  .pair-card .pair-side .pair-name {\n"
        "    font-weight: 700; color: #3d2010;\n"
        "    font-size: 13px; margin-top: 4px;",
        1, "pair-name text"
    ),
    # ===== pair-link arrow =====
    (
        "  .pair-card .pair-link {\n"
        "    font-size: 22px; color: #ff1744;\n"
        "    opacity: 0.7;",
        "  .pair-card .pair-link {\n"
        "    font-size: 22px; color: #c62828;\n"
        "    opacity: 0.75;",
        1, "pair-link arrow"
    ),
    # ===== dex-item (single grid item) =====
    (
        "  .dex-item {\n"
        "    display: flex; flex-direction: column;\n"
        "    align-items: center;\n"
        "    padding: 8px;\n"
        "    background: rgba(0,0,0,0.3);\n"
        "    border: 1.5px solid rgba(255,23,68,0.22);\n"
        "    border-radius: 14px;\n"
        "    cursor: pointer;\n"
        "    transition: all 0.2s ease;\n"
        "    backdrop-filter: blur(4px);\n"
        "  }",
        "  .dex-item {\n"
        "    display: flex; flex-direction: column;\n"
        "    align-items: center;\n"
        "    padding: 8px;\n"
        "    background: rgba(255,255,255,0.55);\n"
        "    border: 1.5px solid rgba(198,40,40,0.25);\n"
        "    border-radius: 14px;\n"
        "    cursor: pointer;\n"
        "    transition: all 0.2s ease;\n"
        "    backdrop-filter: blur(4px);\n"
        "    box-shadow: 0 3px 10px rgba(80,40,20,0.07);\n"
        "  }",
        1, "dex-item"
    ),
    # ===== dex-item hover =====
    (
        "  .dex-item:hover {\n"
        "    border-color: rgba(255,23,68,0.65);\n"
        "    background: rgba(213,0,0,0.16);\n"
        "    transform: translateY(-3px);\n"
        "    box-shadow: 0 6px 16px rgba(0,0,0,0.45);\n"
        "  }",
        "  .dex-item:hover {\n"
        "    border-color: rgba(198,40,40,0.6);\n"
        "    background: rgba(255,255,255,0.85);\n"
        "    transform: translateY(-3px);\n"
        "    box-shadow: 0 8px 22px rgba(198,40,40,0.18);\n"
        "  }",
        1, "dex-item hover"
    ),
    # ===== foundFlash (검색 점프 강조) =====
    (
        "  @keyframes foundFlash {\n"
        "    0% { box-shadow: 0 0 0 0 rgba(255,214,0,0.85); }\n"
        "    100% { box-shadow: 0 0 0 18px rgba(255,214,0,0); }\n"
        "  }",
        "  @keyframes foundFlash {\n"
        "    0% { box-shadow: 0 0 0 0 rgba(249,168,37,0.85); }\n"
        "    100% { box-shadow: 0 0 0 18px rgba(249,168,37,0); }\n"
        "  }",
        1, "foundFlash"
    ),
    # ===== dex-img-wrap img shadow =====
    (
        "  .dex-img-wrap img {\n"
        "    max-width: 100%; max-height: 100%;\n"
        "    object-fit: contain;\n"
        "    filter: drop-shadow(0 2px 8px rgba(0,0,0,0.45));\n"
        "  }",
        "  .dex-img-wrap img {\n"
        "    max-width: 100%; max-height: 100%;\n"
        "    object-fit: contain;\n"
        "    filter: drop-shadow(0 2px 8px rgba(80,40,20,0.18));\n"
        "  }",
        1, "dex-img-wrap img"
    ),
    # ===== dex-name (dex item label) =====
    (
        "  .dex-item .dex-name {\n"
        "    font-weight: 700; color: #ffe5b3;",
        "  .dex-item .dex-name {\n"
        "    font-weight: 700; color: #3d2010;",
        1, "dex-name"
    ),
    # ===== dex-en (italic English subtitle) =====
    (
        "  .dex-item .dex-en {\n"
        "    font-style: italic;\n"
        "    color: rgba(255,229,179,0.62);",
        "  .dex-item .dex-en {\n"
        "    font-style: italic;\n"
        "    color: rgba(80,40,20,0.55);",
        1, "dex-en"
    ),
    # ===== overlay backdrop (어두운 배경 유지하되 따뜻한 톤) =====
    (
        "  .dex-overlay {\n"
        "    position: fixed; inset: 0;\n"
        "    background: rgba(0,0,0,0.82);",
        "  .dex-overlay {\n"
        "    position: fixed; inset: 0;\n"
        "    background: rgba(40,20,10,0.82);",
        1, "overlay backdrop warm dark"
    ),
    # ===== overlay img filter =====
    (
        "  .dex-overlay img {\n"
        "    max-width: 42vmin; max-height: 42vmin;\n"
        "    object-fit: contain;\n"
        "    filter: drop-shadow(0 6px 24px rgba(255,23,68,0.3)) drop-shadow(0 4px 16px rgba(0,0,0,0.6));",
        "  .dex-overlay img {\n"
        "    max-width: 42vmin; max-height: 42vmin;\n"
        "    object-fit: contain;\n"
        "    filter: drop-shadow(0 6px 24px rgba(198,40,40,0.35)) drop-shadow(0 4px 16px rgba(0,0,0,0.5));",
        1, "overlay img glow"
    ),
    # ===== dex-overlay-name (어두운 backdrop 위 — light text) =====
    (
        "  .dex-overlay-name {\n"
        "    color: #ff1744; font-weight: 800; margin-top: 14px;",
        "  .dex-overlay-name {\n"
        "    color: #ff8a80; font-weight: 800; margin-top: 14px;",
        1, "overlay name (light text on warm-dark bg)"
    ),
    # ===== info-chip 각 종류 (overlay backdrop이 어둡기 때문에 칩 색은 비비드 유지) =====
    (
        "  .info-chip.kind-멤버  { background: linear-gradient(135deg, #d50000, #ff5252); }\n"
        "  .info-chip.kind-SKZOO { background: linear-gradient(135deg, #fbc02d, #ffd600); color: #1a1a1a; }\n"
        "  .info-chip.role       { background: linear-gradient(135deg, #424242, #757575); }\n"
        "  .info-chip.species    { background: linear-gradient(135deg, #6a1b9a, #ce93d8); }\n"
        "  .info-chip.origin     { background: linear-gradient(135deg, #1565c0, #64b5f6); }\n"
        "  .info-chip.year       { background: linear-gradient(135deg, #00838f, #4dd0e1); }",
        "  .info-chip.kind-멤버  { background: linear-gradient(135deg, #c62828, #ef5350); }\n"
        "  .info-chip.kind-SKZOO { background: linear-gradient(135deg, #f9a825, #ffc107); color: #3d2010; }\n"
        "  .info-chip.role       { background: linear-gradient(135deg, #5d4037, #8d6e63); }\n"
        "  .info-chip.species    { background: linear-gradient(135deg, #6a1b9a, #ce93d8); }\n"
        "  .info-chip.origin     { background: linear-gradient(135deg, #1565c0, #64b5f6); }\n"
        "  .info-chip.year       { background: linear-gradient(135deg, #00838f, #4dd0e1); }",
        1, "info-chip colors"
    ),
    # ===== pair-link-row button =====
    (
        "  .pair-link-row button {\n"
        "    border: 1.5px solid rgba(255,23,68,0.5);\n"
        "    background: rgba(213,0,0,0.18);\n"
        "    color: #ff5252;",
        "  .pair-link-row button {\n"
        "    border: 1.5px solid rgba(198,40,40,0.55);\n"
        "    background: rgba(198,40,40,0.18);\n"
        "    color: #ffab91;",
        1, "pair-link-row button"
    ),
    (
        "  .pair-link-row button:hover {\n"
        "    background: rgba(213,0,0,0.45);\n"
        "    color: #fff;\n"
        "  }",
        "  .pair-link-row button:hover {\n"
        "    background: rgba(198,40,40,0.45);\n"
        "    color: #fff;\n"
        "  }",
        1, "pair-link-row button hover"
    ),
    # ===== dex-search-input =====
    (
        "  .dex-search-input {\n"
        "    flex: 1;\n"
        "    padding: 10px 16px;\n"
        "    border: 2px solid rgba(255,23,68,0.4);\n"
        "    background: rgba(255,255,255,0.06);\n"
        "    color: #fff;\n"
        "    border-radius: 999px;\n"
        "    font-size: 14px;\n"
        "    outline: none;\n"
        "    backdrop-filter: blur(10px);\n"
        "    transition: border-color 0.2s ease;\n"
        "  }\n"
        "  .dex-search-input::placeholder { color: rgba(255,255,255,0.45); }\n"
        "  .dex-search-input:focus { border-color: rgba(255,23,68,0.85); }\n"
        "  .dex-search-input.error { border-color: #ff1744; background: rgba(255,23,68,0.18); }",
        "  .dex-search-input {\n"
        "    flex: 1;\n"
        "    padding: 10px 16px;\n"
        "    border: 2px solid rgba(198,40,40,0.4);\n"
        "    background: rgba(255,255,255,0.72);\n"
        "    color: #3d2010;\n"
        "    border-radius: 999px;\n"
        "    font-size: 14px;\n"
        "    outline: none;\n"
        "    backdrop-filter: blur(10px);\n"
        "    transition: border-color 0.2s ease;\n"
        "  }\n"
        "  .dex-search-input::placeholder { color: rgba(80,40,20,0.48); }\n"
        "  .dex-search-input:focus { border-color: rgba(198,40,40,0.85); }\n"
        "  .dex-search-input.error { border-color: #c62828; background: rgba(198,40,40,0.16); }",
        1, "dex-search-input"
    ),
    # ===== dex-search-msg =====
    (
        "  .dex-search-msg {\n"
        "    margin-left: 8px;\n"
        "    color: #ff5252;",
        "  .dex-search-msg {\n"
        "    margin-left: 8px;\n"
        "    color: #c62828;",
        1, "dex-search-msg"
    ),
    # ===== dex-search-btn =====
    (
        "  .dex-search-btn {\n"
        "    width: 38px; height: 38px;\n"
        "    border: 0; border-radius: 50%;\n"
        "    background: linear-gradient(135deg, #d50000, #ff5252);\n"
        "    color: #fff; font-weight: 700;",
        "  .dex-search-btn {\n"
        "    width: 38px; height: 38px;\n"
        "    border: 0; border-radius: 50%;\n"
        "    background: linear-gradient(135deg, #c62828, #ef5350);\n"
        "    color: #fff; font-weight: 700;\n"
        "    box-shadow: 0 4px 12px rgba(198,40,40,0.35);",
        1, "dex-search-btn"
    ),
    # ===== home-btn =====
    (
        "  .home-btn {\n"
        "    position: fixed; top: 14px; left: 14px;\n"
        "    z-index: 100;\n"
        "    border: 2px solid rgba(255,214,0,0.45);\n"
        "    background: rgba(255,255,255,0.06);\n"
        "    color: #ffd600; font-weight: 700;",
        "  .home-btn {\n"
        "    position: fixed; top: 14px; left: 14px;\n"
        "    z-index: 100;\n"
        "    border: 2px solid rgba(249,168,37,0.55);\n"
        "    background: rgba(255,255,255,0.72);\n"
        "    color: #c62828; font-weight: 700;",
        1, "home-btn"
    ),
    (
        "  .home-btn:hover { background: rgba(255,214,0,0.18); }",
        "  .home-btn:hover { background: rgba(249,168,37,0.2); }",
        1, "home-btn hover"
    ),
]


def main():
    p = Path("skz.html")
    src = p.read_text(encoding="utf-8")
    out = src
    applied = 0
    for old, new, expected_min, desc in REPLACEMENTS:
        count = out.count(old)
        if count < expected_min:
            print(f"  !! NO MATCH ({count} < {expected_min}): {desc}")
            continue
        out = out.replace(old, new)
        applied += 1
        print(f"  ok: {desc}")
    p.write_text(out, encoding="utf-8")
    print()
    print(f"applied {applied}/{len(REPLACEMENTS)} replacements")
    print(f"new file size: {len(out)} chars")


if __name__ == "__main__":
    main()
