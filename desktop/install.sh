#!/bin/bash
# 맥 로그인 때마다 listener.py 가 백그라운드로 뜨게 등록한다 (launchd). 지우려면 uninstall.sh
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
PY="$(command -v python3)"
LABEL="com.hwadam.ticket-listener"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
LOG="$HOME/Library/Logs/hwadam-listener.log"

[ -f "$DIR/../.ntfy-topic" ] || { echo "✗ $DIR/../.ntfy-topic 이 없습니다"; exit 1; }

mkdir -p "$HOME/Library/LaunchAgents"
cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key>
  <array><string>$PY</string><string>-u</string><string>$DIR/listener.py</string></array>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>$LOG</string>
  <key>StandardErrorPath</key><string>$LOG</string>
</dict>
</plist>
EOF

launchctl bootout "gui/$(id -u)" "$PLIST" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
sleep 2
echo "✓ 알림 수신기 등록 ($LABEL)"
echo "  로그: tail -f $LOG"
tail -3 "$LOG" 2>/dev/null || true
