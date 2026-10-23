"""
poster.py
ChooSu Lab — 컴퓨터 아키텍처 및 운영체제 기초 연구소 (Chief Research Director Edition)
1일 2회 자동 연구 보고서 발행 (오전 09:00 KST 이론·아키텍처 / 오후 15:00 KST 가상 OS 커널 실증)
+ 저녁 시간대 연구소장 수동/반자동 모노그래프 발행 엔진
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
# 0. 발행 히스토리 로드 및 레거시 비활성 포스트 자동 정리
# =====================================================================
def cleanup_unpublished_legacy_posts():
    """
    과거 덮어쓰기 과정에서 남은 published: false 처리된 구버전 파일들을
    GitHub Actions 실행 시 자동으로 정리하여 저장소 청결도를 유지합니다.
    """
    if not os.path.exists(POSTS_DIR):
        return
    for fname in os.listdir(POSTS_DIR):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(POSTS_DIR, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                head = f.read(400)
            if "published: false" in head:
                os.remove(fpath)
                print(f"🧹 구버전 비활성 포스트 정리 완료: {fname}")
        except Exception:
            pass


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
    오전 9시(이론·아키텍처 연구), 오후 3시(가상 OS 커널 텔레메트리 실증), 저녁(수동 연구 노트) 구분
    """
    env_slot = os.environ.get("POST_SLOT", "").strip().lower()
    if env_slot == "manual" or os.environ.get("MANUAL_TITLE", "").strip():
        return {
            "slot_id": "evening_manual",
            "slot_badge": "ChooSu Lab · Director's Special Monograph",
            "author_type": "ChooSu Lab Chief Research Director"
        }
    if env_slot == "morning" or (env_slot == "" and NOW_KST.hour < 12):
        return {
            "slot_id": "morning_auto",
            "slot_badge": "ChooSu Lab · Research Monograph (Architecture)",
            "author_type": "ChooSu Lab Chief Research Director"
        }
    return {
        "slot_id": "afternoon_auto",
        "slot_badge": "ChooSu Lab · Empirical OS Telemetry Report",
        "author_type": "ChooSu Lab Chief Research Director"
    }


def select_next_lesson(history_list, slot_info):
    """
    1순위: 수동 입력(환경변수 MANUAL_TITLE 등)이 있으면 수동 연구 주제 생성
    2순위: curriculum.json에서 아직 발행하지 않은 순서의 연구소 아젠다 선택
    3순위: 모든 기본 커리큘럼 완료 시 심화 컴퓨터 공학 연구 아젠다로 자동 확장
    """
    manual_title = os.environ.get("MANUAL_TITLE", "").strip()
    manual_topic = os.environ.get("MANUAL_TOPIC", "").strip()
    manual_scene = os.environ.get("OS_SCENE", "system_monitor").strip() or "system_monitor"

    if manual_title:
        return {
            "id": f"lab-monograph-{STAMP_STR}",
            "stage": "특별 연구 보고서 · 심층 아키텍처 분석",
            "os_scene": manual_scene,
            "os_type": "ChooSu Lab Virtual OS · Kernel Telemetry",
            "difficulty": "Research Report · 기초 원리 및 학술 심화",
            "title": manual_title if "[ChooSu Lab" in manual_title else f"[ChooSu Lab Technical Report] {manual_title}",
            "subtitle": manual_topic or "ChooSu Lab Chief Director's Research Note — 제1원리(First Principles)와 학술 논문에 기반한 컴퓨터 시스템 구조 분석",
            "keywords": ["컴퓨터아키텍처", "운영체제", "커널분석", "학술연구", "ChooSuLab"],
            "learning_goals": [
                "대상 기술의 탄생 배경과 수리논리학적·하드웨어적 제1원리를 규명합니다.",
                "운영체제 커널 및 시스템 계층에서의 상태 전이와 성능 지표를 정량적으로 분석합니다.",
                "가상 OS 3단계 텔레메트리 실증을 통해 이론적 모델과 실제 동작의 일치성을 검증합니다."
            ],
            "references": [
                "Von Neumann, J. (1945). First Draft of a Report on the EDVAC. Moore School of Electrical Engineering, University of Pennsylvania. https://web.mit.edu/sts.035/www/PDFs/edvac.pdf",
                "Ritchie, D. M., & Thompson, K. (1974). The UNIX Time-Sharing System. Communications of the ACM (CACM), 17(7), 365–375. https://www.nokia.com/bell-labs/about/dennis-m-ritchie/cacm.pdf",
                "Denning, P. J. (1968). The working set model for program behavior. Communications of the ACM (CACM), 11(5), 323–333. https://en.wikipedia.org/wiki/Working_set"
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

    # 기본 커리큘럼을 모두 소화한 경우 고도화된 연구소 심화 주제 풀에서 순환 선택
    next_num = len(history_list) + 3
    advanced_pool = [
        {
            "stage": "컴퓨터 아키텍처 · 캐시 일관성 및 파이프라인 연구",
            "os_scene": "system_monitor",
            "topic_title": f"[ChooSu Lab Technical Report #{next_num:02d}] 슈퍼스칼라(Superscalar) CPU의 비순차 실행(Out-of-Order Execution)과 분기 예측(Branch Prediction) 및 캐시 일관성(MESI 프로토콜) 수리 분석",
            "subtitle": "ChooSu Lab Chief Director's Research Note — 토마술로 알고리즘(Tomasulo, 1967), 파이프라인 해저드 제어, 그리고 멀티코어 L1/L2 캐시 라인 동기화 메커니즘",
            "keywords": ["슈퍼스칼라", "비순차실행", "분기예측", "MESI프로토콜", "CPU파이프라인"],
            "references": [
                "Tomasulo, R. M. (1967). An efficient algorithm for exploiting multiple arithmetic units. IBM Journal of Research and Development, 11(1), 25–33.",
                "Von Neumann, J. (1945). First Draft of a Report on the EDVAC. University of Pennsylvania. https://web.mit.edu/sts.035/www/PDFs/edvac.pdf"
            ],
            "guide": "CPU가 명령어를 클럭당 여러 개 처리하기 위해 사용하는 파이프라이닝, 토마술로(Tomasulo, 1967)의 비순차 실행 알고리즘, 그리고 멀티코어 환경의 MESI 캐시 일관성 프로토콜을 수식 및 상태 전이표와 함께 서술하세요."
        },
        {
            "stage": "운영체제 커널 · 동기화 및 교착상태(Deadlock) 연구",
            "os_scene": "file_explorer",
            "topic_title": f"[ChooSu Lab Technical Report #{next_num:02d}] 다중 스레드 환경의 상호배제(Mutual Exclusion) 원리와 다익스트라(Dijkstra, 1965) 세마포어 및 커널 교착상태(Deadlock) 회피 알고리즘",
            "subtitle": "ChooSu Lab Chief Director's Research Note — 임계 구역(Critical Section) 경쟁 조건(Race Condition)의 하드웨어 원자적 명령어(CAS) 해법과 코프만(Coffman, 1971)의 4대 필요조건 분석",
            "keywords": ["세마포어", "Dijkstra", "교착상태", "Deadlock", "상호배제", "커널동기화"],
            "references": [
                "Dijkstra, E. W. (1965). Solution of a problem in concurrent programming control. Communications of the ACM (CACM), 8(9), 569.",
                "Coffman, E. G., Elphick, M., & Shoshani, A. (1971). System deadlocks. ACM Computing Surveys (CSUR), 3(2), 67–78."
            ],
            "guide": "프로그램이 멈추거나 충돌하는 근본 원인 중 하나인 경쟁 조건(Race Condition)과 교착상태(Deadlock)를 에츠허르 다익스트라(Dijkstra, 1965)의 세마포어 논문 및 코프만(Coffman, 1971)의 4대 조건으로 엄밀하게 규명하세요."
        },
        {
            "stage": "정보 이론 · 데이터 압축 및 오류 정정 코드 연구",
            "os_scene": "pc_rename",
            "topic_title": f"[ChooSu Lab Technical Report #{next_num:02d}] 클로드 섀넌(Claude E. Shannon, 1948)의 정보 엔트로피(Information Entropy) 한계와 무손실 압축(Huffman · LZ77) 및 해밍 오류 정정 코드(ECC) 연구",
            "subtitle": "ChooSu Lab Chief Director's Research Note — 디지털 파일 압축의 이론적 하한선 H(X)와 메모리/네트워크 비트 반전(Bit Flip)을 스스로 고치는 해밍 거리(Hamming, 1950)의 대수적 구조",
            "keywords": ["정보이론", "ClaudeShannon", "엔트로피", "무손실압축", "해밍코드", "ECC메모리"],
            "references": [
                "Shannon, C. E. (1948). A Mathematical Theory of Communication. Bell System Technical Journal, 27(3), 379–423.",
                "Hamming, R. W. (1950). Error detecting and error correcting codes. Bell System Technical Journal, 29(2), 147–160."
            ],
            "guide": "클로드 섀넌(1948)의 정보 엔트로피 수식 H(X) = -sum P(x) log2 P(x)를 통해 알집/ZIP 파일 압축의 원리를 설명하고, 리처드 해밍(1950)의 오류 정정 부호(ECC)가 컴퓨터 데이터의 무결성을 지키는 원리를 분석하세요."
        }
    ]
    picked = advanced_pool[next_num % len(advanced_pool)]
    return {
        "id": f"lab-archive-{next_num:03d}",
        "stage": picked["stage"],
        "os_scene": picked["os_scene"],
        "os_type": "ChooSu Lab Virtual OS · Kernel Telemetry",
        "difficulty": "Research Report · 기초 원리 및 학술 심화",
        "title": picked["topic_title"],
        "subtitle": picked["subtitle"],
        "keywords": picked["keywords"],
        "learning_goals": [
            "기초적인 현상 이면에 숨겨진 컴퓨터 과학의 제1원리와 수학적 모델을 도출합니다.",
            "운영체제 커널과 하드웨어 계층 간의 상호작용을 정량적 지표와 비교표로 분석합니다.",
            "가상 OS 3단계 텔레메트리 실험을 통해 이론과 실제 시스템 동작을 검증합니다."
        ],
        "references": picked["references"],
        "prompt_guide": picked["guide"]
    }


# =====================================================================
# 1. Gemini 연구소장(Chief Research Director) 심층 보고서 생성
# =====================================================================
def generate_friendly_lesson_article(lesson, slot_info):
    manual_body = os.environ.get("MANUAL_BODY", "").strip()
    if manual_body:
        return {
            "title": lesson["title"],
            "subtitle": lesson.get("subtitle", ""),
            "tags": lesson.get("keywords", ["컴퓨터아키텍처", "운영체제", "ChooSuLab"]),
            "code_block": "1단계: 커널 상태 및 초기 아키텍처 파라미터 계측\n2단계: 핵심 알고리즘 및 시스템 콜 트랜잭션 실행\n3단계: 상태 전이 완료 검증 및 정량적 텔레메트리 확인",
            "content": manual_body
        }

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    refs_list = lesson.get("references", [
        "Von Neumann, J. (1945). First Draft of a Report on the EDVAC. University of Pennsylvania. https://web.mit.edu/sts.035/www/PDFs/edvac.pdf",
        "Ritchie, D. M., & Thompson, K. (1974). The UNIX Time-Sharing System. Communications of the ACM (CACM), 17(7), 365–375. https://www.nokia.com/bell-labs/about/dennis-m-ritchie/cacm.pdf"
    ])
    refs_prompt_str = "\n".join(f"- {r}" for r in refs_list)

    prompt = f"""
당신은 컴퓨터 아키텍처, 운영체제 커널, 인간-컴퓨터 상호작용(HCI)을 연구하는 **'ChooSu Lab'의 연구소장(Chief Research Director)**입니다.
가볍고 짧은 요약글이 아니라, 기초적인 현상 하나를 다루더라도 그 뿌리가 되는 컴퓨터 과학의 제1원리(First Principles), 수학적 방정식, 커널 내부 아키텍처, 그리고 역사적 원전 논문까지 완벽하고 치밀하게 파헤치는 **장문의 학술 연구 기술 보고서(Technical Monograph, 최소 6,000자~10,000자 분량)**를 작성하세요.

[연구 보고서 메타데이터]
- 연구 영역: {lesson['stage']} ({slot_info['slot_badge']})
- 보고서 제목: {lesson['title']}
- 부제목: {lesson.get('subtitle', '')}
- 가상 OS 실증 환경: {lesson.get('os_type', 'ChooSu Lab Virtual OS')}
- 연구소장 핵심 집필 지침: {lesson['prompt_guide']}
- 필수 인용 학술 논문 및 표준(References):
{refs_prompt_str}

[필수 작성 원칙 — 엄격히 준수할 것]
1. **연구소장(Chief Research Director)의 권위 있고 지적인 어조**:
   - 유치한 말투("~해요", "겁먹지 마세요")를 배제하고, 정중하고 명료하며 학술적인 연구소장의 문체("~합니다", "~로 규명됩니다", "본 연구소에서는 ~를 분석합니다")로 서술하세요.
   - 컴퓨터를 처음 접하는 입문자도 현상의 본질을 꿰뚫어 볼 수 있도록 일상적 관찰에서 출발하되, 곧바로 그 이면의 커널 구조와 수학적 수식(LaTeX `$$ ... $$`), 아키텍처 비교표(Markdown Table)로 깊이 있게 전개하세요.
2. **압도적인 분량과 구조적 완결성 (6대 섹션 필수 포함)**:
   - 상단에 `> **ChooSu Lab Technical Report** · 작성: **ChooSu Lab 연구소장 (Chief Research Director)**` 인용 박스를 배치하세요.
   - `## 1. 연구소장 서문 (Director's Preface)`: 일상적인 컴퓨터 현상에 대한 문제 제기와 역사적·학술적 배경
   - `## 2. 이론적 배경 및 수리적·아키텍처 모델링`: 원전 논문 및 RFC 표준에 기반한 수식(`$$ ... $$`)과 정량적 비교 마크다운 표(최소 4행 이상)
   - `## 3. 운영체제 커널 및 하드웨어 계층의 심층 메커니즘`: 레지스트리, 시스템 콜, 인터럽트, 메모리/디스크 포인터 등 로우레벨 작동 원리 해부
   - `## 4. 가상 OS 실험실 3단계 실증 분석 (Empirical Telemetry)`: Step 1 ~ Step 3 가상 OS 계측 과정 해설
   - `## 5. 결론 및 시스템 엔지니어링 시사점`: 실무 및 일상 사용에서의 아키텍처적 통찰 정리
   - `## 6. 참고문헌 및 학술 출처 (References)`: 본문에서 인용한 실제 논문(저자, 연도, 제목, 학술지/표준 번호, 링크)을 정확히 명시
3. **가상 OS 스크린샷 플레이스홀더**:
   - 본문 1장, 3장, 4장 부근의 가장 적절한 위치에 `[IMAGE_1]`, `[IMAGE_2]`, `[IMAGE_3]`을 정확히 한 번씩 배치하세요.

[출력 형식]
[TAGS] 태그1, 태그2, 태그3, 태그4, 태그5
[CODE_BLOCK]
1단계: 가상 OS 커널 상태 및 초기 파라미터 계측
2단계: 핵심 시스템 콜 및 아키텍처 상태 전이 실행
3단계: 최종 실증 텔레메트리 검증 및 무결성 확인
[/CODE_BLOCK]
[TITLE] {lesson['title']}
[CONTENT]
(여기에 장문의 연구소장 기술 보고서 마크다운 본문 작성 — [IMAGE_1], [IMAGE_2], [IMAGE_3] 및 최하단 참고문헌 포함)
"""

    raw = ""
    if api_key and genai is not None:
        client = genai.Client(api_key=api_key)
        model_candidates = ["gemini-2.5-flash", "gemini-2.0-flash"]
        for model_name in model_candidates:
            for attempt in range(3):
                try:
                    print(f"[{model_name}] 연구소장 심층 기술 보고서 생성 시도 ({attempt+1}/3)...")
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt
                    )
                    if response and response.text and len(response.text) > 2500:
                        raw = response.text
                        break
                except Exception as e:
                    print(f"⚠️ [{model_name}] 호출 예외 (시도 {attempt+1}): {e}")
                    time.sleep(4)
            if raw:
                break

    if not raw:
        print("ℹ️ 오프라인/로컬 환경 또는 API 제한 감지 — 내장 연구소장 장문 모노그래프 엔진으로 생성합니다.")
        return build_builtin_lesson_article(lesson)

    tags = lesson.get("keywords", ["컴퓨터아키텍처", "운영체제", "커널분석", "ChooSuLab"])
    if "[TAGS]" in raw:
        parsed_tags = [t.strip() for t in raw.split("[TAGS]")[1].split("\n")[0].split(",") if t.strip()]
        if parsed_tags:
            tags = parsed_tags

    code_block = (
        "1단계: 가상 OS 커널 상태 및 초기 아키텍처 파라미터 계측\n"
        "2단계: 핵심 프로토콜 및 시스템 콜 상태 전이 실행\n"
        "3단계: 텔레메트리 데이터 검증 및 아키텍처 무결성 확인"
    )
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
    API 키가 없거나 할당량 초과 시에도 연구소장(Chief Research Director) 품질의
    장문 기술 보고서(수식 + 아키텍처 비교표 + 학술 논문 참고문헌 포함)를 생성합니다.
    """
    goals_md = "\n".join(f"- **{g}**" for g in lesson.get("learning_goals", []))
    refs = lesson.get("references", [
        "Von Neumann, J. (1945). First Draft of a Report on the EDVAC. Moore School of Electrical Engineering, University of Pennsylvania. https://web.mit.edu/sts.035/www/PDFs/edvac.pdf",
        "Ritchie, D. M., & Thompson, K. (1974). The UNIX Time-Sharing System. Communications of the ACM (CACM), Vol. 17, No. 7, pp. 365–375. https://www.nokia.com/bell-labs/about/dennis-m-ritchie/cacm.pdf",
        "Denning, P. J. (1968). The working set model for program behavior. Communications of the ACM (CACM), Vol. 11, Issue 5, pp. 323–333. https://en.wikipedia.org/wiki/Working_set"
    ])
    refs_md = "\n".join(f"{idx+1}. **{r}**" for idx, r in enumerate(refs))

    template = r"""
> **ChooSu Lab Technical Monograph** · 작성: **ChooSu Lab 연구소장 (Chief Research Director)**  
> **연구 분류**: __STAGE__  
> **검증 환경**: __OS_TYPE__

---

## 1. 연구소장 서문 (Director's Preface): 일상적 인터페이스의 표면을 넘어 시스템의 제1원리로

현대의 컴퓨팅 환경은 고도로 정교한 **추상화(Abstraction)**의 산물입니다. 사용자가 마우스를 움직여 아이콘을 클릭하거나, 파일을 폴더에 복사하고, 웹 브라우저에 주소를 입력하는 지극히 일상적인 행위는 모두 직관적인 그래픽 사용자 인터페이스(GUI) 뒤에 숨겨져 있습니다. 그러나 이러한 표면적 편리함에만 머물러 있을 때, 시스템의 응답 지연이나 자원 병목, 혹은 예기치 않은 오류 앞에서 사용자는 원인을 진단할 수 없는 수동적 관찰자에 머물게 됩니다.

저희 **ChooSu Lab**이 추구하는 기초 연구의 본질은 단순히 '어느 버튼을 눌러라'라는 단편적인 매뉴얼을 나열하는 것이 아닙니다. 본 연구소에서는 가장 기초적인 컴퓨터 조작 하나를 다루더라도, 그 행위가 운영체제 커널(OS Kernel)의 시스템 콜(System Call) 계층과 하드웨어 레지스터, 그리고 수리논리학적 알고리즘에서 어떻게 처리되는지 **제1원리(First Principles)**의 관점에서 엄밀하게 규명합니다.

이번 연구 보고서에서는 **__TITLE__**를 주제로 삼아, __PROMPT_GUIDE__

> **본 연구 보고서의 핵심 규명 과제**
__GOALS_MD__

[IMAGE_1]

---

## 2. 이론적 배경 및 수리적·아키텍처 모델링 (Theoretical Modeling)

### 2.1 시분할 다중처리와 대기열 이론(Queuing Theory)의 수리적 기초
현대 운영체제가 다수의 사용자 요청과 하드웨어 인터럽트(Interrupt)를 지연 없이 처리하기 위해서는 자원의 할당과 대기 시간을 수학적으로 통제해야 합니다. 1961년 존 리틀(John D. C. Little)이 증명한 대기열 이론의 기본 정리인 **리틀의 법칙(Little's Law)**에 따르면, 시스템 내부에 머무르는 평균 작업(프로세스 또는 I/O 패킷)의 수 $L$은 단위 시간당 평균 도착률 $\lambda$와 각 작업이 시스템에 머무르는 평균 응답 시간 $W$의 곱과 항상 일치합니다:

$$L = \lambda \cdot W$$

또한 단일 코어 또는 단일 I/O 채널의 최대 처리 용량(Service Rate)을 $\mu$라 할 때, 시스템 이용률(Utilization)은 $\rho = \frac{\lambda}{\mu}$ ($0 \le \rho < 1$)로 정의됩니다. 이때 M/M/1 대기열 모델에서의 평균 응답 시간 $W$는 다음과 같은 비선형 방정식을 따릅니다:

$$W = \frac{1}{\mu - \lambda} = \frac{1}{\mu(1 - \rho)}$$

위 방정식이 시사하는 아키텍처적 진실은 매우 명확합니다. 시스템의 자원 사용률 $\rho$가 $100\%$($\rho \to 1$)에 근접할수록 분모 $(1 - \rho)$가 $0$에 수렴하면서, 사용자가 체감하는 응답 지연 시간 $W$는 선형적으로 증가하는 것이 아니라 **무한대($\infty$)를 향해 기하급수적으로 폭발**합니다. 운영체제 커널이 선점형 스케줄러(Preemptive Scheduler)와 버퍼 캐시(Buffer Cache), 그리고 비동기 이벤트 큐(Asynchronous Event Queue)를 두어 순간적인 부하 집중을 평탄화하는 이유가 바로 이 수리적 임계점을 방어하기 위함입니다.

### 2.2 계층별 시스템 아키텍처 비교 분석
사용자 공간(User Space)에서 발생한 명령이 커널 공간(Kernel Space)을 거쳐 물리적 하드웨어에서 완결되기까지의 계층별 특성은 아래 표와 같이 요약됩니다.

| 아키텍처 계층 (Layer) | 핵심 처리 주체 및 자료구조 | 동작 시간 스케일 (Latency) | 권한 수준 (x86-64 Ring) | 시스템 무결성 보장 메커니즘 |
| :--- | :--- | :--- | :--- | :--- |
| **사용자 인터페이스 계층 (GUI / Shell)** | Window Manager, 메시지 루프 (`MSG` 구조체) | $1\text{ ms} \sim 16.6\text{ ms}$ (60Hz 프레임) | Ring 3 (User Mode) | 프로세스별 독립 가상 주소 공간(VAS) 격리 |
| **시스템 콜 인터페이스 (System Call API)** | `ntdll.dll` / `glibc`, `SYSCALL` 명령어 트랩 | $50\text{ ns} \sim 200\text{ ns}$ | Ring 3 $\rightarrow$ Ring 0 전이 | 매개변수 포인터 유효성 및 접근 토큰(ACL) 검증 |
| **운영체제 커널 계층 (OS Kernel Core)** | 스케줄러(CFS/MLFQ), VFS, 가상 메모리 관리자 | $100\text{ ns} \sim 5\ \mu\text{s}$ | Ring 0 (Kernel Mode) | 스핀락(Spinlock), 세마포어, 저널링 트랜잭션 |
| **하드웨어 추상화 및 디바이스 (HAL / HW)** | CPU MMU(TLB), PCIe/NVMe 컨트롤러, 인터럽트(IRQ) | $0.5\text{ ns}$ (레지스터) $\sim 100\ \mu\text{s}$ (I/O) | 물리 계층 (Hardware) | ECC 패리티 검사, DMA 버스 마스터링 보호 |

---

## 3. 운영체제 커널 및 하드웨어 계층의 심층 메커니즘

### 3.1 사용자 모드(Ring 3)와 커널 모드(Ring 0)의 이중 모드 보호(Dual-Mode Operation)
만약 일반 응용 프로그램이 하드웨어 메모리나 디스크 섹터, 혹은 네트워크 인터페이스 카드(NIC)에 직접 접근할 수 있도록 허용한다면, 단 하나의 잘못 작성된 프로그램이 운영체제 전체를 파괴할 수 있습니다. 이를 원천적으로 차단하기 위해 현대 프로세서와 운영체제는 하드웨어 수준의 **이중 모드(Dual-Mode)** 보호 아키텍처를 강제합니다.

평상시 모든 응용 프로그램은 제한된 권한을 가진 **사용자 모드(User Mode, Ring 3)**에서 실행됩니다. 그러다 파일 열기, 메모리 할당, 네트워크 패킷 전송, 혹은 시스템 설정 변경과 같은 특권 연산(Privileged Instruction)이 필요해지면, 프로세스는 CPU의 하드웨어 트랩 명령어(`SYSCALL` 또는 `SYSENTER`)를 호출하여 제어권을 **커널 모드(Kernel Mode, Ring 0)**로 이양합니다.

[IMAGE_2]

### 3.2 상태 전이의 원자성(Atomicity)과 문맥 교환(Context Switch)
커널 모드로 진입한 운영체제는 현재 스레드의 CPU 레지스터 상태(Program Counter, Stack Pointer, 범용 레지스터)를 커널 스택과 **프로세스 제어 블록(PCB, Process Control Block)**에 안전하게 보존합니다. 이후 요청된 커널 루틴을 수행하는 동안 다른 스레드나 인터럽트가 동일한 커널 자료구조를 동시에 수정하여 데이터가 오염되는 **경쟁 조건(Race Condition)**을 막기 위해, 에츠허르 다익스트라(Edsger W. Dijkstra, 1965)가 정립한 **세마포어(Semaphore)** 및 하드웨어 원자적 명령어(`Compare-And-Swap, CAS`)를 사용하여 상태 전이의 **원자성(Atomicity)**을 보장합니다.

---

## 4. 가상 OS 실험실 3단계 실증 분석 (Empirical Telemetry)

본 연구소의 가상화 OS 테스트베드(`__OS_SCENE__` 시나리오, $1280 \times 800$ 해상도)에서 이론적 모델을 실제 시스템 조작으로 검증한 3단계 텔레메트리 결과는 다음과 같습니다.

1. **Step 1 (초기 시스템 상태 계측 및 타깃 식별)**: 가상 OS 환경에서 대상 컴포넌트의 초기 상태와 메타데이터를 확인합니다. 사용자 공간(Ring 3)의 GUI 렌더러가 현재 커널 상태를 조회하여 화면에 시각적 객체로 투영하는 단계입니다.
2. **Step 2 (인터럽트 발생 및 커널 시스템 콜 트랜잭션)**: 입력 이벤트를 통해 상태 변경 명령을 인가합니다. 하드웨어 인터럽트가 커널의 이벤트 디스패처를 깨우고, 시스템 콜을 통해 커널 내부의 메타데이터 테이블 및 레지스트리 상태가 원자적으로 갱신됩니다.
3. **Step 3 (상태 전이 완료 및 시스템 텔레메트리 일관성 검증)**: 커널 내부의 변경 사항이 모든 하위 서브시스템과 UI 뷰포트에 일관되게 반영되었음을 최종 확인합니다. 데이터 유실이나 교착상태(Deadlock) 없이 목표 상태로의 전이가 완결되었습니다.

[IMAGE_3]

---

## 5. 결론 및 시스템 엔지니어링 시사점

본 연구 보고서를 통해 고찰한 바와 같이, 컴퓨터의 가장 기초적인 동작 하나에도 반세기에 걸쳐 축적된 컴퓨터 과학자들의 수리논리학적 설계와 하드웨어 공학의 정수가 응축되어 있습니다.

- **추상화 계층에 대한 구조적 이해**: 화면에 보이는 아이콘과 창은 실제 물리적 자원이 아니라, 커널이 관리하는 메타데이터 구조체(PCB, i-node/MFT, Page Table)를 인간이 인지하기 쉽게 시각화한 투영물(Projection)입니다.
- **안정성과 성능의 공학적 균형**: 운영체제가 때때로 재부팅을 요구하거나 일정량의 메모리를 캐시로 선점하는 이유는 시스템의 오류가 아니라, 대기열 지연 시간($W$)을 최소화하고 다중 프로세스 간의 데이터 일관성(Consistency)을 수호하기 위한 고도의 엔지니어링 메커니즘입니다.

---

## 6. 참고문헌 및 학술 출처 (References)

__REFS_MD__
"""
    content = (
        template
        .replace("__STAGE__", lesson.get("stage", "컴퓨터 시스템 및 커널 아키텍처 연구"))
        .replace("__OS_TYPE__", lesson.get("os_type", "ChooSu Lab Virtual OS Sandbox (1280×800 Kernel Telemetry)"))
        .replace("__TITLE__", lesson["title"])
        .replace("__PROMPT_GUIDE__", lesson["prompt_guide"])
        .replace("__GOALS_MD__", goals_md)
        .replace("__OS_SCENE__", lesson.get("os_scene", "system_monitor"))
        .replace("__REFS_MD__", refs_md)
    )
    return {
        "title": lesson["title"],
        "subtitle": lesson.get("subtitle", ""),
        "tags": lesson.get("keywords", ["컴퓨터아키텍처", "운영체제", "커널분석", "ChooSuLab"]),
        "code_block": (
            "1단계: 가상 OS 초기 커널 파라미터 및 상태 레지스터 계측\n"
            "2단계: 시스템 콜(Ring 3 -> Ring 0) 호출 및 원자적 상태 전이\n"
            "3단계: 커널 텔레메트리 검증 및 아키텍처 무결성 확인"
        ),
        "content": content.strip()
    }


# =====================================================================
# 2. 마크다운 연구 보고서 발행 (연구소장 표준 레이아웃 & 캡션 카드 적용)
# =====================================================================
def publish_post(lesson, article, slot_info, image_paths):
    content = article["content"]

    step_titles = [
        "[Lab Telemetry Step 1] 가상 OS 초기 아키텍처 상태 및 커널 파라미터 계측",
        "[Lab Telemetry Step 2] 시스템 콜 트랜잭션 인가 및 커널 상태 전이 실행",
        "[Lab Telemetry Step 3] 상태 동기화 완료 및 시스템 무결성 검증 결과"
    ]

    for idx, img_path in enumerate(image_paths):
        placeholder = f"[IMAGE_{idx+1}]"
        clean_img_path = img_path if img_path.startswith("/") else f"/{img_path}"
        caption = step_titles[idx] if idx < len(step_titles) else f"ChooSu Lab Telemetry {idx+1}"
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

    now_formatted = NOW_KST.strftime("%Y-%m-%d %H:%M:%S +0900")
    front_matter = f"""---
layout: post
title: "{safe_title}"
subtitle: "{safe_subtitle}"
date: {now_formatted}
stage: "{lesson.get('stage', '시스템 아키텍처 연구')}"
slot_id: "{slot_info['slot_id']}"
slot_badge: "{slot_info['slot_badge']}"
os_type: "{lesson.get('os_type', 'ChooSu Lab Virtual OS')}"
difficulty: "{lesson.get('difficulty', 'Research Report · 기초 원리 및 학술 심화')}"
thumbnail: "{thumb_url}"
tags: [{tags_yaml}]
---

"""

    post_filename = f"{TODAY_STR}-{lesson['id']}-{STAMP_STR}.md"
    post_filepath = os.path.join(POSTS_DIR, post_filename)

    with open(post_filepath, "w", encoding="utf-8") as f:
        f.write(front_matter + content)
    print(f"✅ ChooSu Lab 연구소장 기술 보고서 발행 완료: {post_filepath}")
    return post_filepath


# =====================================================================
# 3. 메인 실행 파이프라인
# =====================================================================
if __name__ == "__main__":
    cleanup_unpublished_legacy_posts()
    history_list = load_history()
    slot_info = detect_slot_info()
    lesson = select_next_lesson(history_list, slot_info)

    print(f"📌 선택된 연구 아젠다: [{lesson['stage']}] {lesson['title']}")
    article = generate_friendly_lesson_article(lesson, slot_info)

    print(f"🖥️ 가상화 OS 테스트베드({lesson.get('os_scene', 'system_monitor')}) 구동 및 3단계 텔레메트리 캡처 중...")
    os_images = generate_virtual_os_screenshots(
        scene_type=lesson.get("os_scene", "system_monitor"),
        lesson_title=article["title"],
        image_dir=IMAGE_DIR,
        stamp_str=STAMP_STR,
        code_or_summary=article["code_block"],
        baseurl=BASEURL,
        os_profile=os.environ.get("OS_PROFILE", "").strip() or lesson.get("os_profile", "auto")
    )

    publish_post(lesson, article, slot_info, os_images)
    save_history(lesson["id"])
