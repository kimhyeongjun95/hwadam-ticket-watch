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
- 날짜 변경: `watch.py` 의 `TARGET_DATES` 기본값 수정
- 노리는 회차: `watch.py` 의 `EARLIEST_TIME`(기본 11:00) 이상 `LATEST_TIME`(기본 15:00) 전, `QUANTITY`(기본 2)장 이상 남은 회차만 알림·자동 진행 대상. 그 밖은 기록에만 남음
- 끝나면: Actions → watch → ⋯ → Disable workflow

## 맥에서 주문서까지 자동으로 띄우기 (선택)

맥이 켜져 있으면 예약 가능 알림을 받아 크롬에서 날짜·회차·성인·일반·2장을 고르고 '구매하기'까지 누른다. 결제는 직접.

1. 크롬 `chrome://extensions` → 개발자 모드 → 압축해제된 확장 프로그램 로드 → `desktop/extension`
2. 그 크롬(마지막으로 쓰는 프로필)에서 **네이버** 로그인, NOL 은 네이버로 한 번 로그인해 둔다.
   NOL 로그인이 풀려 있으면 확장이 NOL 로그인 화면에서 '네이버로 시작하기'를 눌러 다시 로그인하고 이어 간다.
   네이버 로그인 화면까지 뜨면 크롬이 비밀번호를 자동완성해 둔 경우에만 '로그인'을 눌러 준다
   (크롬 디버거로 누르므로 '디버깅 중' 안내 줄이 잠깐 뜸. 자동입력 방지 문자·2단계 인증이 나오면 거기서 멈춤)
3. `desktop/install.sh` — 로그인할 때마다 `desktop/listener.py` 가 ntfy 를 듣도록 등록 (끄기: `desktop/uninstall.sh`)
4. 처음 한 번 "python3 이(가) Google Chrome 을 제어하려고 합니다" 창이 뜨면 허용 (휴대폰 폭 창으로 열어야 옵션 창이 뜸)

진행 상황은 확장이 수신기로 보내서 `~/Library/Logs/hwadam-listener.log` 에 남는다 (`확장: …` 줄).
확장 파일을 고친 뒤에는 `chrome://extensions` 에서 새로고침(↻) 해야 반영된다.

시험: `python3 desktop/listener.py --test "https://leisure-web.yanolja.com/leisure/10367229#hwadam-auto=2026-10-29_16:40_2_dry"`
(`_dry` 는 구매하기 직전에 멈춤. 날짜·회차는 재고 있는 것으로)
