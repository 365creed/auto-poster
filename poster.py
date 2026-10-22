"""
poster.py
ChooSu Note — 세상에서 가장 친절한 컴퓨터 기초 학교 & 가상 OS 실험실
1일 2회 자동 연산 포스팅 (오전 09:00 KST 기초 원리 / 오후 15:00 KST 가상 OS·게임 실습)
+ 저녁 시간대 인간 수동/반자동 포스팅 지원 엔진
"""

import os
import re
import json
import time
import datetime
try:
    from google import genai
except ImportError:
    genai = None

from os_sandbox import generate_virtual_os_screenshots

KST = datetime.timezone(datetime.timedelta(hours=9))
NOW_KST = datetime.datetime.now(KST)
TODAY_STR = NOW_KST.strftime("%Y-%m-%d")
STAMP_STR = NOW_KST.strftime("%Y%m%d_%H%M%S")

HISTORY_FILE = "posted_history.txt"
CURRICULUM_FILE = "curriculum.json"
POSTS_DIR = "_posts"
IMAGE_DIR = f"assets/images/{TODAY_STR}"
BASEURL = "/choosu-lab"

os.makedirs(POSTS_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)


# =====================================================================
# 0. 발행 히스토리 및 커리큘럼 로드
# =====================================================================
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    return []


def save_history(identifier):
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"{identifier}\n")


def detect_slot_info():
    """
    현재 실행 시간(KST) 또는 환경변수(POST_SLOT)를 기반으로
    오전 9시(기초 원리), 오후 3시(가상 OS·게임 실습), 저녁(수동 에디션) 구분
    """
    env_slot = os.environ.get("POST_SLOT", "").strip().lower()
    if env_slot == "manual" or os.environ.get("MANUAL_TITLE", "").strip():
        return {
            "slot_id": "evening_manual",
            "slot_badge": "🌙 저녁 수동 노트 · 에디터 직접 발행",
            "author_type": "Human Editor"
        }
    if env_slot == "morning" or (env_slot == "" and NOW_KST.hour < 12):
        return {
            "slot_id": "morning_auto",
            "slot_badge": "☀️ 오전 9시 기초 수업 · 역사와 원리",
            "author_type": "AI Teacher (09:00 KST)"
        }
    return {
        "slot_id": "afternoon_auto",
        "slot_badge": "🎮 오후 3시 가상 OS 실습 · 클릭 & 게임",
        "author_type": "AI OS Agent (15:00 KST)"
    }


def select_next_lesson(history_list, slot_info):
    """
    1순위: 수동 입력(환경변수 MANUAL_TITLE 등)이 있으면 수동 커리큘럼 생성
    2순위: curriculum.json에서 아직 발행하지 않은 순서의 기초 수업 선택
    3순위: 모든 기본 커리큘럼 완료 시 자동 심화 기초 주제로 확장
    """
    manual_title = os.environ.get("MANUAL_TITLE", "").strip()
    manual_topic = os.environ.get("MANUAL_TOPIC", "").strip()
    manual_scene = os.environ.get("OS_SCENE", "desktop_windows").strip() or "desktop_windows"

    if manual_title:
        return {
            "id": f"manual-{STAMP_STR}",
            "stage": "특별 보충 수업 · 저녁 수동 노트",
            "os_scene": manual_scene,
            "os_type": "가상 OS 맞춤 실습 환경",
            "difficulty": "Lv.1 친절한 해설",
            "title": manual_title,
            "subtitle": manual_topic or "저녁 시간에 직접 정리하며 함께 따라 해보는 컴퓨터 기초 이야기",
            "keywords": ["컴퓨터기초", "수동노트", "친절한가이드", "가상OS실습"],
            "learning_goals": [
                "오늘의 핵심 개념을 일상 속 쉬운 비유로 이해해요.",
                "가상 OS 실습 화면을 보며 마우스와 키보드 동작을 차근차근 따라 해봐요."
            ],
            "prompt_guide": manual_topic or manual_title
        }

    curriculum = []
    if os.path.exists(CURRICULUM_FILE):
        with open(CURRICULUM_FILE, "r", encoding="utf-8") as f:
            curriculum = json.load(f)

    history_set = set(history_list)
    for item in curriculum:
        if item["id"] not in history_set:
            return item

    # 기본 커리큘럼을 모두 소화한 경우 번호를 늘려 다음 단계 기초 주제 자동 구성
    next_num = len(history_list) + 1
    is_afternoon = slot_info["slot_id"] == "afternoon_auto"
    return {
        "id": f"auto-curriculum-{next_num:03d}",
        "stage": "4교시 · AI 가상 OS 게임 실습" if is_afternoon else "1교시 · 컴퓨터의 역사와 근원",
        "os_scene": "game_minesweeper" if is_afternoon else "click_trainer",
        "os_type": "ChooSu 가상 OS 실습실",
        "difficulty": "Lv.1 완전 입문",
        "title": f"[컴퓨터 기초 {next_num}강] 아무것도 몰라도 괜찮아! 가상 OS로 배우는 친절한 컴퓨터 원리와 실습",
        "subtitle": "학교 수업처럼 차근차근 배우는 컴퓨터·노트북의 근원적 작동 원리와 화면 조작법",
        "keywords": ["컴퓨터기초", "노트북입문", "운영체제실습", "마우스클릭", "초보자용"],
        "learning_goals": [
            "컴퓨터와 운영체제가 사람과 대화하는 가장 기초적인 원리를 이해해요.",
            "가상 OS에서 AI가 직접 클릭하고 실행한 화면을 보며 똑같이 따라 해봐요."
        ],
        "prompt_guide": f"컴퓨터를 처음 배우는 입문자를 위한 {next_num}번째 기초 수업입니다. 이전에 다룬 주제들과 겹치지 않게 웹 브라우저 주소창의 원리, 휴지통에서 파일 되살리기, 화면 캡처하기, 소리 조절하기, 와이파이 연결 원리 중 하나를 골라 '자, 이게 클릭이야!' 할 정도로 눈높이를 낮춰 친절하게 설명해 주세요."
    }


# =====================================================================
# 1. Gemini 기초 수업 글 생성 (친절한 학교 선생님 톤 + 마크다운 구조 유지)
# =====================================================================
def generate_friendly_lesson_article(lesson, slot_info):
    manual_body = os.environ.get("MANUAL_BODY", "").strip()
    if manual_body:
        return {
            "title": lesson["title"],
            "subtitle": lesson.get("subtitle", ""),
            "tags": lesson.get("keywords", ["컴퓨터기초", "수동포스팅"]),
            "code_block": "1. 목표 화면 확인하기\n2. 마우스 커서를 천천히 이동하기\n3. 클릭하여 실행 결과 눈으로 확인하기",
            "content": manual_body
        }

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    prompt = f"""
당신은 컴퓨터를 태어나서 처음 만져보는 학생, 어르신, 입문자에게 세상에서 가장 다정하고 명쾌하게 원리를 알려주는 '컴퓨터 기초 학교 선생님'입니다.

[오늘의 수업 정보]
- 수업 단계: {lesson['stage']} ({slot_info['slot_badge']})
- 수업 제목: {lesson['title']}
- 부제목: {lesson.get('subtitle', '')}
- 실습 가상 OS 환경: {lesson.get('os_type', '가상 OS 데스크톱')}
- 핵심 작성 가이드: {lesson['prompt_guide']}

[작성 원칙 — 반드시 지킬 것]
1. 아무것도 모르는 사람도 읽자마자 "아하! 그래서 그렇구나!" 하고 무릎을 탁 칠 수 있도록 일상적인 비유(예: 공부 책상, 서류봉투, 요리사의 주방, 전등 스위치 등)를 적극 활용하세요.
2. "자, 이게 클릭(Click)이야!", "겁먹지 말고 여기를 한 번 눌러볼까요?"처럼 옆에서 손잡고 알려주는 다정하고 친절한 대화체(~해요, ~랍니다, ~해볼까요?)를 사용하세요.
3. 가독성이 뛰어나도록 마크다운 소제목(`##`), 굵은 글씨(`**강조**`), 인용구(`> 💡 선생님의 한 줄 팁`), 번호 목록을 적극 활용하세요.
4. 본문 중간의 가장 적절한 위치 3곳에 반드시 `[IMAGE_1]`, `[IMAGE_2]`, `[IMAGE_3]` 플레이스홀더를 한 번씩 넣어주세요. (가상 OS에서 AI가 직접 조작하고 캡처한 1~3단계 스크린샷이 들어갑니다.)
5. 특정 기업 홍보나 어려운 전문가용 서버 약어 나열은 절대 금지합니다.

[출력 형식]
[TAGS] 태그1, 태그2, 태그3, 태그4, 태그5
[CODE_BLOCK]
오늘의 실습 3단계 핵심 요약 (4~6줄 이내, 가상 OS 화면 안에 표시될 짧은 텍스트)
[/CODE_BLOCK]
[TITLE] {lesson['title']}
[CONTENT]
(여기에 마크다운 본문 작성 — [IMAGE_1], [IMAGE_2], [IMAGE_3] 포함)
"""

    raw = ""
    if api_key and genai is not None:
        client = genai.Client(api_key=api_key)
        model_candidates = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-3.8-flash"]
        for model_name in model_candidates:
            for attempt in range(3):
                try:
                    print(f"[{model_name}] 기초 수업 포스트 생성 시도 ({attempt+1}/3)...")
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt
                    )
                    if response and response.text:
                        raw = response.text
                        break
                except Exception as e:
                    print(f"⚠️ [{model_name}] 호출 예외 (시도 {attempt+1}): {e}")
                    time.sleep(4)
            if raw:
                break

    if not raw:
        print("ℹ️ API 키 미설정 또는 로컬 테스트 환경 감지 — 내장 고품질 기초 수업 교안으로 생성합니다.")
        return build_builtin_lesson_article(lesson)

    tags = lesson.get("keywords", ["컴퓨터기초", "친절한수업", "가상OS실습"])
    if "[TAGS]" in raw:
        parsed_tags = [t.strip() for t in raw.split("[TAGS]")[1].split("\n")[0].split(",") if t.strip()]
        if parsed_tags:
            tags = parsed_tags

    code_block = "1단계: 마우스 화살표(커서)를 목표 아이콘 위에 올리기\n2단계: 왼쪽 버튼 한 번 딸깍(좌클릭)으로 선택하기\n3단계: 연속 두 번 따닥(더블클릭)으로 창 열기!"
    if "[CODE_BLOCK]" in raw and "[/CODE_BLOCK]" in raw:
        code_block = raw.split("[CODE_BLOCK]")[1].split("[/CODE_BLOCK]")[0].strip()

    title = lesson["title"]
    if "[TITLE]" in raw and "[CONTENT]" in raw:
        parsed_title = raw.split("[TITLE]")[1].split("[CONTENT]")[0].strip()
        if parsed_title:
            title = parsed_title

    content = raw.split("[CONTENT]")[1].strip() if "[CONTENT]" in raw else raw
    return {
        "title": title,
        "subtitle": lesson.get("subtitle", ""),
        "tags": tags,
        "code_block": code_block,
        "content": content
    }


def build_builtin_lesson_article(lesson):
    """
    오프라인 테스트 및 초기 샘플 생성 시 작동하는 초친절 입문자용 교안 생성기
    """
    goals_md = "\n".join(f"- ✅ {g}" for g in lesson.get("learning_goals", []))
    content = f"""## 👋 들어가며: 컴퓨터 앞에만 서면 손이 멈추는 분들을 위해

처음 컴퓨터나 노트북 전원을 켜면 화면 가득 알 수 없는 그림(아이콘)들이 떠 있고, 마우스를 조금만 움직여도 작은 화살표가 이리저리 날아다녀서 당황스럽기 마련이에요. **"혹시 내가 잘못 눌러서 컴퓨터가 고장 나면 어쩌지?"** 하고 걱정하신 적 있나요?

걱정하지 마세요! 컴퓨터는 우리가 생각하는 것보다 훨씬 튼튼하고, 원리만 알면 세상에서 가장 친절한 도구가 되어준답니다. 오늘 수업에서는 학교에서 선생님이 바로 옆자리에 앉아 손잡고 알려주듯, **{lesson['title']}**에 대해 가장 근원적인 이야기부터 차근차근 풀어볼게요.

> 💡 **오늘 수업에서 함께 배울 목표**
{goals_md}

[IMAGE_1]

## 1️⃣ 근원부터 이해하기: 왜 이렇게 만들어졌을까요?

우리가 매일 쓰는 기술도 처음부터 지금 같은 모습은 아니었어요. {lesson['prompt_guide']}

컴퓨터 화면 속에 보이는 작은 화살표는 바로 **내 손가락을 대신하는 아바타(커서, Cursor)**예요. 손으로 모니터 유리를 직접 찌르는 대신, 책상 위의 마우스를 살며시 밀면 화면 속 화살표가 똑같은 방향으로 미끄러지듯 따라오죠.

| 동작 이름 | 손가락 움직임 | 컴퓨터가 알아듣는 뜻 | 일상 속 비유 |
| :--- | :--- | :--- | :--- |
| **가리키기 (Hover)** | 버튼은 누르지 않고 화살표만 올리기 | "이 물건이 뭔지 살짝 볼까?" | 상점에서 물건 앞에 서서 구경하기 |
| **클릭 (좌클릭 1번)** | 검지로 왼쪽 버튼을 **'딸깍'** 한 번 누르기 | **"자, 너로 정했어!" (선택/확인)** | 메뉴판에서 원하는 메뉴 손가락으로 짚기 |
| **더블클릭 (연속 2번)** | 검지로 왼쪽 버튼을 빠르게 **'따닥!'** 누르기 | **"문을 열고 안으로 들어가자!" (실행)** | 방문을 똑똑 두드려 활짝 열기 |
| **우클릭 (오른쪽 1번)** | 중지로 오른쪽 버튼을 **'딸깍'** 누르기 | **"여기서 할 수 있는 메뉴판 보여줘!"** | 식당에서 직원분께 추가 메뉴판 요청하기 |

[IMAGE_2]

## 2️⃣ 가상 OS 실험실에서 AI가 직접 해본 단계별 실습

백 번 글로 읽는 것보다 실제 운영체제(OS) 화면에서 어떻게 움직이는지 눈으로 보는 게 가장 빠르겠죠? 저희 블로그의 **가상 OS 실험실**에서 AI가 직접 마우스를 움직이고 클릭하며 촬영한 화면을 함께 살펴봐요!

1. **1단계 (목표 찾기)**: 먼저 바탕화면에서 내가 열고 싶은 아이콘이나 게임 칸을 눈으로 찾은 뒤, 마우스를 천천히 움직여 화살표 끝을 그 위에 올려놓습니다.
2. **2단계 (클릭 & 우클릭 실행)**: 검지손가락으로 마우스 왼쪽 버튼을 가볍게 **'딸깍(Click)'** 누르면 아이콘 색깔이 바뀌며 선택됩니다. 만약 숨겨진 기능을 보고 싶다면 오른쪽 버튼을 눌러보세요!
3. **3단계 (결과 확인하기)**: 프로그램을 열 때는 쉬지 않고 **'따닥!'** 두 번 연속으로 누르는 더블클릭을 합니다. 만약 두 번 누르는 게 너무 느리면 컴퓨터가 "아, 한 번씩 두 번 선택했구나"라고 착각할 수 있으니, 심장이 두근거리듯 **'따-닥!'** 리듬감 있게 눌러주는 것이 비결이에요.

[IMAGE_3]

## 3️⃣ 오늘 배운 내용, 이것만은 꼭 기억해요!

- **클릭(Click)**이라는 말은 마우스 버튼을 누를 때 나는 **'딸깍'** 소리에서 그대로 따온 이름이에요.
- 무언가 잘못 눌렀거나 낯선 메뉴판이 튀어나왔을 때는 당황하지 말고 **빈 바탕화면을 왼쪽 클릭 한 번** 하거나, 키보드 왼쪽 맨 위의 **`Esc` (탈출) 키**를 누르면 언제든 안전하게 원래대로 돌아갑니다.
- 다음 시간에도 가상 OS 환경에서 직접 미니게임을 플레이하고 창을 다루면서 컴퓨터와 더 친해지는 시간을 가져볼게요!
"""
    return {
        "title": lesson["title"],
        "subtitle": lesson.get("subtitle", ""),
        "tags": lesson.get("keywords", ["컴퓨터기초", "클릭이란", "가상OS실습"]),
        "code_block": "1단계: 마우스 화살표를 아이콘 정중앙에 올리기 (Hover)\n2단계: 왼쪽 버튼 한 번 '딸깍!' 눌러 선택하기 (Click)\n3단계: 왼쪽 버튼 두 번 '따닥!' 눌러 창 열기 (Double Click)\n4단계: 오른쪽 버튼 '딸깍!' 눌러 보조 메뉴판 부르기 (Right Click)",
        "content": content
    }


# =====================================================================
# 2. 마크다운 포스트 발행 (예쁜 레이아웃 & 이미지 캡션 카드 적용)
# =====================================================================
def publish_post(lesson, article, slot_info, image_paths):
    content = article["content"]

    step_titles = [
        "🖥️ [가상 OS 실습 1단계] 시작 화면과 목표 위치 확인하기",
        "🖱️ [가상 OS 실습 2단계] AI가 직접 마우스 클릭 및 조작을 수행하는 순간",
        "🎉 [가상 OS 실습 3단계] 실행 완료 화면 및 핵심 원리 정리"
    ]

    for idx, img_path in enumerate(image_paths):
        placeholder = f"[IMAGE_{idx+1}]"
        clean_img_path = img_path if img_path.startswith("/") else f"/{img_path}"
        caption = step_titles[idx] if idx < len(step_titles) else f"가상 OS 실습 화면 {idx+1}"
        md_img = (
            f'\n\n<figure class="os-screenshot-card">\n'
            f'  <div class="os-screenshot-bar"><span>🔴 🟡 🟢</span><span class="os-bar-title">{caption}</span></div>\n'
            f'  <img src="{clean_img_path}" alt="{caption}" loading="lazy" />\n'
            f'  <figcaption>{caption}</figcaption>\n'
            f'</figure>\n\n'
        )
        if placeholder in content:
            content = content.replace(placeholder, md_img, 1)
        else:
            content += md_img

    content = re.sub(r'\[IMAGE_\d+\]', '', content)

    tags_yaml = ", ".join(f'"{t}"' for t in article["tags"])
    thumb_url = image_paths[1] if len(image_paths) > 1 else (image_paths[0] if image_paths else "")
    safe_title = article["title"].replace('"', '\\"')
    safe_subtitle = article.get("subtitle", "").replace('"', '\\"')

    front_matter = f"""---
layout: post
title: "{safe_title}"
subtitle: "{safe_subtitle}"
date: {NOW_KST.strftime('%Y-%m-%d %H:%M:%S +0900')}
stage: "{lesson.get('stage', '기초 컴퓨터 수업')}"
slot_id: "{slot_info['slot_id']}"
slot_badge: "{slot_info['slot_badge']}"
os_type: "{lesson.get('os_type', 'ChooSu Virtual OS')}"
difficulty: "{lesson.get('difficulty', 'Lv.1 완전 입문')}"
thumbnail: "{thumb_url}"
tags: [{tags_yaml}]
---

"""

    post_filename = f"{TODAY_STR}-{lesson['id']}-{STAMP_STR}.md"
    post_filepath = os.path.join(POSTS_DIR, post_filename)

    with open(post_filepath, "w", encoding="utf-8") as f:
        f.write(front_matter + content)
    print(f"✅ 기초 컴퓨터 수업 포스트 생성 완료: {post_filepath}")
    return post_filepath


# =====================================================================
# 3. 메인 실행 파이프라인
# =====================================================================
if __name__ == "__main__":
    history_list = load_history()
    slot_info = detect_slot_info()
    lesson = select_next_lesson(history_list, slot_info)

    print(f"📌 선택된 커리큘럼: [{lesson['stage']}] {lesson['title']}")
    article = generate_friendly_lesson_article(lesson, slot_info)

    print(f"🖥️ 가상화 OS 환경({lesson.get('os_scene', 'click_trainer')}) 구동 및 AI 실습 스크린샷 3장 촬영 중...")
    os_images = generate_virtual_os_screenshots(
        scene_type=lesson.get("os_scene", "click_trainer"),
        lesson_title=article["title"],
        image_dir=IMAGE_DIR,
        stamp_str=STAMP_STR,
        code_or_summary=article["code_block"],
        baseurl=BASEURL
    )

    publish_post(lesson, article, slot_info, os_images)
    save_history(lesson["id"])
