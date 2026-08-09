Here is the updated script. It creates the /opt/targets directory and an ips.txt file inside it.

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

# --- Setup Targets Directory ---
setup_targets() {
    TARGETS_DIR="/opt/SSHToolkit/targets"
    IPS_FILE="${TARGETS_DIR}/ips.txt"

    log_info "Creating targets directory: ${TARGETS_DIR}..."
    mkdir -p "${TARGETS_DIR}"

    # Create ips.txt if it doesn't exist, or clear it
    touch "${IPS_FILE}"
    log_info "Created ${IPS_FILE}"
}
setup_password(){
    TOOLKIT_DIR="/opt/SSHToolkit"
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PASSWORDS_ARCHIVE="${SCRIPT_DIR}/passwords.tgz"
    EXTRACT_DIR="${TOOLKIT_DIR}" 

    if [ ! -f "$PASSWORDS_ARCHIVE" ]; then
        log_warn "passwords.tgz not found in ${SCRIPT_DIR}. Skipping..."
        return 0
    fi

    log_info "Extracting passwords.tgz to ${EXTRACT_DIR}..."
    # -C changes to the directory before extracting
    tar -xvzf "$PASSWORDS_ARCHIVE" -C "$EXTRACT_DIR"
    log_info "Passwords extracted successfully.
}
# --- Move Crawler.py and Setup Systemd Service ---
setup_crawler() {
    TOOLKIT_DIR="/opt/SSHToolkit"
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    CRAWLER_SOURCE="${SCRIPT_DIR}/crawler.py"
    CRAWLER_DEST="${TOOLKIT_DIR}/crawler.py"
    SERVICE_NAME="crawler"
    SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

    # 1. Move crawler.py from script directory to Toolkit directory
    if [ -f "$CRAWLER_SOURCE" ]; then
        log_info "Moving crawler.py from ${SCRIPT_DIR} to ${TOOLKIT_DIR}..."
        mv "$CRAWLER_SOURCE" "$CRAWLER_DEST"
        chmod +x "$CRAWLER_DEST"
        log_info "crawler.py moved successfully."
    else
        log_warn "crawler.py not found in ${SCRIPT_DIR}. Service may fail."
    fi

    # 2. Create systemd service
    log_info "Creating systemd service for crawler.py..."
    
    cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=SSH Toolkit Crawler
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 ${CRAWLER_DEST}
WorkingDirectory=${TOOLKIT_DIR}
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
    
    # Create /opt/SSHtoolKit directory
    TOOLKIT_DIR="/opt/SSHToolkit"
    if [ ! -d "$TOOLKIT_DIR" ]; then
        log_info "Creating toolkit directory: $TOOLKIT_DIR"
        mkdir -p "$TOOLKIT_DIR"
    fi
    
    install_hydra
    install_ssh_mitm
    setup_targets
    setup_passwords
    setup_crawler
    
    echo -e "\n${GREEN} Verification Complete${NC}"
    echo -e "-> Hydra version: $(hydra -h | head -n 1)"
    echo -e "-> SSH-MITM path: /usr/local/bin/ssh-mitm"
    echo -e "-> Targets directory: /opt/targets"
    echo -e "-> Crawler Service: active (run 'systemctl status crawler' for details)"
    echo -e "\nYou can now run the tools globally using ${YELLOW}hydra${NC} or ${YELLOW}ssh-mitm${NC}."
}

main

