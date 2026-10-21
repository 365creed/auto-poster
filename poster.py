import os
import re
import datetime
import requests
import urllib.request
import xml.etree.ElementTree as ET
from io import BytesIO
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont, ImageOps
from google import genai

HISTORY_FILE = "posted_history.txt"
TODAY_STR = datetime.datetime.now().strftime("%Y-%m-%d")
STAMP_STR = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

POSTS_DIR = "_posts"
IMAGE_DIR = f"assets/images/{TODAY_STR}"
os.makedirs(POSTS_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def save_history(identifier):
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"{identifier}\n")

# 원문 이미지 가공
def process_and_frame_image(img_bytes, idx):
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
        return f"/auto-poster/{IMAGE_DIR}/{filename}"
    except Exception as e:
        print(f"이미지 가공 실패: {e}")
        return None

# dain2013 RSS 수집
def fetch_source(history):
    rss_url = "https://dain2013.tistory.com/rss"
    try:
        req = urllib.request.Request(rss_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as res:
            root = ET.fromstring(res.read())

        for item in root.findall('.//item'):
            title = item.find('title').text.strip()
            link = item.find('link').text.strip()
            if link in history:
                continue

            desc_html = item.find('description').text or ""
            soup = BeautifulSoup(desc_html, "html.parser")
            
            saved_images = []
            for img_tag in soup.find_all("img"):
                src = img_tag.get("src") or img_tag.get("data-origin-url")
                if src and src.startswith("http"):
                    try:
                        r = requests.get(src, timeout=10)
                        if r.status_code == 200:
                            rel_path = process_and_frame_image(r.content, len(saved_images) + 1)
                            if rel_path:
                                saved_images.append(rel_path)
                        if len(saved_images) >= 2:
                            break
                    except Exception:
                        pass

            return {
                "id": link,
                "title": title,
                "content": soup.get_text(separator="\n").strip()[:3500],
                "images": saved_images
            }
    except Exception as e:
        print(f"RSS 수집 예외: {e}")
    return None

# PIL 기반 터미널 캡처 이미지 생성
def create_code_screenshot_pil(code_text, title_text, filename="terminal_capture.png"):
    width = 900
    lines = code_text.strip().split("\n")
    line_height = 28
    height = max(320, 120 + len(lines) * line_height)

    img = Image.new("RGB", (width, height), color="#0d1117")
    draw = ImageDraw.Draw(img)

    draw.rectangle([(0, 0), (width, 48)], fill="#161b22")
    draw.ellipse([(20, 18), (32, 30)], fill="#ff5f56")
    draw.ellipse([(42, 18), (54, 30)], fill="#ffbd2e")
    draw.ellipse([(64, 18), (76, 30)], fill="#27c93f")

    font_paths = [
        "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
    ]
    font_title = ImageFont.load_default()
    font_code = ImageFont.load_default()
    for fp in font_paths:
        if os.path.exists(fp):
            font_title = ImageFont.truetype(fp, 16)
            font_code = ImageFont.truetype(fp, 15)
            break

    draw.text((95, 15), f"{title_text} — ChooSu Note Lab", fill="#8b949e", font=font_title)

    y_text = 70
    for idx, line in enumerate(lines):
        draw.text((25, y_text), f"{idx+1:02d}", fill="#484f58", font=font_code)
        draw.text((65, y_text), line[:85], fill="#e6edf3", font=font_code)
        y_text += line_height

    framed = ImageOps.expand(img, border=4, fill="#30363d")
    out_filename = f"term_{STAMP_STR}.png"
    out_path = os.path.abspath(os.path.join(IMAGE_DIR, out_filename))
    framed.save(out_path, "PNG")
    return f"/auto-poster/{IMAGE_DIR}/{out_filename}"

# Gemini 글 생성
import time

# Gemini 글 생성 (503 에러 자동 재시도 방어 로직 추가)
def generate_article(source_data):
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    base_info = f"참고 원문 제목: {source_data['title']}\n내용:\n{source_data['content']}" if source_data else "시놀로지 NAS 또는 실무 PC 세팅 가이드"

    prompt = f"""
    {base_info}

    위 내용을 바탕으로 'ChooSu Note' 스타일의 기술 블로그 글을 작성해주세요.
    - 서론: "내가 찾는 건 늘 없었다 (...)" 스타일의 담백한 독백으로 시작
    - 섹션 이모지: 📘, 📝, 1️⃣, 2️⃣, 📅, 💡, 📂, 🙌 순서로 구성
    - 마크다운 별표(**)나 샵(##) 기호 금지! 순수 텍스트와 줄바꿈으로만 구성.
    - [CODE_BLOCK] 안에는 핵심 설정값이나 CLI 명령어 요약 8~12줄을 작성할 것.

    출력 형식:
    [TAGS] 태그1, 태그2, 태그3, 태그4, 태그5
    [CODE_BLOCK]
    설정 요약 텍스트
    [/CODE_BLOCK]
    [TITLE] 포스팅 제목
    [CONTENT]
    본문 텍스트 ([IMAGE_1], [IMAGE_2] 위치 포함)
    """

    # 503 에러 대비 최대 3회 재시도 루프
    max_retries = 3
    raw = ""
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',  # 안정적인 모델로 변경
                contents=prompt
            )
            raw = response.text.replace("**", "")
            break
        except Exception as e:
            print(f"⚠️ Gemini API 요청 실패 (시도 {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(5)  # 5초 대기 후 재시도
            else:
                raise e

    tags = ["시놀로지", "홈랩", "IT가이드", "서버구축"]
    if "[TAGS]" in raw:
        tags = [t.strip() for t in raw.split("[TAGS]")[1].split("\n")[0].split(",") if t.strip()]

    code_block = "1. Check System Environment\n2. Configure Storage Path\n3. Apply Network & Firewall Rules\n4. Verify Service Status"
    if "[CODE_BLOCK]" in raw and "[/CODE_BLOCK]" in raw:
        code_block = raw.split("[CODE_BLOCK]")[1].split("[/CODE_BLOCK]")[0].strip()

    title = raw.split("[TITLE]")[1].split("[CONTENT]")[0].strip() if "[TITLE]" in raw else "실전 IT 환경 구축 통합 가이드"
    content = raw.split("[CONTENT]")[1].strip() if "[CONTENT]" in raw else raw

    return {"title": title, "content": content, "tags": tags, "code_block": code_block}

    title = raw.split("[TITLE]")[1].split("[CONTENT]")[0].strip() if "[TITLE]" in raw else "실전 IT 환경 구축 통합 가이드"
    content = raw.split("[CONTENT]")[1].strip() if "[CONTENT]" in raw else raw

    return {"title": title, "content": content, "tags": tags, "code_block": code_block}

# GitHub Pages 마크다운 파일 생성
def publish_post(article, image_paths):
    content = article["content"]
    for idx, img_path in enumerate(image_paths):
        placeholder = f"[IMAGE_{idx+1}]"
        md_img = f"\n\n![실제 화면 {idx+1}]({img_path})\n\n"
        if placeholder in content:
            content = content.replace(placeholder, md_img, 1)
        else:
            content += md_img

    content = re.sub(r'\[IMAGE_\d+\]', '', content)

    tags_yaml = ", ".join(f'"{t}"' for t in article["tags"])
    front_matter = f"""---
layout: default
title: "{article['title']}"
date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S +0900')}
tags: [{tags_yaml}]
---

# {article['title']}

> 🏷️ **태그:** {', '.join(article['tags'])}

---

"""

    post_filename = f"{TODAY_STR}-post-{STAMP_STR}.md"
    post_filepath = os.path.join(POSTS_DIR, post_filename)

    with open(post_filepath, "w", encoding="utf-8") as f:
        f.write(front_matter + content)
    print(f"포스트 파일 생성 완료: {post_filepath}")

if __name__ == "__main__":
    hist = load_history()
    src = fetch_source(hist)
    art = generate_article(src)

    term_img = create_code_screenshot_pil(art["code_block"], art["title"][:20])
    all_imgs = (src["images"] if src and src.get("images") else []) + [term_img]

    publish_post(art, all_imgs[:3])
    if src:
        save_history(src["id"])
