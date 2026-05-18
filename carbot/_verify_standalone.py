"""
STANDALONE_ROBOTS 후보 86종을 모두 나무위키에서 검증.
infobox에서 '합체' 필드가 있으면 → 멤버로봇 (개별 아님)
"""
import json
import re
import time
import urllib.parse
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = Path(__file__).parent

# 검증 대상 (STANDALONE_ROBOTS 의 이름만)
CANDIDATES = [
    # 시즌 1
    "카봇 호크",
    # 시즌 2
    "카봇 트루", "카봇 본",
    # 시즌 3
    "카봇 우가바", "카봇 골드렉스", "카봇 제트렌", "카봇 킹가이즈",
    # 시즌 5
    "카봇 빌디언", "카봇 크랜", "카봇 듀크",
    "카봇 비트런", "카봇 메가볼드", "카봇 오토소닉",
    # 시즌 6
    "카봇 아이언트", "카봇 컨버스터", "카봇 아이누크", "카봇 스타피너",
    # 시즌 7
    "카봇 스피너블", "카봇 버디가드",
    "카봇 유니크루저", "카봇 제트크루저",
    "카봇 메디언트", "카봇 파이언트", "카봇 라이캅스", "카봇 앵그리퍼프",
    # 시즌 8
    "카봇 테크노마스터",
    # 시즌 9
    "카봇 파워크루저", "카봇 모:반", "카봇 울티맥스",
    # 시즌 10
    "카봇 마이티로",
    # 시즌 11 쌈바
    "카봇 저스포스", "카봇 레드와일러", "카봇 나이트호퍼", "카봇 맥스도저",
    "카봇 샌드버스터", "카봇 록캔",
    # 시즌 11 하이더
    "카봇 베어하이더", "카봇 이글하이더",
    # 시즌 12 붐바
    "카봇 스크류붐바", "카봇 파워붐바",
    "카봇 드릴버스트", "카봇 스톰다이버", "카봇 라란자",
    # 시즌 12 밤밤
    "카봇 도저밤밤", "카봇 레미밤밤", "카봇 아레스밤밤", "카봇 포레밤밤", "카봇 큐어밤밤",
    # 시즌 13 젬
    "카봇 윙버드젬", "카봇 디고베어젬", "카봇 토터젬",
    "카봇 톡시젬", "카봇 스나이퍼젬", "카봇 캥복스젬", "카봇 로어젬",
    "카봇 레포스", "카봇 일렉트롬",
    # 시즌 14
    "카봇 라이프 X", "카봇 빅터", "카봇 티라쿵",
    # 시즌 15
    "카봇 펀치마스터", "카봇 호프",
    # 시즌 16
    "카봇 캐논 X", "카봇 하이드",
    # 시즌 17
    "카봇 빅포트", "카봇 EV 커맨더",
    # 극장판
    "카봇 티라클레스", "카봇 트리톤", "카봇 테라제트", "카봇 테고",
    "카봇 에이샤크", "카봇 크라이언", "카봇 팔로", "카봇 마이모스", "카봇 티라투스", "카봇 코어",
    "카봇 그린팜", "카봇 스카이거너", "카봇 소나다이버",
    # 알카봇 쿵
    "피노쿵", "아르케쿵", "디메트로쿵", "파키케쿵", "람포린",
    # 유니티
    "라고", "미리내프라임",
]


def parse_combine_field(text: str):
    """
    페이지 innerText 에서 infobox '합체' 필드 값 추출.
    필드 라벨 '합체' 다음 줄(들)에 합체 로봇 이름(들)이 옴.
    인접 필드 라벨('첫 등장', '구성원', '성우' 등)을 만나면 종료.
    """
    # 일반적인 infobox 다음 필드 라벨
    boundary = r'(?:첫 등장|마지막 등장|성별|성우|기체 특징|구성원|비클 모드|차량 모델|대표 색상|사용 장비|사용 기술|사용 무장|추가 기술|추가 무장|높이|제작|유통|장르|플랫폼)'
    # 합체 라벨 + 빈줄 + 값들 + 빈줄 + 다음 라벨
    m = re.search(r'(?:^|\n)\s*합체\s*\n+(.+?)\n\s*\n\s*' + boundary, text, re.DOTALL)
    if not m:
        # 라벨 직후 한 줄만이라도 잡기
        m = re.search(r'(?:^|\n)\s*합체\s*\n+([^\n]+(?:\n[^\n]+){0,2})', text)
        if not m:
            return []
    raw = m.group(1).strip()
    # 줄별로 분리, 빈 줄 제거, 너무 긴 줄/숫자/괄호만 있는 줄 제거
    candidates = []
    for line in raw.split('\n'):
        line = line.strip()
        if not line:
            continue
        if len(line) > 40:  # 본문일 가능성
            break
        if line.startswith('[') or line.startswith('('):  # 각주/부가 설명
            continue
        # 카봇/그랜드 카봇/뱅 종결 또는 한글 시작
        if (line.startswith('카봇 ') or line.startswith('그랜드 카봇 ') or
                line.endswith('뱅') or line.endswith('GX') or line.endswith('X')):
            candidates.append(line)
        elif re.match(r'^[가-힣]', line) and len(line) < 30:
            # 한글 시작 짧은 줄 (괄호 표기 같은 부가설명)
            # 단, 다른 필드 라벨이면 종료
            if re.match(r'^(?:첫 등장|마지막 등장|성우|성별)', line):
                break
            candidates.append(line)
        else:
            break
    return candidates


def check_robot(page, name: str) -> dict:
    url = "https://namu.wiki/w/" + urllib.parse.quote(name)
    result = {'name': name, 'url': url}
    try:
        page.goto(url, wait_until='domcontentloaded', timeout=30000)
        # 본문 로딩 대기
        try:
            page.wait_for_function("() => document.body.innerText.length > 800", timeout=10000)
        except Exception:
            pass
        text = page.evaluate("document.body.innerText")
        title = page.evaluate("document.title")
        result['title'] = title
        result['exists'] = '나무위키' in title and '편집 역사가 없는' not in text
        if not result['exists']:
            result['note'] = 'page_not_found_or_empty'
            return result
        combine_to = parse_combine_field(text)
        result['combine_to'] = combine_to
        result['is_member'] = len(combine_to) > 0
        # 추가 단서
        result['has_constituent_field'] = bool(re.search(r'\n\s*구성원\s*\n', text))
    except Exception as e:
        result['error'] = str(e)[:200]
    return result


def main():
    print(f"검증 대상: {len(CANDIDATES)}종")
    print()
    results = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        ctx = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="ko-KR",
            extra_http_headers={"Referer": "https://namu.wiki/"},
        )
        page = ctx.new_page()
        for i, name in enumerate(CANDIDATES, 1):
            r = check_robot(page, name)
            tag = ''
            if r.get('error'):
                tag = f'ERR {r["error"][:40]}'
            elif not r.get('exists'):
                tag = '[ NO PAGE ]'
            elif r.get('is_member'):
                tag = f'★ 멤버 → {r["combine_to"]}'
            else:
                tag = '○ standalone'
            print(f"  [{i:3d}/{len(CANDIDATES)}] {name:18s} {tag}")
            results.append(r)
            time.sleep(0.3)
        browser.close()

    # 저장
    out_json = BASE / '_verify_results.json'
    out_json.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')

    # 요약
    members  = [r for r in results if r.get('is_member')]
    standalone = [r for r in results if r.get('exists') and not r.get('is_member')]
    notfound = [r for r in results if r.get('exists') is False]
    errors   = [r for r in results if r.get('error')]

    print()
    print('=' * 60)
    print(f'검증 총: {len(results)}')
    print(f'  • 확정 개별 (합체 필드 없음): {len(standalone)}')
    print(f'  • 확정 멤버 (합체 필드 있음): {len(members)}')
    print(f'  • 페이지 없음: {len(notfound)}')
    print(f'  • 에러: {len(errors)}')

    if members:
        print()
        print('★ 개별 리스트에서 제거해야 할 로봇 (실제로는 멤버):')
        for m in members:
            combos = ', '.join(m['combine_to'])
            print(f'  - {m["name"]:18s} → 합체: {combos}')

    if notfound:
        print()
        print('[ NO PAGE ] 나무위키 페이지 없음 (이름 변형 필요):')
        for n in notfound:
            print(f'  - {n["name"]}')

    print(f'\n→ 상세 결과: {out_json}')


if __name__ == "__main__":
    main()
