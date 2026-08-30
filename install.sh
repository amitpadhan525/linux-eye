#!/usr/bin/env bash
# ==============================================================================
# LinuxEye Installer Script
# Installs LinuxEye to /opt/linux-eye, configures venv, and sets up systemd service.
# ==============================================================================

set -e

INSTALL_DIR="/opt/linux-eye"
SERVICE_FILE="systemd/linux-eye.service"
SYSTEMD_DIR="/etc/systemd/system"
BIN_LINK="/usr/local/bin/linux-eye"

# 1. Require root privileges
if [ "$EUID" -ne 0 ]; then
    echo "[!] Please run this installer as root or with sudo:"
    echo "    sudo ./install.sh"
    exit 1
fi

echo "=========================================="
echo "    👁️  Installing LinuxEye Security Monitor"
echo "=========================================="

# 2. Check for Python 3
if ! command -v python3 &>/dev/null; then
    echo "[!] Python 3 is required but was not found. Please install Python 3."
    exit 1
fi

# 3. Create target directories
echo "[*] Setting up installation directory at ${INSTALL_DIR}..."
mkdir -p "${INSTALL_DIR}"
mkdir -p "${INSTALL_DIR}/logs"
mkdir -p "${INSTALL_DIR}/config"

# 4. Copy source files
echo "[*] Copying project files..."
cp -r linux_eye "${INSTALL_DIR}/"
cp -r config/* "${INSTALL_DIR}/config/" 2>/dev/null || cp config/config.yaml "${INSTALL_DIR}/config/"
cp requirements.txt "${INSTALL_DIR}/"
cp pyproject.toml "${INSTALL_DIR}/" 2>/dev/null || true

# 5. Set up virtual environment
echo "[*] Configuring Python virtual environment..."
python3 -m venv "${INSTALL_DIR}/.venv"
"${INSTALL_DIR}/.venv/bin/pip" install --upgrade pip --quiet
"${INSTALL_DIR}/.venv/bin/pip" install -r "${INSTALL_DIR}/requirements.txt" --quiet

# 6. Create global CLI launcher script
echo "[*] Creating CLI command at ${BIN_LINK}..."
cat << 'EOF' > "${BIN_LINK}"
#!/usr/bin/env bash
cd /opt/linux-eye && sudo /opt/linux-eye/.venv/bin/python -m linux_eye.main "$@"
EOF
chmod +x "${BIN_LINK}"
ln -sf "${BIN_LINK}" /usr/bin/linux-eye 2>/dev/null || true

# 7. Install systemd service unit
if [ -f "${SERVICE_FILE}" ]; then
    echo "[*] Installing systemd service unit..."
    cp "${SERVICE_FILE}" "${SYSTEMD_DIR}/linux-eye.service"
    systemctl daemon-reload
    systemctl enable linux-eye.service
    echo "[*] Starting LinuxEye daemon..."
    systemctl restart linux-eye.service
fi

echo ""
echo "=========================================="
echo "🎉 LinuxEye installed successfully!"
echo "=========================================="
echo ""
echo "Useful Commands:"
echo "  • Run interactively : sudo linux-eye"
echo "  • Service status    : sudo systemctl status linux-eye"
echo "  • View live logs    : sudo journalctl -u linux-eye -f"
echo "  • View audit log    : cat /opt/linux-eye/logs/linux-eye.log"
echo "  • Uninstall         : sudo ./uninstall.sh"
echo ""
