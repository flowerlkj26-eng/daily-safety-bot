import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# 1. 환경 변수에서 안전하게 카카오 토큰 로드
KAKAO_TOKEN = os.environ.get('KAKAO_TOKEN')

def get_mois_report():
    """행정안전부 일일상황보고서 최신글 크롤링"""
    # [주의] 실제 행안부 게시판 구조에 따라 URL 및 Selector 조정 필요
    url = "https://www.mois.go.kr/frt/bbs/type011/commonSelectBoardList.do?bbsId=BBSMSTR_000000000040"
    try:
        res = requests.get(url, verify=False, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        latest_post = soup.select_one('.table_style1 tbody tr td.subject a')
        
        if latest_post:
            title = latest_post.text.strip()
            link = "https://www.mois.go.kr" + latest_post['href']
            return title, link
    except Exception as e:
        return f"통신 에러 발생: {e}", url
    return "최신 업데이트 없음", url

def get_kosha_siren():
    """안전보건공단 중대재해사이렌 최신글 크롤링"""
    # [주의] 실제 공단 게시판 구조에 따라 URL 및 Selector 조정 필요
    url = "https://www.kosha.or.kr/kosha/board/board.do?menuId=11531"
    try:
        res = requests.get(url, verify=False, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        latest_post = soup.select_one('td.title a')
        
        if latest_post:
            title = latest_post.text.strip()
            link = "https://www.kosha.or.kr" + latest_post['href']
            return title, link
    except Exception as e:
        return f"통신 에러 발생: {e}", url
    return "최신 업데이트 없음", url

def send_kakao_message(text):
    """카카오톡 나에게 보내기 API 호출"""
    header = {"Authorization": f"Bearer {KAKAO_TOKEN}"}
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    
    post = {
        "object_type": "text",
        "text": text,
        "link": {
            "web_url": "https://www.kosha.or.kr",
            "mobile_web_url": "https://www.mois.go.kr"
        },
        "button_title": "원문 확인"
    }
    data = {"template_object": json.dumps(post)}
    response = requests.post(url, headers=header, data=data)
    
    if response.status_code != 200:
        print(f"[ERROR] 메시지 전송 실패: {response.text}")
    else:
        print("[SUCCESS] 카카오톡 메시지 전송 완료")

def main():
    mois_title, mois_link = get_mois_report()
    kosha_title, kosha_link = get_kosha_siren()
    
    # 한국 시간 기준 오늘 날짜
    kst_now = datetime.utcnow() + timedelta(hours=9)
    today_str = kst_now.strftime("%Y-%m-%d")
    
    # Retro-Tech Terminal 포맷팅 적용 (Bold 등은 카카오톡 텍스트 내에서 가독성을 높이기 위해 기호 활용)
    message = f"""[SYS_START] :: DAILY_SAFETY_REPORT
==============================
> DATE: {today_str}
> TARGET: MOIS & KOSHA
> STATUS: FETCHED 100%
==============================

[1] 행정안전부 일일상황보고서
- 제목: {mois_title}
- 요약: 주요 재난·안전 관리 상황 및 대처 계획
- 링크: {mois_link}

[2] KOSHA 중대재해사이렌
- 제목: {kosha_title}
- 요약: 동종·유사 재해 예방을 위한 사고 사례 및 대책
- 링크: {kosha_link}

==============================
[SYS_END] :: TRANSMISSION OK"""

    send_kakao_message(message)

if __name__ == "__main__":
    main()
