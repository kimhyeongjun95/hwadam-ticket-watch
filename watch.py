#!/usr/bin/env python3
"""화담숲(NOL/야놀자) 지정일 취소표 감시.

지정한 날짜가 품절 → 판매중으로 바뀌면 ntfy / 텔레그램으로 알린다.
상태는 state.json 에 남겨 바뀔 때만 알림이 가도록 한다.
LOG_DIR 이 있으면 실행마다 결과(날짜.csv)와 API 응답 원문(날짜.jsonl)을 쌓는다.
"""
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone

PRODUCT_URL = "https://leisure-web.yanolja.com/leisure/10367229"
# NOL 앱 안에서 상품 페이지를 바로 여는 주소 (사이트가 쓰는 webView 링크와 같은 형식)
APP_PRODUCT_URL = f"nol-app://wv?url={PRODUCT_URL}"
# EARLIEST_TIME 이상 LATEST_TIME 전에 입장하고 QUANTITY 장 이상 남은 회차만 노린다.
# 그 밖의 회차는 재고가 생겨도 알리지 않는다 (기록에는 남김)
QUANTITY = int(os.environ.get("QUANTITY", "2"))
EARLIEST_TIME = os.environ.get("EARLIEST_TIME", "09:00")
LATEST_TIME = os.environ.get("LATEST_TIME", "15:00")
API = "https://leisure-web-api.yanolja.com/product/v1/products/10367229/option-groups/10480706"
# 사이트 JS 에 들어 있는 웹 공용 토큰. 계정과 무관하고 모든 브라우저가 같은 값을 보낸다.
API_HEADERS = {
    # Cloudflare 가 파이썬 기본 User-Agent 는 403 으로 막는다.
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "platform": "Web",
    "Access-Token": "442A472D4B6150645367566B59703373367639792442264528482B4D62516554",
    "Origin": "https://leisure-web.yanolja.com",
    "Referer": "https://leisure-web.yanolja.com/",
}

KST = timezone(timedelta(hours=9))
QUIET_START, QUIET_END = (0, 0), (7, 30)  # 이 시간대(KST)에는 조회하지 않는다
TARGET_DATES = [d.strip() for d in os.environ.get("TARGET_DATES", "2026-10-31,2026-11-01").split(",") if d.strip()]
STATE_FILE = os.environ.get("STATE_FILE", "state.json")
LOG_DIR = os.environ.get("LOG_DIR")
WEEKDAYS = "월화수목금토일"
RAW = []  # 이번 실행의 API 응답 원문 (로그용)


def label(d):
    x = date.fromisoformat(d)
    return f"{x.month}/{x.day}({WEEKDAYS[x.weekday()]})"


def http(url, data=None, headers=None, timeout=15):
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers or {})
    if body is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def describe(e):
    return f"HTTP {e.code}" if isinstance(e, urllib.error.HTTPError) else repr(e)


def api(path):
    for attempt in range(2):
        try:
            body = http(API + path, headers=API_HEADERS)["body"]
            RAW.append({"path": path, "body": body})
            return body
        except Exception as e:
            RAW.append({"path": path, "error": describe(e)})
            if attempt:
                raise
            time.sleep(5)


def fetch(dates):
    """날짜별 {status, slots:[(시간, 수량)], rounds_ok}"""
    schedules = api(f"/schedules?startDate={min(dates)}&endDate={max(dates)}")
    status = {s["date"]: s["scheduleStatusCode"] for s in schedules}
    result = {}
    for d in dates:
        st = status.get(d, "UNKNOWN")
        slots, rounds_ok = [], False
        if st == "IN_SALE":
            try:
                slots = [(r["time"], r["inventoryQuantity"]) for r in api(f"/rounds?date={d}")
                         if r["inventoryQuantity"] > 0]
                rounds_ok = True
            except Exception:
                pass  # 회차 조회가 실패해도 예약 가능 알림은 보낸다
        result[d] = {"status": st, "slots": slots, "rounds_ok": rounds_ok}
    return result


def notify(title, message, priority=3, pc_url=None):
    """pc_url: 맥의 알림 수신기(desktop/listener.py)가 크롬으로 열어 주문서까지 자동 진행할 주소"""
    print(f"[알림 p{priority}] {title}\n{message}")
    if pc_url:
        print(f"  [PC 자동 진행] {pc_url}")
    sent = False
    topic = os.environ.get("NTFY_TOPIC")
    if topic:
        http("https://ntfy.sh/", {
            "topic": topic, "title": title, "message": message,
            "priority": priority, "click": APP_PRODUCT_URL,
            "actions": [{"action": "view", "label": "앱에서 열기", "url": APP_PRODUCT_URL, "clear": True},
                        {"action": "view", "label": "웹에서 열기", "url": PRODUCT_URL, "clear": True}]
                       + ([{"action": "view", "label": "PC 자동 진행", "url": pc_url, "clear": True}] if pc_url else []),
            "tags": ["maple_leaf"] if priority >= 4 else [],
        })
        sent = True
    token, chat = os.environ.get("TELEGRAM_BOT_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    if token and chat:
        http(f"https://api.telegram.org/bot{token}/sendMessage", {
            "chat_id": chat, "text": f"{title}\n{message}\n{PRODUCT_URL}",
            "disable_web_page_preview": True, "disable_notification": priority <= 2,
        })
        sent = True
    if not sent:
        print("(알림 채널이 설정되지 않아 출력만 함)")


def in_quiet_hours(now):
    return QUIET_START <= (now.hour, now.minute) < QUIET_END


def cell(v):
    if v["status"] == "IN_SALE":
        return f"판매중 {sum(q for _, q in v['slots'])}장"
    return "품절" if v["status"] == "SOLD_OUT" else v["status"]


def write_log(now, dates, cur=None, error=None):
    """실행 결과 한 줄: LOG_DIR 의 날짜.csv / 날짜.jsonl, 그리고 Actions 실행 요약"""
    run = os.environ.get("GITHUB_RUN_ID", "local")
    header = ["시각(KST)", "결과"] + [label(d) for d in dates] + ["실행"]
    row = [f"{now:%H:%M:%S}", error or "정상"] + [cell(cur[d]) if cur else "" for d in dates] + [run]
    if LOG_DIR:
        os.makedirs(LOG_DIR, exist_ok=True)
        csv_path = os.path.join(LOG_DIR, f"{now:%Y-%m-%d}.csv")
        new = not os.path.exists(csv_path)
        with open(csv_path, "a", newline="") as f:
            w = csv.writer(f)
            if new:
                w.writerow(header)
            w.writerow(row)
        with open(os.path.join(LOG_DIR, f"{now:%Y-%m-%d}.jsonl"), "a") as f:
            rec = {"t": now.isoformat(timespec="seconds"), "run": run, "error": error, "raw": RAW}
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a") as f:
            f.write("| " + " | ".join(header[:-1]) + " |\n" + "|---" * (len(header) - 1) + "|\n")
            f.write("| " + " | ".join(row[:-1]) + " |\n")


def main():
    now = datetime.now(KST)
    if os.environ.get("NOTIFY_TEST"):
        notify("화담숲 감시 테스트", f"알림이 잘 옵니다. ({now:%m/%d %H:%M})", 3)
        return
    if in_quiet_hours(now) and not os.environ.get("FORCE"):
        print(f"{now:%H:%M} KST 조용한 시간대라 건너뜀")
        return
    dates = [d for d in TARGET_DATES if d >= now.date().isoformat()]
    if not dates:
        print("감시할 날짜가 모두 지났음")
        return

    try:
        with open(STATE_FILE) as f:
            state = json.load(f)
    except FileNotFoundError:
        state = {}
    prev = state.get("dates", {})
    prev_open = state.get("open", {})  # 날짜별로 지난번에 재고가 있던 회차

    # 알림은 예약 가능해졌을 때만. 품절·조회 실패는 기록(logs)에만 남긴다.
    try:
        cur = fetch(dates)
    except Exception as e:
        reason = describe(e)
        print(f"조회 실패: {reason}")
        if os.environ.get("GITHUB_ACTIONS"):
            print(f"::warning title=조회 실패::{reason}")  # 실행 페이지에 경고로 표시
        write_log(now, dates, error=reason)
        return

    for d, v in cur.items():
        print(d, v["status"], v["slots"])
    write_log(now, dates, cur)

    # 회차(하루 27개, 08:00~16:40 20분 간격) 중 노리는 회차에 QUANTITY 장 이상 새로 생기면 알린다.
    # 날짜가 이미 판매중이어도 다른 회차가 새로 열리면 다시 알린다.
    cur_open = {d: sorted(t for t, q in cur[d]["slots"]
                          if q >= QUANTITY and EARLIEST_TIME <= t < LATEST_TIME) for d in dates}
    opened = {}
    for d in dates:
        new = [t for t in cur_open[d] if t not in prev_open.get(d, [])]
        # 회차 조회가 실패해 회차를 모르면 날짜가 새로 열린 것만이라도 알린다
        unknown = cur[d]["status"] == "IN_SALE" and not cur[d]["rounds_ok"] and prev.get(d) != "IN_SALE"
        if new or unknown:
            opened[d] = new
    if opened:
        lines, target = [], None
        for d, new in opened.items():
            # 알림 링크로 주문서까지 바로 가는 건 사이트 버그로 막혀 있어(INVALID_LEISURE_TOKEN),
            # 앱 상품 페이지를 열고 고를 회차를 알려 준다.
            qty = dict(cur[d]["slots"])
            lines.append(f"{label(d)} 새로 열림: {', '.join(f'{t}({qty[t]})' for t in new) or '회차 정보 없음'}")
            lines.append(f"  {EARLIEST_TIME}~{LATEST_TIME} {QUANTITY}장 이상 남은 회차: "
                         f"{', '.join(f'{t}({qty[t]})' for t in cur_open[d][:6]) or '없음'}")
            # PC 자동 진행 대상: 새로 열린 회차 중 가장 이른 것
            if target is None and new:
                target = (d, new[0])
        lines.append("누르면 NOL 앱 상품 페이지가 열려요.")
        pc_url = f"{PRODUCT_URL}#hwadam-auto={target[0]}_{target[1]}_{QUANTITY}" if target else None
        if pc_url:
            lines.append(f"맥이 켜져 있으면 {label(target[0])} {target[1]} 성인 {QUANTITY}장 주문서를 띄워요.")
        notify(f"화담숲 {' · '.join(label(d) for d in opened)} 예약 가능!", "\n".join(lines), 5, pc_url=pc_url)

    save({"dates": {d: cur[d]["status"] for d in dates}, "open": cur_open})


def save(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=1)
        f.write("\n")


if __name__ == "__main__":
    sys.exit(main())
