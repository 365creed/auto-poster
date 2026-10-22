"""
os_sandbox.py
가상화 OS 환경(Virtual OS Desktop & Interactive Mini-Game Simulator)에서
AI 에이전트가 직접 마우스 클릭, 창 제어, 미니게임 플레이, 시스템 탐색을 수행하고
단계별(Step 1 -> Step 2 -> Step 3) 고해상도 스크린샷을 촬영하는 모듈입니다.
"""

import os
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
            "h3": ImageFont.truetype(b_path, 19),
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
    ring_color = "#f43f5e" if is_right_click else "#facc15"
    draw.ellipse([(cx - 28, cy - 28), (cx + 28, cy + 28)], outline=ring_color, width=4)
    if is_double:
        draw.ellipse([(cx - 38, cy - 38), (cx + 38, cy + 38)], outline="#38bdf8", width=3)

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

    pill_x = min(cx + 32, 810)
    pill_y = max(cy - 36, 62)
    pill_w = min(max(len(label_text) * 14 + 34, 240), 440)
    bg_col = "#f43f5e" if is_right_click else "#facc15"
    fg_col = "#ffffff" if is_right_click else "#0f172a"
    draw.rounded_rectangle([(pill_x, pill_y), (pill_x + pill_w, pill_y + 38)], radius=18, fill=bg_col, outline="#0f172a", width=2)
    draw.text((pill_x + 16, pill_y + 9), label_text, fill=fg_col, font=f["bold"])


def render_os_desktop_pil(scene_type, step_idx, lesson_title, out_png_path, code_or_summary="", custom_caption=""):
    f = _load_fonts()
    width, height = 1280, 800
    img = Image.new("RGB", (width, height), color="#0f172a")
    draw = ImageDraw.Draw(img)

    # 1. 바탕화면 데스크톱 영역
    draw.rectangle([(0, 48), (width, height - 56)], fill="#172554")
    draw.ellipse([(-120, 120), (620, 860)], fill="#1e3a8a")
    draw.ellipse([(680, -80), (1380, 620)], fill="#1e1b4b")

    # 2. 상단 실습 진행 배너
    draw.rectangle([(0, 0), (width, 48)], fill="#0f172a")
    draw.line([(0, 48), (width, 48)], fill="#38bdf8", width=2)
    draw.text((24, 13), f"STEP {step_idx}/3  ·  {lesson_title[:46]}", fill="#f8fafc", font=f["bold"])
    draw.rounded_rectangle([(1005, 9), (1256, 39)], radius=14, fill="#0284c7")
    draw.text((1022, 15), "AI Virtual OS · 1280x800 캡처", fill="#ffffff", font=f["sm_b"])

    # 3. 좌측 바탕화면 아이콘 3개
    icons = [
        ("내 첫 노트.txt", "TXT", 78),
        ("학교 수업자료", "DIR", 205),
        ("지뢰찾기 게임", "GAME", 332),
    ]
    for idx, (label, kind, iy) in enumerate(icons):
        is_sel = (scene_type == "click_trainer" and idx == 0 and step_idx >= 1) or (scene_type == "game_minesweeper" and idx == 2)
        if is_sel:
            fill_c = "#1d4ed8" if step_idx >= 2 else "#1e40af"
            out_c = "#60a5fa" if step_idx >= 2 else "#38bdf8"
            draw.rounded_rectangle([(26, iy), (154, iy + 108)], radius=12, fill=fill_c, outline=out_c, width=2)
        icon_bg = "#f8fafc" if kind == "TXT" else ("#facc15" if kind == "DIR" else "#10b981")
        draw.rounded_rectangle([(62, iy + 12), (118, iy + 62)], radius=10, fill=icon_bg, outline="#0f172a", width=2)
        draw.text((71, iy + 27), kind, fill="#0f172a", font=f["sm_b"])
        draw.text((38, iy + 74), label, fill="#ffffff", font=f["sm_b"])

    # 4. 시나리오별 메인 창 & 인터랙션 렌더링
    if scene_type == "click_trainer":
        draw.rounded_rectangle([(740, 82), (1235, 560)], radius=18, fill="#ffffff", outline="#93c5fd", width=3)
        draw.text((768, 104), "AI 마우스 클릭 실시간 감지 트레이너", fill="#0f172a", font=f["h3"])
        draw.line([(768, 138), (1205, 138)], fill="#e2e8f0", width=2)

        left_fill = "#ef4444" if step_idx == 2 else ("#2563eb" if step_idx == 3 else "#f1f5f9")
        left_txt = "#ffffff" if step_idx >= 2 else "#334155"
        draw.rounded_rectangle([(825, 158), (945, 255)], radius=16, fill=left_fill, outline="#64748b", width=2)
        draw.text((845, 182), "왼쪽 버튼", fill=left_txt, font=f["bold"])
        draw.text((840, 210), "딸깍! ON" if step_idx == 2 else ("따닥! 2번" if step_idx == 3 else "대기 중"), fill=left_txt, font=f["sm_b"])

        draw.rounded_rectangle([(955, 168), (995, 245)], radius=10, fill="#cbd5e1")
        draw.text((967, 196), "휠", fill="#1e293b", font=f["sm_b"])

        draw.rounded_rectangle([(1005, 158), (1125, 255)], radius=16, fill="#f1f5f9", outline="#64748b", width=2)
        draw.text((1020, 182), "오른쪽 버튼", fill="#334155", font=f["bold"])
        draw.text((1025, 210), "메뉴 부르기", fill="#64748b", font=f["sm"])

        steps_info = [
            ("1단계: 마우스 화살표(커서) 올리기", step_idx >= 1),
            ("2단계: 왼쪽 버튼 1번 '딸깍!' (선택)", step_idx >= 2),
            ("3단계: 연속 2번 '따닥!' (더블클릭 열기)", step_idx >= 3),
        ]
        sy = 285
        for st_label, done in steps_info:
            bg = "#eff6ff" if done else "#f8fafc"
            bd = "#3b82f6" if done else "#cbd5e1"
            draw.rounded_rectangle([(768, sy), (1205, sy + 52)], radius=10, fill=bg, outline=bd, width=2)
            draw.text((786, sy + 16), st_label, fill="#1e293b", font=f["bold"])
            draw.rounded_rectangle([(1115, sy + 12), (1190, sy + 40)], radius=12, fill="#16a34a" if done else "#94a3b8")
            draw.text((1130, sy + 17), "완료" if done else "대기", fill="#ffffff", font=f["sm_b"])
            sy += 66

        if step_idx == 1:
            _draw_cursor_and_click(draw, 115, 145, "1단계: 아이콘 위에 화살표 올리기 (Hover)")
        elif step_idx == 2:
            draw.rounded_rectangle([(205, 125), (465, 345)], radius=12, fill="#ffffff", outline="#64748b", width=2)
            draw.rectangle([(205, 125), (465, 162)], fill="#f1f5f9")
            draw.text((220, 135), "우클릭 시 열리는 보조 메뉴판", fill="#475569", font=f["sm_b"])
            menu_items = ["열기 (더블클릭과 같음)", "이름 바꾸기 (F2)", "복사하기 (Ctrl+C)", "속성 자세히 보기"]
            my = 172
            for mi_idx, mi in enumerate(menu_items):
                if mi_idx == 0:
                    draw.rounded_rectangle([(215, my - 4), (455, my + 30)], radius=8, fill="#eff6ff")
                draw.text((228, my), mi, fill="#2563eb" if mi_idx == 0 else "#1e293b", font=f["body"])
                my += 40
            _draw_cursor_and_click(draw, 105, 130, "자, 이게 클릭(좌클릭)이야! [딸깍!]")
        else:
            draw.rounded_rectangle([(195, 92), (715, 560)], radius=16, fill="#ffffff", outline="#60a5fa", width=3)
            draw.rounded_rectangle([(195, 92), (715, 142)], radius=16, fill="#0f172a")
            draw.text((220, 108), "내 첫 노트.txt — 메모장 (더블클릭 실행 완료!)", fill="#ffffff", font=f["bold"])
            draw.rounded_rectangle([(665, 102), (698, 132)], radius=6, fill="#ef4444")
            draw.text((676, 108), "X", fill="#ffffff", font=f["bold"])

            notes = [
                "축하합니다! 더블클릭으로 창을 열었어요!",
                "",
                "• 가리키기: 화살표만 살며시 올려놓기",
                "• 좌클릭(1번): '너로 정했어!' 아이콘 선택",
                "• 더블클릭(2번): '문을 열어라!' 프로그램 실행",
                "• 우클릭(오른쪽): 숨겨진 메뉴판 부르기",
            ]
            ny = 168
            for line in notes:
                draw.text((225, ny), line, fill="#0f172a" if ny > 170 else "#1d4ed8", font=f["bold"] if ny == 168 else f["body"])
                ny += 34

            draw.rounded_rectangle([(220, 395), (690, 535)], radius=10, fill="#0f172a")
            cy_text = 410
            for cline in (code_or_summary or "실습 완료: 마우스 4대 동작 마스터!").splitlines()[:4]:
                draw.text((238, cy_text), cline[:42], fill="#38bdf8", font=f["sm_b"])
                cy_text += 28
            _draw_cursor_and_click(draw, 430, 260, "따닥! 더블클릭으로 창 열기 성공!", is_double=True)

    elif scene_type == "game_minesweeper":
        draw.rounded_rectangle([(185, 78), (1225, 575)], radius=16, fill="#ffffff", outline="#94a3b8", width=3)
        draw.rounded_rectangle([(185, 78), (1225, 128)], radius=16, fill="#0f172a")
        draw.text((210, 94), "ChooSu OS — AI 지뢰찾기(Minesweeper) 마우스 좌·우클릭 실전 플레이", fill="#ffffff", font=f["bold"])

        draw.rounded_rectangle([(215, 150), (675, 545)], radius=12, fill="#cbd5e1", outline="#64748b", width=2)
        draw.rounded_rectangle([(235, 168), (655, 218)], radius=8, fill="#0f172a")
        draw.text((255, 182), f"MINE: 00{3 if step_idx < 3 else 0}", fill="#ef4444", font=f["num"])
        draw.text((425, 182), "WIN!" if step_idx == 3 else "PLAY", fill="#facc15", font=f["num"])
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
                    draw.rounded_rectangle([(x1, y1), (x2, y2)], radius=6, fill="#fef2f2", outline="#ef4444", width=2)
                    draw.text((x1 + 11, y1 + 11), "깃발", fill="#dc2626", font=f["sm_b"])
                else:
                    draw.rounded_rectangle([(x1, y1), (x2, y2)], radius=6, fill="#f8fafc", outline="#cbd5e1", width=1)
                    if val in ("1", "2"):
                        col = "#2563eb" if val == "1" else "#16a34a"
                        draw.text((x1 + 18, y1 + 10), val, fill=col, font=f["num"])

        draw.rounded_rectangle([(700, 150), (1195, 545)], radius=12, fill="#f8fafc", outline="#cbd5e1", width=2)
        draw.text((725, 172), "AI 실시간 마우스 플레이 해설", fill="#0f172a", font=f["h3"])
        logs = [
            ("좌클릭 (땅 파기)", "안전해 보이는 칸을 왼쪽 클릭해 숫자를 확인해요.", True),
            ("우클릭 (깃발 꽂기)", "숫자 힌트로 찾은 지뢰 칸에 우클릭으로 깃발을 세워요.", step_idx >= 2),
            ("스테이지 클리어!", "좌·우클릭 조합으로 모든 안전 구역을 열었어요!", step_idx == 3),
        ]
        ly = 218
        for l_title, l_desc, active in logs:
            bg = "#eff6ff" if active else "#f1f5f9"
            bd = "#2563eb" if active else "#cbd5e1"
            draw.rounded_rectangle([(722, ly), (1172, ly + 74)], radius=10, fill=bg, outline=bd, width=2)
            draw.text((740, ly + 12), l_title, fill="#1d4ed8" if active else "#64748b", font=f["bold"])
            draw.text((740, ly + 40), l_desc, fill="#1e293b", font=f["sm"])
            ly += 88

        if step_idx == 1:
            _draw_cursor_and_click(draw, 360, 300, "1단계: 좌클릭으로 안전한 칸 열기!")
        elif step_idx == 2:
            _draw_cursor_and_click(draw, 305, 295, "2단계: 지뢰 칸에 우클릭으로 깃발 꽂기!", is_right_click=True)
        else:
            _draw_cursor_and_click(draw, 520, 410, "3단계: 지뢰찾기 완벽 클리어 성공!", is_double=True)

    else:
        draw.rounded_rectangle([(195, 82), (1220, 570)], radius=16, fill="#ffffff", outline="#60a5fa", width=3)
        draw.rounded_rectangle([(195, 82), (1220, 134)], radius=16, fill="#0f172a")
        draw.text((222, 98), f"ChooSu Virtual OS — {lesson_title[:38]}", fill="#ffffff", font=f["bold"])
        draw.rounded_rectangle([(1090, 94), (1122, 122)], radius=6, fill="#334155")
        draw.text((1100, 98), "_", fill="#ffffff", font=f["bold"])
        draw.rounded_rectangle([(1130, 94), (1162, 122)], radius=6, fill="#334155")
        draw.text((1140, 98), "□", fill="#ffffff", font=f["bold"])
        draw.rounded_rectangle([(1170, 94), (1202, 122)], radius=6, fill="#ef4444")
        draw.text((1180, 98), "X", fill="#ffffff", font=f["bold"])

        draw.rectangle([(198, 134), (1217, 170)], fill="#f1f5f9")
        draw.text((222, 143), f"실습 단계: Step {step_idx} / 3   |   모드: 가상 OS 직접 조작 & 화면 캡처", fill="#475569", font=f["sm_b"])

        draw.rounded_rectangle([(225, 192), (735, 540)], radius=12, fill="#f8fafc", outline="#cbd5e1", width=2)
        draw.text((248, 212), f"AI의 가상 OS 단계별 실습 노트 (Step {step_idx})", fill="#1d4ed8", font=f["h3"])
        sy = 258
        for sline in (code_or_summary or "1. 바탕화면에서 아이콘 위치 확인\n2. 마우스 커서를 이동해 클릭 실행\n3. 열린 창에서 결과 확인").splitlines()[:6]:
            draw.text((248, sy), f"• {sline[:40]}", fill="#1e293b", font=f["body"])
            sy += 40

        draw.rounded_rectangle([(760, 192), (1190, 540)], radius=12, fill="#0f172a", outline="#38bdf8", width=2)
        draw.text((785, 212), "컴퓨터 내부 실시간 동작 원리", fill="#38bdf8", font=f["h3"])
        sys_lines = [
            "[0과 1 전기 신호] 이진수 데이터 변환 정상",
            f"[CPU 두뇌 요리사] 명령어 처리 중 ({step_idx * 33}%)",
            "[RAM 작업 식탁] 현재 열린 창 데이터 보관",
            "[SSD 책장 창고] 파일 영구 저장 준비 완료",
            f"[마우스 이벤트] Step {step_idx} 클릭 신호 전달됨!",
        ]
        ey = 262
        for el in sys_lines:
            draw.text((785, ey), el, fill="#e2e8f0", font=f["sm_b"])
            ey += 44

        cx = 360 + (step_idx - 1) * 220
        cy = 310 + (step_idx - 1) * 35
        _draw_cursor_and_click(draw, cx, cy, f"STEP {step_idx}: 여기를 클릭해 실습 진행!")

    # 5. 하단 친절한 AI 선생님 코칭 바
    draw.rounded_rectangle([(26, 600), (1254, 718)], radius=16, fill="#ffffff", outline="#38bdf8", width=3)
    draw.rounded_rectangle([(46, 622), (225, 696)], radius=12, fill="#0284c7")
    draw.text((66, 648), "친절한 AI 선생님", fill="#ffffff", font=f["bold"])
    bubble = custom_caption or "겁먹지 말고 화면 속 노란색 동그라미 위치를 마우스 왼쪽 버튼으로 가볍게 '딸깍!' 눌러보세요!"
    draw.text((248, 634), bubble[:68], fill="#0f172a", font=f["h3"])
    draw.text((248, 668), "잘못 눌러도 언제든 Esc 키나 닫기(X) 버튼을 누르면 안전하게 돌아갈 수 있어요.", fill="#475569", font=f["body"])

    # 6. 최하단 OS 작업표시줄 (Taskbar)
    draw.rectangle([(0, height - 56), (width, height)], fill="#090d16")
    draw.rounded_rectangle([(24, height - 46), (150, height - 10)], radius=10, fill="#2563eb")
    draw.text((42, height - 37), "시작 (Start)", fill="#ffffff", font=f["bold"])
    draw.text((175, height - 37), "파일 탐색기   |   마우스 클릭 연습기   |   지뢰찾기 실습실", fill="#cbd5e1", font=f["sm_b"])
    draw.text((920, height - 37), "ChooSu 컴퓨터 기초 학교  ·  100% 연결됨", fill="#38bdf8", font=f["sm_b"])

    img.save(out_png_path, "PNG")
    return True


def generate_virtual_os_screenshots(scene_type, lesson_title, image_dir, stamp_str, code_or_summary="", baseurl="/choosu-lab"):
    os.makedirs(image_dir, exist_ok=True)
    saved_urls = []

    step_captions = {
        1: "1단계: 가상 OS 바탕화면에서 오늘 배울 아이콘과 프로그램 위치를 먼저 눈으로 확인해요.",
        2: "2단계: AI가 직접 마우스를 움직여 클릭(딸깍!)하거나 미니게임을 조작하는 순간이에요.",
        3: "3단계: 클릭과 조작이 성공적으로 반영되어 창이 열리고 실습 목표를 달성한 화면이에요!"
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

    return saved_urls
