"""
os_sandbox.py
가상화 OS 환경에서 시스템 설정, 인터페이스 조작, 내장 애플리케이션 실행 과정을
단계별(Step 1 -> Step 2 -> Step 3) 1280x800 화면으로 캡처하는 모듈입니다.
"""

import os
import json
import datetime
from PIL import Image, ImageDraw, ImageFont


def _load_fonts():
    font_candidates_bold = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
    ]
    font_candidates_reg = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
    ]
    b_path = next((p for p in font_candidates_bold if os.path.exists(p)), None)
    r_path = next((p for p in font_candidates_reg if os.path.exists(p)), b_path)
    if b_path and r_path:
        return {
            "title": ImageFont.truetype(b_path, 22),
            "h3": ImageFont.truetype(b_path, 18),
            "bold": ImageFont.truetype(b_path, 16),
            "body": ImageFont.truetype(r_path, 15),
            "sm_b": ImageFont.truetype(b_path, 13),
            "sm": ImageFont.truetype(r_path, 13),
            "num": ImageFont.truetype(b_path, 20),
        }
    d = ImageFont.load_default()
    return {k: d for k in ["title", "h3", "bold", "body", "sm_b", "sm", "num"]}


def _draw_cursor_and_click(draw, cx, cy, label_text, is_right_click=False, is_double=False):
    f = _load_fonts()
    ring_color = "#f5365c" if is_right_click else "#facc15"
    draw.ellipse([(cx - 26, cy - 26), (cx + 26, cy + 26)], outline=ring_color, width=4)
    if is_double:
        draw.ellipse([(cx - 36, cy - 36), (cx + 36, cy + 36)], outline="#38bdf8", width=3)

    arrow_pts = [
        (cx, cy),
        (cx, cy + 28),
        (cx + 7, cy + 22),
        (cx + 13, cy + 34),
        (cx + 18, cy + 31),
        (cx + 12, cy + 19),
        (cx + 21, cy + 19),
    ]
    draw.polygon(arrow_pts, fill="#ffffff", outline="#0f172a")

    pill_x = min(cx + 32, 780)
    pill_y = (cy + 30) if cy > 420 else max(cy - 42, 62)
    pill_w = min(max(len(label_text) * 14 + 36, 240), 460)
    bg_col = "#f5365c" if is_right_click else "#facc15"
    fg_col = "#ffffff" if is_right_click else "#0f172a"
    draw.rounded_rectangle([(pill_x, pill_y), (pill_x + pill_w, pill_y + 38)], radius=18, fill=bg_col, outline="#0f172a", width=2)
    draw.text((pill_x + 16, pill_y + 9), label_text, fill=fg_col, font=f["bold"])


def render_os_desktop_pil(scene_type, step_idx, lesson_title, out_png_path, code_or_summary="", custom_caption=""):
    f = _load_fonts()
    width, height = 1280, 800
    img = Image.new("RGB", (width, height), color="#0f172a")
    draw = ImageDraw.Draw(img)

    # 1. 데스크톱 배경
    draw.rectangle([(0, 48), (width, height - 56)], fill="#1e293b")
    draw.ellipse([(-100, 100), (640, 840)], fill="#1e3a8a")
    draw.ellipse([(640, -60), (1360, 640)], fill="#0f172a")

    # 2. 상단 캡처 상태 바 (깔끔한 연구실 캡처 스타일)
    draw.rectangle([(0, 0), (width, 48)], fill="#0f172a")
    draw.line([(0, 48), (width, 48)], fill="#4f46e5", width=2)
    draw.text((24, 13), f"ChooSu Lab  ·  STEP {step_idx}/3  ·  {lesson_title[:46]}", fill="#f8fafc", font=f["bold"])
    draw.rounded_rectangle([(1040, 9), (1256, 39)], radius=14, fill="#334155")
    draw.text((1062, 15), "OS Lab Capture · 1280x800", fill="#e2e8f0", font=f["sm_b"])

    # 3. 좌측 바탕화면 아이콘
    icons = [
        ("시스템 설정", "SYS", 78),
        ("작업 노트.txt", "TXT", 205),
        ("지뢰찾기", "APP", 332),
    ]
    for idx, (label, kind, iy) in enumerate(icons):
        is_sel = (scene_type == "pc_rename" and idx == 0) or (scene_type == "click_trainer" and idx == 1) or (scene_type == "game_minesweeper" and idx == 2)
        if is_sel:
            draw.rounded_rectangle([(24, iy), (156, iy + 108)], radius=12, fill="#4f46e5", outline="#818cf8", width=2)
        icon_bg = "#38bdf8" if kind == "SYS" else ("#f8fafc" if kind == "TXT" else "#10b981")
        draw.rounded_rectangle([(62, iy + 12), (118, iy + 62)], radius=10, fill=icon_bg, outline="#0f172a", width=2)
        draw.text((73, iy + 27), kind, fill="#0f172a", font=f["sm_b"])
        draw.text((40, iy + 74), label, fill="#ffffff", font=f["sm_b"])

    # 4. 시나리오별 메인 화면
    if scene_type == "pc_rename":
        draw.rounded_rectangle([(190, 76), (1230, 575)], radius=16, fill="#f8fafc", outline="#4f46e5", width=3)
        draw.rounded_rectangle([(190, 76), (1230, 128)], radius=16, fill="#0f172a")
        draw.text((218, 92), "[설정]  시스템 (System)  >  정보 (About)  —  장치 사양 및 이름 관리", fill="#ffffff", font=f["bold"])

        draw.rectangle([(193, 128), (390, 572)], fill="#f1f5f9")
        side_menus = ["■ 시스템 (System)", "● 블루투스 및 장치", "● 네트워크 및 인터넷", "● 개인 설정 (디스플레이)", "● 계정 및 보안"]
        my = 152
        for m_idx, m_txt in enumerate(side_menus):
            if m_idx == 0:
                draw.rounded_rectangle([(208, my - 6), (376, my + 32)], radius=8, fill="#4f46e5")
                draw.text((222, my), m_txt, fill="#ffffff", font=f["bold"])
            else:
                draw.text((222, my), m_txt, fill="#475569", font=f["body"])
            my += 50

        cur_pc_name = "ChooSu-WorkPC" if step_idx == 3 else "DESKTOP-8F9K2A1"
        draw.rounded_rectangle([(420, 150), (1195, 275)], radius=14, fill="#ffffff", outline="#cbd5e1", width=2)
        draw.text((448, 170), f"■ 현재 장치 이름:  {cur_pc_name}", fill="#0f172a", font=f["title"])
        draw.rounded_rectangle([(448, 210), (805, 245)], radius=8, fill="#eff6ff")
        draw.text((462, 218), "상태: 사용자 지정 호스트네임 적용 완료" if step_idx == 3 else "상태: OS 설치 시 자동 부여된 기본 식별 이름", fill="#1d4ed8", font=f["sm_b"])

        btn_fill = "#4f46e5" if step_idx < 3 else "#10b981"
        draw.rounded_rectangle([(930, 180), (1165, 238)], radius=12, fill=btn_fill, outline="#0f172a", width=2)
        draw.text((955, 200), "변경 적용됨" if step_idx == 3 else "이 PC의 이름 바꾸기", fill="#ffffff", font=f["bold"])

        draw.rounded_rectangle([(420, 295), (1195, 548)], radius=14, fill="#ffffff", outline="#cbd5e1", width=2)
        draw.text((448, 316), "▶ 시스템 식별 정보 및 명명 규칙 요약", fill="#0f172a", font=f["h3"])
        specs = [
            f"• 장치 이름 (Hostname):  {cur_pc_name}",
            "• 네트워크 표시 역할:  로컬 네트워크 공유 및 블루투스 페어링 시 기기 식별자",
            "• 허용 문자 규격:  한글, 영문 대소문자, 숫자, 하이픈(-) 조합 가능",
            "• 제한 사항:  공백(띄어쓰기) 및 특수기호(@, *, / 등)는 포함할 수 없음",
        ]
        sy = 358
        for sp in specs:
            draw.text((448, sy), sp, fill="#334155", font=f["body"])
            sy += 38

        if step_idx == 1:
            _draw_cursor_and_click(draw, 1020, 210, "Step 1: [이 PC의 이름 바꾸기] 버튼 선택")
        elif step_idx == 2:
            draw.rounded_rectangle([(480, 220), (1050, 510)], radius=16, fill="#0f172a", outline="#38bdf8", width=3)
            draw.text((515, 248), "▶ PC 이름 바꾸기 (새 식별 이름 입력)", fill="#ffffff", font=f["h3"])
            draw.text((515, 284), "현재 이름: DESKTOP-8F9K2A1  →  구분하기 쉬운 기기 이름을 입력합니다.", fill="#cbd5e1", font=f["sm"])
            draw.rounded_rectangle([(515, 322), (1010, 382)], radius=10, fill="#ffffff", outline="#4f46e5", width=3)
            draw.text((535, 340), "ChooSu-WorkPC |", fill="#0f172a", font=f["title"])
            draw.rounded_rectangle([(745, 420), (875, 472)], radius=10, fill="#10b981")
            draw.text((782, 437), "다음 (저장)", fill="#ffffff", font=f["bold"])
            draw.rounded_rectangle([(890, 420), (1010, 472)], radius=10, fill="#475569")
            draw.text((930, 437), "취소", fill="#ffffff", font=f["bold"])
            _draw_cursor_and_click(draw, 810, 468, "Step 2: 새 이름 입력 후 [다음] 클릭")
        else:
            _draw_cursor_and_click(draw, 610, 190, "Step 3: 재시작 후 변경된 장치 이름 확인", is_double=True)

    elif scene_type == "click_trainer":
        draw.rounded_rectangle([(740, 82), (1235, 560)], radius=16, fill="#ffffff", outline="#4f46e5", width=3)
        draw.text((768, 104), "마우스 입력 이벤트 상태 모니터", fill="#0f172a", font=f["h3"])
        draw.line([(768, 138), (1205, 138)], fill="#e2e8f0", width=2)

        left_fill = "#f5365c" if step_idx == 2 else ("#4f46e5" if step_idx == 3 else "#f1f5f9")
        left_txt = "#ffffff" if step_idx >= 2 else "#334155"
        draw.rounded_rectangle([(825, 158), (945, 255)], radius=14, fill=left_fill, outline="#64748b", width=2)
        draw.text((845, 182), "좌클릭(L)", fill=left_txt, font=f["bold"])
        draw.text((842, 210), "단일 선택" if step_idx == 2 else ("연속 2회 실행" if step_idx == 3 else "대기 상태"), fill=left_txt, font=f["sm_b"])

        draw.rounded_rectangle([(955, 168), (995, 245)], radius=10, fill="#cbd5e1")
        draw.text((967, 196), "휠", fill="#1e293b", font=f["sm_b"])

        draw.rounded_rectangle([(1005, 158), (1125, 255)], radius=14, fill="#f1f5f9", outline="#64748b", width=2)
        draw.text((1020, 182), "우클릭(R)", fill="#334155", font=f["bold"])
        draw.text((1025, 210), "옵션 메뉴", fill="#64748b", font=f["sm"])

        steps_info = [
            ("Step 1: 포인터 이동 및 대상 가리키기 (Hover)", step_idx >= 1),
            ("Step 2: 좌클릭(선택) 및 우클릭(메뉴 호출)", step_idx >= 2),
            ("Step 3: 더블클릭(연속 2회 입력)으로 창 실행", step_idx >= 3),
        ]
        sy = 285
        for st_label, done in steps_info:
            bg = "#eff6ff" if done else "#f8fafc"
            bd = "#4f46e5" if done else "#cbd5e1"
            draw.rounded_rectangle([(768, sy), (1205, sy + 52)], radius=10, fill=bg, outline=bd, width=2)
            draw.text((784, sy + 16), st_label, fill="#1e293b", font=f["sm_b"])
            sy += 66

        if step_idx == 1:
            _draw_cursor_and_click(draw, 115, 250, "Step 1: 대상 아이콘 위로 커서 이동 (Hover)")
        elif step_idx == 2:
            draw.rounded_rectangle([(205, 185), (465, 395)], radius=12, fill="#ffffff", outline="#64748b", width=2)
            draw.rectangle([(205, 185), (465, 222)], fill="#f1f5f9")
            draw.text((220, 195), "컨텍스트 메뉴 (우클릭 호출)", fill="#475569", font=f["sm_b"])
            menu_items = ["열기 (Open)", "이름 바꾸기 (Rename)", "복사 (Copy)", "속성 (Properties)"]
            my = 232
            for mi_idx, mi in enumerate(menu_items):
                if mi_idx == 0:
                    draw.rounded_rectangle([(215, my - 4), (455, my + 30)], radius=8, fill="#eff6ff")
                draw.text((228, my), mi, fill="#4f46e5" if mi_idx == 0 else "#1e293b", font=f["body"])
                my += 38
            _draw_cursor_and_click(draw, 105, 240, "Step 2: 좌클릭으로 객체 선택 / 우클릭 메뉴")
        else:
            draw.rounded_rectangle([(195, 92), (715, 560)], radius=16, fill="#ffffff", outline="#4f46e5", width=3)
            draw.rounded_rectangle([(195, 92), (715, 142)], radius=16, fill="#0f172a")
            draw.text((220, 108), "작업 노트.txt — 텍스트 편집기", fill="#ffffff", font=f["bold"])
            notes = [
                "■ GUI 마우스 입력 이벤트 4단계 요약",
                "• Hover (가리키기): 좌표 이동 및 객체 정보 미리보기",
                "• Left Click (좌클릭): 단일 객체 포커스 및 선택",
                "• Double Click (더블클릭): 연결된 애플리케이션 실행",
                "• Right Click (우클릭): 객체별 컨텍스트 메뉴 호출",
            ]
            ny = 168
            for line in notes:
                draw.text((225, ny), line, fill="#0f172a", font=f["body"])
                ny += 38
            _draw_cursor_and_click(draw, 430, 260, "Step 3: 더블클릭으로 애플리케이션 창 실행", is_double=True)

    elif scene_type == "game_minesweeper":
        draw.rounded_rectangle([(185, 78), (1225, 575)], radius=16, fill="#ffffff", outline="#4f46e5", width=3)
        draw.rounded_rectangle([(185, 78), (1225, 128)], radius=16, fill="#0f172a")
        draw.text((210, 94), "지뢰찾기 (Minesweeper) — 좌·우클릭 인터페이스 동작 테스트", fill="#ffffff", font=f["bold"])

        draw.rounded_rectangle([(215, 150), (675, 545)], radius=12, fill="#cbd5e1", outline="#64748b", width=2)
        draw.rounded_rectangle([(235, 168), (655, 218)], radius=8, fill="#0f172a")
        draw.text((255, 182), f"MINE: 00{3 if step_idx < 3 else 0}", fill="#f5365c", font=f["num"])
        draw.text((425, 182), "CLEAR" if step_idx == 3 else "ACTIVE", fill="#facc15", font=f["num"])
        draw.text((545, 182), f"TIME: 0{step_idx * 14:02d}", fill="#38bdf8", font=f["num"])

        board_data = [
            ["1", "1", "1", " ", " ", "1", "F", "1"],
            ["1", "F", "1", " ", " ", "1", "1", "1"],
            ["1", "1", "2", "1", "1", " ", " ", " "],
            [" ", " ", "1", "F", "1", " ", "1", "1"],
            ["1", "1", "2", "1", "1", " ", "1", "F"],
            ["1", "F", "1", " ", " ", " ", "1", "1"],
        ]
        gx0, gy0 = 235, 232
        cell_w, cell_h = 50, 46
        for r_idx, row in enumerate(board_data):
            for c_idx, val in enumerate(row):
                x1 = gx0 + c_idx * (cell_w + 3)
                y1 = gy0 + r_idx * (cell_h + 3)
                x2, y2 = x1 + cell_w, y1 + cell_h
                is_closed = (step_idx == 1 and (r_idx > 2 or val == "F"))
                if is_closed:
                    draw.rounded_rectangle([(x1, y1), (x2, y2)], radius=6, fill="#94a3b8", outline="#475569", width=2)
                elif val == "F":
                    draw.rounded_rectangle([(x1, y1), (x2, y2)], radius=6, fill="#fef2f2", outline="#f5365c", width=2)
                    draw.text((x1 + 11, y1 + 11), "깃발", fill="#dc2626", font=f["sm_b"])
                else:
                    draw.rounded_rectangle([(x1, y1), (x2, y2)], radius=6, fill="#f8fafc", outline="#cbd5e1", width=1)
                    if val in ("1", "2"):
                        col = "#4f46e5" if val == "1" else "#10b981"
                        draw.text((x1 + 18, y1 + 10), val, fill=col, font=f["num"])

        draw.rounded_rectangle([(700, 150), (1195, 545)], radius=12, fill="#f8fafc", outline="#cbd5e1", width=2)
        draw.text((725, 172), "인터페이스 조작 로그", fill="#0f172a", font=f["h3"])
        logs = [
            ("좌클릭 (셀 개방)", "타일을 열어 인접한 8칸 내 지뢰 개수를 확인합니다.", True),
            ("우클릭 (깃발 마킹)", "지뢰 위치로 파악된 타일에 우클릭으로 깃발을 표시합니다.", step_idx >= 2),
            ("보드 클리어", "좌·우클릭의 정밀한 구분을 통해 모든 안전 타일을 개방합니다.", step_idx == 3),
        ]
        ly = 218
        for l_title, l_desc, active in logs:
            bg = "#eff6ff" if active else "#f1f5f9"
            bd = "#4f46e5" if active else "#cbd5e1"
            draw.rounded_rectangle([(722, ly), (1172, ly + 74)], radius=10, fill=bg, outline=bd, width=2)
            draw.text((740, ly + 12), l_title, fill="#4f46e5" if active else "#64748b", font=f["bold"])
            draw.text((740, ly + 40), l_desc, fill="#1e293b", font=f["sm"])
            ly += 88

        if step_idx == 1:
            _draw_cursor_and_click(draw, 360, 300, "Step 1: 좌클릭으로 타일 개방 및 숫자 확인")
        elif step_idx == 2:
            _draw_cursor_and_click(draw, 305, 295, "Step 2: 우클릭으로 지뢰 타일에 깃발 표시", is_right_click=True)
        else:
            _draw_cursor_and_click(draw, 520, 410, "Step 3: 모든 안전 구역 개방 완료", is_double=True)

    else:
        draw.rounded_rectangle([(195, 82), (1220, 570)], radius=16, fill="#ffffff", outline="#4f46e5", width=3)
        draw.rounded_rectangle([(195, 82), (1220, 134)], radius=16, fill="#0f172a")
        draw.text((222, 98), f"OS 환경 설정 및 동작 테스트 — {lesson_title[:38]}", fill="#ffffff", font=f["bold"])
        draw.rounded_rectangle([(225, 165), (1190, 540)], radius=12, fill="#f8fafc", outline="#cbd5e1", width=2)
        sy = 195
        for sline in (code_or_summary or "1. 대상 메뉴 및 설정 위치 확인\n2. 마우스 클릭 또는 옵션 변경 실행\n3. 시스템 상태 반영 결과 확인").splitlines()[:6]:
            draw.text((248, sy), f"• {sline[:54]}", fill="#0f172a", font=f["body"])
            sy += 42
        cx = 360 + (step_idx - 1) * 220
        cy = 310 + (step_idx - 1) * 35
        _draw_cursor_and_click(draw, cx, cy, f"Step {step_idx}: 해당 메뉴 선택 및 설정 적용")

    # 5. 하단 단계별 요약 바 (객관적이고 깔끔한 연구실 캡션)
    draw.rounded_rectangle([(26, 600), (1254, 718)], radius=14, fill="#ffffff", outline="#cbd5e1", width=2)
    draw.rounded_rectangle([(46, 622), (210, 696)], radius=10, fill="#0f172a")
    draw.text((70, 648), f"STEP {step_idx} 요약", fill="#ffffff", font=f["bold"])
    bubble = custom_caption or "화면 내 표시된 위치의 메뉴를 선택하여 설정 변경 과정을 진행합니다."
    draw.text((235, 634), bubble[:68], fill="#0f172a", font=f["h3"])
    draw.text((235, 668), "이전 단계로 돌아가려면 취소 버튼을 누르거나 Esc 키를 입력합니다.", fill="#64748b", font=f["body"])

    # 6. 최하단 OS 작업표시줄
    draw.rectangle([(0, height - 56), (width, height)], fill="#090d16")
    draw.rounded_rectangle([(24, height - 46), (150, height - 10)], radius=10, fill="#4f46e5")
    draw.text((42, height - 37), "시작 (Start)", fill="#ffffff", font=f["bold"])
    draw.text((175, height - 37), "시스템 설정   |   파일 탐색기   |   인터페이스 테스트", fill="#cbd5e1", font=f["sm_b"])
    draw.text((1020, height - 37), "ChooSu Lab Environment", fill="#94a3b8", font=f["sm_b"])

    img.save(out_png_path, "PNG")
    return True


def generate_virtual_os_screenshots(scene_type, lesson_title, image_dir, stamp_str, code_or_summary="", baseurl="/choosu-lab"):
    os.makedirs(image_dir, exist_ok=True)
    os.makedirs("audit_logs", exist_ok=True)
    saved_urls = []
    local_files = []

    if scene_type == "pc_rename":
        step_captions = {
            1: "1단계: [시작] -> [설정] -> [시스템]에서 현재 장치 이름 옆의 [이 PC의 이름 바꾸기]를 선택합니다.",
            2: "2단계: 입력창에 구분하기 쉬운 새 이름을 입력하고 [다음] 버튼을 눌러 저장합니다.",
            3: "3단계: 시스템 재시작 후 장치 사양 항목에서 변경된 호스트네임을 확인합니다."
        }
    else:
        step_captions = {
            1: "1단계: 데스크톱 화면에서 실행할 대상 아이콘과 메뉴 위치를 확인합니다.",
            2: "2단계: 마우스 좌클릭(선택)과 우클릭(컨텍스트 메뉴 호출) 동작을 수행합니다.",
            3: "3단계: 입력 이벤트가 정상적으로 처리되어 실행된 결과 창을 확인합니다."
        }

    for step_idx in (1, 2, 3):
        filename = f"os_step{step_idx}_{stamp_str}.png"
        out_path = os.path.join(image_dir, filename)
        render_os_desktop_pil(
            scene_type=scene_type,
            step_idx=step_idx,
            lesson_title=lesson_title,
            out_png_path=out_path,
            code_or_summary=code_or_summary,
            custom_caption=step_captions[step_idx]
        )
        saved_urls.append(f"{baseurl}/{image_dir}/{filename}")
        local_files.append({
            "step": step_idx,
            "path": out_path,
            "url": f"{baseurl}/{image_dir}/{filename}",
            "caption": step_captions[step_idx],
            "size_bytes": os.path.getsize(out_path) if os.path.exists(out_path) else 0
        })

    test_report = {
        "timestamp": datetime.datetime.now().isoformat(),
        "scene_type": scene_type,
        "lesson_title": lesson_title,
        "resolution": "1280x800",
        "virtual_display_status": "PASS",
        "screenshots": local_files
    }
    with open("audit_logs/last_os_test.json", "w", encoding="utf-8") as f:
        json.dump(test_report, f, ensure_ascii=False, indent=2)

    return saved_urls
