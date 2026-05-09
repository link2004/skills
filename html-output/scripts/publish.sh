#!/bin/bash
# Upload HTML to the configured bucket and print a public URL.
# Reads HTML from stdin (preferred — no local file pollution) or a file path.
#
# Naming:
#   - Name provided  → <name>-<8hex>.html  (persistent doc; for wiki-style references)
#   - No name        → <YYYY-MM-DDTHHMM>-<8hex>.html  (timestamp; for ephemeral output)
#
# Usage:
#   echo "$HTML" | publish.sh                    # → 2026-...-xxxxxx.html
#   echo "$HTML" | publish.sh setup-guide        # → setup-guide-xxxxxx.html
#   publish.sh path/to/file.html                 # file mode, timestamp name
#   publish.sh path/to/file.html setup-guide     # file mode, named
#
# All output URLs are public + permanent. To remove, use:
#   AWS_PROFILE=<profile> aws s3 rm s3://<bucket>/<key>

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG="$SCRIPT_DIR/../config.json"

if [[ ! -f "$CONFIG" ]]; then
  echo "error: config.json not found at $CONFIG. see references/setup.md." >&2
  exit 1
fi

read_cfg() {
  python3 -c "import json; v=json.load(open('$CONFIG')).get('$1'); print('' if v is None else v)"
}

BUCKET=$(read_cfg bucket)
REGION=$(read_cfg region)
PROFILE=$(read_cfg aws_profile)

if [[ -z "$BUCKET" || "$BUCKET" == "<"* || -z "$PROFILE" || "$PROFILE" == "<"* ]]; then
  echo "error: config.json has unfilled placeholders. see references/setup.md." >&2
  exit 1
fi

# Resolve input source and name
SRC=""
NAME=""
CLEANUP_TMP=""

if [[ -t 0 ]]; then
  if [[ $# -eq 0 ]]; then
    echo "usage: publish.sh < file.html [name]   OR   publish.sh path/to/file.html [name]" >&2
    exit 1
  fi
  if [[ -f "$1" ]]; then
    SRC="$1"
    NAME="${2:-}"
  else
    echo "error: file not found: $1" >&2
    exit 1
  fi
else
  SRC=$(mktemp -t html-output.XXXXXX)
  CLEANUP_TMP="$SRC"
  trap '[[ -n "$CLEANUP_TMP" ]] && rm -f "$CLEANUP_TMP"' EXIT
  cat > "$SRC"
  NAME="${1:-}"
fi

# Determine key (8hex always at the tail):
#   - Arg ends in .html  → use as-is (overwrite mode)
#   - Arg is name        → <slug>-<8hex>.html (new named doc)
#   - No arg             → <timestamp>-<8hex>.html (ephemeral)
if [[ "$NAME" == *.html ]]; then
  KEY="$NAME"
elif [[ -n "$NAME" ]]; then
  SLUG=$(echo "$NAME" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9-]+/-/g; s/^-+|-+$//g; s/-+/-/g')
  if [[ -z "$SLUG" ]]; then
    echo "error: name must contain alphanumeric chars" >&2
    exit 1
  fi
  RAND=$(python3 -c "import secrets; print(secrets.token_hex(4))")
  KEY="${SLUG}-${RAND}.html"
else
  TS=$(date -u +%Y-%m-%dT%H%M)
  RAND=$(python3 -c "import secrets; print(secrets.token_hex(4))")
  KEY="${TS}-${RAND}.html"
fi

AWS_PROFILE="$PROFILE" aws s3 cp "$SRC" "s3://$BUCKET/$KEY" \
  --content-type "text/html; charset=utf-8" >&2

echo "https://${BUCKET}.s3.${REGION}.amazonaws.com/${KEY}"
