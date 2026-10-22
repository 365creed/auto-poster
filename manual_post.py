"""
manual_post.py
저녁 시간대(인간이 직접 수동으로 올리는 시간)에 사용하는 간편 수동 발행 CLI 도구입니다.
"""

import os
import argparse
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description="ChooSu Note 저녁 수동 포스팅 발행 도구")
    parser.add_argument("--title", required=True, help="포스팅 제목")
    parser.add_argument("--topic", default="", help="부제목 또는 AI 보조 작성용 메모")
    parser.add_argument("--body", default="", help="직접 작성한 마크다운 본문 텍스트")
    parser.add_argument("--body-file", default="", help="직접 작성한 마크다운 파일 경로")
    parser.add_argument(
        "--scene",
        default="click_trainer",
        choices=["click_trainer", "game_minesweeper", "game_typing", "desktop_windows", "history_simulator", "system_monitor", "file_explorer"],
        help="가상 OS 스크린샷 실습 시나리오 선택"
    )
    args = parser.parse_args()

    body_text = args.body
    if args.body_file and os.path.exists(args.body_file):
        with open(args.body_file, "r", encoding="utf-8") as f:
            body_text = f.read()

    env = os.environ.copy()
    env["POST_SLOT"] = "manual"
    env["MANUAL_TITLE"] = args.title
    env["MANUAL_TOPIC"] = args.topic
    env["MANUAL_BODY"] = body_text
    env["OS_SCENE"] = args.scene

    print("🌙 [저녁 수동 포스팅 모드] 가상 OS 스크린샷 촬영 및 포스트 발행을 시작합니다...")
    res = subprocess.run([sys.executable, "poster.py"], env=env)
    if res.returncode == 0:
        print("✨ 저녁 수동 포스팅이 _posts/ 폴더에 성공적으로 생성되었습니다!")
    else:
        sys.exit(res.returncode)


if __name__ == "__main__":
    main()
