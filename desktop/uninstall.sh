#!/bin/bash
# install.sh 로 등록한 알림 수신기를 멈추고 지운다
PLIST="$HOME/Library/LaunchAgents/com.hwadam.ticket-listener.plist"
launchctl bootout "gui/$(id -u)" "$PLIST" 2>/dev/null || true
rm -f "$PLIST"
PLUGINS="$(defaults read com.ameba.SwiftBar PluginDirectory 2>/dev/null || true)"
[ -n "$PLUGINS" ] && rm -f "$PLUGINS/hwadam.10s.sh"
echo "✓ 알림 수신기를 지웠습니다"
