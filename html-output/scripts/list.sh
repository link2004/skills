#!/bin/bash
# List public URLs of HTML docs in the bucket, optionally filtered by name prefix.
# Useful for finding existing docs to cross-link in wiki-style documents.
#
# Usage:
#   list.sh                   # all HTML files
#   list.sh setup-guide       # files matching prefix "setup-guide"
#   list.sh setup-guide --keys-only   # just keys, no URL prefix

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG="$SCRIPT_DIR/../config.json"

read_cfg() {
  python3 -c "import json; v=json.load(open('$CONFIG')).get('$1'); print('' if v is None else v)"
}

BUCKET=$(read_cfg bucket)
REGION=$(read_cfg region)
PROFILE=$(read_cfg aws_profile)

PREFIX="${1:-}"
KEYS_ONLY=0
if [[ "${2:-}" == "--keys-only" || "${1:-}" == "--keys-only" ]]; then
  KEYS_ONLY=1
  PREFIX="${1:-}"
  [[ "$PREFIX" == "--keys-only" ]] && PREFIX=""
fi

LIST=$(AWS_PROFILE="$PROFILE" aws s3 ls "s3://$BUCKET/$PREFIX" 2>/dev/null | awk '{print $4}' | grep -E '\.html$' || true)

if [[ -z "$LIST" ]]; then
  exit 0
fi

if [[ "$KEYS_ONLY" == "1" ]]; then
  echo "$LIST"
else
  echo "$LIST" | sed "s|^|https://${BUCKET}.s3.${REGION}.amazonaws.com/|"
fi
