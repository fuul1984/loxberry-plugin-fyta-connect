#!/bin/bash
# FYTA Connect: vorhandene Benutzereinstellungen vor einem Upgrade sichern.
set -u
LBHOME="${LBHOMEDIR:-/opt/loxberry}"
CFG="$LBHOME/config/plugins/fyta_connect/fyta.cfg"
BACKUP_DIR="/tmp/fyta_connect_upgrade"
mkdir -p "$BACKUP_DIR"
if [ -f "$CFG" ]; then
    cp -p "$CFG" "$BACKUP_DIR/fyta.cfg"
fi
exit 0
