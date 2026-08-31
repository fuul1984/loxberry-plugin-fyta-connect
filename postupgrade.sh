#!/bin/bash
# FYTA Connect: Einstellungen/Auth-Daten wiederherstellen und neue Schlüssel ergänzen.
set -u
LBHOME="${LBHOMEDIR:-/opt/loxberry}"
CFG_DIR="$LBHOME/config/plugins/fyta_connect"
CFG="$CFG_DIR/fyta.cfg"
DATA_DIR="$LBHOME/data/plugins/fyta_connect"
BACKUP_DIR="/tmp/fyta_connect_upgrade"
mkdir -p "$CFG_DIR" "$DATA_DIR"
[ -f "$BACKUP_DIR/fyta.cfg" ] && cp -p "$BACKUP_DIR/fyta.cfg" "$CFG"
[ -f "$BACKUP_DIR/auth.json" ] && cp -p "$BACKUP_DIR/auth.json" "$DATA_DIR/auth.json"
[ -f "$BACKUP_DIR/.auth.key" ] && cp -p "$BACKUP_DIR/.auth.key" "$DATA_DIR/.auth.key"
[ -f "$CFG" ] || touch "$CFG"
ensure_key() {
    local key="$1" value="$2"
    grep -q "^${key}=" "$CFG" 2>/dev/null || printf '%s=%s\n' "$key" "$value" >> "$CFG"
}
ensure_key PLUGIN_ENABLED true
ensure_key FYTA_TOKEN ""
ensure_key FYTA_EMAIL ""
ensure_key MINISERVER_NO ""
ensure_key MINISERVER_NAME ""
ensure_key UDP_ENABLED true
ensure_key UDP_HOST ""
ensure_key UDP_PORT 5007
ensure_key INTERVAL 15
ensure_key LOXONE_SSL false
ensure_key LOXONE_HOST ""
ensure_key LOXONE_PORT 443
ensure_key LOXONE_USER ""
ensure_key LOXONE_PASSWORD ""
chown -R loxberry:loxberry "$CFG_DIR" "$DATA_DIR" 2>/dev/null || true
chmod 600 "$CFG" 2>/dev/null || true
[ -f "$DATA_DIR/auth.json" ] && chmod 600 "$DATA_DIR/auth.json" 2>/dev/null || true
[ -f "$DATA_DIR/.auth.key" ] && chmod 600 "$DATA_DIR/.auth.key" 2>/dev/null || true
rm -rf "$BACKUP_DIR"
exit 0
