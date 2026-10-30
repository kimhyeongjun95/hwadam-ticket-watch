#!/usr/bin/env python3
"""맥에서 ntfy 토픽을 듣다가 '예약 가능' 알림에 PC 자동 진행 주소가 있으면 크롬으로 연다.

크롬에 넣은 확장(desktop/extension)이 그 주소의 #hwadam-auto=날짜_시간_매수 를 읽어
날짜·회차·성인·일반·매수를 고르고 '구매하기'까지 눌러 주문서를 띄운다. 결제는 사람이 한다.

맥 조회를 켜 두면 GitHub 의 1분 조회 사이사이에 맥에서도 20초마다(.poll-every 로 이 맥만 바꿀 수 있음) 직접 조회해 같은 식으로 알리고 띄운다.
켜고 끄기는 메뉴 막대 🍁(SwiftBar, desktop/swiftbar) 나 http://127.0.0.1:8789/poll/toggle.
상태·로그는 http://127.0.0.1:8789/ 에서 본다. 노리는 날짜·회차·매수도 거기서 바꾼다 (GitHub 저장소 변수로 저장해
GitHub 조회와 맥 조회가 같은 값을 쓴다. GitHub 에서 직접 고친 값도 몇 분 안에 따라감).

  python3 desktop/listener.py           # 계속 듣기 (launchd 로 띄우는 게 기본)
  python3 desktop/listener.py --test URL  # 알림 없이 그 주소를 바로 크롬으로 열기
"""
import json
import os
import shutil
import ssl
import subprocess
import sys
import threading
import time
import urllib.request
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, ROOT)
import watch  # noqa: E402  맥 조회도 GitHub 과 같은 조회·판정 코드를 쓴다
TOPIC_FILE = os.path.join(ROOT, ".ntfy-topic")
AUTO_MARK = "#hwadam-auto="
LOG_PORT = 8789  # 크롬 확장이 진행 상황을 보내오고, 메뉴 막대·단축어가 맥 조회를 켜고 끄는 로컬 포트
POLL_FLAG = os.path.join(ROOT, ".local-poll")  # 이 파일이 있으면 맥 조회가 켜진 것 (껐다 켜도 유지)
POLL_EVERY_FILE = os.path.join(ROOT, ".poll-every")  # 이 맥에서만 간격을 바꾸려면 초를 한 줄로 (git 에 안 올림)
try:
    with open(POLL_EVERY_FILE) as f:
        POLL_EVERY = max(1, int(f.read().strip()))  # 초
except (OSError, ValueError):
    POLL_EVERY = 20  # 초
REOPEN_AFTER = 10 * 60  # 같은 회차는 이 시간(초) 안에 다시 알려도 크롬을 또 열지 않는다
# 알림이 오면 바로 고르도록 상품 페이지를 미리 띄워 Dock 에 내려 둔 창 (대기 창). 창 번호를 적어 둔다 (git 에 안 올림)
STANDBY_FILE = os.path.join(ROOT, ".standby-window")
STANDBY_HASH = "#hwadam-standby"
STANDBY_REARM = 2 * 60  # 초. 대기 창을 쓰고 나서 이만큼 뒤에 새로 띄운다 (그 창에서 결제 중일 수 있어서)
LOG_FILE = os.path.expanduser("~/Library/Logs/hwadam-listener.log")  # install.sh 가 launchd 출력을 여기로 보낸다
DASHBOARD = os.path.join(HERE, "dashboard.html")  # http://127.0.0.1:8789/ 상태·로그 화면
REPO = "kimhyeongjun95/hwadam-ticket-watch"
DAY_LOG_URL = f"https://github.com/{REPO}/blob/logs/{{:%Y-%m-%d}}.csv"
SETTINGS_CACHE = os.path.join(ROOT, ".settings.json")  # GitHub 변수와 마지막으로 맞춘 설정 (못 붙을 때도 같은 기준으로 돌게)
SETTINGS_SYNC = 5 * 60  # 초. 이만큼마다 GitHub 변수를 다시 읽는다
# launchd 로 뜨면 PATH 가 짧아 Homebrew 의 gh 를 못 찾으니 흔한 위치도 본다
GH = shutil.which("gh") or next((p for p in ("/usr/local/bin/gh", "/opt/homebrew/bin/gh") if os.path.exists(p)), None)
# python.org 파이썬은 인증서 묶음이 없어 HTTPS 가 실패하니 macOS 시스템 인증서를 쓴다
SSL_CTX = ssl.create_default_context()
if os.path.exists("/etc/ssl/cert.pem"):
    SSL_CTX.load_verify_locations("/etc/ssl/cert.pem")
# 회사 망처럼 TLS 를 가로채는 프록시 뒤라면 그 CA 묶음도 읽는다.
# 프록시 인증서는 파이썬 3.13 의 엄격 검사(Authority Key Identifier 필수)에 걸려서 그때는 그 검사를 끈다.
EXTRA_CA = os.path.expanduser(os.environ.get("EXTRA_CA_FILE", "~/.local/share/corp-ca.pem"))
if os.path.exists(EXTRA_CA):
    SSL_CTX.load_verify_locations(EXTRA_CA)
    SSL_CTX.verify_flags &= ~ssl.VERIFY_X509_STRICT


def log(msg):
    print(f"{datetime.now():%m/%d %H:%M:%S} {msg}", flush=True)


def front_app():
    """지금 맨 앞 앱의 번들 ID (자동화 권한 없이 읽힌다)"""
    r = subprocess.run(["/bin/sh", "-c", "lsappinfo info -only bundleid $(lsappinfo front)"], capture_output=True, text=True)
    return r.stdout.split("=")[-1].strip().strip('"')


def chrome(script):
    """크롬에 AppleScript 를 보내고 결과 글자를 돌려준다 (실패하면 None)"""
    r = subprocess.run(["osascript", "-e", f'tell application "Google Chrome"\n{script}\nend tell'],
                       capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def new_window(url):
    """PC 폭에서는 '옵션 선택하기'가 창을 안 열고 스크롤만 해서, 휴대폰 폭(480px)의 새 창으로 연다.
    크롬에서 마지막으로 쓰던 프로필(= NOL 로그인된 프로필)로 열린다.
    하던 일을 가리지 않게 창은 바로 내려(최소화) 두고 쓰던 앱을 다시 앞으로 돌린다. 창 번호를 돌려준다"""
    before = front_app()
    wid = chrome(f'''set w to make new window
  set bounds of w to {{60, 40, 540, 980}}
  set URL of active tab of w to "{url}"
  set minimized of w to true
  return id of w''')
    if wid and before and before != "com.google.Chrome":
        subprocess.run(["osascript", "-e", f'tell application id "{before}" to activate'], check=False)
    return wid


def read_standby():
    try:
        with open(STANDBY_FILE) as f:
            return int(f.read())
    except (OSError, ValueError):
        return None


def write_standby(wid):
    if wid:
        with open(STANDBY_FILE, "w") as f:
            f.write(str(wid))
    elif os.path.exists(STANDBY_FILE):
        os.remove(STANDBY_FILE)


def standby_state(wid):
    """대기 창 상태: "ready"(상품 페이지에서 내려가 있음), "busy"(내려간 채 로그인하러 감), "gone"(닫혔거나 사람이 열어 봄)"""
    out = chrome(f'''if not (exists window id {wid}) then return "gone"
  set w to window id {wid}
  return (minimized of w as text) & " " & (URL of active tab of w)''')
    if not out or not out.startswith("true "):
        return "gone"
    return "ready" if out[5:].startswith(watch.PRODUCT_URL) else "busy"


# 대기 창에 알림 넘기기. AppleScript 로 주소를 바꾸면 내려 둔 창이 올라와 버려서 (10/30) 확장을 거친다:
# 대기 창의 확장(background.js)이 /standby/wait 로 계속 기다리고 있다가 받으면 바로 고르고 /standby/ack 로 받았다고 알린다
standby_cond = threading.Condition()
standby_queue = []  # [(주소, 넣은 시각)]
standby_seen = 0  # 확장이 마지막으로 /standby/wait 를 부른 시각
standby_ack = threading.Event()


def hand_to_standby(url):
    """대기 창이 기다리고 있으면 주소를 넘기고 1.5초 안에 받았다고 하면 True"""
    if time.time() - standby_seen > 30:
        return False
    standby_ack.clear()
    with standby_cond:
        standby_queue[:] = [(url, time.time())]
        standby_cond.notify_all()
    if standby_ack.wait(1.5):
        return True
    with standby_cond:
        standby_queue.clear()  # 늦게라도 가져가서 두 창에서 같이 돌지 않게
    return False


def open_in_chrome(url):
    # 대기 창이 있으면 이미 떠 있는 페이지에서 바로 고르게 한다. 없거나 반응이 없으면 새 창으로.
    # 주문서가 뜨면 확장이 창을 올리고 show_chrome 이 크롬을 앞으로 띄운다
    global last_open
    last_open = time.time()
    # Playwright 같은 자동화 도구가 띄운 크롬(--user-data-dir 로 따로 뜸)이 있으면 osascript 가 그쪽으로 가서
    # 확장도 로그인도 없는 창이 열린다 (10/30). 고칠 길이 없어 알리기만 한다
    other = subprocess.run(["pgrep", "-f", "Google Chrome.app/Contents/MacOS/Google Chrome .*--user-data-dir"],
                           capture_output=True, text=True).stdout.split()
    if other:
        log(f"자동화용 크롬이 떠 있음 (pid {', '.join(other)}) — 엉뚱한 크롬에 열릴 수 있음")
        notify_mac("자동화용 크롬이 떠 있어 평소 크롬이 아닌 곳에 열릴 수 있어요. 그 크롬을 닫아 주세요.", "Basso")
    if hand_to_standby(url):
        write_standby(None)  # 한 번 쓰면 끝 (그 창에서 주문·결제를 한다)
        log("대기 창에서 바로 진행")
    elif not new_window(url):
        # 자동화 권한을 안 줬으면 일반 탭으로라도 연다 (폭이 넓으면 확장이 멈추고 안내를 띄움)
        log("좁은 창 열기 실패, 일반 탭으로 엶")
        subprocess.run(["open", "-a", "Google Chrome", url], check=False)
    notify_mac("예약 가능! 뒤에서 주문서를 띄우는 중이에요. 뜨면 크롬이 앞으로 나와요.", "Glass")
    # 확장이 끝(주문서 뜸·멈춤)을 알려 오지 않은 채 1분이 지나면 숨은 창에서 막힌 것일 수 있으니 알린다
    opened = time.time()
    timer = threading.Timer(60, lambda: last_done < opened and notify_mac(
        "1분이 지나도 주문서가 안 떴어요. Dock 의 크롬 창을 확인하세요.", "Basso"))
    timer.daemon = True
    timer.start()


def show_chrome():
    """확장이 내려 뒀던 창을 올렸다고 알려 오면 크롬을 맨 앞으로 (주문서가 떴거나 네이버 로그인을 눌러야 할 때)"""
    subprocess.run(["osascript", "-e", 'tell application "Google Chrome" to activate'], check=False)


opened_at = {}  # PC 자동 진행 주소 → 크롬으로 연 시각
last_poll = ""  # 맥 조회 마지막 결과 (/poll 과 상태 화면에 보여 줌)
last_alert = (0, "")  # (받은 시각, "월/일 시:분 제목") — 메뉴 막대에 띄움
paused_until = 0  # 403·429 로 맥 조회를 쉬는 끝 시각
last_done = 0  # 확장이 자동 진행 끝(주문서 뜸·멈춤)을 마지막으로 알려 온 시각
last_open = 0  # 마지막으로 자동 진행 창을 연 시각
opened_lock = threading.Lock()
settings_lock = threading.Lock()
settings_sync = {"at": "", "error": ""}  # GitHub 변수와 마지막으로 맞춘 시각, 실패 이유


def claim(url):
    """GitHub 알림과 맥 조회가 같은 회차를 겹쳐 알려도 크롬은 한 번만 열도록, 처음이면 True"""
    with opened_lock:
        if time.time() - opened_at.get(url, 0) < REOPEN_AFTER:
            return False
        opened_at[url] = time.time()
        return True


def note_alert(title):
    global last_alert
    last_alert = (time.time(), f"{datetime.now():%m/%d %H:%M} {title}")


def notify_mac(text, sound=None):
    text = text.replace("\\", "\\\\").replace('"', '\\"')  # 확장이 보낸 글도 들어온다
    sound = f' sound name "{sound}"' if sound else ""
    subprocess.run(["osascript", "-e", f'display notification "{text}" with title "화담숲 감시"{sound}'], check=False)


def poll_on():
    return os.path.exists(POLL_FLAG)


def set_poll(on):
    if on:
        open(POLL_FLAG, "w").close()
    elif poll_on():
        os.remove(POLL_FLAG)
    log(f"맥 조회 {poll_text()}")
    notify_mac(f"맥 조회 {poll_text()}")


def poll_text():
    return f"켜짐 ({POLL_EVERY}초마다)" if poll_on() else "꺼짐"


def tail(path, n=1000):
    """로그 파일의 마지막 n 줄 (끝 256KB 만 읽는다)"""
    try:
        with open(path, "rb") as f:
            size = f.seek(0, os.SEEK_END)
            f.seek(max(0, size - 256 * 1024))
            lines = f.read().decode("utf-8", "replace").splitlines()
            return lines[1 if size > 256 * 1024 else 0:][-n:]  # 중간부터 읽었으면 잘린 첫 줄은 버린다
    except FileNotFoundError:
        return []


def gh(*args):
    if not GH:
        raise RuntimeError("gh 명령을 못 찾음 (brew install gh, gh auth login)")
    r = subprocess.run([GH, *args, "-R", REPO], capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip() or f"gh {' '.join(args[:2])} 실패")
    return r.stdout


def apply_settings(values, source):
    """설정을 맥 조회(watch 모듈)에 반영하고 캐시에 남긴다. 잘못된 항목 목록을 돌려준다"""
    before = dict(watch.CURRENT)
    errors = watch.configure(values)
    if watch.CURRENT != before:
        log(f"설정 바뀜 ({source}): {watch.describe_settings()}")
    with open(SETTINGS_CACHE, "w") as f:
        json.dump(watch.CURRENT, f, ensure_ascii=False, indent=1)
    return errors


def load_settings():
    """시작할 때는 지난번에 맞춘 값부터 쓴다. 곧이어 settings_loop 가 GitHub 변수와 맞춘다"""
    try:
        with open(SETTINGS_CACHE) as f:
            watch.configure(json.load(f))
    except (FileNotFoundError, ValueError):
        pass


def pull_settings():
    """GitHub 저장소 변수를 읽어 맞춘다 (폰으로 GitHub 에서 고친 값도 따라간다)"""
    with settings_lock:
        try:
            rows = json.loads(gh("variable", "list", "--json", "name,value"))
            values = {r["name"]: r["value"] for r in rows if r["name"] in watch.SETTINGS}
            errors = apply_settings(values, "GitHub")
            settings_sync.update(at=f"{datetime.now():%H:%M:%S}",
                                 error="; ".join(f"GitHub 변수 {e} 는 잘못돼서 기본값을 씀" for e in errors))
        except Exception as e:
            if not settings_sync["error"].startswith("GitHub 변수를 못 읽음"):
                log(f"설정: GitHub 변수를 못 읽음 {e}")
            settings_sync["error"] = f"GitHub 변수를 못 읽음: {e}"


def push_settings(values):
    """화면에서 저장: 검사 → GitHub 변수 → 맥 조회 순서. 잘못된 항목이 있으면 아무것도 안 바꾸고 그 목록을 돌려준다"""
    v, errors = watch.parse_settings(values)
    if errors:
        return errors
    with settings_lock:
        on_github = {r["name"]: r["value"] for r in json.loads(gh("variable", "list", "--json", "name,value"))}
        for name, value in v.items():
            if on_github.get(name) != value:  # 바뀐 것만 고친다 (하나에 1초 가까이 걸림)
                gh("variable", "set", name, "--body", value)
        apply_settings(v, "맥 화면")
        settings_sync.update(at=f"{datetime.now():%H:%M:%S}", error="")
    return []


def settings_loop():
    while True:
        pull_settings()
        time.sleep(SETTINGS_SYNC)


def settings_view():
    return {"values": watch.CURRENT, "describe": watch.describe_settings(),
            "fields": {k: {"default": d, "label": desc} for k, (d, desc) in watch.SETTINGS.items()},
            "synced_at": settings_sync["at"], "error": settings_sync["error"],
            "github_url": f"https://github.com/{REPO}/settings/variables/actions"}


def swiftbar_menu():
    """메뉴 막대 플러그인(desktop/swiftbar)이 그대로 찍는 SwiftBar 메뉴. 첫 줄이 막대 제목, --- 아래가 펼친 메뉴"""
    on, now = poll_on(), time.time()
    alert_at, alert = last_alert
    # SwiftBar 는 | 뒤를 옵션으로 읽으니 조회 결과·알림 제목에 섞인 | 는 바꿔 둔다
    poll, alert = last_poll.replace("|", "｜"), alert.replace("|", "｜")
    if now - alert_at < REOPEN_AFTER:
        title = "🍁 예약 가능! | color=#e5484d"
    elif on and now < paused_until:
        title = "🍁 쉼 | color=#d97706"
    else:
        title = "🍁 켜짐" if on else "🍁 꺼짐"
    menu = [title, "---", f"맥 조회 {poll_text()}"]
    if on:
        if now < paused_until:
            menu.append(f"조회가 막혀서 {datetime.fromtimestamp(paused_until):%H:%M} 까지 쉼")
        elif watch.in_quiet_hours(datetime.now(watch.KST)):
            menu.append("밤 00:00~07:30 은 쉼")
        menu.append(f"마지막 조회 {poll}" if poll else "곧 첫 조회")
    menu.append(f"노림: {watch.describe_settings()}")
    if alert:
        menu.append(f"최근 알림 {alert}")
    curl = f"bash=/usr/bin/curl param1=-s param2=http://127.0.0.1:{LOG_PORT}/poll/{'off' if on else 'on'}"
    menu += ["---",
             f"{'끄기 (GitHub 1분 조회만 남김)' if on else '켜기'} | {curl} terminal=false refresh=true",
             "---",
             f"로그·설정 화면 | href=http://127.0.0.1:{LOG_PORT}/",
             f"상품 페이지 | href={watch.PRODUCT_URL}",
             f"GitHub 오늘 조회 기록 | href={DAY_LOG_URL.format(datetime.now(watch.KST))}"]
    return "\n".join(menu)


class LocalServer(BaseHTTPRequestHandler):
    """POST /log {"log": "..."}: 확장이 보낸 진행 상황을 이 로그에 남긴다.
    GET /: 상태·로그 화면 (dashboard.html), /api/state: 그 화면이 3초마다 읽는 JSON
    GET /poll (상태) · /poll/toggle · /poll/on · /poll/off: 맥 조회를 켜고 끈다.
    GET /swiftbar: 메뉴 막대 🍁 내용
    GET /api/settings: 노리는 날짜·회차·매수, POST /api/settings: 바꾸기 (GitHub 변수까지)"""

    def do_GET(self):
        path = self.path.split("?")[0].rstrip("/") or "/"
        if path == "/":
            with open(DASHBOARD, "rb") as f:
                self.reply(f.read(), "text/html")
        elif path == "/api/state":
            state = {"on": poll_on(), "status": poll_text(), "last_poll": last_poll, "lines": tail(LOG_FILE)}
            self.reply(json.dumps(state, ensure_ascii=False).encode(), "application/json")
        elif path in ("/poll", "/poll/toggle", "/poll/on", "/poll/off"):
            if path != "/poll":
                set_poll(not poll_on() if path == "/poll/toggle" else path == "/poll/on")
            body = f"맥 조회 {poll_text()}" + (f"\n마지막 조회 {last_poll}" if poll_on() and last_poll else "")
            self.reply(body.encode(), "text/plain")
        elif path == "/swiftbar":
            self.reply(swiftbar_menu().encode(), "text/plain")
        elif path == "/api/settings":
            self.reply_json(settings_view())
        elif path == "/standby/wait":
            self.standby_wait()
        else:
            self.send_error(404)

    def standby_wait(self):
        """대기 창 확장이 부른다: 20초까지 알림을 기다려 주소를 주거나 204 (확장이 바로 다시 부름)"""
        global standby_seen
        standby_seen = time.time()
        with standby_cond:
            standby_cond.wait_for(lambda: standby_queue, 20)
            item = standby_queue.pop() if standby_queue else None
        standby_seen = time.time()
        if item and time.time() - item[1] < 5:
            return self.reply_json({"url": item[0]})
        self.send_response(204)
        self.end_headers()

    def reply_json(self, obj, status=200):
        self.reply(json.dumps(obj, ensure_ascii=False).encode(), "application/json", status)

    def reply(self, body, content_type, status=200):
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        global last_done
        if self.path.split("?")[0] == "/api/settings":
            return self.save_settings()
        if self.path.split("?")[0] == "/standby/ack":
            standby_ack.set()
            self.send_response(204)
            return self.end_headers()
        if self.path.split("?")[0] == "/api/test":
            return self.run_test()
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            log(f"확장: {body.get('log')}")
            # 확장이 끝을 알려 온다: 주문서가 떴으면 크롬을 앞으로, 멈췄으면 알림만 (창은 Dock 에 내려가 있음)
            if body.get("done"):
                last_done = time.time()
            if body.get("done") == "ok":
                show_chrome()
                notify_mac(f"주문서가 떴어요. 결제하세요. {body.get('log')}", "Glass")
            elif body.get("show"):
                show_chrome()
            elif body.get("done") == "fail":
                notify_mac(f"자동 진행이 멈췄어요. Dock 의 크롬 창에서 직접 진행하세요. {body.get('log')}", "Basso")
        except Exception as e:
            log(f"확장 로그 읽기 실패: {e!r}")
        self.send_response(204)
        self.end_headers()

    def run_test(self):
        """listener.py --test 가 부른다 (대기 창은 이 수신기 안에서만 넘길 수 있어서). 화담숲 자동 진행 주소만 연다"""
        if self.headers.get("Origin") is not None or not (self.headers.get("Content-Type") or "").startswith("application/json"):
            return self.reply_json({"ok": False}, 403)
        url = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}").get("url") or ""
        if not url.startswith(watch.PRODUCT_URL + AUTO_MARK):
            return self.reply_json({"ok": False}, 400)
        threading.Thread(target=open_in_chrome, args=(url,), daemon=True).start()
        self.reply_json({"ok": True})

    def save_settings(self):
        # 아무 웹페이지나 이 주소로 설정을 바꾸지 못하게, 이 화면에서 JSON 으로 보낸 요청만 받는다
        # (다른 사이트가 JSON 으로 보내려면 브라우저가 먼저 허락을 묻는데 여기서는 답하지 않으니 막힌다)
        origin = self.headers.get("Origin")
        if origin not in (None, f"http://127.0.0.1:{LOG_PORT}") or \
                not (self.headers.get("Content-Type") or "").startswith("application/json"):
            return self.reply_json({"ok": False, "errors": ["이 화면에서만 바꿀 수 있어요"]}, 403)
        try:
            values = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            errors = push_settings(values)
        except Exception as e:
            log(f"설정 저장 실패: {e}")
            return self.reply_json({"ok": False, "errors": [f"GitHub 변수 저장 실패: {e}"], **settings_view()}, 502)
        if errors:
            return self.reply_json({"ok": False, "errors": [f"{e} 이(가) 잘못됐어요" for e in errors], **settings_view()}, 400)
        self.reply_json({"ok": True, **settings_view()})

    def log_message(self, *args):
        pass  # 접속 기록은 남기지 않는다


def serve_local():
    try:
        server = ThreadingHTTPServer(("127.0.0.1", LOG_PORT), LocalServer)
    except OSError as e:
        log(f"로컬 서버를 못 띄움 (포트 {LOG_PORT}): {e}")
        return
    threading.Thread(target=server.serve_forever, daemon=True).start()


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
                    note_alert(msg.get("title") or "")
                    if target:
                        if claim(target):
                            open_in_chrome(target)
                        else:
                            log("  방금 크롬으로 연 회차라 건너뜀")
        except Exception as e:
            log(f"연결 끊김: {e!r} — 5초 뒤 다시 연결")
            time.sleep(5)


def standby_loop():
    """대기 창을 하나 띄워 둔다 (10분마다 새로 읽는 건 확장이 함). 쓰였거나 닫혔으면 새로 띄운다.
    크롬이 꺼져 있거나(띄우면 크롬이 켜져 버림) 크롬을 쓰는 중이거나(새 창이 하던 일을 가림) 방금 자동 진행에 썼으면 미룬다"""
    busy_since, since = 0, time.time()  # since: 대기 창을 띄운(또는 이 수신기가 뜬) 시각
    while True:
        time.sleep(30)
        try:
            if subprocess.run(["pgrep", "-x", "Google Chrome"], capture_output=True).returncode != 0:
                continue
            wid = read_standby()
            state = standby_state(wid) if wid else "gone"
            if state == "busy":
                busy_since = busy_since or time.time()
                if time.time() - busy_since < 5 * 60:
                    continue  # 미리 로그인하러 간 중. 5분 넘게 안 돌아오면 닫고 새로 띄운다
                chrome(f"close window id {wid}")
            busy_since = 0
            if state == "ready":
                if time.time() - max(since, standby_seen) < 90:
                    continue
                # 확장을 새로 읽으면 그 전에 떠 있던 대기 창은 알림을 못 받는다 → 닫고 새로
                log("대기 창이 알림을 기다리지 않아 새로 띄움")
                chrome(f"close window id {wid}")
            write_standby(None)
            if time.time() - last_open < STANDBY_REARM or front_app() == "com.google.Chrome":
                continue
            wid = new_window(watch.PRODUCT_URL + STANDBY_HASH)
            if wid:
                write_standby(wid)
                since = time.time()
                log(f"대기 창 띄움 ({wid})")
        except Exception as e:
            log(f"대기 창 관리 실패: {e!r}")


def poll_loop(topic):
    """맥 조회가 켜져 있으면 POLL_EVERY 초마다 직접 조회한다. 판정·알림은 GitHub 과 같은 watch.py 코드."""
    watch.SSL_CONTEXT = SSL_CTX
    os.environ["NTFY_TOPIC"] = topic
    global last_poll, paused_until
    prev, prev_open, cells, was_on = {}, {}, {}, None
    while True:
        started = time.time()
        try:
            on = poll_on()
            if on != was_on:
                # 켤 때마다 처음부터 본다 = 그때 이미 열려 있는 회차도 한 번 알린다
                prev, prev_open, cells, was_on, last_poll = {}, {}, {}, on, ""
            now = datetime.now(watch.KST)
            if on and not watch.in_quiet_hours(now):
                dates = [d for d in watch.TARGET_DATES if d >= now.date().isoformat()]
                watch.RAW.clear()
                cur = watch.fetch(dates)
                last_poll = f"{now:%H:%M:%S} " + ", ".join(f"{watch.label(d)} {watch.cell(cur[d])}" for d in dates)
                for d in dates:  # 날짜별 상태가 바뀔 때만 로그에 남긴다
                    c = watch.cell(cur[d]) + (f" {[t for t, _ in cur[d]['slots']]}" if cur[d]["slots"] else "")
                    if cells.get(d) != c:
                        log(f"맥 조회: {watch.label(d)} {c}")
                        cells[d] = c
                cur_open, alert = watch.find_opened(dates, cur, prev, prev_open)
                if alert:
                    title, message, url = alert
                    note_alert(title)
                    if url and not claim(url):
                        log(f"맥 조회: {title} — 방금 크롬으로 연 회차라 알림 생략")
                    else:
                        log(f"맥 조회: {title}")
                        try:
                            watch.notify(title, message + f"\n(맥 {POLL_EVERY}초 조회에서 찾음)", 5, pc_url=url)
                        except Exception as e:  # 폰 알림이 실패해도 크롬은 띄운다
                            log(f"맥 조회: 폰 알림 실패 {watch.describe(e)}")
                        if url:
                            open_in_chrome(url)
                prev, prev_open = {d: cur[d]["status"] for d in dates}, cur_open
        except Exception as e:
            reason = watch.describe(e)
            log(f"맥 조회 실패: {reason}")
            last_poll = f"{datetime.now(watch.KST):%H:%M:%S} 조회 실패 {reason}"
            if reason in ("HTTP 403", "HTTP 429"):
                # 막히기 시작했으면 같은 IP 로 결제할 크롬까지 막히지 않게 한동안 쉰다
                log("맥 조회 10분 쉼")
                started += 10 * 60
                paused_until = started
        # 껐다 켜면 바로 반응하도록 잘게 나눠 잔다
        while time.time() < started + POLL_EVERY and poll_on() == was_on:
            time.sleep(1)


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--test":
        # 떠 있는 수신기에 맡긴다 (대기 창을 쓰려면). 수신기가 없으면 여기서 새 창으로
        req = urllib.request.Request(f"http://127.0.0.1:{LOG_PORT}/api/test", json.dumps({"url": sys.argv[2]}).encode(),
                                     {"Content-Type": "application/json"})
        try:
            urllib.request.urlopen(req, timeout=5)
        except OSError:
            open_in_chrome(sys.argv[2])
        return
    with open(TOPIC_FILE) as f:
        topic = f.read().strip()
    load_settings()
    serve_local()
    threading.Thread(target=settings_loop, daemon=True).start()
    threading.Thread(target=poll_loop, args=(topic,), daemon=True).start()
    threading.Thread(target=standby_loop, daemon=True).start()
    listen(topic)


if __name__ == "__main__":
    main()
