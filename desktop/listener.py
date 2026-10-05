#!/usr/bin/env python3
"""맥에서 ntfy 토픽을 듣다가 '예약 가능' 알림에 PC 자동 진행 주소가 있으면 크롬으로 연다.

크롬에 넣은 확장(desktop/extension)이 그 주소의 #hwadam-auto=날짜_시간_매수 를 읽어
날짜·회차·성인·일반·매수를 고르고 '구매하기'까지 눌러 주문서를 띄운다. 결제는 사람이 한다.

  python3 desktop/listener.py           # 계속 듣기 (launchd 로 띄우는 게 기본)
  python3 desktop/listener.py --test URL  # 알림 없이 그 주소를 바로 크롬으로 열기
"""
import json
import os
import ssl
import subprocess
import sys
import time
import urllib.request
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
TOPIC_FILE = os.path.join(HERE, "..", ".ntfy-topic")
AUTO_MARK = "#hwadam-auto="
# python.org 파이썬은 인증서 묶음이 없어 HTTPS 가 실패하니 macOS 시스템 인증서를 쓴다
SSL_CTX = ssl.create_default_context()
if os.path.exists("/etc/ssl/cert.pem"):
    SSL_CTX.load_verify_locations("/etc/ssl/cert.pem")


def log(msg):
    print(f"{datetime.now():%m/%d %H:%M:%S} {msg}", flush=True)


def open_in_chrome(url):
    # PC 폭에서는 '옵션 선택하기'가 창을 안 열고 스크롤만 해서, 휴대폰 폭(480px)의 새 창으로 연다.
    # 크롬에서 마지막으로 쓰던 프로필(= NOL 로그인된 프로필)로 열린다.
    script = f'''
tell application "Google Chrome"
  activate
  set w to make new window
  set bounds of w to {{60, 40, 540, 980}}
  set URL of active tab of w to "{url}"
end tell'''
    r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if r.returncode != 0:
        # 자동화 권한을 안 줬으면 일반 탭으로라도 연다 (폭이 넓으면 확장이 멈추고 안내를 띄움)
        log(f"좁은 창 열기 실패, 일반 탭으로 엶: {r.stderr.strip()}")
        subprocess.run(["open", "-a", "Google Chrome", url], check=False)
    subprocess.run(["osascript", "-e",
                    'display notification "크롬에서 주문서를 띄우는 중이에요. 결제만 하세요." '
                    'with title "화담숲 예약 가능" sound name "Glass"'], check=False)


def pc_url(msg):
    for a in msg.get("actions") or []:
        if AUTO_MARK in (a.get("url") or ""):
            return a["url"]
    return None


def listen(topic):
    since = None  # 끊겼다 다시 붙을 때 그 사이 온 알림도 받는다
    seen = set()
    while True:
        url = f"https://ntfy.sh/{topic}/json" + (f"?since={since}" if since else "")
        try:
            with urllib.request.urlopen(url, timeout=90, context=SSL_CTX) as r:
                log("연결됨")
                for line in r:
                    msg = json.loads(line)
                    if msg.get("event") != "message":
                        continue  # open / keepalive
                    since = msg["id"]
                    if msg["id"] in seen:
                        continue
                    seen.add(msg["id"])
                    target = pc_url(msg)
                    log(f"알림: {msg.get('title')} → {target or '자동 진행 대상 아님'}")
                    if target:
                        open_in_chrome(target)
        except Exception as e:
            log(f"연결 끊김: {e!r} — 5초 뒤 다시 연결")
            time.sleep(5)


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--test":
        open_in_chrome(sys.argv[2])
        return
    with open(TOPIC_FILE) as f:
        topic = f.read().strip()
    listen(topic)


if __name__ == "__main__":
    main()
