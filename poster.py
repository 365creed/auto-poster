"""
poster.py
[생산 전담: 제미나이(Gemini) Virtual OS Test & Post Producer]
- 하루 2회(오전 09:00 KST, 오후 15:00 KST) 가상화 OS 환경에서 직접 PC 이름 바꾸기, 마우스 클릭,
  지뢰찾기 게임, 바탕화면 설정 등을 테스트하고 3단계 스크린샷을 찍어 초보자 눈높이 포스팅을 생산합니다.
- 생산 직후 GPT Think 검증기(verifier_gpt_think.py)를 호출해 검증 통과 인증을 받은 뒤 Git에 반영합니다.
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
from verifier_gpt_think import verify_post_and_os_test

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


def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    return []


def save_history(identifier):
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"{identifier}\n")


def detect_slot_info():
    env_slot = os.environ.get("POST_SLOT", "").strip().lower()
    if env_slot == "manual" or os.environ.get("MANUAL_TITLE", "").strip():
        return {
            "slot_id": "evening_manual",
            "slot_badge": "🌙 저녁 수동 노트 · 에디터 & GPT Think 검증",
            "author_type": "Human Editor + GPT Think QA"
        }
    if env_slot == "morning" or (env_slot == "" and NOW_KST.hour < 12):
        return {
            "slot_id": "morning_auto",
            "slot_badge": "☀️ 오전 9시 기초·설정 실습 (Gemini 가상OS 테스트)",
            "author_type": "Gemini Producer (09:00 KST)"
        }
    return {
        "slot_id": "afternoon_auto",
        "slot_badge": "🎮 오후 3시 가상OS·게임 실습 (Gemini 가상OS 테스트)",
        "author_type": "Gemini OS Agent (15:00 KST)"
    }


def select_next_lesson(history_list, slot_info):
    manual_title = os.environ.get("MANUAL_TITLE", "").strip()
    manual_topic = os.environ.get("MANUAL_TOPIC", "").strip()
    manual_scene = os.environ.get("OS_SCENE", "pc_rename").strip() or "pc_rename"

    if manual_title:
        return {
            "id": f"manual-{STAMP_STR}",
            "stage": "방과후 보충 수업 · 저녁 수동 노트",
            "os_scene": manual_scene,
            "os_type": "Argon 가상 OS 맞춤 테스트",
            "difficulty": "Lv.1 친절한 해설",
            "title": manual_title,
            "subtitle": manual_topic or "저녁 시간에 직접 정리하며 가상 OS 테스트 화면과 함께 살펴보는 기초 가이드",
            "keywords": ["컴퓨터기초", "수동노트", "가상OS테스트", "컴맹탈출"],
            "learning_goals": [
                "오늘의 핵심 설정과 원리를 일상 속 쉬운 비유로 이해해요.",
                "제미나이가 가상 OS에서 테스트한 화면을 보며 똑같이 따라 해봐요."
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

    next_num = len(history_list) + 1
    is_afternoon = slot_info["slot_id"] == "afternoon_auto"
    return {
        "id": f"auto-curriculum-{next_num:03d}",
        "stage": "실습 교시 · 가상 OS 테스트" if is_afternoon else "실전 교시 · 컴맹 필수 설정",
        "os_scene": "game_minesweeper" if is_afternoon else "pc_rename",
        "os_type": "Argon Virtual OS Sandbox",
        "difficulty": "Lv.1 완전 입문",
        "title": f"[컴맹 탈출 {next_num}강] 제미나이가 가상 OS에서 직접 눌러보고 알려주는 초간단 컴퓨터 설정",
        "subtitle": "아무것도 모르는 분도 사진 속 노란 동그라미만 따라 누르면 끝나는 친절한 실습 교실",
        "keywords": ["컴퓨터기초", "노트북설정", "가상OS테스트", "컴맹탈출"],
        "learning_goals": [
            "컴퓨터를 처음 켰을 때 가장 당황스러운 설정을 3단계 클릭으로 해결해요.",
            "가상 OS에서 사전 테스트된 안전한 화면을 보며 겁먹지 않고 따라 해요."
        ],
        "prompt_guide": f"컴퓨터 초보자가 가장 자주 검색하는 기초 설정 {next_num}번째 수업입니다."
    }


def build_builtin_lesson_article(lesson):
    goals_md = "\n".join(f"- ✅ {g}" for g in lesson.get("learning_goals", []))
    scene = lesson.get("os_scene", "pc_rename")

    if scene == "pc_rename":
        content = f"""## 👋 들어가며: "DESKTOP-8F9K2A1이 누구 컴퓨터야?" 당황하셨나요?

새로 산 노트북이나 컴퓨터에 블루투스 이어폰을 연결하려거나, 집에서 와이파이(공유기)에 연결된 기기를 확인할 때 **`DESKTOP-8F9K2A1`**처럼 알 수 없는 영어와 숫자가 섞인 이름을 본 적이 있으신가요? 아무것도 모르는 상태에서는 *"어? 누가 내 컴퓨터에 해킹 프로그램을 깔았나?"* 하고 덜컥 겁이 나기도 합니다.

안심하세요! 이 복잡한 이름은 컴퓨터 공장에서 윈도우(운영체제)를 처음 설치할 때 임시로 붙여놓은 **'공장 출고용 번호표'**일 뿐이랍니다. 오늘 수업에서는 **제미나이(Gemini)가 가상 OS 환경에서 직접 마우스를 움직여 내 컴퓨터 이름을 `우리집-첫노트북`으로 바꾸는 전 과정을 테스트하고 찍은 사진**으로 한 눈금씩 친절하게 알려드릴게요!

> 💡 **오늘 수업에서 함께 해볼 목표**
{goals_md}

[IMAGE_1]

## 1️⃣ 왜 컴퓨터에게도 '이름표'가 필요할까요?

우리 집에 노트북이 한 대뿐일 때도 스마트폰, 태블릿, 블루투스 마우스, 프린터가 서로 전파를 주고받으며 대화합니다. 이때 기계들끼리 **"나는 거실에 있는 노트북이야!"** 하고 서로 알아보기 위해 부르는 이름을 전문 용어로 **호스트네임(Hostname, 장치 이름)**이라고 불러요.

| 구분 | 공장 초기 이름 (`DESKTOP-8F9K2A1`) | 내가 바꾼 친절한 이름 (`우리집-첫노트북`) |
| :--- | :--- | :--- |
| **알아보기 쉬움** | 외계어 같아서 내 컴퓨터인지 구분 불가 | 가족 누구나 보자마자 내 컴퓨터인지 단번에 확인 |
| **블루투스·파일 전송** | 옆집 기기인지 내 기기인지 헷갈림 | 스마트폰에서 사진 보낼 때 내 노트북을 1초 만에 선택 |
| **안전한 이름 규칙** | 영문 대문자 + 무작위 숫자 조합 | **한글, 영문, 숫자, 붙임표(`-`)** 사용 가능 (띄어쓰기 제외) |

[IMAGE_2]

## 2️⃣ 제미나이가 가상 OS에서 직접 테스트한 'PC 이름 바꾸기' 3단계

자, 이제 위 사진 속 노란색 말풍선을 보면서 천천히 따라 해볼까요?

1. **1단계 ([설정] → [시스템] 열기)**: 화면 맨 아래 왼쪽(또는 가운데)의 **시작 버튼(`❖`)**을 누른 뒤 톱니바퀴 모양의 **[설정(⚙️)]**을 클릭합니다. 왼쪽 메뉴 맨 위의 **[시스템]**을 누르면 지금 내 컴퓨터의 임시 이름(`DESKTOP-8F9K2A1`)과 바로 옆의 파란색 **`[이 PC의 이름 바꾸기]`** 버튼이 보입니다. 여기를 마우스 왼쪽 버튼으로 **'딸깍!'** 클릭하세요.
2. **2단계 (새 이름 적고 [다음] 누르기)**: 파란색 입력 창이 뜨면 키보드로 내가 원하는 이름(예: **`우리집-첫노트북`** 또는 **`민수-컴퓨터`**)을 적어줍니다. 이때 **빈칸(띄어쓰기)이나 특수기호(`!`, `@`, `*`)는 넣을 수 없으니** 단어 사이에는 빼기 기호(`-`)를 쓰면 아주 깔끔해요! 다 적었으면 **`[다음]`** 버튼을 클릭합니다.
3. **3단계 (다시 시작 후 바뀐 이름 확인!)**: 컴퓨터가 새 이름표를 단단히 붙이려면 한 번 껐다 켜는 **[지금 다시 시작]** 과정이 필요해요. 작업 중이던 문서를 저장하고 다시 시작을 누르면, 세 번째 사진처럼 내 컴퓨터 이름이 **`우리집-첫노트북`**으로 멋지게 바뀐 것을 확인할 수 있답니다!

[IMAGE_3]

## 3️⃣ 컴맹 탈출 핵심 요약: 이것만 기억하세요!

- **PC 이름을 바꾼다고 해서 내 파일이나 사진이 지워지지 않으니** 안심하고 바꿔보세요.
- 이름을 지을 때 **"이 이름은 사용할 수 없습니다"**라는 안내가 나온다면, 십중팔구 **띄어쓰기(스페이스바)**가 들어갔기 때문이에요. 띄어쓰기 대신 붙임표(`-`)를 넣어주면 바로 통과됩니다!
"""
        code_block = "1단계: [시작] -> [설정(⚙️)] -> [시스템] 클릭\n2단계: [이 PC의 이름 바꾸기] 버튼 좌클릭\n3단계: 공백 없이 '우리집-첫노트북' 입력 후 [다음]\n4단계: 재부팅 후 바뀐 장치 이름 확인 완료!"
    else:
        content = f"""## 👋 들어가며: 컴퓨터 앞에만 서면 손이 멈추는 분들을 위해

처음 컴퓨터나 노트북 전원을 켜면 화면 가득 알 수 없는 그림(아이콘)들이 떠 있고, 마우스를 조금만 움직여도 작은 화살표가 이리저리 날아다녀서 당황스럽기 마련이에요. 오늘 수업에서는 제미나이가 **가상 OS 실험실**에서 직접 테스트하고 캡처한 화면으로 **{lesson['title']}**을 가장 친절하게 알려드릴게요.

> 💡 **오늘 수업에서 함께 배울 목표**
{goals_md}

[IMAGE_1]

## 1️⃣ 근원부터 이해하기: 왜 이렇게 만들어졌을까요?

{lesson['prompt_guide']}

| 동작 이름 | 손가락 움직임 | 컴퓨터가 알아듣는 뜻 | 일상 속 비유 |
| :--- | :--- | :--- | :--- |
| **가리키기 (Hover)** | 버튼은 누르지 않고 화살표만 올리기 | "이 물건이 뭔지 살짝 볼까?" | 상점에서 물건 앞에 서서 구경하기 |
| **클릭 (좌클릭 1번)** | 검지로 왼쪽 버튼을 **'딸깍'** 한 번 누르기 | **"자, 너로 정했어!" (선택/확인)** | 메뉴판에서 원하는 메뉴 손가락으로 짚기 |
| **더블클릭 (연속 2번)** | 검지로 왼쪽 버튼을 빠르게 **'따닥!'** 누르기 | **"문을 열고 안으로 들어가자!" (실행)** | 방문을 똑똑 두드려 활짝 열기 |
| **우클릭 (오른쪽 1번)** | 중지로 오른쪽 버튼을 **'딸깍'** 누르기 | **"여기서 할 수 있는 메뉴판 보여줘!"** | 식당에서 직원분께 추가 메뉴판 요청하기 |

[IMAGE_2]

## 2️⃣ 제미나이 가상 OS 실험실에서 직접 해본 단계별 실습

1. **1단계 (목표 찾기)**: 바탕화면이나 게임 창에서 내가 누르고 싶은 위치를 눈으로 찾은 뒤, 마우스를 천천히 움직여 화살표 끝을 그 위에 올려놓습니다.
2. **2단계 (클릭 & 우클릭 실행)**: 검지손가락으로 마우스 왼쪽 버튼을 가볍게 **'딸깍(Click)'** 누르면 선택됩니다. 보조 메뉴나 깃발 꽂기가 필요할 땐 오른쪽 버튼(우클릭)을 눌러보세요!
3. **3단계 (결과 확인하기)**: 프로그램을 열 때는 쉬지 않고 **'따닥!'** 두 번 연속으로 누르는 더블클릭을 하면 창이 활짝 열립니다.

[IMAGE_3]

## 3️⃣ 오늘 배운 내용, 이것만은 꼭 기억해요!

- 무언가 잘못 눌렀거나 낯선 메뉴판이 튀어나왔을 때는 당황하지 말고 **빈 바탕화면을 왼쪽 클릭 한 번** 하거나, 키보드 왼쪽 맨 위의 **`Esc` (탈출) 키**를 누르면 언제든 안전하게 돌아갑니다.
"""
        code_block = "1단계: 마우스 화살표를 목표 위치에 올리기\n2단계: 왼쪽 버튼 딸깍(좌클릭) / 오른쪽 버튼(우클릭)\n3단계: 실행 결과 화면 눈으로 확인하기"

    return {
        "title": lesson["title"],
        "subtitle": lesson.get("subtitle", ""),
        "tags": lesson.get("keywords", ["컴퓨터기초", "가상OS테스트", "컴맹탈출"]),
        "code_block": code_block,
        "content": content
    }


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
    if api_key and genai is not None:
        client = genai.Client(api_key=api_key)
        prompt = f"""
당신은 컴퓨터를 전혀 모르는 컴맹 입문자를 위해 가상 OS에서 직접 기능을 테스트하고 세상에서 가장 친절하게 설명하는 '제미나이 컴퓨터 기초 선생님'입니다.
수업 제목: {lesson['title']}
부제목: {lesson.get('subtitle', '')}
작성 가이드: {lesson['prompt_guide']}
반드시 마크다운 소제목(##), 비교표(| 컬럼 |), 인용구(> 💡 팁), 1~3단계 설명과 [IMAGE_1], [IMAGE_2], [IMAGE_3] 플레이스홀더를 포함하세요.
출력 형식:
[TAGS] 태그1, 태그2, 태그3, 태그4
[CODE_BLOCK]
3~4줄 실습 요약
[/CODE_BLOCK]
[TITLE] {lesson['title']}
[CONTENT]
본문
"""
        for model_name in ["gemini-2.5-flash", "gemini-2.0-flash"]:
            try:
                resp = client.models.generate_content(model=model_name, contents=prompt)
                if resp and resp.text and "[CONTENT]" in resp.text:
                    raw = resp.text
                    tags = [t.strip() for t in raw.split("[TAGS]")[1].split("\n")[0].split(",") if t.strip()] if "[TAGS]" in raw else lesson.get("keywords", [])
                    cb = raw.split("[CODE_BLOCK]")[1].split("[/CODE_BLOCK]")[0].strip() if "[CODE_BLOCK]" in raw else "가상 OS 3단계 테스트 완료"
                    body = raw.split("[CONTENT]")[1].strip()
                    return {"title": lesson["title"], "subtitle": lesson.get("subtitle", ""), "tags": tags, "code_block": cb, "content": body}
            except Exception as e:
                print(f"⚠️ Gemini API 전환: {e}")

    return build_builtin_lesson_article(lesson)


def publish_post(lesson, article, slot_info, image_paths):
    content = article["content"]
    step_titles = [
        "🖥️ [제미나이 가상 OS 테스트 1단계] 시작 화면 및 버튼 위치 찾기",
        "🖱️ [제미나이 가상 OS 테스트 2단계] 마우스 클릭 및 값 입력 실행 순간",
        "🎉 [제미나이 가상 OS 테스트 3단계] 설정 반영 완료 및 결과 화면 확인"
    ]

    for idx, img_path in enumerate(image_paths):
        placeholder = f"[IMAGE_{idx+1}]"
        clean_img_path = img_path if img_path.startswith("/") else f"/{img_path}"
        caption = step_titles[idx] if idx < len(step_titles) else f"가상 OS 실습 화면 {idx+1}"
        md_img = (
            f'\n\n<figure class="os-screenshot-card">\n'
            f'  <div class="os-screenshot-bar"><span>🔴 🟡 🟢</span><span class="os-bar-title">{caption}</span><span class="os-bar-badge">Argon OS Sandbox</span></div>\n'
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
os_type: "{lesson.get('os_type', 'Argon Virtual OS')}"
os_scene: "{lesson.get('os_scene', 'pc_rename')}"
difficulty: "{lesson.get('difficulty', 'Lv.1 완전 입문')}"
verified_by: "GPT Think Reasoning Gatekeeper"
theme_system: "Argon Design System"
thumbnail: "{thumb_url}"
tags: [{tags_yaml}]
---

"""
    post_filename = f"{TODAY_STR}-{lesson['id']}-{STAMP_STR}.md"
    post_filepath = os.path.join(POSTS_DIR, post_filename)
    with open(post_filepath, "w", encoding="utf-8") as f:
        f.write(front_matter + content)
    print(f"✅ [1단계: Gemini 생산 완료] 포스트 파일 생성: {post_filepath}")
    return post_filepath


if __name__ == "__main__":
    history_list = load_history()
    slot_info = detect_slot_info()
    lesson = select_next_lesson(history_list, slot_info)

    print(f"📌 [Gemini 생산 시작] 커리큘럼: [{lesson['stage']}] {lesson['title']}")
    article = generate_friendly_lesson_article(lesson, slot_info)

    print(f"🖥️ [가상화 OS 테스트] 시나리오({lesson.get('os_scene', 'pc_rename')}) 실행 및 3단계 스크린샷 캡처 중...")
    os_images = generate_virtual_os_screenshots(
        scene_type=lesson.get("os_scene", "pc_rename"),
        lesson_title=article["title"],
        image_dir=IMAGE_DIR,
        stamp_str=STAMP_STR,
        code_or_summary=article["code_block"],
        baseurl=BASEURL
    )

    post_path = publish_post(lesson, article, slot_info, os_images)

    # GPT Think 추론 검증 게이트 실행
    print("🔍 [2단계: GPT Think 추론 검증 시작] 포스트 내용 및 가상 OS 테스트 증적을 대조합니다...")
    verify_report = verify_post_and_os_test(post_path, "audit_logs/last_os_test.json")
    if verify_report["verdict"] != "APPROVED":
        raise RuntimeError("GPT Think 검증 기준 미달로 배포를 중단합니다.")

    save_history(lesson["id"])
    print("🚀 [3단계: Git 운영 승인] 모든 생산·가상OS 테스트·GPT Think 검증이 완료되었습니다!")
