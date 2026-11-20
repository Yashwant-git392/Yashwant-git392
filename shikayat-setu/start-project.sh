#!/bin/sh
# Works from any directory and does not activate or modify your shell.
set -eu
cd "$(dirname "$0")"
if command -v python3 >/dev/null 2>&1; then
    exec python3 start_project.py
fi
printf '%s\n' 'Python 3 was not found. Install Python 3.11 or 3.12, then try again.' >&2
exit 1
