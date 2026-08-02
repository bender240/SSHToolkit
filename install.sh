
Copy
#!/bin/bash

# Exit on any error, unset variable, or failed pipe
set -euo pipefail

# --- Color Codes for Output ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# --- System & Privilege Checks ---
check_requirements() {
    if [ "$EUID" -ne 0 ]; then
        log_error "This script installs system packages. Please run with sudo: sudo $0"
    fi

    if [ ! -f /etc/os-release ]; then
        log_error "Unsupported OS. /etc/os-release not found."
    fi

    . /etc/os-release
    DISTRO=$ID
}

# --- Install Hydra and Core Dependencies ---
install_hydra() {
    log_info "Detecting package manager to install Hydra..."
    
    case "$DISTRO" in
        ubuntu|debian|pop|mint)
            apt-get update -y
            apt-get install -y hydra wget curl python3
            ;;
        fedora|rhel|centos)
            dnf install -y hydra wget curl python3
            ;;
        arch)
            pacman -Syu --noconfirm
            pacman -S --noconfirm hydra wget curl python3
            ;;
        *)
            log_warn "Unknown distro '$DISTRO'. Attempting fallback to 'hydra' package..."
            if command -v apt-get &> /dev/null; then apt-get install -y hydra wget curl python3
            elif command -v dnf &> /dev/null; then dnf install -y hydra wget curl python3
            else log_error "Could not safely determine package manager. Install 'hydra' and 'python3' manually."; fi
            ;;
    esac
}

# --- Download & Configure SSH-MITM ---
install_ssh_mitm() {
    TARGET_DIR="/opt/SSHToolkit/mitm"
    BIN_DIR="/usr/local/bin"
    APPIMAGE_NAME="ssh-mitm-x86_64.AppImage"
    
    # Correct URL provided by user
    URL="https://github.com/ssh-mitm/ssh-mitm/releases/latest/download/ssh-mitm-x86_64.AppImage"

    log_info "Creating target directory at ${TARGET_DIR}..."
    mkdir -p "${TARGET_DIR}"

    log_info "Downloading the Latest SSH-MITM AppImage..."
    wget -q --show-progress "$URL" -O "${TARGET_DIR}/${APPIMAGE_NAME}"

    log_info "Setting executable permissions..."
    chmod +x "${TARGET_DIR}/${APPIMAGE_NAME}"

    log_info "Creating global shortcut 'ssh-mitm' in system PATH..."
    ln -sf "${TARGET_DIR}/${APPIMAGE_NAME}" "${BIN_DIR}/ssh-mitm"
}

# --- Setup Crawler.py Systemd Service ---
setup_crawler_service() {
    CRAWLER_PY="/opt/SSHToolkit/crawler.py"
    SERVICE_NAME="crawler"
    SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

    if [ ! -f "$CRAWLER_PY" ]; then
        log_warn "crawler.py not found at $CRAWLER_PY. Service may fail until file is placed."
    fi

    log_info "Creating systemd service for crawler.py..."
    
    cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=SSH Toolkit Crawler
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 ${CRAWLER_PY}
WorkingDirectory=/opt/SSHtToolkit
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    log_info "Reloading systemd daemon..."
    systemctl daemon-reload

    log_info "Enabling and starting ${SERVICE_NAME}.service..."
    systemctl enable ${SERVICE_NAME}.service
    systemctl start ${SERVICE_NAME}.service

    log_info "Crawler service status:"
    systemctl status ${SERVICE_NAME}.service --no-pager || true
}

# --- Main Flow ---
main() {
    check_requirements
    
    # NEW: Create and CD into /opt/SSHtoolKit
    TOOLKIT_DIR="/opt/SSHToolkit"
    if [ ! -d "$TOOLKIT_DIR" ]; then
        log_info "Creating toolkit directory: $TOOLKIT_DIR"
        mkdir -p "$TOOLKIT_DIR"
    fi
    
    log_info "Changing directory to $TOOLKIT_DIR"
    cd "$TOOLKIT_DIR"
    
    install_hydra
    install_ssh_mitm
    setup_crawler_service
    
    echo -e "\n${GREEN}✔ Verification Complete!${NC}"
    echo -e "-> Hydra version: $(hydra -h | head -n 1)"
    echo -e "-> SSH-MITM path: /usr/local/bin/ssh-mitm"
    echo -e "-> Crawler Service: active (run 'systemctl status crawler' for details)"
    echo -e "\nYou can now run the tools globally using ${YELLOW}hydra${NC} or ${YELLOW}ssh-mitm${NC}."
}

main

