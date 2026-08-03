#!/bin/bash
set -euo pipefail

OWNER="${1:-fuul1984}"
REPO="${2:-loxberry-plugin-fyta-connect}"
VERSION="$(awk -F= '/^VERSION=/{print $2; exit}' plugin.cfg | tr -d '\r')"
RAW_BASE="https://raw.githubusercontent.com/${OWNER}/${REPO}/main"
RELEASE_BASE="https://github.com/${OWNER}/${REPO}"

cat > release.cfg <<CFG
[AUTOUPDATE]
VERSION=${VERSION}
ARCHIVEURL=${RELEASE_BASE}/releases/download/v${VERSION}/FYTA_Connect_v${VERSION}.zip
INFOURL=${RELEASE_BASE}/releases/tag/v${VERSION}
CFG

cp release.cfg prerelease.cfg

python3 - "$RAW_BASE" <<'PY'
from pathlib import Path
import sys
raw = sys.argv[1]
p = Path('plugin.cfg')
s = p.read_text()
block = (
    '[AUTOUPDATE]\n'
    'AUTOMATIC_UPDATES=true\n'
    f'RELEASECFG={raw}/release.cfg\n'
    f'PRERELEASECFG={raw}/prerelease.cfg\n'
)
if '[AUTOUPDATE]' in s:
    start = s.index('[AUTOUPDATE]')
    end = s.find('\n[', start + 1)
    if end < 0:
        end = len(s)
    s = s[:start] + block + s[end:]
else:
    s += '\n' + block
p.write_text(s)
PY

echo "AutoUpdate configured for ${OWNER}/${REPO} (version ${VERSION})."
