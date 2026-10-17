#!/bin/zsh
set -euo pipefail

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
LABEL="com.michaelhackman.recomp-index-refresh"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
LOG_DIR="$HOME/Library/Logs"
uid="$(id -u)"

mkdir -p "$HOME/Library/LaunchAgents" "$LOG_DIR" "$HOME/.local/state"

cat > "$PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/zsh</string>
    <string>$ROOT/scripts/refresh_and_publish.sh</string>
  </array>
  <key>StartInterval</key><integer>10800</integer>
  <key>RunAtLoad</key><true/>
  <key>ProcessType</key><string>Background</string>
  <key>EnvironmentVariables</key>
  <dict><key>PATH</key><string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string></dict>
  <key>StandardOutPath</key><string>$LOG_DIR/recomp-index-refresh.log</string>
  <key>StandardErrorPath</key><string>$LOG_DIR/recomp-index-refresh.err.log</string>
</dict>
</plist>
PLIST

launchctl bootout "gui/$uid/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$uid" "$PLIST"
launchctl kickstart -k "gui/$uid/$LABEL"
echo "REFRESH_AGENT_INSTALLED"
