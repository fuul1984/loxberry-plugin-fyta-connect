#!/bin/bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
    echo "Usage: $0 GITHUB_USER REPOSITORY"
    exit 1
fi

OWNER="$1"
REPO="$2"
VERSION="$(awk -F= '/^VERSION=/{print $2; exit}' plugin.cfg | tr -d '\r')"
RAW_BASE="https://raw.githubusercontent.com/${OWNER}/${REPO}/main"
RELEASE_BASE="https://github.com/${OWNER}/${REPO}"

cat > release.cfg <<EOF
[AUTOUPDATE]
VERSION=${VERSION}
ARCHIVEURL=${RELEASE_BASE}/releases/download/v${VERSION}/FYTA_Connect_v${VERSION}.zip
INFOURL=${RELEASE_BASE}/releases
EOF

cp release.cfg prerelease.cfg

python3 - "$RAW_BASE" <<'PY'
from pathlib import Path
import sys
raw = sys.argv[1]
p = Path('plugin.cfg')
s = p.read_text()
if '[AUTOUPDATE]' in s:
    start = s.index('[AUTOUPDATE]')
    end = s.find('\n[', start + 1)
    if end < 0:
        end = len(s)
    block = '[AUTOUPDATE]\nAUTOMATIC_UPDATES=true\nRELEASECFG=' + raw + '/release.cfg\nPRERELEASECFG=' + raw + '/prerelease.cfg\n'
    s = s[:start] + block + s[end:]
else:
    s += '\n[AUTOUPDATE]\nAUTOMATIC_UPDATES=true\nRELEASECFG=' + raw + '/release.cfg\nPRERELEASECFG=' + raw + '/prerelease.cfg\n'
p.write_text(s)
PY

echo "AutoUpdate configured for ${OWNER}/${REPO} (version ${VERSION})."
