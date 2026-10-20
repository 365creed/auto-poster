import os
import re
import json
import time
import requests
import urllib.request
import xml.etree.ElementTree as ET
from io import BytesIO
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageOps
from google import genai
from playwright.sync_api import sync_playwright

BLOG_NAME = "daynote365"
HISTORY_FILE = "posted_history.txt"
IMAGE_DIR = "captured_images"
os.makedirs(IMAGE_DIR, exist_ok=True)


# =====================================================================
# 0. 중복 발행 방지 히스토리 관리
# =====================================================================
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def save_history(identifier):
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"{identifier}\n")


# =====================================================================
# 1. [방식 1] 기존 블로그(dain2013, teon7070) 글 & 실제 캡처 이미지 수집
# =====================================================================
def process_and_frame_image(img_bytes, idx):
    """원본 이미지를 다운로드하여 중복 문서 회피용 다크 프레임 + 여백 가공 후 저장"""
    try:
        img = Image.open(BytesIO(img_bytes)).convert("RGB")
        # 너무 작은 아이콘이나 배너는 제외
        if img.width < 250 or img.height < 150:
            return None
        
        # 가로 최대 900px로 리사이징
        if img.width > 900:
            ratio = 900 / float(img.width)
            new_height = int(float(img.height) * ratio)
            img = img.resize((900, new_height), Image.Resampling.LANCZOS)

        # 모던한 다크 그레이 테두리 프레임 추가 (새 이미지로 인식되도록 변형)
        framed = ImageOps.expand(img, border=12, fill="#1e293b")
        
        out_path = os.path.join(IMAGE_DIR, f"source_img_{idx}.png")
        framed.save(out_path, "PNG", quality=95)
        return os.path.abspath(out_path)
    except Exception as e:
        print(f"이미지 가공 실패: {e}")
        return None

def fetch_from_dain_tistory(history):
    """dain2013.tistory.com RSS에서 글과 실제 캡처 이미지를 추출"""
    print("dain2013.tistory.com 에서 글감 탐색 중...")
    rss_url = "https://dain2013.tistory.com/rss"
    try:
        req = urllib.request.Request(rss_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as res:
            root = ET.fromstring(res.read())

        for item in root.findall('.//item'):
            title = item.find('title').text.strip()
            link = item.find('link').text.strip()
            if link in history or title in history:
                continue

            desc_html = item.find('description').text or ""
            soup = BeautifulSoup(desc_html, "html.parser")
            
            # 본문 내 실제 이미지 URL 추출 및 다운로드 (최대 4장)
            saved_images = []
            for img_tag in soup.find_all("img"):
                src = img_tag.get("src") or img_tag.get("data-origin-url")
                if src and src.startswith("http"):
                    try:
                        r = requests.get(src, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                        if r.status_code == 200:
                            processed_path = process_and_frame_image(r.content, len(saved_images) + 1)
                            if processed_path:
                                saved_images.append(processed_path)
                        if len(saved_images) >= 4:
                            break
                    except Exception:
                        pass

            text_content = soup.get_text(separator="\n").strip()
            if len(text_content) > 100:
                print(f"✅ dain2013 글 선정 완료: {title} (추출된 실화면 이미지: {len(saved_images)}장)")
                return {
                    "id": link,
                    "title": title,
                    "content": text_content[:4000],
                    "images": saved_images
                }
    except Exception as e:
        print(f"dain2013 수집 중 예외: {e}")
    return None

def fetch_from_teon_naver(history):
    """blog.naver.com/teon7070 RSS에서 '시놀로지/Synology/NAS' 글과 실제 캡처 이미지 추출"""
    print("blog.naver.com/teon7070 에서 시놀로지 글감 탐색 중...")
    rss_url = "https://rss.blog.naver.com/teon7070.xml"
    try:
        req = urllib.request.Request(rss_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as res:
            root = ET.fromstring(res.read())

        for item in root.findall('.//item'):
            title = item.find('title').text.strip()
            link = item.find('link').text.strip()
            desc_html = item.find('description').text or ""

            # 시놀로지 관련 키워드 필터링
            combined_check = (title + " " + desc_html).lower()
            if not any(k in combined_check for k in ["시놀로지", "synology", "nas", "나스", "도커", "docker"]):
                continue

            if link in history or title in history:
                continue

            # 모바일 상세 페이지로 접속해 원본 본문과 실제 이미지 추출
            log_no_match = re.search(r'/(\d+)$', link) or re.search(r'logNo=(\d+)', link)
            saved_images = []
            full_text = BeautifulSoup(desc_html, "html.parser").get_text(separator="\n")

            if log_no_match:
                log_no = log_no_match.group(1)
                m_url = f"https://m.blog.naver.com/teon7070/{log_no}"
                r = requests.get(m_url, headers={'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)'}, timeout=15)
                if r.status_code == 200:
                    m_soup = BeautifulSoup(r.text, "html.parser")
                    container = m_soup.select_one('.se-main-container, #viewTypeSelector')
                    if container:
                        full_text = container.get_text(separator="\n").strip()
                        for img_tag in container.find_all("img"):
                            src = img_tag.get("data-lazy-src") or img_tag.get("src")
                            if src and src.startswith("http") and "storep" not in src and "profile" not in src:
                                try:
                                    img_res = requests.get(src, headers={'Referer': 'https://m.blog.naver.com/'}, timeout=10)
                                    if img_res.status_code == 200:
                                        p_path = process_and_frame_image(img_res.content, len(saved_images) + 1)
                                        if p_path:
                                            saved_images.append(p_path)
                                    if len(saved_images) >= 4:
                                        break
                                except Exception:
                                    pass

            print(f"✅ teon7070 시놀로지 글 선정 완료: {title} (추출된 실화면 이미지: {len(saved_images)}장)")
            return {
                "id": link,
                "title": title,
                "content": full_text[:4000],
                "images": saved_images
            }
    except Exception as e:
        print(f"teon7070 수집 중 예외: {e}")
    return None


# =====================================================================
# 2. [방식 3] Playwright로 실제 개발 환경(터미널/코드) & 공식 웹 UI 캡처 생성
# =====================================================================
def generate_real_tech_screenshots(p, code_snippet, command_title, doc_url=None):
    """
    1) 실제 VS Code / Ubuntu 터미널 UI 스타일의 설정·구축 화면을 렌더링해 고해상도 캡처
    2) 공식 GitHub/문서 URL이 있으면 실제 웹 화면을 캡처
    """
    generated_files = []
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 1000, "height": 700}, device_scale_factor=2)
    page = context.new_page()

    # ① 실제 개발 환경 / 터미널 설정 화면 HTML 렌더링 후 캡처
    escaped_code = (
        code_snippet.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    terminal_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
        body {{
            margin: 0; padding: 30px;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            font-family: 'NanumGothic', monospace, sans-serif;
            display: flex; justify-content: center; align-items: center;
        }}
        .window {{
            width: 880px; background: #0d1117; border-radius: 12px;
            box-shadow: 0 20px 50px rgba(0,0,0,0.6); border: 1px solid #30363d; overflow: hidden;
        }}
        .titlebar {{
            background: #161b22; padding: 12px 18px; display: flex; align-items: center;
            border-bottom: 1px solid #30363d;
        }}
        .dots {{ display: flex; gap: 8px; margin-right: 16px; }}
        .dot {{ width: 12px; height: 12px; border-radius: 50%; }}
        .red {{ background: #ff5f56; }} .yellow {{ background: #ffbd2e; }} .green {{ background: #27c93f; }}
        .filename {{ color: #8b949e; font-size: 14px; font-weight: bold; }}
        .content {{
            padding: 24px; color: #e6edf3; font-size: 15px; line-height: 1.6;
            white-space: pre-wrap; word-break: break-all; font-family: monospace, 'NanumGothic';
        }}
        .badge {{
            display: inline-block; background: #238636; color: #ffffff;
            padding: 3px 10px; border-radius: 6px; font-size: 12px; margin-left: auto;
        }}
    </style>
    </head>
    <body>
        <div class="window" id="capture-target">
            <div class="titlebar">
                <div class="dots"><div class="dot red"></div><div class="dot yellow"></div><div class="dot green"></div></div>
                <div class="filename">{command_title}</div>
                <div class="badge">ChooSu Note Lab</div>
            </div>
            <div class="content">{escaped_code}</div>
        </div>
    </body>
    </html>
    """
    page.set_content(terminal_html)
    page.wait_for_timeout(500)
    term_path = os.path.abspath(os.path.join(IMAGE_DIR, "env_setup_capture.png"))
    page.locator("#capture-target").screenshot(path=term_path)
    generated_files.append(term_path)
    print(f"✅ [방식 3] 실제 구축/설정 환경 캡처 이미지 생성: {term_path}")

    # ② 공식 문서 / GitHub 저장소 실제 화면 캡처
    if doc_url and doc_url.startswith("http"):
        try:
            page.goto(doc_url, wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(2000)
            web_path = os.path.abspath(os.path.join(IMAGE_DIR, "official_ui_capture.png"))
            page.screenshot(path=web_path, full_page=False)
            generated_files.append(web_path)
            print(f"✅ [방식 3] 공식 레퍼런스 웹 화면 캡처 완료: {web_path}")
        except Exception as e:
            print(f"공식 URL 캡처 건너뜀: {e}")

    browser.close()
    return generated_files


# =====================================================================
# 3. Gemini를 이용해 ChooSu Note 양식으로 글 재구성
# =====================================================================
def generate_article_with_gemini(source_data):
    print("Gemini를 사용해 ChooSu Note 양식으로 글을 작성합니다...")
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")

    client = genai.Client(api_key=api_key)

    if source_data:
        source_prompt = f"""
        아래 [원문 자료]는 내가 이전에 작성했던 기술 블로그 글입니다.
        이 글의 핵심 기술 내용과 단계별 설정 흐름을 바탕으로, 우리 블로그('ChooSu Note')의 
        통합 가이드 양식에 맞춰 깔끔하게 다듬어 재작성해주세요.

        [원문 제목]: {source_data['title']}
        [원문 내용]:
        {source_data['content']}
        """
    else:
        source_prompt = """
        시놀로지 NAS 실전 구축(Docker 컨테이너 활용, 역방향 프록시, 백업 서버 등) 또는 
        실무 PC/개발 환경 구축(Ventoy, WSL2, 네트워크 세팅 등) 중 당장 따라 하기 좋은 실전 주제를 하나 선정해 작성해주세요.
        """

    prompt = f"""
    {source_prompt}

    [필수 작성 양식 - ChooSu Note 스타일]:
    1. 서론 인트로는 반드시 "내가 찾는 건 늘 없었다 (...)" 처럼 흩어져 있는 정보 대신 직접 처음부터 끝까지 하나로 통합해 정리한다는 담백한 톤으로 시작할 것.
    2. 소제목과 섹션에 아래 이모지 구성을 그대로 사용할 것:
       - 📘 [주제 핵심 개요]
       - 📝 [사용 개요 및 권장 환경]
       - 1️⃣ [주요 특징 및 개념]
       - 2️⃣ [사전 준비물]
       - 📅 [초기 설치 및 구축 방법 (①, ②, ③ 단계별 정리)]
       - 💡 [세부 설정 및 실무 팁]
       - 📂 [실사용 연결 방법 및 체크리스트]
       - 🙌 [마무리 한 마디 (1. -> 2. -> 3. 핵심 3줄 요약)]
    3. 절대 마크다운 별표(**)나 마크다운 헤더(##)를 본문에 그대로 노출하지 말 것!
       강조할 단어는 <b>태그를 쓰고, 단락과 줄바꿈을 명확히 할 것.
    4. 본문 중간에 실제 이미지가 들어갈 가장 적절한 위치 2곳에 각각 [IMAGE_1], [IMAGE_2] 표시를 단독 줄로 넣어줄 것.
    5. [CODE_BLOCK] 항목에는 이 글의 가장 핵심이 되는 docker-compose.yml 설정, CLI 명령어, 또는 단계별 설정 요약본(10~18줄 분량)을 적어줄 것 (실제 터미널 캡처 이미지를 만드는 데 사용됨).
    6. [OFFICIAL_URL] 항목에는 관련 오픈소스 공식 GitHub 주소나 공식 다운로드/문서 URL 1개를 적어줄 것 (예: https://github.com/dani-garcia/vaultwarden). 없으면 NONE.

    [출력 포맷]:
    [TAGS] 태그1, 태그2, 태그3, 태그4, 태그5, 태그6
    [OFFICIAL_URL] https://...
    [CODE_TITLE] Terminal / Configuration — Setup
    [CODE_BLOCK]
    여기에 실제 설정 코드나 명령어 요약 작성
    [/CODE_BLOCK]
    [TITLE] 깔끔하고 직관적인 포스팅 제목
    [CONTENT]
    여기에 본문 작성 ([IMAGE_1], [IMAGE_2] 포함)
    """

    response = client.models.generate_content(
        model='gemini-3.8-flash',
        contents=prompt,
    )
    raw = response.text

    # 태그 파싱
    tags = ["시놀로지", "NAS", "홈랩", "구축가이드", "IT팁"]
    if "[TAGS]" in raw:
        try:
            t_str = raw.split("[TAGS]")[1].split("\n")[0].strip()
            tags = [t.strip() for t in t_str.split(",") if t.strip()]
        except Exception:
            pass

    # 공식 URL 파싱
    official_url = None
    if "[OFFICIAL_URL]" in raw:
        try:
            u_str = raw.split("[OFFICIAL_URL]")[1].split("\n")[0].strip()
            if u_str.startswith("http"):
                official_url = u_str
        except Exception:
            pass

    # 코드 타이틀 & 블록 파싱
    code_title = "System Configuration / CLI"
    if "[CODE_TITLE]" in raw:
        try:
            code_title = raw.split("[CODE_TITLE]")[1].split("\n")[0].strip()
        except Exception:
            pass

    code_block = "# Configuration Setup\nversion: '3'\nservices:\n  app:\n    restart: unless-stopped"
    if "[CODE_BLOCK]" in raw and "[/CODE_BLOCK]" in raw:
        try:
            code_block = raw.split("[CODE_BLOCK]")[1].split("[/CODE_BLOCK]")[0].strip()
        except Exception:
            pass

    # 제목 및 본문 파싱
    title = "실무 기준 통합 구축 가이드"
    content = raw
    if "[TITLE]" in raw and "[CONTENT]" in raw:
        title = raw.split("[TITLE]")[1].split("[CONTENT]")[0].strip()
        content = raw.split("[CONTENT]")[1].strip()

    # 마크다운 기호(**) 완전 제거
    title = title.replace("**", "").strip()
    content = content.replace("**", "").strip()

    return {
        "title": title,
        "content": content,
        "tags": tags,
        "official_url": official_url,
        "code_title": code_title,
        "code_block": code_block
    }


# =====================================================================
# 4. 티스토리 에디터에 이미지 실제 업로드 및 본문 발행
# =====================================================================
def upload_image_to_tistory(page, image_path):
    """티스토리 에디터의 숨겨진 input[type='file']을 통해 실제 이미지 파일을 업로드"""
    try:
        file_inputs = page.locator('input[type="file"]')
        if file_inputs.count() > 0:
            file_inputs.first.set_input_files(image_path)
            page.wait_for_timeout(4000) # 이미지 업로드 및 렌더링 대기
            print(f"📸 이미지 업로드 성공: {os.path.basename(image_path)}")
            return True
    except Exception as e:
        print(f"이미지 업로드 중 예외: {e}")
    return False

def post_to_tistory(p, article_data, image_paths):
    print("티스토리 에디터 자동화 시작...")
    raw_cookies = os.environ.get("TISTORY_COOKIE_JSON")
    if not raw_cookies:
        raise ValueError("TISTORY_COOKIE_JSON 환경변수가 없습니다.")

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
            "sameSite": c.get("sameSite") if c.get("sameSite") in ["Strict", "Lax", "None"] else "Lax"
        }
        formatted_cookies.append(cookie_dict)

    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    context.add_cookies(formatted_cookies)
    page = context.new_page()

    # 임시저장 알림창 자동 닫기
    page.on("dialog", lambda dialog: dialog.dismiss())

    write_url = f"https://{BLOG_NAME}.tistory.com/manage/newpost/"
    page.goto(write_url, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)

    if "login" in page.url:
        browser.close()
        raise RuntimeError("티스토리 쿠키가 만료되어 로그인 페이지로 이동되었습니다.")

    # 1. 제목 입력
    title_locator = page.locator('textarea[placeholder="제목을 입력하세요"], #post-title-inp')
    title_locator.wait_for(state="visible", timeout=15000)
    title_locator.fill(article_data["title"])
    print(f"제목 입력 완료: {article_data['title']}")

    # 2. 본문 영역 포커스 및 구간별 텍스트 + 실제 이미지 파일 교차 업로드
    page.click("#editor-root, body")
    page.wait_for_timeout(1000)

    content = article_data["content"]
    # [IMAGE_1], [IMAGE_2] 플레이스홀더 기준으로 본문을 분할하여 사이사이에 실제 이미지 파일 업로드
    segments = re.split(r'\[IMAGE_\d+\]', content)

    for idx, segment in enumerate(segments):
        clean_seg = segment.strip()
        if clean_seg:
            page.keyboard.insert_text(clean_seg + "\n\n")
            page.wait_for_timeout(500)

        # 해당 구간 뒤에 넣을 실제 이미지가 남아있다면 즉시 업로드
        if idx < len(image_paths):
            upload_image_to_tistory(page, image_paths[idx])
            page.keyboard.press("Enter")
            page.wait_for_timeout(500)

    # 남은 이미지가 더 있다면 하단에 추가 업로드
    if len(image_paths) > len(segments):
        for extra_img in image_paths[len(segments):]:
            upload_image_to_tistory(page, extra_img)

    print("본문 및 이미지 삽입 완료.")

    # 3. 완료 레이어 열기
    finish_btn = page.locator('#publish-layer-btn, button:has-text("완료")')
    finish_btn.wait_for(state="visible", timeout=10000)
    finish_btn.click()
    page.wait_for_timeout(2000)

    # 4. 태그 자동 입력
    tag_input = page.locator('#tagText, input[placeholder*="태그"]')
    if tag_input.count() > 0:
        for tag in article_data["tags"]:
            t_clean = tag.strip()
            if t_clean:
                tag_input.fill(t_clean)
                tag_input.press("Enter")
                page.wait_for_timeout(300)
        print(f"태그 입력 완료: {article_data['tags']}")

    # 5. 공개 설정 및 최종 발행
    public_radio = page.locator('label:has-text("공개"), input[value="3"]')
    if public_radio.count() > 0:
        public_radio.first.click()

    submit_btn = page.locator('#publish-btn, button:has-text("발행하기"), button:has-text("발행")')
    submit_btn.wait_for(state="visible", timeout=10000)
    submit_btn.click()

    page.wait_for_timeout(7000)
    print(f"🎉 최종 발행 성공! 현재 URL: {page.url}")
    browser.close()


if __name__ == "__main__":
    history = load_history()

    # 1순위: teon7070 네이버 블로그(시놀로지 글) 탐색 -> 없으면 dain2013 티스토리 탐색
    source_data = fetch_from_teon_naver(history)
    if not source_data:
        source_data = fetch_from_dain_tistory(history)

    # Gemini로 ChooSu Note 스타일 글 생성
    article_data = generate_article_with_gemini(source_data)

    with sync_playwright() as p:
        # [방식 1] 기존 블로그에서 가져온 실제 캡처 이미지 목록
        final_images = source_data["images"] if (source_data and source_data.get("images")) else []

        # [방식 3] 실제 터미널/설정 화면 렌더링 캡처 & 공식 사이트 캡처 추가 생성
        tech_captures = generate_real_tech_screenshots(
            p,
            code_snippet=article_data["code_block"],
            command_title=article_data["code_title"],
            doc_url=article_data["official_url"]
        )

        # 방식 1 이미지와 방식 3 이미지를 합쳐서 본문에 배치 (최대 4장)
        combined_images = (final_images + tech_captures)[:4]
        print(f"총 첨부할 실화면 이미지 개수: {len(combined_images)}장")

        # 티스토리 업로드 및 발행
        post_to_tistory(p, article_data, combined_images)

    # 발행 성공 시 중복 방지를 위해 히스토리 기록
    if source_data:
        save_history(source_data["id"])
