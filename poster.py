"""
poster.py
ChooSu Lab — 컴퓨팅 아카이브 & 디지털 리터러시 연구실 자동 발행 엔진
- 하루 2회(오전 9시, 오후 3시) 가상 OS 환경 테스트 및 리서치 노트를 자동 생성하고,
  내부 검증(verifier_gpt_think.py)을 거친 뒤 Git에 반영합니다.
- 외부 화면에는 내부 검증 과정이나 '초보/학교/선생님' 같은 표현을 노출하지 않고,
  진입장벽이 낮고 정돈된 연구실(Lab) 아카이브 톤으로 글을 작성합니다.
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


def select_next_lesson(history_list):
    manual_title = os.environ.get("MANUAL_TITLE", "").strip()
    manual_topic = os.environ.get("MANUAL_TOPIC", "").strip()
    manual_scene = os.environ.get("OS_SCENE", "pc_rename").strip() or "pc_rename"

    if manual_title:
        return {
            "id": f"lab-note-{STAMP_STR}",
            "category": "리서치 노트",
            "os_scene": manual_scene,
            "os_type": "OS 테스트 환경",
            "title": manual_title,
            "subtitle": manual_topic or "시스템 환경 설정과 기본 작동 원리에 관한 아카이브 기록",
            "keywords": ["시스템설정", "운영체제", "컴퓨팅기초", "리서치노트"],
            "key_points": [
                "핵심 작동 원리와 배경 구조 정리",
                "단계별 인터페이스 조작 및 설정 적용 과정 확인"
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
    scenes = ["pc_rename", "click_trainer", "game_minesweeper", "desktop_windows", "history_simulator"]
    chosen_scene = scenes[next_num % len(scenes)]
    return {
        "id": f"lab-archive-{next_num:03d}",
        "category": "OS 환경 설정" if next_num % 2 == 1 else "인터페이스 원리",
        "os_scene": chosen_scene,
        "os_type": "OS 테스트 환경",
        "title": f"시스템 기본 환경 구성 및 인터페이스 작동 원리 탐구 #{next_num}",
        "subtitle": "운영체제 내부 설정 구조와 직관적인 디바이스 제어를 위한 단계별 가이드",
        "keywords": ["운영체제", "시스템설정", "인터페이스", "아카이브"],
        "key_points": [
            "기능이 설계된 배경과 기본 작동 메커니즘 이해",
            "가상 환경 테스트를 통한 단계별 설정 절차 확인"
        ],
        "prompt_guide": f"컴퓨터와 운영체제의 기초 원리 및 실용적인 설정 주제({next_num}번째 기록)를 다루되, 전문 용어의 장벽을 낮춰 누구나 명쾌하게 이해할 수 있는 연구실 아카이브 톤으로 작성하세요."
    }


def build_builtin_lesson_article(lesson):
    points_md = "\n".join(f"- **{p}**" for p in lesson.get("key_points", []))
    scene = lesson.get("os_scene", "pc_rename")

    if scene == "pc_rename":
        content = f"""## 개요: 초기 장치 이름(DESKTOP-XXXX)은 왜 자동으로 부여될까?

운영체제를 처음 설치하거나 새 PC를 구동하면 시스템 정보 항목에 **`DESKTOP-8F9K2A1`**과 같이 영문과 난수가 결합된 이름이 기본으로 지정되어 있습니다. 이는 네트워크 상에서 여러 기기가 서로 충돌하지 않도록 운영체제 설치 프로그램이 임의로 생성한 **호스트네임(Hostname, 장치 식별자)**입니다.

단일 기기만 사용할 때는 기본 이름을 그대로 두어도 무방하지만, 무선 네트워크(Wi-Fi) 공유기 관리 화면이나 블루투스 주변기기 연결, 로컬 파일 공유 환경에서는 어떤 기기인지 직관적으로 식별하기 어렵습니다. 따라서 용도나 위치에 맞게 장치 이름을 변경해 두면 기기 관리 효율이 크게 높아집니다.

> **핵심 요약**
{points_md}

[IMAGE_1]

## 1. 기본 호스트네임과 사용자 지정 이름의 비교

네트워크 환경에서 장치 이름이 사용되는 방식과 명명 규칙의 차이는 다음과 같습니다.

| 구분 | 초기 자동 생성 이름 (`DESKTOP-8F9K2A1`) | 사용자 지정 이름 (`ChooSu-WorkPC`) |
| :--- | :--- | :--- |
| **생성 방식** | OS 설치 시 무작위 영문·숫자 조합으로 자동 부여 | 사용자가 용도·위치에 맞춰 직접 지정 |
| **기기 식별성** | 블루투스 페어링 및 네트워크 목록에서 구분이 어려움 | 연결 기기 목록에서 즉시 식별 가능 |
| **작성 규칙** | 영문 대문자 및 숫자 | **한글, 영문, 숫자, 하이픈(`-`)** 허용 (공백 및 특수기호 제외) |

[IMAGE_2]

## 2. 단계별 장치 이름 변경 절차

시스템 설정 메뉴를 통해 호스트네임을 변경하는 과정은 3단계로 이루어집니다.

1. **시스템 정보 메뉴 접근 (Step 1)**: 작업표시줄의 **[시작]** 버튼을 누른 뒤 **[설정] → [시스템] → [정보]** 순서로 이동합니다. 상단 사양 요약 영역에 현재 부여된 장치 이름과 함께 **`[이 PC의 이름 바꾸기]`** 버튼이 표시됩니다.
2. **새 식별 이름 입력 (Step 2)**: 버튼을 클릭하여 입력 창이 열리면 구분하기 쉬운 새 이름을 입력합니다. 이때 네트워크 표준 규격상 **띄어쓰기(공백)나 특수문자(`@`, `*`, `/`)는 허용되지 않으므로**, 단어를 구분할 때는 하이픈(`-`)을 사용하는 것이 안전합니다. 입력 후 **`[다음]`**을 누릅니다.
3. **시스템 재시작 및 반영 확인 (Step 3)**: 변경된 호스트네임은 시스템 부팅 과정에서 네트워크 서비스에 등록되므로, 작업 중인 문서를 저장한 뒤 **[지금 다시 시작]**을 실행합니다. 재부팅 후 시스템 정보 화면에서 변경된 이름이 정상적으로 적용된 것을 확인할 수 있습니다.

[IMAGE_3]

## 3. 참고 사항 및 정리

- 장치 이름을 변경하더라도 내부 저장소의 개인 파일이나 설치된 프로그램 데이터에는 영향을 주지 않습니다.
- 만약 입력 과정에서 사용 불가 안내가 표시된다면 공백 문자가 포함되었는지 확인한 뒤 하이픈(`-`)으로 대체하면 정상적으로 등록됩니다.
"""
        code_block = "1. [시작] -> [설정] -> [시스템] -> [정보] 이동\n2. [이 PC의 이름 바꾸기] 선택\n3. 공백 없이 새 이름(예: ChooSu-WorkPC) 입력 후 [다음]\n4. 시스템 재시작 후 변경된 호스트네임 확인"

    elif scene == "click_trainer":
        content = f"""## 개요: 명령어 입력(CLI)에서 그래픽 인터페이스(GUI)로의 전환

초기 컴퓨팅 환경에서는 파일을 열거나 프로그램을 실행하기 위해 키보드로 직접 명령어와 경로를 입력해야 했습니다. 이후 화면 속 그래픽 요소(아이콘, 창, 메뉴)를 포인팅 디바이스로 직접 가리켜 제어하는 **GUI(Graphical User Interface)**가 도입되면서, 마우스 커서와 클릭 체계는 현대 운영체제의 가장 기본적인 입력 표준으로 자리 잡았습니다.

마우스 조작은 단순히 버튼을 누르는 행위처럼 보이지만, 내부적으로는 **위치 지정(Hover), 단일 선택(Click), 프로세스 실행(Double-Click), 보조 옵션 호출(Right-Click)**의 4가지 독립된 이벤트로 구분되어 작동합니다.

> **핵심 요약**
{points_md}

[IMAGE_1]

## 1. 마우스 4대 입력 이벤트의 구조와 역할

운영체제가 마우스의 움직임과 버튼 입력을 해석하는 기준은 다음과 같습니다.

| 입력 구분 | 물리적 동작 | 시스템 내부 동작 | 주요 활용 상황 |
| :--- | :--- | :--- | :--- |
| **가리키기 (Hover)** | 버튼을 누르지 않고 대상 위로 커서 이동 | 해당 좌표의 객체 인식 및 요약 정보(툴팁) 표시 | 아이콘·버튼의 기능 사전 확인 |
| **좌클릭 (Single Click)** | 왼쪽 버튼 1회 입력 | 대상 객체에 포커스(Focus) 부여 및 선택 | 파일 선택, 메뉴 및 버튼 실행 |
| **더블클릭 (Double Click)** | 짧은 간격으로 왼쪽 버튼 연속 2회 입력 | 선택된 객체를 연결된 기본 프로그램으로 실행 | 폴더 진입, 문서 및 애플리케이션 열기 |
| **우클릭 (Right Click)** | 오른쪽 버튼 1회 입력 | 대상 객체에서 수행 가능한 **컨텍스트 메뉴** 호출 | 복사, 이름 바꾸기, 속성 확인, 새 폴더 생성 |

[IMAGE_2]

## 2. 단계별 인터페이스 동작 확인

데스크톱 환경에서 텍스트 문서를 선택하고 실행할 때 일어나는 상태 변화는 다음과 같습니다.

1. **커서 이동 및 객체 인식 (Step 1)**: 마우스를 움직여 화면 속 화살표(커서) 끝을 대상 아이콘 위에 위치시킵니다. 운영체제는 커서 좌표를 실시간으로 추적하여 해당 아이콘의 테두리를 하이라이트하고 파일 정보를 표시합니다.
2. **단일 선택과 컨텍스트 메뉴 비교 (Step 2)**: 왼쪽 버튼을 한 번 누르면 해당 아이콘이 '선택됨' 상태로 전환됩니다. 같은 위치에서 오른쪽 버튼(우클릭)을 누르면 해당 파일에 적용할 수 있는 작업 목록(열기, 이름 바꾸기, 복사, 속성)이 담긴 보조 메뉴가 나타납니다.
3. **연속 입력을 통한 실행 (Step 3)**: 왼쪽 버튼을 빠르게 두 번 연속 누르면(더블클릭) 운영체제가 해당 확장자에 연결된 기본 편집기를 호출하여 화면에 새로운 창(Window)을 띄웁니다. 만약 두 번 누르는 간격이 길어지면 시스템은 이를 '단일 선택 2회'로 인식하므로 일정한 간격으로 연속 입력하는 것이 핵심입니다.

[IMAGE_3]

## 3. 참고 사항 및 정리

- 의도하지 않은 우클릭 메뉴나 선택 상태가 활성화되었을 때는 바탕화면의 빈 공간을 좌클릭하거나 키보드의 **`Esc`** 키를 누르면 즉시 초기 상태로 돌아갑니다.
- 더블클릭 속도가 너무 빠르거나 느려서 실행이 원활하지 않은 경우, 운영체제의 **[마우스 설정]**에서 더블클릭 인식 간격을 사용자의 입력 템포에 맞게 조정할 수 있습니다.
"""
        code_block = "1. 커서 이동(Hover): 대상 좌표 인식 및 하이라이트\n2. 좌클릭(Click): 단일 객체 포커스 및 선택\n3. 우클릭(Right Click): 상황별 컨텍스트 메뉴 호출\n4. 더블클릭(Double Click): 연결된 애플리케이션 실행"

    elif scene == "game_minesweeper":
        content = f"""## 개요: 고전 OS 내장 게임에 담긴 인터페이스 설계 의도

1990년대 초 그래픽 기반 운영체제(Windows 3.0 및 3.1)가 처음 보급되던 시기, 가장 큰 기술적 과제는 기존 키보드 중심 사용자들이 **'마우스'라는 새로운 입력 장치에 익숙해지도록 만드는 것**이었습니다.

이를 위해 운영체제 설계자들은 별도의 학습 매뉴얼을 읽게 하는 대신, 자연스러운 몰입을 통해 마우스 조작 숙련도를 높일 수 있는 소프트웨어를 기본 탑재했습니다. 카드 게임인 **솔리테어(Solitaire)**가 마우스 버튼을 누른 채 이동하는 '드래그 앤 드롭(Drag & Drop)'을 체득하게 했다면, **지뢰찾기(Minesweeper)**는 **좌클릭과 우클릭의 기능적 차이 및 정밀한 포인팅**을 훈련하기 위해 고안된 프로그램이었습니다.

> **핵심 요약**
{points_md}

[IMAGE_1]

## 1. 지뢰찾기 규칙과 마우스 입력의 대응 구조

지뢰찾기의 게임 메커니즘은 마우스의 양쪽 버튼을 정확히 구분해서 사용해야만 클리어할 수 있도록 설계되어 있습니다.

| 게임 내 동작 | 마우스 입력 방식 | 인터페이스 훈련 목적 |
| :--- | :--- | :--- |
| **타일 개방 (Open)** | **좌클릭 (왼쪽 버튼)** | 작은 격자(Grid) 안에 커서를 정확히 위치시키는 정밀 포인팅 숙련 |
| **깃발 표시 (Flag)** | **우클릭 (오른쪽 버튼)** | 좌클릭(실행)과 우클릭(보조 상태 마킹)의 반사적 구분 능력 향상 |
| **인접 숫자 판독 (1, 2...)** | 주변 8칸의 지뢰 개수 추론 | 화면의 시각적 피드백을 읽고 다음 입력 좌표를 결정하는 과정 반복 |

[IMAGE_2]

## 2. 가상 환경에서의 단계별 동작 분석

1. **초기 타일 개방과 숫자 피드백 (Step 1)**: 닫혀 있는 격자 타일 중 하나를 **좌클릭**하여 개방합니다. 타일에 표시되는 숫자 `1` 또는 `2`는 해당 타일을 둘러싼 주변 8칸 안에 숨겨진 지뢰의 총개수를 의미합니다.
2. **우클릭을 통한 지뢰 위치 마킹 (Step 2)**: 숫자 배열을 통해 지뢰가 위치한 칸을 특정한 뒤, 해당 칸 위에서 **우클릭**을 수행합니다. 타일이 열리지 않고 깃발(Flag) 표식이 세워지며, 이후 실수로 좌클릭하더라도 폭발하지 않도록 보호 상태가 설정됩니다.
3. **안전 구역 완전 개방 (Step 3)**: 좌클릭(안전 타일 개방)과 우클릭(지뢰 타일 잠금)을 교차 수행하여 지뢰가 없는 모든 타일을 개방하면 보드가 클리어됩니다.

[IMAGE_3]

## 3. 참고 사항 및 정리

- 이처럼 초기 운영체제의 기본 내장 애플리케이션들은 단순한 여가용 도구를 넘어, 새로운 컴퓨팅 패러다임(GUI)의 진입장벽을 낮추는 정교한 인터페이스 튜토리얼 역할을 수행했습니다.
"""
        code_block = "1. 좌클릭(Left Click): 지정된 격자 타일 개방 및 주변 숫자 확인\n2. 숫자 분석: 인접한 8칸 내 지뢰 분포 추론\n3. 우클릭(Right Click): 지뢰 타일에 보호 깃발 마킹\n4. 모든 안전 타일 개방 시 보드 클리어"

    else:
        content = f"""## 개요: {lesson['title']}

컴퓨터 시스템을 효율적으로 다루기 위해서는 화면에 표시되는 그래픽 요소와 운영체제 내부 설정이 어떻게 연결되어 작동하는지 이해하는 것이 중요합니다. 본 노트에서는 **{lesson['title']}**의 핵심 구조와 단계별 설정 절차를 살펴봅니다.

> **핵심 요약**
{points_md}

[IMAGE_1]

## 1. 작동 구조 및 주요 설정 비교

{lesson['prompt_guide']}

| 구분 | 기본 상태 (Default) | 설정 조정 후 (Configured) | 비고 |
| :--- | :--- | :--- | :--- |
| **화면 표시 및 식별** | 시스템 초기 기본값 적용 | 사용자의 작업 환경 및 해상도에 최적화 | 즉시 반영 |
| **접근 경로** | 컨텍스트 메뉴(우클릭) 또는 시스템 설정 | 단축키 및 빠른 실행 메뉴 병행 가능 | 표준 GUI 규격 |

[IMAGE_2]

## 2. 단계별 환경 설정 및 테스트 과정

1. **대상 메뉴 및 현재 상태 확인 (Step 1)**: 데스크톱 바탕화면 또는 시스템 설정 창에서 현재 적용된 기본 옵션을 확인합니다.
2. **옵션 변경 및 명령 실행 (Step 2)**: 컨텍스트 메뉴(우클릭) 또는 설정 패널의 세부 항목을 선택하여 원하는 배율과 정렬 방식을 지정합니다.
3. **변경 결과 확인 (Step 3)**: 설정이 화면에 즉시 반영되어 가독성과 작업 공간의 정돈 상태가 개선된 것을 확인합니다.

[IMAGE_3]

## 3. 참고 사항 및 정리

- 모든 시스템 환경 설정은 언제든 동일한 경로를 통해 초기 기본값으로 되돌릴 수 있으므로, 사용하는 모니터 해상도와 작업 스타일에 맞춰 유연하게 조정하는 것이 좋습니다.
"""
        code_block = "1. 현재 시스템 설정 및 표시 상태 확인\n2. 설정 메뉴 또는 컨텍스트 메뉴(우클릭) 호출\n3. 변경 옵션 적용 및 화면 반영 결과 확인"

    return {
        "title": lesson["title"],
        "subtitle": lesson.get("subtitle", ""),
        "tags": lesson.get("keywords", ["운영체제", "시스템설정", "컴퓨팅기초"]),
        "code_block": code_block,
        "content": content
    }


def generate_lab_article(lesson):
    manual_body = os.environ.get("MANUAL_BODY", "").strip()
    if manual_body:
        return {
            "title": lesson["title"],
            "subtitle": lesson.get("subtitle", ""),
            "tags": lesson.get("keywords", ["리서치노트", "시스템설정"]),
            "code_block": "1. 대상 설정 위치 확인\n2. 옵션 변경 실행\n3. 반영 결과 확인",
            "content": manual_body
        }

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if api_key and genai is not None:
        client = genai.Client(api_key=api_key)
        prompt = f"""
당신은 'ChooSu Lab (컴퓨팅 아카이브 & 디지털 리터러시 연구실)'의 총괄 에디터입니다.
아래 주제를 바탕으로 컴퓨터의 기초 원리와 환경 설정을 명쾌하게 정리한 리서치 노트를 작성하세요.

[절대 준수 원칙]
1. 독자를 '초보자', '컴맹', '학생', '어르신'으로 부르거나 "쉽게 설명할게요~", "선생님과 함께", "1교시" 같은 유치하거나 가르치려 드는 표현을 절대 사용하지 마세요.
2. 대신 전문 용어의 진입장벽은 자연스럽게 낮추어(괄호 안에 쉬운 풀이나 직관적인 비유 병기), 누구나 읽었을 때 막힘없이 이해되면서도 지적인 연구실 아카이브(배움센터·리서치 노트)의 품격이 느껴지도록 담백하고 정돈된 문체(~합니다, ~입니다)로 작성하세요.
3. 마크다운 소제목(`##`), 비교표(`| 구분 |`), 핵심 요약 인용구(`>`), 단계별 설명(Step 1~3)과 `[IMAGE_1]`, `[IMAGE_2]`, `[IMAGE_3]` 플레이스홀더를 반드시 포함하세요.

- 주제 제목: {lesson['title']}
- 부제목: {lesson.get('subtitle', '')}
- 작성 가이드: {lesson['prompt_guide']}

출력 형식:
[TAGS] 태그1, 태그2, 태그3, 태그4
[CODE_BLOCK]
3~4줄 핵심 절차 요약
[/CODE_BLOCK]
[TITLE] {lesson['title']}
[CONTENT]
마크다운 본문
"""
        for model_name in ["gemini-2.5-flash", "gemini-2.0-flash"]:
            try:
                resp = client.models.generate_content(model=model_name, contents=prompt)
                if resp and resp.text and "[CONTENT]" in resp.text:
                    raw = resp.text
                    tags = [t.strip() for t in raw.split("[TAGS]")[1].split("\n")[0].split(",") if t.strip()] if "[TAGS]" in raw else lesson.get("keywords", [])
                    cb = raw.split("[CODE_BLOCK]")[1].split("[/CODE_BLOCK]")[0].strip() if "[CODE_BLOCK]" in raw else "1. 설정 메뉴 확인\n2. 옵션 변경\n3. 결과 확인"
                    body = raw.split("[CONTENT]")[1].strip()
                    return {"title": lesson["title"], "subtitle": lesson.get("subtitle", ""), "tags": tags, "code_block": cb, "content": body}
            except Exception as e:
                print(f"Gemini API 전환: {e}")

    return build_builtin_lesson_article(lesson)


def publish_post(lesson, article, image_paths):
    content = article["content"]
    step_titles = [
        "Step 1 · 초기 상태 및 대상 메뉴 위치 확인",
        "Step 2 · 인터페이스 조작 및 설정 값 입력",
        "Step 3 · 시스템 반영 완료 및 결과 화면"
    ]

    for idx, img_path in enumerate(image_paths):
        placeholder = f"[IMAGE_{idx+1}]"
        clean_img_path = img_path if img_path.startswith("/") else f"/{img_path}"
        caption = step_titles[idx] if idx < len(step_titles) else f"실습 화면 {idx+1}"
        md_img = (
            f'\n\n<figure class="os-screenshot-card">\n'
            f'  <div class="os-screenshot-bar"><span>🔴 🟡 🟢</span><span class="os-bar-title">{caption}</span><span class="os-bar-badge">ChooSu Lab</span></div>\n'
            f'  <img src="{clean_img_path}" alt="{caption}" loading="lazy" />\n'
            f'  <figcaption>{caption}</figcaption>\n'
            f'</figure>\n\n'
        )
        if placeholder in content:
            content = content.replace(placeholder, md_img, 1)
        else:
            content += md_img

    content = re.sub(r'\[IMAGE_\d+\]', '', content)

    # 하단에는 간결한 1줄 AI 활용 안내 문구만 부착
    ai_footer = "\n\n---\n\n<p class=\"ai-footnote\">본 아카이브 노트는 AI를 활용하여 생성·정리되었습니다.</p>\n"
    content += ai_footer

    tags_yaml = ", ".join(f'"{t}"' for t in article["tags"])
    thumb_url = image_paths[1] if len(image_paths) > 1 else (image_paths[0] if image_paths else "")
    safe_title = article["title"].replace('"', '\\"')
    safe_subtitle = article.get("subtitle", "").replace('"', '\\"')

    front_matter = f"""---
layout: post
title: "{safe_title}"
subtitle: "{safe_subtitle}"
date: {NOW_KST.strftime('%Y-%m-%d %H:%M:%S +0900')}
category: "{lesson.get('category', 'OS 환경 설정')}"
os_type: "{lesson.get('os_type', 'OS 테스트 환경')}"
os_scene: "{lesson.get('os_scene', 'pc_rename')}"
thumbnail: "{thumb_url}"
tags: [{tags_yaml}]
---

"""
    post_filename = f"{TODAY_STR}-{lesson['id']}-{STAMP_STR}.md"
    post_filepath = os.path.join(POSTS_DIR, post_filename)
    with open(post_filepath, "w", encoding="utf-8") as f:
        f.write(front_matter + content)
    print(f"포스트 생성 완료: {post_filepath}")
    return post_filepath


if __name__ == "__main__":
    history_list = load_history()
    lesson = select_next_lesson(history_list)

    print(f"[ChooSu Lab] 주제: [{lesson.get('category')}] {lesson['title']}")
    article = generate_lab_article(lesson)

    os_images = generate_virtual_os_screenshots(
        scene_type=lesson.get("os_scene", "pc_rename"),
        lesson_title=article["title"],
        image_dir=IMAGE_DIR,
        stamp_str=STAMP_STR,
        code_or_summary=article["code_block"],
        baseurl=BASEURL
    )

    post_path = publish_post(lesson, article, os_images)
    verify_post_and_os_test(post_path, "audit_logs/last_os_test.json")
    save_history(lesson["id"])
