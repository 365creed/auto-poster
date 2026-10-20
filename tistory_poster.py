import os
import json
import time
from google import genai
from playwright.sync_api import sync_playwright

BLOG_NAME = "daynote365"

def generate_article():
    print("1. Gemini를 사용해 초보자 눈높이 맞춤 글을 생성합니다...")
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")

    client = genai.Client(api_key=api_key)
    
    prompt = """
    주제: PC/스마트폰 활용 꿀팁, 일상 업무 생산성 소프트웨어, 또는 시놀로지 NAS의 기초적인 활용법 중 
    일반인/초보자도 바로 따라 할 수 있는 쉬운 주제 하나를 선정해주세요.

    [작성 규칙]:
    1. 난이도는 '초보자도 쉽게 따라 하는 친절한 가이드' 톤으로 작성하세요. 너무 어려운 전문 엔지니어링 용어나 복잡한 명령어는 피하고 단계별(Step 1, Step 2)로 쉽게 설명하세요.
    2. 절대 마크다운 별표(**)를 사용하지 마세요! 강조하고 싶은 부분은 <b>태그나 <strong>태그를 사용하세요.
    3. 본문은 줄바꿈과 단락 구분을 명확히 하고, 소제목은 <h3> 태그를 사용하세요.
    4. 글 주제와 가장 잘 어울리는 영어 단어 1개(예: computer, office, storage, data, network 등)를 [IMAGE_KEYWORD] 태그 뒤에 적어주세요.

    [출력 포맷]:
    [IMAGE_KEYWORD] 영어단어
    [TITLE] 호기심을 끄는 친절한 제목
    [CONTENT]
    HTML 형식으로 작성된 본문 (p, h3, ul, li, strong 등만 사용)
    """

    response = client.models.generate_content(
        model='gemini-3.8-flash',
        contents=prompt,
    )
    
    raw_text = response.text

    # 키워드, 제목, 본문 분리
    img_keyword = "technology"
    if "[IMAGE_KEYWORD]" in raw_text:
        try:
            img_keyword = raw_text.split("[IMAGE_KEYWORD]")[1].split("[TITLE]")[0].strip()
        except Exception:
            img_keyword = "technology"

    title = "알아두면 유용한 IT/생활 꿀팁 가이드"
    content = raw_text

    if "[TITLE]" in raw_text and "[CONTENT]" in raw_text:
        title_part = raw_text.split("[CONTENT]")[0]
        title = title_part.split("[TITLE]")[1].strip()
        content = raw_text.split("[CONTENT]")[1].strip()

    # Unsplash 무료 이미지 HTML 태그 상단 삽입
    image_html = f'<p style="text-align: center;"><img src="https://source.unsplash.com/800x450/?{img_keyword}" alt="{title}" style="max-width:100%; height:auto; border-radius: 8px; margin-bottom: 20px;"></p>'
    
    # 마크다운 ** 기호가 혹시 남아있다면 제거
    content = content.replace("**", "")
    final_content = f"{image_html}\n{content}"

    print(f"생성 완료 - 제목: {title}")
    return title, final_content

def post_to_tistory(title, content):
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

        # 브라우저 Alert (임시저장 불러오기 확인창 등) 자동 취소 처리
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
        # 제목 필드 찾기
        title_locator = page.locator('textarea[placeholder="제목을 입력하세요"], #post-title-inp')
        title_locator.wait_for(state="visible", timeout=15000)
        title_locator.fill(title)
        print("제목 입력 완료.")

        print("본문 입력 중...")
        # 티스토리 에디터 본문 영역 클릭 후 텍스트 입력
        page.click("#editor-root, body")
        page.wait_for_timeout(1000)
        page.keyboard.type(content)
        print("본문 입력 완료.")

        print("완료 버튼 클릭 시도...")
        finish_btn = page.locator('#publish-layer-btn, button:has-text("완료")')
        finish_btn.wait_for(state="visible", timeout=10000)
        finish_btn.click()
        page.wait_for_timeout(2000)

        print("최종 공개 발행 버튼 클릭 시도...")
        submit_btn = page.locator('#publish-btn, button:has-text("발행하기"), button:has-text("발행")')
        submit_btn.wait_for(state="visible", timeout=10000)
        submit_btn.click()

        # 발행 후 리다이렉트 대기
        page.wait_for_timeout(7000)
        print(f"발행 작업 종료. 최종 페이지 URL: {page.url}")
        browser.close()

if __name__ == "__main__":
    try:
        t, c = generate_article()
        post_to_tistory(t, c)
    except Exception as e:
        print(f"❌ 실행 중 치명적 오류 발생: {e}")
        raise e
