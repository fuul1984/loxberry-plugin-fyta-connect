#!/bin/bash
# FYTA Connect: Benutzereinstellungen und geschützte Auth-Daten vor Upgrade sichern.
set -u
LBHOME="${LBHOMEDIR:-/opt/loxberry}"
CFG="$LBHOME/config/plugins/fyta_connect/fyta.cfg"
DATA_DIR="$LBHOME/data/plugins/fyta_connect"
BACKUP_DIR="/tmp/fyta_connect_upgrade"
mkdir -p "$BACKUP_DIR"
[ -f "$CFG" ] && cp -p "$CFG" "$BACKUP_DIR/fyta.cfg"
[ -f "$DATA_DIR/auth.json" ] && cp -p "$DATA_DIR/auth.json" "$BACKUP_DIR/auth.json"
[ -f "$DATA_DIR/.auth.key" ] && cp -p "$DATA_DIR/.auth.key" "$BACKUP_DIR/.auth.key"
exit 0
