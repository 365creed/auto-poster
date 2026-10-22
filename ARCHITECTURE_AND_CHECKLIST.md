# 🛡️ ChooSu 컴퓨터 기초 학교 — 전체 작동 구조 & 자가 점검 완벽 가이드

본 문서는 **제미나이(Gemini · 생산 및 가상 OS 테스트)** + **Argon(외관·형식 표준)** + **GPT Think(추론 검증 게이트)** + **Git(무중단 운영)** 4대 분업 체제가 어떻게 연결되어 돌아가는지, 그리고 운영자(사용자)가 **어디서 무엇을 확인하고 점검하면 되는지** 정리한 통합 운영 매뉴얼입니다.

---

## 1. 4대 핵심 역할 분담 및 하루 3회 자동화 사이클

| 담당 주체 | 핵심 역할 | 실행 주기 (한국 시간 KST) | 담당 스크립트 / 파일 |
| :--- | :--- | :--- | :--- |
| **1. 생산 (Gemini)** | • **포스팅 2회**: 가상 OS에서 PC 이름 바꾸기·클릭·미니게임을 직접 실행해 3단계 캡처 + 초보자 눈높이 글 생산<br>• **사이트 발전 1회**: 블로그의 초보자 편의 기능 및 UI를 매일 1단계씩 진화 | • **새벽 03:00**: 사이트 발전 1회<br>• **오전 09:00**: 실전 기초 설정 포스팅<br>• **오후 15:00**: 가상 OS·게임 실습 포스팅 | `poster.py`<br>`os_sandbox.py`<br>`site_evolver.py` |
| **2. 외관·형식 (Argon)** | • 모든 페이지와 신규 위젯을 **Argon Design System**(`#5e72e4` 인디고, `#2dce89` 에메랄드, `#11cdef` 시안, 입체 글래스 카드) 규격으로만 통일 | 상시 적용 및 일일 진화 시 토큰 강제 | `_layouts/default.html`<br>`_layouts/post.html`<br>`index.md` |
| **3. 검증 (GPT Think)** | • 제미나이가 생산한 글과 가상 OS 캡처 3장이 일치하는지, 컴맹 눈높이에 맞는지, Argon 레이아웃이 깨지지 않았는지 추론 검증 후 승인(`APPROVED`) | 매 포스팅 생산 직후 & 사이트 발전 직후 즉시 실행 | `verifier_gpt_think.py`<br>`audit_logs/`<br>`_data/verification_history.json` |
| **4. 운영 (Git / Pages)** | • 오직 GPT Think 검증을 통과한 산출물만 자동 커밋·푸시하여 GitHub Pages로 무중단 배포 (저녁 시간은 인간 에디터 수동 발행 지원) | 검증 통과 즉시 자동 `git commit & push` | `.github/workflows/auto_post.yml`<br>`status.html`<br>`studio.html` |

---

## 2. 포스팅 1편이 만들어지고 검증되는 상세 흐름 (예: "PC 이름 바꾸기")

1. **커리큘럼 선택 (`curriculum.json` & `posted_history.txt`)**
   - `poster.py`가 실행되면 아직 발행하지 않은 가장 기초적인 컴맹 필수 주제(예: `lesson-01-rename-pc` — *"내 컴퓨터 이름이 왜 DESKTOP-8F9K2A일까? PC 이름 바꾸기"*)를 선택합니다.
2. **제미나이 가상화 OS 직접 테스트 및 3단계 촬영 (`os_sandbox.py`)**
   - GitHub Actions의 `Xvfb` 가상 모니터(1280×800) 환경에서 제미나이가 실제로 화면을 띄우고 마우스 커서를 이동해:
     - **Step 1**: `[시작] → [설정] → [시스템]`에서 초기 이름(`DESKTOP-8F9K2A1`) 옆의 **`[이 PC의 이름 바꾸기]`** 버튼 위치 가리키기 캡처
     - **Step 2**: 입력창에 **`우리집-첫노트북`**을 입력하고 **`[다음]`** 버튼을 클릭하는 순간 캡처
     - **Step 3**: 재부팅 후 시스템 이름이 **`우리집-첫노트북`**으로 변경 완료된 화면 캡처
   - 촬영된 이미지 3장과 테스트 증적(`audit_logs/last_os_test.json`)을 생성합니다.
3. **GPT Think 다단계 추론 검증 (`verifier_gpt_think.py`)**
   - **검증 항목 1 (가상 OS 증적 대조)**: 스크린샷 3장이 모두 정상 해상도(1280×800)와 용량으로 생성되었는지 확인합니다.
   - **검증 항목 2 (컴맹 친화성 추론)**: 어려운 용어(예: 호스트네임)가 일상 비유(이름표)로 설명되었는지, 띄어쓰기 금지 같은 실수 방지 팁이 있는지, 표와 1~3단계 번호가 있는지 검증합니다.
   - **검증 항목 3 (Argon 규격 검사)**: Argon 전용 스크린샷 액자(`figure.os-screenshot-card`)와 Front Matter가 정확한지 확인합니다.
   - 검증 통과 시 포스트 하단에 **`🛡️ GPT Think 검증 완료 인증서 박스`**를 부착하고 `_data/verification_history.json`에 이력을 남깁니다.
4. **Git 자동 커밋 및 배포**
   - `verifier_gpt_think.py`가 `APPROVED`를 반환하면 GitHub Actions가 자동으로 변경분만 커밋·푸시합니다.

---

## 3. 내가 어디서 무엇을 확인하면 되나요? (자가 점검 체크리스트)

운영자(사용자)는 코드를 일일이 열어볼 필요 없이 아래 **5곳**만 확인하면 모든 것이 정상 작동하는지 즉시 점검할 수 있습니다.

### ✅ 점검 1: 웹 브라우저에서 실시간 관제 센터 열기 (가장 쉬운 방법!)
- **접속 주소**: `https://365creed.github.io/choosu-lab/status.html` (블로그 상단 메뉴의 **[🛡️ 작동 구조 & 자가 점검 센터]** 클릭)
- **확인할 내용**:
  - 최근 포스팅들이 **GPT Think 검증(Score 100/100 · APPROVED)**을 통과했는지 실시간 카드 리스트로 확인
  - 매일 새벽 3시에 실행된 **Argon 사이트 외관 자동 발전 내역(`Argon v2.1`, `v2.2`...)** 확인

### ✅ 점검 2: 각 포스트 맨 아래의 'GPT Think 검증 인증 박스' 확인
- 블로그에서 아무 글이나 클릭해 맨 아래로 스크롤하면 초록색 테두리의 **`🛡️ GPT Think 검증 완료`** 박스가 보입니다.
- 여기에 **어떤 가상 OS 시나리오(`pc_rename`, `click_trainer`, `game_minesweeper`)로 테스트했는지**, **GPT Think가 어떤 추론 심사평을 남겼는지**, **몇 시에 검증되었는지**가 투명하게 표시됩니다.

### ✅ 점검 3: GitHub 저장소의 [Actions] 탭 확인
- **위치**: GitHub 저장소 상단 메뉴의 **`Actions`** 탭 클릭 &rarr; 왼쪽의 **`Argon Blog — Gemini Producer (2x Post + 1x Site Evolution) & GPT Think Verifier`** 클릭
- **확인할 내용**:
  - 하루 3번(새벽 3시 사이트 발전, 오전 9시·오후 3시 포스팅) 초록색 체크 표시(✅)가 찍혀 있는지 확인
  - 즉시 테스트해보고 싶을 때는 우측의 **`Run workflow`** 버튼을 눌러 `action_mode` (`post`, `evolve`, `both`)와 `os_scene` (`pc_rename` 등)을 선택해 수동으로 돌려볼 수 있습니다.

### ✅ 점검 4: GitHub Secrets (API 키) 설정 점검
- **위치**: GitHub 저장소 상단 **`Settings`** &rarr; 좌측 **`Secrets and variables`** &rarr; **`Actions`**
- **등록할 키**:
  - `GEMINI_API_KEY`: 제미나이(생산 전담) API 키 (필수)
  - `OPENAI_API_KEY`: GPT Think (`o3-mini` / `o1` / `gpt-4o` 추론 검증 전담) API 키 (선택 — 미등록 시에도 내장 CoT 규칙 추론 검증 엔진이 무중단으로 자동 작동함)

### ✅ 점검 5: 저녁 수동 포스팅 & 커리큘럼 추가 방법
- **저녁에 내가 직접 글 올리기**: 블로그 상단 **[🌙 저녁 수동 스튜디오 (`/choosu-lab/studio.html`)]**에서 글을 쓰거나, GitHub Actions의 **`Run workflow`**에서 제목과 메모만 입력하면 가상 OS 캡처와 GPT Think 검증까지 자동으로 거쳐 발행됩니다.
- **컴맹 질문 주제 추가하기**: 저장소의 `curriculum.json` 파일에 내가 다루고 싶은 주제(예: "한영키가 안 바뀔 때 해결법", "바탕화면에 휴지통이 사라졌을 때")를 한 줄 추가해 두면 제미나이가 순서대로 가상 OS에서 테스트 후 포스팅합니다.
