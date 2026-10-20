import os
import json
import urllib.request
from bs4 import BeautifulSoup
import google.generativeai as genai
from playwright.sync_api import sync_playwright

GEMINI_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_KEY)
BLOG_NAME = "daynote365"

def get_recent_post_sample():
    """내 블로그의 최신 글 하나를 읽어와 포맷/스타일 예시로 추출"""
    try:
        url = f"https://{BLOG_NAME}.tistory.com"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        html = urllib.request.urlopen(req).read().decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        
        # 첫 번째 글 본문 요약 추출 (사이트 템플릿에 맞춰 조정 가능)
        entry = soup.select_one('.entry-content, .article_content, .content')
        if entry:
            return entry.get_text()[:600] # 앞 600자 스타일 샘플
    except Exception as e:
        print(f"스타일 샘플 수집 건너뜀: {e}")
    return "안녕하세요! 실무에서 겪은 유용한 팁을 정리해 드립니다."

def get_custom_topic_or_default():
    """
    topics.txt에 남겨둔 메모가 있으면 그걸 가져오고 파일에서 삭제,
    없으면 기본 트렌드 주제를 자동 생성하도록 None 반환
    """
    if os.path.exists("topics.txt"):
        with open("topics.txt", "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        if lines:
            target_topic = lines[0]
            # 사용한 주제는 파일에서 제거하고 다시 저장
            with open("topics.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(lines[1:]))
            return target_topic
    return None

def generate_article():
    sample_style = get_recent_post_sample()
    custom_topic = get_custom_topic_or_default()
    
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    if custom_topic:
        topic_instruction = f"""
        주제/메모: {custom_topic}
        주의: 사내 기밀, 특정 회사명, 민감한 개인정보가 있다면 완전히 일반화된 실무 테크/업무 노하우 형태로 각색해줘.
        """
    else:
        topic_instruction = "주제: 최신 IT 실무 생산성 툴 또는 유용한 개발/업무 자동화 노하우 1선 자동 선정"

    prompt = f"""
    당신은 블로그 운영자입니다. 아래 [스타일 샘플]의 말투, 서론/결론 패턴, 소제목 활용 방식을 모방하여 글을 작성하세요.

    [스타일 샘플]:
    {sample_style}

    [글 작성 요청]:
    {topic_instruction}

    출력 포맷:
    [TITLE] 매력적인 포스팅 제목
    [CONTENT] 본문 (반드시 HTML 태그 p, h2, h3, ul, li 등을 적용하여 깔끔하고 구조화된 서식으로 작성)
    """
    res = model.generate_content(prompt).text
    title = res.split("[CONTENT]")[0].replace("[TITLE]", "").strip()
    content = res.split("[CONTENT]")[1].strip()
    return title, content

# post_to_tistory(...) 함수는 기존 Playwright 코드 유지
