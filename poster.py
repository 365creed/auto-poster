import time

def generate_article(source_data):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")

    client = genai.Client(api_key=api_key)
    base_info = f"참고 원문 제목: {source_data['title']}\n내용:\n{source_data['content']}" if source_data else "시놀로지 NAS 또는 실무 PC 세팅 가이드"

    prompt = f"""
    {base_info}

    위 내용을 바탕으로 'ChooSu Note' 개인 기술 블로그 스타일의 가이드 글을 작성해주세요.
    
    [절대 금지 및 보안 사항]:
    - '다인엔시스', 특정 기업명, 영업 멘트, 견적 문의, 납품 안내 같은 홍보성 문구는 절대 포함하지 마세요.
    - 마크다운 별표(**)나 샵(##) 기호 사용 금지! 순수 텍스트와 줄바꿈으로만 구성할 것.

    [작성 양식]:
    - 서론: "내가 찾는 건 늘 없었다 (...)" 스타일의 담백한 독백으로 시작
    - 섹션 이모지: 📘, 📝, 1️⃣, 2️⃣, 📅, 💡, 📂, 🙌 순서로 구성
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

    # 503 에러 대비: 최대 5회 재시도하며 점진적으로 대기 시간 증가 (10초, 20초, 30초...)
    max_retries = 5
    raw = ""

    for attempt in range(max_retries):
        try:
            print(f"[gemini-3.8-flash] 글 생성 시도 (시도 {attempt+1}/{max_retries})...")
            response = client.models.generate_content(
                model='gemini-3.8-flash',
                contents=prompt
            )
            raw = response.text.replace("**", "")
            if raw:
                break
        except Exception as e:
            print(f"⚠️ 요청 실패 (시도 {attempt+1}): {e}")
            if attempt < max_retries - 1:
                sleep_sec = (attempt + 1) * 10
                print(f"⏳ 서버 혼잡으로 {sleep_sec}초 대기 후 다시 시도합니다...")
                time.sleep(sleep_sec)
            else:
                raise RuntimeError("gemini-3.8-flash가 지속적인 503 에러로 응답하지 않습니다.")

    if not raw:
        raise RuntimeError("AI 응답 내용이 비어 있습니다.")

    tags = ["시놀로지", "홈랩", "IT가이드", "서버구축"]
    if "[TAGS]" in raw:
        tags = [t.strip() for t in raw.split("[TAGS]")[1].split("\n")[0].split(",") if t.strip()]

    code_block = "1. Check System Environment\n2. Configure Storage Path\n3. Apply Network & Firewall Rules\n4. Verify Service Status"
    if "[CODE_BLOCK]" in raw and "[/CODE_BLOCK]" in raw:
        code_block = raw.split("[CODE_BLOCK]")[1].split("[/CODE_BLOCK]")[0].strip()

    title = raw.split("[TITLE]")[1].split("[CONTENT]")[0].strip() if "[TITLE]" in raw else "실전 IT 환경 구축 통합 가이드"
    content = raw.split("[CONTENT]")[1].strip() if "[CONTENT]" in raw else raw

    return {"title": title, "content": content, "tags": tags, "code_block": code_block}

def publish_post(article, image_paths):
    content = article["content"]
    
    # 법적 AI 고지 문구 자동 삽입 (상단)
    legal_header = """
> ⚖️ **법적 고지 및 안내:** 본 포스팅에 포함된 텍스트 및 기술 가이드는 정확성 향상과 효율적인 정보 전달을 위해 **AI(인공지능) 자동화 기술을 활용하여 생성 및 검수**되었습니다.
---
"""
    content = legal_header + "\n" + content

    for idx, img_path in enumerate(image_paths):
        placeholder = f"[IMAGE_{idx+1}]"
        md_img = f"\n\n![실제 구축 및 상세 화면 {idx+1}]({img_path})\n\n"
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
