#!/usr/bin/env bash
# ==============================================================================
# LinuxEye Uninstaller Script
# Removes LinuxEye service, binary symlink, and /opt/linux-eye files.
# ==============================================================================

set -e

INSTALL_DIR="/opt/linux-eye"
SERVICE_FILE="/etc/systemd/system/linux-eye.service"
BIN_LINK="/usr/local/bin/linux-eye"

if [ "$EUID" -ne 0 ]; then
    echo "[!] Please run this uninstaller as root or with sudo:"
    echo "    sudo ./uninstall.sh"
    exit 1
fi

echo "=========================================="
echo "    👁️  Uninstalling LinuxEye..."
echo "=========================================="

# 1. Stop and disable systemd service
if systemctl is-active --quiet linux-eye.service 2>/dev/null; then
    echo "[*] Stopping linux-eye service..."
    systemctl stop linux-eye.service
fi

if [ -f "${SERVICE_FILE}" ]; then
    echo "[*] Removing systemd service file..."
    systemctl disable linux-eye.service 2>/dev/null || true
    rm -f "${SERVICE_FILE}"
    systemctl daemon-reload
fi

# 2. Remove CLI script
if [ -f "${BIN_LINK}" ]; then
    echo "[*] Removing binary link ${BIN_LINK}..."
    rm -f "${BIN_LINK}"
fi

# 3. Remove /opt/linux-eye directory
if [ -d "${INSTALL_DIR}" ]; then
    echo "[*] Removing directory ${INSTALL_DIR}..."
    rm -rf "${INSTALL_DIR}"
fi

echo ""
echo "=========================================="
echo "✅ LinuxEye has been completely uninstalled."
echo "=========================================="
