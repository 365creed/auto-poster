import os
import json
import time
from google import genai
from playwright.sync_api import sync_playwright

BLOG_NAME = "daynote365"

def generate_article():
    print("1. Gemini를 사용해 글 생성을 시작합니다...")
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")

    client = genai.Client(api_key=api_key)
    prompt = """
    IT/테크, 생산성 소프트웨어 팁, 시놀로지 NAS 활용 팁 중 흥미로운 주제 하나를 선정하여 
    티스토리 블로그용 전문 기술 포스팅을 작성해줘.
    
    규칙:
    - 반드시 첫 줄에 [TITLE] 제목 형태로 제목을 출력할 것.
    - 그 다음 줄부터 [CONTENT] 본문 형태로 출력할 것.
    - 본문은 친절한 설명과 소제목 구조로 작성할 것.
    """
    
    response = client.models.generate_content(
        model='gemini-3.8-flash',
        contents=prompt,
    )
    
    text = response.text
    if "[CONTENT]" in text:
        parts = text.split("[CONTENT]")
        title = parts[0].replace("[TITLE]", "").strip()
        content = parts[1].strip()
    else:
        title = "IT 생산성을 높여주는 유용한 기술 가이드"
        content = text

    print(f"글 생성 완료: {title}")
    return title, content

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
