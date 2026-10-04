# hwadam-ticket-watch

[NOL(야놀자) 화담숲 입장권](https://leisure-web.yanolja.com/leisure/10367229)에서 지정한 날짜(기본 10/31, 11/1)가
품절에서 판매중으로 바뀌면 폰으로 알려 주는 GitHub Actions 감시기.

- 5분마다 조회, 한국 시간 00:00~07:30 은 쉼 (`.github/workflows/watch.yml`)
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
- 끝나면: Actions → watch → ⋯ → Disable workflow
