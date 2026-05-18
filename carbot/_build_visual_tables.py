"""
카봇 시각화 (표 버전) — HTML 재생성 전용.
1. 개별 로봇 전체 표 (1개)
2. 합체 로봇별 멤버 표 (합체로봇 1개 = 표 1개)
"""
import hashlib
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).parent
SRC  = BASE / "img_carbot_src"

# ─────────────────────────────────────────────────────────────────────────
# 개별 로봇 데이터 (hello_carbot_robots.md 기반)
# ─────────────────────────────────────────────────────────────────────────

# (이름, 시즌, 분류, 비고)
STANDALONE_ROBOTS = [
    # ★ 나무위키 전수 검증 결과 (2026-05-18): 86종 중 12종이 멤버로 확인됨 → 제거
    # 제거된 12종은 COMBO_ROBOTS 의 해당 합체 멤버 항목에 반영됨

    # 시즌 1
    ("카봇 호크",         "1",   "정규",         "차탄의 첫 카봇. 펜타스톰에 합체 안 함 (차탄 호위)"),
    # 시즌 2
    ("카봇 트루",         "2",   "정규",         "미래 카봇"),
    ("카봇 본",           "2",   "정규",         ""),
    # 시즌 3
    ("카봇 우가바",       "3",   "미래 카봇",     ""),
    ("카봇 골드렉스",     "3",   "미래 카봇",     ""),
    ("카봇 제트렌",       "3",   "미래 카봇",     ""),
    ("카봇 킹가이즈",     "3",   "미래 카봇",     ""),
    # 시즌 5 — [REMOVED] 빌디언/크랜/듀크 → 카봇 하이퍼빌디언 멤버
    ("카봇 비트런",       "5",   "오토봇",       "원액션 변신"),
    ("카봇 메가볼드",     "5",   "오토봇",       "원액션 변신"),
    ("카봇 오토소닉",     "5",   "오토봇",       "원액션 변신"),
    # 시즌 6
    ("카봇 아이언트",     "6",   "크루",         "엔지니어 크루 (파트너십, 합체 아님)"),
    ("카봇 컨버스터",     "6",   "오토봇",       ""),
    ("카봇 아이누크",     "6",   "크루",         "레스큐 크루"),
    ("카봇 스타피너",     "6",   "오토봇",       ""),
    # 시즌 7
    ("카봇 스피너블",     "7",   "정규",         ""),
    ("카봇 버디가드",     "7",   "정규",         ""),
    ("카봇 유니크루저",   "7",   "크루저",       "파일럿 크루. 변신 불가"),
    ("카봇 제트크루저",   "7",   "크루저",       "크루 에어"),
    ("카봇 메디언트",     "7",   "크루",         "엠뷸런스 크루"),
    ("카봇 파이언트",     "7",   "크루",         "119 크루"),
    ("카봇 라이캅스",     "7",   "크루",         "크루 기동대"),
    ("카봇 앵그리퍼프",   "7",   "크루",         "크루 워커"),
    # 시즌 8
    ("카봇 테크노마스터", "8",   "정규",         ""),
    # 시즌 9
    ("카봇 파워크루저",   "9",   "크루저",       "크루 파워"),
    ("카봇 모:반",        "9",   "정규",         ""),
    ("카봇 울티맥스",     "9",   "정규",         ""),
    # 시즌 10
    ("카봇 마이티로",     "10",  "정규",         ""),
    # 시즌 11 쌈바
    ("카봇 저스포스",     "11",  "쌈바",         "파트너: 폴리독 (합체 아님)"),
    ("카봇 레드와일러",   "11",  "쌈바",         "파트너: 롱고"),
    ("카봇 나이트호퍼",   "11",  "쌈바",         "파트너: 앰뷰버드. 여성형"),
    ("카봇 맥스도저",     "11",  "쌈바",         "파트너: 맥스릴라"),
    ("카봇 샌드버스터",   "11",  "쌈바",         "파트너: 와일리온"),
    ("카봇 록캔",         "11",  "쌈바",         "파트너: 아쿠아리노"),
    # 시즌 11 하이더
    ("카봇 베어하이더",   "11",  "하이더",       "곰형 비스트"),
    ("카봇 이글하이더",   "11",  "하이더",       "독수리형 비스트"),
    # 시즌 12 붐바
    ("카봇 스크류붐바",   "12",  "붐바",         ""),
    ("카봇 파워붐바",     "12",  "붐바",         ""),
    ("카봇 드릴버스트",   "12",  "쌈바",         "파트너: 몰리켓"),
    ("카봇 스톰다이버",   "12",  "쌈바",         "파트너: 롤링크록"),
    ("카봇 라란자",       "12",  "정규",         "여성형. 호크의 여친"),
    # 시즌 12 밤밤
    ("카봇 도저밤밤",     "12",  "밤밤",         "카봇붐 변형 시스템"),
    ("카봇 레미밤밤",     "12",  "밤밤",         ""),
    ("카봇 아레스밤밤",   "12",  "밤밤",         ""),
    ("카봇 포레밤밤",     "12",  "밤밤",         "여성형"),
    ("카봇 큐어밤밤",     "12",  "밤밤",         "여성형"),
    # 시즌 13 젬 — [REMOVED] 윙버드젬 (다른 젬 시리즈와 합체)
    ("카봇 디고베어젬",   "13",  "젬",           "= 디고베어 + 디고베어카. 곰형 비스트"),
    ("카봇 토터젬",       "13",  "젬",           "= 토터 + 토터카"),
    ("카봇 톡시젬",       "13",  "젬",           "인피니툴. 여성형"),
    ("카봇 스나이퍼젬",   "13",  "젬",           "인피니툴"),
    ("카봇 캥복스젬",     "13",  "젬",           "인피니툴"),
    ("카봇 로어젬",       "13",  "젬",           "인피니툴"),
    ("카봇 레포스",       "13",  "정규",         "여성형"),
    ("카봇 일렉트롬",     "13",  "정규",         ""),
    # 시즌 14 — [REMOVED] 라이프 X → 펜타스톰 X 라이프 캐논 모드 멤버
    ("카봇 빅터",         "14",  "정규",         ""),
    ("카봇 티라쿵",       "14",  "알카봇 쿵",    ""),
    # 시즌 15
    ("카봇 펀치마스터",   "15",  "정규",         ""),
    ("카봇 호프",         "15",  "정규",         ""),
    # 시즌 16 — [REMOVED] 캐논 X → 그랜드 카봇 GX 멤버
    ("카봇 하이드",       "16",  "마법사",       "용사로 분류되지 않음"),
    # 시즌 17 — [REMOVED] 빅포트, EV 커맨더 → 카봇 울트라포트 멤버
    # 극장판 1기 (백악기)
    ("카봇 티라클레스",   "극장판 1기", "백악기", "티라노사우루스. 불 속성"),
    ("카봇 트리톤",       "극장판 1기", "백악기", "공룡형. 물 속성"),
    ("카봇 테라제트",     "극장판 1기", "백악기", "공룡형 여성형. 바람 속성"),
    ("카봇 테고",         "극장판 1기", "백악기", "공룡형. 땅 속성"),
    # 극장판 2기 (옴파로스) — [REMOVED] 크라이언/티라투스/코어 → 카봇 티라이오 멤버
    ("카봇 에이샤크",     "극장판 2기", "옴파로스 섬", "상어형 비스트. 여성형"),
    ("카봇 팔로",         "극장판 2기", "옴파로스 섬", "아프리카물소형. 트리플 체인저 (역대 유일)"),
    ("카봇 마이모스",     "극장판 2기", "옴파로스 섬", "비스트"),
    # 극장판 4기
    ("카봇 그린팜",       "극장판 4기", "극장판",   "여성형"),
    ("카봇 스카이거너",   "극장판",     "극장판",   "항공기"),
    ("카봇 소나다이버",   "극장판",     "극장판",   "잠수정"),
    # 알카봇 (쿵)
    ("피노쿵",            "쿵 시리즈", "알카봇",   "여성형"),
    ("아르케쿵",          "쿵 시리즈", "알카봇",   "여성형"),
    ("디메트로쿵",        "쿵 시리즈", "알카봇",   "여성형"),
    ("파키케쿵",          "쿵 시리즈", "알카봇",   "여성형"),
    ("람포린",            "쿵 시리즈", "알카봇",   "여성형"),
    # 유니티 (메카드 콜라보) — [REMOVED] 미리내프라임 → 에반 프라임 멤버
    ("라고",              "유니티",   "유니티",   "메카드 콜라보. 여성형"),
]


# ─────────────────────────────────────────────────────────────────────────
# 합체 로봇 데이터 (hello_carbot_robots.md "합체 카봇 표")
# (합체이름, 시즌, 단수, [멤버들], 비고)
# ─────────────────────────────────────────────────────────────────────────

COMBO_ROBOTS = [
    # 시즌 1
    ("카봇 펜타스톰",                   "1",   "5단",        ["카봇 에이스", "카봇 프론", "카봇 댄디", "카봇 스카이", "카봇 스톰"],
     "최초 합체 카봇. 검증 완료 (basic/gold/refine 3변종)"),
    # 시즌 2
    ("카봇 로드세이버",                 "2~15", "3단",       ["카봇 아티 (택시)", "카봇 마이스터 (택시)", "카봇 세이버"],
     "검증 완료. 인간형 ↔ 로어세이버(곰형) 두 모드. basic/allstar 2변종"),
    # [REMOVED → TEAM] 카봇 삼총사 — 나무위키 확인 결과 합체 아닌 3인조 팀. TEAM_ROBOTS로 이동.
    # 시즌 3
    ("카봇 마이티가드",                 "3",   "4단",        ["카봇 레디", "카봇 큐어", "카봇 가드", "카봇 헬프"], ""),
    ("카봇 마이티가드 X",               "14",  "—",          ["(마이티가드 빅큐브 X 업그레이드)"],
     "마이티가드의 X 강화판"),
    ("카봇 K-캅스",                     "3",   "4단",        ["카봇 썬더", "카봇 스피드", "카봇 터보", "카봇 캅스"], ""),
    # 시즌 4
    ("카봇 슈퍼패트론",                 "4",   "4단",        ["카봇 패트론", "카봇 스키드", "카봇 다이어", "카봇 리프"],
     "패트론S + 다이어EX의 그레이트 합체"),
    ("카봇 패트론S",                    "4",   "2단",        ["카봇 패트론", "카봇 스키드"], "슈퍼패트론의 상체"),
    ("카봇 다이어EX",                   "4",   "2단",        ["카봇 다이어", "카봇 리프"], "슈퍼패트론의 하체"),
    # 시즌 5
    ("카봇 하이퍼빌디언",               "5",   "그레이트",   ["카봇 빌디언", "카봇 크랜", "카봇 듀크", "카봇 프라우드제트", "카봇 스타블래스터"],
     "그레이트 합체. 빌디언/크랜/듀크 (나무위키 확인) + 프라우드제트/스타블래스터 (md 기재). 다층 구조"),
    ("카봇 프라우드제트",               "5",   "2단",        ["카봇 프라우드", "카봇 제스티"], ""),
    ("카봇 스타블래스터",               "5",   "2단",        ["카봇 블래스터", "카봇 스타비"], ""),
    ("카봇 아머다이저",                 "5",   "—",          ["카봇 킹다이저", "카봇 아머포스"], ""),
    ("카봇 마하피스",                   "5",   "교차 합체",  ["카봇 마하 (상체)", "카봇 피스 (하체)"], "크로스 콤비네이션"),
    ("카봇 브레이피스",                 "5",   "교차 합체",  ["카봇 브레이브 (상체)", "카봇 피스 (하체)"], "크로스 콤비네이션"),
    ("카봇 마하로드",                   "5",   "교차 합체",  ["카봇 마하 (상체)", "카봇 로드 (하체)"], "크로스 콤비네이션"),
    ("카봇 브레이로드",                 "5",   "교차 합체",  ["카봇 브레이브 (상체)", "카봇 로드 (하체)"], "크로스 콤비네이션"),
    # 시즌 6
    ("카봇 럭키펀치",                   "6",   "2단",        ["카봇 럭키", "카봇 펀치"], ""),
    # 시즌 9 — 펜타스톰 X 패밀리 (검증 완료)
    ("카봇 펜타스톰 X",                 "9~15", "5단",       ["카봇 스톰 X", "카봇 에이스 레스큐 X", "카봇 프론 폴리스 X", "카봇 댄디 앰뷸런스 X", "카봇 스카이 S.W.A.T X"],
     "X 강화판. 검증 완료 (basic/crystal/bigcube/lifecannon 4변종)"),
    ("카봇 펜타스톰 X 빅큐브",          "14",  "5단+빅큐브", ["카봇 스톰 X 빅큐브", "카봇 에이스 레스큐 X", "카봇 프론 폴리스 X", "카봇 댄디 앰뷸런스 X", "카봇 스카이 S.W.A.T X", "(+ 빅큐브 무장)"],
     "빅큐브 무장 장착. 부스터 모드 / 기어 모드"),
    ("카봇 펜타스톰 X 라이프 캐논 모드", "14", "6단 그레이트", ["카봇 스톰 X", "카봇 에이스 레스큐 X", "카봇 프론 폴리스 X", "카봇 댄디 앰뷸런스 X", "카봇 스카이 S.W.A.T X", "카봇 라이프 X"],
     "6단 그레이트 합체. 새니타이저 캐논, 콰트로 클로 (라이프 X 변형)"),
    ("크리스탈 카봇 펜타스톰 X",        "13",  "5단",        ["크리스탈 스톰 X", "크리스탈 에이스 레스큐 X", "크리스탈 프론 폴리스 X", "크리스탈 댄디 앰뷸런스 X", "크리스탈 스카이 S.W.A.T X"],
     "13기 한정. 반투명 크리스탈 재질"),
    # 시즌 10 - 가디언트 / 자이언트 로더
    ("카봇 가디언트",                   "10",  "2단",        ["카봇 덤피", "카봇 브로피"], ""),
    ("카봇 자이언트 로더",              "10",  "3단",        ["카봇 페이저", "카봇 소닉붐", "카봇 로더"], ""),
    # 시즌 10 뱅 시리즈
    ("잭슈트뱅",                        "10",  "2단",        ["카봇 잭슈트", "카봇 타우", "카봇 퓨처버스"], "6대륙 카봇 뱅"),
    ("페로뱅",                          "10",  "2단",        ["카봇 페로", "카봇 파우", "카봇 퓨처버스"], "6대륙 카봇 뱅"),
    ("나노티스뱅",                      "10",  "2단",        ["카봇 나노티스", "카봇 도우", "카봇 퓨처버스"], "6대륙 카봇 뱅"),
    ("썬런뱅",                          "10",  "2단",        ["카봇 썬런", "카봇 미우", "카봇 파이트라"], "6대륙 카봇 뱅"),
    ("호스퍼스뱅",                      "10",  "2단",        ["카봇 호스퍼스", "카봇 바우", "카봇 파이트라"], "6대륙 카봇 뱅"),
    ("자크뱅",                          "10",  "2단",        ["카봇 자크", "카봇 바우", "카봇 파이트라"], "6대륙 카봇 뱅"),
    ("자크레인뱅",                      "10",  "—",          ["카봇 자크", "카봇 자크레인"], "6대륙 카봇 뱅"),
    # 시즌 11
    ("카봇 킹가이더",                   "11",  "2단",        ["카봇 핫가이더", "카봇 쿨가이더"],
     "쌈바 카봇 (핫가이더=브라키레인 파트너, 쿨가이더=트리카고 파트너)"),
    # 시즌 12
    ("카봇 하이퍼캅스",                 "12",  "합체",       ["카봇 드로캅", "카봇 이그리붐", "카봇 푸르디붐", "카봇 서포티붐"],
     "나무위키 명시 4종 (추가 멤버 미확인)"),
    # 시즌 13
    ("카봇 사파리세이버",               "13",  "5단",        ["카봇 드럼킹", "카봇 호크하이", "카봇 하울러", "카봇 타이거붐", "카봇 스터번"],
     "펜타스톰 다음 5단 합체"),
    # 시즌 14
    ("펜타스톰 X 라이프 캐논 모드 (재기재)", "14",  "(중복)",  ["(위 펜타스톰 X 라이프 캐논 모드 항목 참조)"], ""),
    # 시즌 15
    ("카봇 스타가디언",                 "15",  "4단(+1)",    ["카봇 폴리스타", "카봇 스카이스타", "카봇 아이언스타", "카봇 파이어스타", "(+ 파이터 비클)"], ""),
    # 시즌 16
    ("그랜드 카봇 GX",                  "16",  "그레이트",   ["카봇 X", "카봇 캐논 X", "카봇 엑스 파이터", "카봇 엑스 트레인", "(+ 하이드 제외 시즌 16 용사 카봇 전원)"],
     "시즌 16 그레이트 합체. 캐논 X는 나무위키 확인됨"),
    ("그랜드 카봇 X",                   "16",  "3단",        ["카봇 X", "카봇 엑스 파이터", "카봇 엑스 트레인"],
     "1번째 용사 카봇 그룹"),
    ("카봇 패트롤가이즈",               "16",  "—",          ["카봇 히트가이", "카봇 코드가이"], "3번째 용사 카봇"),
    ("카봇 마이티캅스",                 "16",  "—",          ["(미확인)"], "시즌 16 합체"),
    # 시즌 17
    ("카봇 울트라포트 GX",              "17",  "그레이트",   ["카봇 빅포트", "카봇 EV 커맨더", "(+ 미공개 4종)"],
     "시즌 17 그레이트 합체. 빅포트/EV 커맨더는 나무위키 확인"),
    ("카봇 울트라포트",                 "17",  "—",          ["카봇 빅포트", "카봇 EV 커맨더", "(+ 미공개 2종)"],
     "시즌 17 합체. 빅포트/EV 커맨더는 나무위키 확인, 나머지 2종 미공개"),
    # [REMOVED → TEAM] 카봇 스카이 트리오 — 나무위키 명시: "합체가 불가능한 3인조 카봇". TEAM_ROBOTS로 이동.
    # 극장판 (나무위키 검증으로 신규 발견)
    ("카봇 티라이오",                   "극장판 2기", "합체",  ["카봇 크라이언", "카봇 티라투스", "카봇 코어"],
     "★ 나무위키 검증으로 신규 발견. 옴파로스 섬의 비밀 (2019). md 합체 카봇 표에는 없음"),
    # 유니티 (나무위키 검증으로 신규 발견)
    ("에반 프라임",                     "유니티",     "합체",  ["미리내프라임", "(+ 미확인 멤버)"],
     "★ 나무위키 검증으로 신규 발견. 유니티 시리즈. md 합체 카봇 표에는 없음"),
]


# ─────────────────────────────────────────────────────────────────────────
# 팀 로봇 (비합체 3인조)
# (팀이름, 시즌, 단수, [팀원들], 비고)
# ─────────────────────────────────────────────────────────────────────────

TEAM_ROBOTS = [
    ("카봇 삼총사",        "2~",  "3인조 (기본)",
     ["카봇 나이트", "카봇 루크", "카봇 폰"],
     "★ 나무위키 확인: 합체 아닌 팀. 손잡고 회전하는 '바람개비', 트라이앵글 배리어 등 팀 연계 기술"),
    ("카봇 테이프 삼총사",  "15~", "3인조 (X 강화)",
     ["카봇 나이트 X", "카봇 루크 X", "카봇 폰 X"],
     "★ 나무위키 확인: 카봇 삼총사의 X 강화판. 시즌 17 12화부터는 '삼총사 X'로도 불림. 각자 다른 색 테이프 탑재 (레드/블루/오렌지). 테이프 윕/스틱/회오리 기술"),
    ("카봇 스카이 트리오",  "17",  "3인조",
     ["카봇 제트밴더 (4번째 용사)", "카봇 에어밴더 (5번째 용사)", "카봇 헬리밴더 (6번째 용사)"],
     "★ 나무위키 명시: '합체가 불가능한 3인조 카봇' (삼총사에 이어 두 번째). 브레이브 킹덤 공중 근위대. 슬랩밴드로 헥사 밴드 사이클론 등 연계 기술"),
]


# ─────────────────────────────────────────────────────────────────────────
# 인벤토리 스캔
# ─────────────────────────────────────────────────────────────────────────

def scan_inventory():
    all_files = [f for f in SRC.iterdir() if f.is_file() and f.suffix == '.webp']
    cats = {'_zz': 0, '_xxyy': 0, '_xx': 0, '(clean)': 0}
    for f in all_files:
        s = f.stem
        if s.endswith('_zz'):    cats['_zz'] += 1
        elif s.endswith('_xxyy'):cats['_xxyy'] += 1
        elif s.endswith('_xx'):  cats['_xx'] += 1
        else:                    cats['(clean)'] += 1
    return cats, len(all_files)


# ─────────────────────────────────────────────────────────────────────────
# HTML 빌드
# ─────────────────────────────────────────────────────────────────────────

def esc(s):
    return (str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            .replace('"', '&quot;'))


def build_html(out_path):
    cats, total = scan_inventory()

    # 시즌별 그룹 표시를 위해 정렬용 키
    def season_sort_key(row):
        season = row[1]
        # "1", "2", "10", "극장판 1기", "쿵 시리즈", "유니티"
        if season.startswith('극장판'):
            return (200, season)
        if '쿵' in season:
            return (300, season)
        if '유니티' in season:
            return (400, season)
        try:
            return (int(season.split('~')[0]), '')
        except ValueError:
            return (500, season)

    standalone_sorted = sorted(STANDALONE_ROBOTS, key=season_sort_key)
    combo_sorted = sorted(COMBO_ROBOTS, key=season_sort_key)
    team_sorted = sorted(TEAM_ROBOTS, key=season_sort_key)

    # 통계
    n_standalone = len(STANDALONE_ROBOTS)
    n_combo = len(COMBO_ROBOTS)
    n_team  = len(TEAM_ROBOTS)
    n_team_members = sum(len(t[3]) for t in TEAM_ROBOTS)
    n_unique_members = len({m for c in COMBO_ROBOTS for m in c[3] if not m.startswith('(') and '미확인' not in m and '미공개' not in m})

    # === 개별 로봇 표 행 빌드 ===
    standalone_rows = []
    for name, season, category, note in standalone_sorted:
        standalone_rows.append(f"""<tr>
            <td class="name">{esc(name)}</td>
            <td class="season">{esc(season)}</td>
            <td class="category">{esc(category)}</td>
            <td class="note">{esc(note)}</td>
        </tr>""")

    # === 팀 로봇별 표 빌드 ===
    team_blocks = []
    for team_name, season, units, members, note in team_sorted:
        member_rows = ''.join(f"""<tr>
            <td class="idx">{i+1}</td>
            <td class="member">{esc(m)}</td>
        </tr>""" for i, m in enumerate(members))

        team_blocks.append(f"""
<div class="combo-card team-card" id="team-{esc(team_name)}">
  <div class="combo-header">
    <div class="combo-title">{esc(team_name)} <span class="team-tag">팀</span></div>
    <div class="combo-meta">
      <span class="badge badge-season">시즌 {esc(season)}</span>
      <span class="badge badge-units">{esc(units)}</span>
      <span class="badge badge-count">{len(members)}명</span>
    </div>
  </div>
  {f'<div class="combo-note">{esc(note)}</div>' if note else ''}
  <table class="member-table">
    <thead><tr><th class="idx">#</th><th class="member">팀원</th></tr></thead>
    <tbody>{member_rows}</tbody>
  </table>
</div>
""")

    # === 합체 로봇별 표 빌드 ===
    combo_blocks = []
    for combo_name, season, units, members, note in combo_sorted:
        member_rows = ''.join(f"""<tr>
            <td class="idx">{i+1}</td>
            <td class="member">{esc(m)}</td>
        </tr>""" for i, m in enumerate(members))

        combo_blocks.append(f"""
<div class="combo-card" id="combo-{esc(combo_name)}">
  <div class="combo-header">
    <div class="combo-title">{esc(combo_name)}</div>
    <div class="combo-meta">
      <span class="badge badge-season">시즌 {esc(season)}</span>
      <span class="badge badge-units">{esc(units)}</span>
      <span class="badge badge-count">{len(members)}명</span>
    </div>
  </div>
  {f'<div class="combo-note">{esc(note)}</div>' if note else ''}
  <table class="member-table">
    <thead><tr><th class="idx">#</th><th class="member">멤버 로봇</th></tr></thead>
    <tbody>{member_rows}</tbody>
  </table>
</div>
""")

    # === TOC ===
    toc_links = ''.join(f'<li><a href="#combo-{esc(c[0])}">{esc(c[0])}</a></li>' for c in combo_sorted)
    team_toc_links = ''.join(f'<li><a href="#team-{esc(t[0])}">{esc(t[0])}</a></li>' for t in team_sorted)

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="apple-mobile-web-app-capable" content="yes">
<title>카봇 카탈로그 (표)</title>
<style>
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Apple SD Gothic Neo', 'Noto Sans KR', sans-serif;
    margin: 0; padding: 0; background: #f5f7fa; color: #2c3e50;
    line-height: 1.5;
  }}
  .container {{ display: grid; grid-template-columns: 240px 1fr; min-height: 100vh; }}
  aside {{
    background: #305496; color: white; padding: 20px 16px;
    position: sticky; top: 0; height: 100vh; overflow-y: auto;
    box-sizing: border-box;
  }}
  aside h3 {{ margin: 8px 0 12px; color: #fff; font-size: 14px; opacity: 0.85; text-transform: uppercase; letter-spacing: 0.5px; }}
  aside .nav-section a {{ display: block; color: #d6e4f7; text-decoration: none; padding: 6px 10px; border-radius: 4px; font-size: 13px; }}
  aside .nav-section a:hover {{ background: rgba(255,255,255,0.1); color: white; }}
  aside ul {{ list-style: none; padding: 0; margin: 0 0 20px; }}
  main {{ padding: 28px 40px; max-width: 1100px; }}
  h1 {{ color: #305496; margin: 0 0 4px; }}
  .subtitle {{ color: #6c757d; margin: 0 0 24px; font-size: 14px; }}
  .stats {{
    display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin-bottom: 28px;
  }}
  .stat {{
    background: white; padding: 14px; border-radius: 10px; text-align: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  }}
  .stat .num {{ font-size: 28px; font-weight: bold; color: #305496; }}
  .stat .label {{ font-size: 11px; color: #6c757d; margin-top: 4px; }}

  section {{ margin-bottom: 40px; }}
  h2 {{
    color: #305496; border-bottom: 3px solid #305496; padding-bottom: 6px;
    margin-top: 36px; font-size: 22px;
  }}
  .section-desc {{ color: #6c757d; font-size: 13px; margin-bottom: 16px; }}

  /* 개별 로봇 표 */
  table.standalone {{
    width: 100%; border-collapse: collapse; background: white; border-radius: 10px;
    overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    font-size: 13px;
  }}
  table.standalone thead th {{
    background: #305496; color: white; font-weight: 600; text-align: left;
    padding: 10px 14px; font-size: 12px; text-transform: uppercase; letter-spacing: 0.3px;
  }}
  table.standalone tbody tr {{ border-top: 1px solid #eef1f5; }}
  table.standalone tbody tr:hover {{ background: #f8f9fc; }}
  table.standalone td {{ padding: 8px 14px; vertical-align: top; }}
  table.standalone .name {{ font-weight: 600; color: #2c3e50; width: 22%; }}
  table.standalone .season {{ color: #6c757d; width: 12%; white-space: nowrap; }}
  table.standalone .category {{
    width: 14%;
  }}
  table.standalone .category::before {{
    content: ''; display: inline-block; width: 6px; height: 6px;
    border-radius: 50%; margin-right: 6px; background: #305496;
  }}
  table.standalone .note {{ color: #6c757d; font-size: 12.5px; }}

  /* 합체 로봇 카드 */
  .combo-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }}
  .combo-card {{
    background: white; border-radius: 10px; padding: 16px 18px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    scroll-margin-top: 16px;
  }}
  .combo-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }}
  .combo-title {{ font-size: 15px; font-weight: 700; color: #305496; }}
  .combo-meta {{ display: flex; gap: 4px; }}
  .badge {{
    display: inline-block; padding: 2px 8px; font-size: 10.5px;
    border-radius: 10px; font-weight: 600;
  }}
  .badge-season {{ background: #e8eef7; color: #305496; }}
  .badge-units {{ background: #fef0e6; color: #c75e17; }}
  .badge-count {{ background: #e6f4ea; color: #2d7d3e; }}
  .combo-note {{
    font-size: 11.5px; color: #6c757d; margin: 6px 0 10px;
    padding: 6px 10px; background: #f8f9fa; border-left: 3px solid #6c757d; border-radius: 3px;
  }}
  table.member-table {{
    width: 100%; border-collapse: collapse; font-size: 12.5px; margin-top: 8px;
  }}
  table.member-table thead th {{
    background: #f5f7fa; color: #495057; font-weight: 600;
    padding: 6px 10px; text-align: left; font-size: 11px;
  }}
  table.member-table tbody tr {{ border-top: 1px solid #f0f2f5; }}
  table.member-table td {{ padding: 6px 10px; vertical-align: middle; }}
  table.member-table .idx {{ width: 24px; color: #adb5bd; font-weight: 600; }}
  table.member-table .member {{ color: #2c3e50; }}
  th.idx {{ width: 24px; }}

  /* 팀 카드 (비합체 3인조) */
  .team-card {{ border-left: 4px solid #ad6800; background: #fffbf0; }}
  .team-card .combo-title {{ color: #ad6800; }}
  .team-tag {{
    display: inline-block; background: #ad6800; color: white;
    font-size: 10px; padding: 1px 6px; border-radius: 6px;
    vertical-align: middle; margin-left: 4px; font-weight: 600;
  }}
  .stat-team .num {{ color: #ad6800 !important; }}
</style>
</head>
<body>
<div class="container">

<aside>
  <h3>섹션</h3>
  <div class="nav-section">
    <a href="#sec-standalone">▸ 개별 로봇 ({n_standalone})</a>
    <a href="#sec-team">▸ 팀 (비합체) ({n_team})</a>
    <a href="#sec-combo">▸ 합체 로봇 ({n_combo})</a>
  </div>
  <h3>팀 목차</h3>
  <ul class="nav-section">
    {team_toc_links}
  </ul>
  <h3>합체 로봇 목차</h3>
  <ul class="nav-section">
    {toc_links}
  </ul>
</aside>

<main>
  <h1>카봇 카탈로그</h1>
  <p class="subtitle">개별 로봇 + 팀 (비합체 3인조) + 합체 로봇별 멤버 표</p>

  <div class="stats">
    <div class="stat"><div class="num">{n_standalone}</div><div class="label">개별 로봇</div></div>
    <div class="stat stat-team"><div class="num">{n_team}</div><div class="label">팀 (비합체)</div></div>
    <div class="stat"><div class="num">{n_combo}</div><div class="label">합체 로봇</div></div>
    <div class="stat"><div class="num">{n_unique_members}</div><div class="label">합체 멤버 (고유)</div></div>
    <div class="stat"><div class="num">{n_team_members}</div><div class="label">팀원</div></div>
  </div>

  <section id="sec-standalone">
    <h2>① 개별 로봇 ({n_standalone}종)</h2>
    <p class="section-desc">합체에도 팀에도 속하지 않는 완전 단독 로봇. 시즌순 정렬. 극장판/알카봇/유니티 포함.</p>
    <table class="standalone">
      <thead>
        <tr>
          <th>로봇 이름</th>
          <th>시즌</th>
          <th>분류</th>
          <th>비고</th>
        </tr>
      </thead>
      <tbody>
        {''.join(standalone_rows)}
      </tbody>
    </table>
  </section>

  <section id="sec-team">
    <h2>② 팀 — 비합체 3인조 ({n_team}팀)</h2>
    <p class="section-desc">각 멤버는 독립된 로봇이고, 팀 단위로 함께 활동하지만 <b>합체는 하지 않음</b>. 손잡고 회전·연계 기술 등 팀워크로 싸움. 나무위키 명시 분류.</p>
    <div class="combo-grid">
      {''.join(team_blocks)}
    </div>
  </section>

  <section id="sec-combo">
    <h2>③ 합체 로봇 → 멤버 ({n_combo}종)</h2>
    <p class="section-desc">각 합체 로봇별 구성 멤버. 사이드바의 합체 이름을 클릭하면 해당 표로 이동.</p>
    <div class="combo-grid">
      {''.join(combo_blocks)}
    </div>
  </section>

</main>
</div>
</body>
</html>
"""
    out_path.write_text(html, encoding='utf-8')
    print(f"[html] {out_path}")
    print(f"  개별 로봇: {n_standalone}, 팀: {n_team}, 합체 로봇: {n_combo}, 고유 멤버: {n_unique_members}")


if __name__ == "__main__":
    build_html(BASE / "carbot_visual.html")
