#!/usr/bin/env bash
# Send a DataCards session feedback report (markdown) to the feedback endpoint.
#
# Usage:
#   send-feedback.sh [--dry-run] REPORT.md
#   send-feedback.sh [--dry-run] -          # read the report from stdin
#
# The endpoint is taken from DC_FEEDBACK_URL, else from the default below.
set -euo pipefail

DEFAULT_URL="https://workflowhooks.cavorit.de/eng/pair-skill-feedback"
url="${DC_FEEDBACK_URL:-$DEFAULT_URL}"

usage() {
  echo "Usage: send-feedback.sh [--dry-run] REPORT.md | -" >&2
  exit 2
}

dry_run=0
report=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) dry_run=1 ;;
    -h|--help) usage ;;
    -) report="-" ;;
    -*) echo "Unknown option: $1" >&2; usage ;;
    *) [[ -z "$report" ]] || usage; report="$1" ;;
  esac
  shift
done
[[ -n "$report" ]] || usage

tmp=""
cleanup() { [[ -z "$tmp" ]] || rm -f "$tmp"; }
trap cleanup EXIT

if [[ "$report" == "-" ]]; then
  tmp="$(mktemp)"
  cat > "$tmp"
  report="$tmp"
elif [[ ! -f "$report" ]]; then
  echo "Report file not found: $report" >&2
  exit 1
fi

if [[ ! -s "$report" ]]; then
  echo "The report is empty; nothing to send." >&2
  exit 1
fi

if [[ "$dry_run" -eq 1 ]]; then
  echo "POST $url"
  echo "Content-Type: text/markdown; charset=utf-8"
  echo
  cat "$report"
  exit 0
fi

command -v curl >/dev/null 2>&1 || { echo "send-feedback.sh needs curl on PATH." >&2; exit 1; }

status="$(curl --silent --show-error --output /dev/null --write-out '%{http_code}' \
  --max-time 30 \
  --request POST \
  --header 'Content-Type: text/markdown; charset=utf-8' \
  --data-binary "@${report}" \
  "$url")" || { echo "Sending failed: could not reach $url" >&2; exit 1; }

if [[ "$status" =~ ^2 ]]; then
  echo "Feedback sent (HTTP $status)."
else
  echo "Sending failed: HTTP $status from $url" >&2
  exit 1
fi
