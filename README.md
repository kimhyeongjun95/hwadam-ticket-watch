# hwadam-ticket-watch

[NOL(야놀자) 화담숲 입장권](https://leisure-web.yanolja.com/leisure/10367229)에서 지정한 날짜(기본 10/31, 11/1)가
품절에서 판매중으로 바뀌면 폰으로 알려 주는 GitHub Actions 감시기.

- 1분마다 조회, 한국 시간 00:00~07:30 은 쉼. GitHub 크론이 잘 안 돌아서 cron-job.org 가 workflow_dispatch 로 실행시킨다
- 알림은 예약 가능해졌을 때만 (긴급). 품절·조회 실패는 알리지 않고 실행 기록에만 남김
- 직전 상태는 `state.json` 에 커밋해 둠

## 알림 설정 (Settings → Secrets and variables → Actions)

| 채널 | secret |
|---|---|
| ntfy | `NTFY_TOPIC` — 앱에서 같은 토픽을 구독. 토픽 이름이 곧 비밀번호라 길고 무작위로 |
| 텔레그램 | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` |

둘 다 넣으면 둘 다 받는다.

## 실행 기록

[`logs` 브랜치](../../tree/logs)에 한국 시간 기준 날짜별로 쌓인다.

- `YYYY-MM-DD.csv` — 실행마다 한 줄 (시각, 결과, 날짜별 상태, 실행 번호). GitHub 에서 표로 보인다
- `YYYY-MM-DD.jsonl` — 같은 실행의 API 응답 원문

조회 실패는 실행이 초록이어도 결과 칸에 `HTTP 403` 같은 오류가 찍히고, 실행 페이지에 경고가 뜬다.

## 사용

- 테스트 알림: Actions → watch → Run workflow → "테스트 알림만 보내기" 체크
- 노리는 날짜·회차·매수: 코드를 고치지 않고 저장소 변수(Settings → Secrets and variables → Actions → **Variables**)로 바꾼다.
  맥 수신기 화면 <http://127.0.0.1:8789/> 의 '노리는 것'에서 저장하면 이 변수를 고치고, 폰에서는 GitHub 웹에서 직접 고쳐도 된다.
  GitHub 조회는 다음 실행부터, 맥 조회는 바로(GitHub 에서 고쳤으면 5분 안에) 따라간다. 변수가 비었거나 잘못되면 `watch.py` 기본값

  | 변수 | 기본값 | 뜻 |
  |---|---|---|
  | `TARGET_DATES` | `2026-10-31,2026-11-01` | 노리는 날짜 (쉼표로 구분) |
  | `EARLIEST_TIME` | `09:00` | 이 시각 이상 입장 회차부터 (두 자리 `09:00`) |
  | `LATEST_TIME` | `15:00` | 이 시각 전 입장 회차까지 |
  | `MIN_QUANTITY` | `1` | 이만큼 이상 남은 회차만 알림·자동 진행. 그 밖은 기록에만 남음 |
  | `QUANTITY` | `2` | 이만큼까지 산다. 모자라면 남은 만큼(1장이라도). 여러 회차가 같이 열리면 이만큼 다 남은 회차를 먼저 고름 |
- 끝나면: Actions → watch → ⋯ → Disable workflow

## 맥에서 주문서까지 자동으로 띄우기 (선택)

맥이 켜져 있으면 예약 가능 알림을 받아 크롬에서 날짜·회차·성인·일반·매수(2장, 모자라면 남은 만큼)를 고르고 '구매하기'까지 누른다. 결제는 직접.

1. 크롬 `chrome://extensions` → 개발자 모드 → 압축해제된 확장 프로그램 로드 → `desktop/extension`
2. 그 크롬(마지막으로 쓰는 프로필)에서 **네이버** 로그인, NOL 은 네이버로 한 번 로그인해 둔다.
   NOL 로그인이 풀려 있으면 확장이 NOL 로그인 화면에서 '네이버로 시작하기'를 눌러 다시 로그인하고 이어 간다.
   네이버 로그인 화면까지 뜨면 크롬이 비밀번호를 자동완성해 둔 경우에만 '로그인'을 눌러 준다
   (크롬 디버거로 누르므로 '디버깅 중' 안내 줄이 잠깐 뜸. 자동입력 방지 문자·2단계 인증이 나오면 거기서 멈춤)
3. 저장소 맨 위에 `.ntfy-topic` 파일을 만들고 GitHub secret `NTFY_TOPIC` 과 같은 토픽 이름을 한 줄로 넣는다.
   git 에 올리지 않는 파일이라 새로 clone 한 맥에서는 쓰던 맥의 것을 복사해 온다
4. `desktop/install.sh` — 로그인할 때마다 `desktop/listener.py` 가 ntfy 를 듣도록 등록 (끄기: `desktop/uninstall.sh`).
   SwiftBar 가 깔려 있으면 메뉴 막대 🍁 도 같이 넣는다 (아래)
5. 처음 한 번 "python3 이(가) Google Chrome 을 제어하려고 합니다" 창이 뜨면 허용 (휴대폰 폭 창으로 열어야 옵션 창이 뜸)

회사 망처럼 HTTPS 를 가로채는 프록시 뒤라면 그 루트 인증서를 `~/.local/share/corp-ca.pem` 에 두면 수신기가 같이 읽는다.
여러 맥에 깔면 알림이 올 때 켜져 있는 맥마다 크롬을 연다.

진행 상황은 확장이 수신기로 보내서 `~/Library/Logs/hwadam-listener.log` 에 남는다 (`확장: …` 줄).
확장 파일을 고친 뒤에는 `chrome://extensions` 에서 새로고침(↻) 해야 반영된다.

### 맥에서도 20초마다 조회 (선택)

수신기(`listener.py`)가 GitHub 의 1분 조회 사이사이 맥에서도 20초마다 직접 조회한다. 판정·알림은 `watch.py` 와 같은 코드.
맥이 켜져 있을 때만 돌고, 켜고 끈 상태는 `.local-poll` 파일로 남아 재부팅해도 유지된다.
GitHub 알림과 같은 회차가 겹치면 크롬은 10분 안에 한 번만 연다. 회사 망이면 회사 IP 로 조회하는 셈이라, 403·429 가 나면 10분 쉰다.

- 메뉴 막대: `brew install --cask swiftbar` 후 `desktop/install.sh` 를 다시 돌리면 메뉴 막대에 🍁 켜짐/꺼짐이 뜬다
  (10초마다 갱신. 눌러서 켜기/끄기·마지막 조회·로그 화면. 예약 가능 알림 뒤 10분은 🍁 예약 가능!, 403·429 로 쉬는 동안은 🍁 쉼).
  처음 뜨는 '인터넷에서 다운로드된 앱' 창에서 열기, SwiftBar 설정에서 'Launch at login'을 켜 둔다. 플러그인은 `desktop/swiftbar/hwadam.10s.sh`
- 상태·로그·설정 화면: <http://127.0.0.1:8789/>
- 켜기/끄기: `curl 127.0.0.1:8789/poll/toggle` (`/poll/on`, `/poll/off`, 상태·마지막 조회는 `/poll`).
  단축어 앱에서 'URL 콘텐츠 가져오기'로 이 주소를 부르는 단축어를 만들어 위젯으로 둬도 된다

시험: `python3 desktop/listener.py --test "https://leisure-web.yanolja.com/leisure/10367229#hwadam-auto=2026-10-29_16:40_2_dry"`
(`_dry` 는 구매하기 직전에 멈춤. 날짜·회차는 재고 있는 것으로)

## 다른 맥에서 이 저장소에 커밋할 때

clone 직후 저장소 안에서 개인 계정으로 맞춘다 (전역 설정이 회사 계정이어도 이 저장소만 바뀜).

```
git config user.name kimhyeongjun95
git config user.email hjthelegend@naver.com
```
