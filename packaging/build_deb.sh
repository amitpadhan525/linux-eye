#!/usr/bin/env bash
# ==============================================================================
# LinuxEye Debian Package (.deb) Builder
# Automatically builds .deb using dpkg-deb or native Python builder.
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="python3"

if [ -f "${SCRIPT_DIR}/../.venv/bin/python" ]; then
    PYTHON_BIN="${SCRIPT_DIR}/../.venv/bin/python"
fi

echo "=========================================="
echo "    📦 Building LinuxEye Debian Package   "
echo "=========================================="

"${PYTHON_BIN}" "${SCRIPT_DIR}/build_deb.py"
