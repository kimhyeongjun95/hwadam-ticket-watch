#!/bin/bash
# install.sh 로 등록한 알림 수신기를 멈추고 지운다
PLIST="$HOME/Library/LaunchAgents/com.hwadam.ticket-listener.plist"
launchctl bootout "gui/$(id -u)" "$PLIST" 2>/dev/null || true
rm -f "$PLIST"
echo "✓ 알림 수신기를 지웠습니다"
