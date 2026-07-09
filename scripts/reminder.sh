#!/bin/bash
# 工作日定时午饭提醒
#
# 添加到 crontab（每个工作日 11:50）：
#   50 11 * * 1-5 /path/to/grill-me-lunch/scripts/reminder.sh
#
# 或添加到 launchd（macOS）：
#   参考: https://github.com/HardenGale/grill-me-lunch/wiki

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# macOS 系统通知
if [[ "$OSTYPE" == "darwin"* ]]; then
  osascript -e "display notification \"到点了！今天午饭吃什么？\" \
    with title \"🍜 grill-me-lunch\" \
    subtitle \"别纠结了，让 AI 帮你选\" \
    sound name \"Ping\""

# Linux (需要 notify-send)
elif command -v notify-send &> /dev/null; then
  notify-send \
    -i food \
    "🍜 grill-me-lunch" \
    "到点了！今天午饭吃什么？\n别纠结了，让 AI 帮你选"

# Windows (PowerShell)
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
  powershell.exe -Command "
    Add-Type -AssemblyName System.Windows.Forms;
    \$notify = New-Object System.Windows.Forms.NotifyIcon;
    \$notify.Icon = [System.Drawing.Icon]::ExtractAssociatedIcon('powershell.exe');
    \$notify.BalloonTipTitle = '🍜 grill-me-lunch';
    \$notify.BalloonTipText = '到点了！今天午饭吃什么？';
    \$notify.Visible = \$true;
    \$notify.ShowBalloonTip(5000);
  "
fi

echo "🍜 午饭时间到！"
echo "   运行 /lunch 开始今天的午饭拷问 👇"
echo "   cd $(dirname "$SCRIPT_DIR") && ./scripts/grill-lunch.sh"
