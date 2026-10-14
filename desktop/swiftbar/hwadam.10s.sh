#!/bin/bash
# <swiftbar.title>화담숲 감시</swiftbar.title>
# <swiftbar.desc>맥 20초 조회 켜짐/꺼짐을 메뉴 막대에 띄우고 켜고 끈다</swiftbar.desc>
# <swiftbar.hideRunInTerminal>true</swiftbar.hideRunInTerminal>
# <swiftbar.hideAbout>true</swiftbar.hideAbout>
#
# SwiftBar 메뉴 막대 플러그인 (파일 이름의 10s = 10초마다 새로 그림). 메뉴 내용은 수신기(listener.py)가 만든다.
# desktop/install.sh 가 SwiftBar 플러그인 폴더로 복사해 둔다.
curl -s --max-time 2 http://127.0.0.1:8789/swiftbar && exit
echo "🍁 ⚠︎ | color=#e5484d"
echo "---"
echo "수신기(listener.py)가 안 떠 있어요"
echo "다시 띄우기 | bash=/bin/launchctl param1=kickstart param2=-k param3=gui/$(id -u)/com.hwadam.ticket-listener terminal=false refresh=true"
echo "로그 파일 열기 | bash=/usr/bin/open param1=$HOME/Library/Logs/hwadam-listener.log terminal=false"
