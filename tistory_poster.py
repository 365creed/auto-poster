import os
import re
import datetime
import requests
import urllib.request
import xml.etree.ElementTree as ET
from io import BytesIO
from bs4 import BeautifulSoup
from PIL import Image, ImageOps
from google import genai
from playwright.sync_api import sync_playwright

HISTORY_FILE = "posted_history.txt"
TODAY_STR = datetime.datetime.now().strftime("%Y-%m-%d")
STAMP_STR = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

POSTS_DIR = "_posts"
IMAGE_DIR = f"assets/images/{TODAY_STR}"
os.makedirs(POSTS_DIR, exist_ok=True)
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
# 1. [방식 1] 기존 블로그(dain2013, teon7070) 글 & 실제 이미지 추출
# =====================================================================
def process_and_frame_image(img_bytes, idx):
    """원본 이미지를 다크 프레임 가공 후 assets/images 폴더에 저장"""
    try:
        img = Image.open(BytesIO(img_bytes)).convert("RGB")
        if img.width < 250 or img.height < 150:
            return None
        
        if img.width > 900:
            ratio = 900 / float(img.width)
            new_height = int(float(img.height) * ratio)
            img = img.resize((900, new_height), Image.Resampling.LANCZOS)

        framed = ImageOps.expand(img, border=10, fill="#1e293b")
        filename = f"capture_{STAMP_STR}_{idx}.png"
        out_path = os.path.join(IMAGE_DIR, filename)
        framed.save(out_path, "PNG", quality=95)
        # 마크다운에서 불러올 상대 경로 반환
        return f"../{IMAGE_DIR}/{filename}"
    except Exception as e:
        print(f"이미지 가공 실패: {e}")
        return None

def fetch_from_dain_tistory(history):
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
            
            saved_images = []
            for img_tag in soup.find_all("img"):
                src = img_tag.get("src") or img_tag.get("data-origin-url")
                if src and src.startswith("http"):
                    try:
                        r = requests.get(src, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                        if r.status_code == 200:
                            rel_path = process_and_frame_image(r.content, len(saved_images) + 1)
                            if rel_path:
                                saved_images.append(rel_path)
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
    print("blog.naver.com/teon7070 에서 시놀로지 기술 글감 탐색 중...")
    rss_url = "https://rss.blog.naver.com/teon7070.xml"
    try:
        req = urllib.request.Request(rss_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as res:
            root = ET.fromstring(res.read())

        for item in root.findall('.//item'):
            title = item.find('title').text.strip()
            link = item.find('link').text.strip()
            desc_html = item.find('description').text or ""

            if any(skip_word in title for skip_word in ["견적", "납품", "출고", "도입 사례", "견적사례"]):
                continue

            combined_check = (title + " " + desc_html).lower()
            if not any(k in combined_check for k in ["시놀로지", "synology", "nas", "나스", "도커", "docker", "설정", "백업", "가이드"]):
                continue

            if link in history or title in history:
                continue

            log_no_match = re.search(r'/(\d+)$', link) or re.search(r'logNo=(\d+)', link)
            saved_images = []
            full_text = BeautifulSoup(desc_html, "html.parser").get_text(separator="\n")

            if log_no_match:
                log_no = log_no_match.group(1)
                m_url = f"https://m.blog.naver.com/PostView.naver?blogId=teon7070&logNo={log_no}"
                r = requests.get(m_url, headers={'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)'}, timeout=15)
                if r.status_code == 200:
                    m_soup = BeautifulSoup(r.text, "html.parser")
                    container = m_soup.select_one('.se-main-container, #viewTypeSelector, .post_ct')
                    if container:
                        full_text = container.get_text(separator="\n").strip()
                        for img_tag in container.find_all("img"):
                            src = img_tag.get("data-lazy-src") or img_tag.get("src")
                            if src and ("pstatic.net" in src or "blogfiles" in src or "postfiles" in src):
                                if any(ignore in src for ignore in ["storep", "profile", "sticker", "icon"]):
                                    continue
                                try:
                                    img_res = requests.get(src, headers={'Referer': 'https://m.blog.naver.com/'}, timeout=10)
                                    if img_res.status_code == 200:
                                        rel_path = process_and_frame_image(img_res.content, len(saved_images) + 1)
                                        if rel_path:
                                            saved_images.append(rel_path)
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
# 2. [방식 3] Playwright로 실제 개발/설정 환경 & 공식 웹 화면 캡처
# =====================================================================
def generate_real_tech_screenshots(code_snippet, command_title, doc_url=None):
    generated_rel_paths = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1000, "height": 700}, device_scale_factor=2)
        page = context.new_page()

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
        term_filename = f"env_setup_{STAMP_STR}.png"
        term_path = os.path.join(IMAGE_DIR, term_filename)
        page.locator("#capture-target").screenshot(path=term_path)
        generated_rel_paths.append(f"../{IMAGE_DIR}/{term_filename}")
        print(f"✅ [방식 3] 실제 구축/설정 환경 캡처 이미지 생성: {term_path}")

        if doc_url and doc_url.startswith("http"):
            try:
                page.goto(doc_url, wait_until="domcontentloaded", timeout=15000)
                page.wait_for_timeout(2000)
                web_filename = f"official_ui_{STAMP_STR}.png"
                web_path = os.path.join(IMAGE_DIR, web_filename)
                page.screenshot(path=web_path, full_page=False)
                generated_rel_paths.append(f"../{IMAGE_DIR}/{web_filename}")
                print(f"✅ [방식 3] 공식 레퍼런스 웹 화면 캡처 완료: {web_path}")
            except Exception as e:
                print(f"공식 URL 캡처 건너뜀: {e}")

        browser.close()
    return generated_rel_paths


# =====================================================================
# 3. Gemini를 이용해 ChooSu Note 양식으로 글 생성
# =====================================================================
def generate_article_with_gemini(source_data):
    print("Gemini를 사용해 ChooSu Note 양식으로 글을 작성합니다...")
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")

    client = genai.Client(api_key=api_key)

    if source_data:
        source_prompt = f"""
        아래 [원문 자료]는 내가 작성했던 기술 블로그 글입니다.
        특정 회사명이나 영업 멘트는 제거하고, 독자에게 실질적인 도움이 되는 
        '실전 하드웨어/인프라/설정 통합 가이드'로 우리 블로그('ChooSu Note') 양식에 맞춰 재작성해주세요.

        [원문 제목]: {source_data['title']}
        [원문 내용]:
        {source_data['content']}
        """
    else:
        source_prompt = """
        시놀로지 NAS 실전 구축(Docker 컨테이너, 백업 자동화, 역방향 프록시 등) 또는 
        실무 PC/개발 환경 세팅 중 실용적인 주제를 하나 선정해 작성해주세요.
        """

    prompt = f"""
    {source_prompt}

    [필수 작성 양식 - ChooSu Note 스타일]:
    1. 서론 인트로는 반드시 "내가 찾는 건 늘 없었다 (...)" 처럼 파편화된 정보 대신 처음부터 끝까지 하나로 통합해 정리한다는 담백한 독백으로 시작할 것.
    2. 소제목과 섹션에 아래 이모지 구성을 그대로 사용할 것:
       - ### 📘 [주제 핵심 개요]
       - ### 📝 [사용 개요 및 권장 환경]
       - ### 1️⃣ [주요 특징 및 스펙/개념]
       - ### 2️⃣ [사전 준비물 및 환경]
       - ### 📅 [단계별 구축 및 활용 방법 (①, ②, ③)]
       - ### 💡 [세부 설정 및 실무 기준 요약 표] (마크다운 표 포함)
       - ### 📂 [실사용 체크리스트 및 팁]
       - ### 🙌 [마무리 한 마디 (1. -> 2. -> 3. 핵심 3줄 요약)]
    3. 본문 중간에 이미지가 들어갈 위치 3곳에 각각 [IMAGE_1], [IMAGE_2], [IMAGE_3] 표시를 단독 줄로 넣어줄 것.
    4. [CODE_BLOCK] 항목에는 이 글의 가장 핵심이 되는 설정값 요약, 하드웨어/시스템 구성 요약, 또는 CLI 명령어(10~15줄 분량)를 적어줄 것.
    5. [OFFICIAL_URL] 항목에는 관련 공식 사이트나 오픈소스 URL 1개를 적어줄 것. 없으면 NONE.

    [출력 포맷]:
    [TAGS] 태그1, 태그2, 태그3, 태그4, 태그5
    [OFFICIAL_URL] https://...
    [CODE_TITLE] System Specs & Configuration Summary
    [CODE_BLOCK]
    여기에 핵심 요약이나 설정 코드 작성
    [/CODE_BLOCK]
    [TITLE] 깔끔하고 직관적인 포스팅 제목
    [CONTENT]
    여기에 마크다운 본문 작성 ([IMAGE_1], [IMAGE_2], [IMAGE_3] 포함)
    """

    response = client.models.generate_content(
        model='gemini-3.8-flash',
        contents=prompt,
    )
    raw = response.text

    tags = ["시놀로지", "NAS", "홈랩", "구축가이드", "IT팁"]
    if "[TAGS]" in raw:
        try:
            t_str = raw.split("[TAGS]")[1].split("\n")[0].strip()
            tags = [t.strip() for t in t_str.split(",") if t.strip()]
        except Exception:
            pass

    official_url = None
    if "[OFFICIAL_URL]" in raw:
        try:
            u_str = raw.split("[OFFICIAL_URL]")[1].split("\n")[0].strip()
            if u_str.startswith("http"):
                official_url = u_str
        except Exception:
            pass

    code_title = "System Configuration / Summary"
    if "[CODE_TITLE]" in raw:
        try:
            code_title = raw.split("[CODE_TITLE]")[1].split("\n")[0].strip()
        except Exception:
            pass

    code_block = "# System Summary\n- Check Environment\n- Apply Optimal Settings"
    if "[CODE_BLOCK]" in raw and "[/CODE_BLOCK]" in raw:
        try:
            code_block = raw.split("[CODE_BLOCK]")[1].split("[/CODE_BLOCK]")[0].strip()
        except Exception:
            pass

    title = "실무 기준 통합 가이드"
    content = raw
    if "[TITLE]" in raw and "[CONTENT]" in raw:
        title = raw.split("[TITLE]")[1].split("[CONTENT]")[0].strip()
        content = raw.split("[CONTENT]")[1].strip()

    title = title.replace("**", "").replace('"', "'").strip()

    return {
        "title": title,
        "content": content,
        "tags": tags,
        "official_url": official_url,
        "code_title": code_title,
        "code_block": code_block
    }


# =====================================================================
# 4. GitHub Pages (_posts 폴더)에 마크다운 포스트로 영구 발행 (에러율 0%)
# =====================================================================
def publish_to_github_pages(article_data, image_rel_paths):
    content = article_data["content"]

    # [IMAGE_1], [IMAGE_2] 위치에 GitHub Pages 표준 경로로 이미지 삽입
    for idx, img_path in enumerate(image_rel_paths):
        placeholder = f"[IMAGE_{idx+1}]"
        # '../assets/...' 형태를 '/auto-poster/assets/...' 형태로 보정
        clean_path = img_path.replace("../", "/auto-poster/")
        md_img = f"\n\n![실제 구축 및 상세 화면 {idx+1}]({clean_path})\n\n"
        if placeholder in content:
            content = content.replace(placeholder, md_img, 1)
        else:
            content += md_img

    content = re.sub(r'\[IMAGE_\d+\]', '', content)

    tags_yaml = ", ".join(f'"{t}"' for t in article_data["tags"])
    front_matter = f"""---
layout: default
title: "{article_data['title']}"
date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S +0900')}
tags: [{tags_yaml}]
---

# {article_data['title']}

> 🏷️ **태그:** {', '.join(article_data['tags'])}

---

"""

    post_filename = f"{TODAY_STR}-post-{STAMP_STR}.md"
    post_filepath = os.path.join(POSTS_DIR, post_filename)

    with open(post_filepath, "w", encoding="utf-8") as f:
        f.write(front_matter + content)

    print(f"🎉 GitHub Pages 포스팅 파일 생성 완료: {post_filepath} (삽입된 실제 이미지: {len(image_rel_paths)}장)")


if __name__ == "__main__":
    history = load_history()

    source_data = fetch_from_dain_tistory(history)
    if not source_data:
        source_data = fetch_from_teon_naver(history)

    article_data = generate_article_with_gemini(source_data)

    final_images = source_data["images"] if (source_data and source_data.get("images")) else []
    tech_captures = generate_real_tech_screenshots(
        code_snippet=article_data["code_block"],
        command_title=article_data["code_title"],
        doc_url=article_data["official_url"]
    )

    combined_images = (final_images + tech_captures)[:5]
    publish_to_github_pages(article_data, combined_images)

    if source_data:
        save_history(source_data["id"])
