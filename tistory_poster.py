import os
import json
import time
from google import genai
from playwright.sync_api import sync_playwright

BLOG_NAME = "daynote365"

def generate_article():
    print("1. Gemini를 사용해 고유 블로그 양식에 맞춘 글과 태그를 생성합니다...")
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")

    client = genai.Client(api_key=api_key)
    
    prompt = """
    당신은 IT/테크 실무 및 홈랩, PC/스마트폰 활용 팁을 정리하는 'ChooSu Note' 블로그의 전문 필진입니다.
    PC/스마트폰 활용 꿀팁, 일상 업무 생산성 소프트웨어, 또는 시놀로지 NAS(도커, 백업, 네트워크 등) 활용법 중 
    하나의 유용한 기술 주제를 선정하여 아래 [작성 양식]을 철저히 따라 작성해주세요.

    [작성 양식 규칙]:
    1. 서론 인트로는 반드시 "내가 찾는 건 늘 없었다 (...)" 처럼 흩어져 있는 자료에 지쳐 직접 통합 정리한다는 담백한 독백 톤으로 시작할 것.
    2. 소제목과 섹션 분할에 직관적인 이모지를 필수 사용할 것:
       - 📘 [주제 개요]
       - 📝 [사용 개요 및 권장 대상]
       - 1️⃣ [도구/기능 소개 및 핵심 특징]
       - 2️⃣ [준비물]
       - 📅 [구축 및 설치 방법 단계별 안내 (①, ②, ③)]
       - 💡 [핵심 설정 및 팁]
       - 📂 [실사용 연결 방법 및 트러블슈팅]
       - 🙌 [마무리 3단계 핵심 흐름 요약]
    3. 절대 마크다운 별표(**)를 남발하지 말 것! 텍스트 강조는 <b>태그나 <strong>태그를 사용할 것.
    4. 글 중간에 핵심 설정이나 흐름을 보여주는 깔끔한 텍스트 박스(====== 형태)를 최소 1개 포함할 것.
    5. 글과 관련된 검색용 핵심 태그 5~7개를 쉼표(,)로 구분하여 [TAGS]에 지정할 것.
    6. 글 주제에 맞는 무료 이미지 검색용 영어 단어 1개를 [IMAGE_KEYWORD]에 적을 것.

    [출력 포맷]:
    [TAGS] 태그1, 태그2, 태그3, 태그4, 태그5
    [IMAGE_KEYWORD] 영어단어
    [TITLE] 매력적이고 군더더기 없는 제목
    [CONTENT]
    본문 내용 (위 작성 양식을 적용한 완성도 높은 본문)
    """

    response = client.models.generate_content(
        model='gemini-3.8-flash',
        contents=prompt,
    )
    
    raw_text = response.text

    # 태그 추출
    tags = ["IT팁", "테크가이드", "생산성", "시놀로지", "홈랩"]
    if "[TAGS]" in raw_text:
        try:
            tag_line = raw_text.split("[TAGS]")[1].split("[IMAGE_KEYWORD]")[0].strip()
            tags = [t.strip() for t in tag_line.split(",") if t.strip()]
        except Exception:
            pass

    # 이미지 키워드 추출
    img_keyword = "technology"
    if "[IMAGE_KEYWORD]" in raw_text:
        try:
            img_keyword = raw_text.split("[IMAGE_KEYWORD]")[1].split("[TITLE]")[0].strip()
        except Exception:
            img_keyword = "technology"

    # 제목 및 본문 분리
    title = "알아두면 유용한 IT 실무 및 환경 설정 가이드"
    content = raw_text

    if "[TITLE]" in raw_text and "[CONTENT]" in raw_text:
        title_part = raw_text.split("[CONTENT]")[0]
        title = title_part.split("[TITLE]")[1].strip()
        content = raw_text.split("[CONTENT]")[1].strip()

    # Unsplash 무료 이미지 상단 삽입
    image_html = f'<p style="text-align: center;"><img src="https://images.unsplash.com/photo-1518770660439-4636190af475?w=1000&auto=format&fit=crop&q=80" alt="{title}" style="max-width:100%; height:auto; border-radius: 8px; margin-bottom: 20px;"></p>'
    
    # 혹시 모를 마크다운 별표 치환 및 정제
    content = content.replace("**", "")
    final_content = f"{image_html}\n{content}"

    print(f"생성 완료 - 제목: {title}")
    print(f"추출된 태그: {tags}")
    return title, final_content, tags

def post_to_tistory(title, content, tags):
    print("2. 티스토리 브라우저 자동화를 시작합니다...")
    raw_cookies = os.environ.get("TISTORY_COOKIE_JSON")
    if not raw_cookies:
        raise ValueError("TISTORY_COOKIE_JSON 환경변수가 설정되지 않았습니다.")

    cookies = json.loads(raw_cookies)
    formatted_cookies = []
    for c in cookies:
        cookie_dict = {
            "name": c.get("name"),
            "value": c.get("value"),
            "domain": c.get("domain"),
            "path": c.get("path", "/"),
            "secure": c.get("secure", False),
            "httpOnly": c.get("httpOnly", False),
        }
        same_site = c.get("sameSite", "Lax")
        if same_site in ["Strict", "Lax", "None"]:
            cookie_dict["sameSite"] = same_site
        else:
            cookie_dict["sameSite"] = "Lax"
        formatted_cookies.append(cookie_dict)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        context.add_cookies(formatted_cookies)
        page = context.new_page()

        # 브라우저 Alert (임시저장 불러오기 등) 자동 취소 처리
        page.on("dialog", lambda dialog: dialog.dismiss())

        write_url = f"https://{BLOG_NAME}.tistory.com/manage/newpost/"
        print(f"에디터 페이지로 이동: {write_url}")
        page.goto(write_url, wait_until="domcontentloaded")
        page.wait_for_timeout(5000)

        # 로그인 체크
        if "login" in page.url:
            print(f"❌ 실패: 현재 URL이 {page.url} 입니다. 쿠키 인증이 풀렸습니다.")
            browser.close()
            return

        print("제목 입력 대기 중...")
        title_locator = page.locator('textarea[placeholder="제목을 입력하세요"], #post-title-inp')
        title_locator.wait_for(state="visible", timeout=15000)
        title_locator.fill(title)
        print("제목 입력 완료.")

        print("본문 입력 중...")
        page.click("#editor-root, body")
        page.wait_for_timeout(1000)
        page.keyboard.type(content)
        print("본문 입력 완료.")

        print("하단 완료 버튼 클릭...")
        finish_btn = page.locator('#publish-layer-btn, button:has-text("완료")')
        finish_btn.wait_for(state="visible", timeout=10000)
        finish_btn.click()
        page.wait_for_timeout(2000)

        # 태그 입력 처리
        print("태그 입력 진행 중...")
        tag_input = page.locator('#tagText, input[placeholder*="태그"]')
        if tag_input.count() > 0:
            for tag in tags:
                tag_name = tag.strip()
                if tag_name:
                    tag_input.fill(tag_name)
                    tag_input.press("Enter")
                    page.wait_for_timeout(300)
            print("태그 입력 완료.")

        print("최종 공개 발행 버튼 클릭...")
        submit_btn = page.locator('#publish-btn, button:has-text("발행하기"), button:has-text("발행")')
        submit_btn.wait_for(state="visible", timeout=10000)
        submit_btn.click()

        # 발행 후 리다이렉트 대기
        page.wait_for_timeout(7000)
        print(f"발행 작업 종료. 최종 페이지 URL: {page.url}")
        browser.close()

if __name__ == "__main__":
    try:
        t, c, tags = generate_article()
        post_to_tistory(t, c, tags)
    except Exception as e:
        print(f"❌ 실행 중 치명적 오류 발생: {e}")
        raise e
