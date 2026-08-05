#!/bin/bash
# FYTA Connect: Einstellungen nach dem Upgrade wiederherstellen und neue Schlüssel ergänzen.
set -u
LBHOME="${LBHOMEDIR:-/opt/loxberry}"
CFG_DIR="$LBHOME/config/plugins/fyta_connect"
CFG="$CFG_DIR/fyta.cfg"
BACKUP="/tmp/fyta_connect_upgrade/fyta.cfg"
mkdir -p "$CFG_DIR"
if [ -f "$BACKUP" ]; then
    cp -p "$BACKUP" "$CFG"
fi
[ -f "$CFG" ] || touch "$CFG"
ensure_key() {
    local key="$1" value="$2"
    grep -q "^${key}=" "$CFG" 2>/dev/null || printf '%s=%s\n' "$key" "$value" >> "$CFG"
}
ensure_key PLUGIN_ENABLED true
ensure_key FYTA_TOKEN ""
ensure_key MINISERVER_NO 1
ensure_key UDP_ENABLED true
ensure_key UDP_HOST ""
ensure_key UDP_PORT 5007
ensure_key INTERVAL 15
ensure_key LOXONE_SSL false
ensure_key LOXONE_HOST ""
ensure_key LOXONE_PORT 443
ensure_key LOXONE_USER ""
ensure_key LOXONE_PASSWORD ""
chown loxberry:loxberry "$CFG" 2>/dev/null || true
chmod 600 "$CFG" 2>/dev/null || true
rm -rf /tmp/fyta_connect_upgrade
exit 0
