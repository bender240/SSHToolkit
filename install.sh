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
            apt-get install -y hydra wget curl
            ;;
        fedora|rhel|centos)
            dnf install -y hydra wget curl
            ;;
        arch)
            pacman -Syu --noconfirm
            pacman -S --noconfirm hydra wget curl
            ;;
        *)
            log_warn "Unknown distro '$DISTRO'. Attempting fallback to 'hydra' package..."
            if command -v apt-get &> /dev/null; then apt-get install -y hydra wget
            elif command -v dnf &> /dev/null; then dnf install -y hydra wget
            else log_error "Could not safely determine package manager. Install 'hydra' manually."; fi
            ;;
    esac
}

# --- Download & Configure SSH-MITM ---
install_ssh_mitm() {
    TARGET_DIR="/opt/SSHtoolKit/mitm"
    BIN_DIR="/usr/local/bin"
    APPIMAGE_NAME="ssh-mitm-x86_64.AppImage"
    URL="https://github.com{APPIMAGE_NAME}"

    log_info "Creating target directory at ${TARGET_DIR}..."
    mkdir -p "${TARGET_DIR}"

    log_info "Downloading the Latest SSH-MITM AppImage..."
    wget -q --show-progress "$URL" -O "${TARGET_DIR}/${APPIMAGE_NAME}"

    log_info "Setting executable permissions..."
    chmod +x "${TARGET_DIR}/${APPIMAGE_NAME}"

    log_info "Creating global shortcut 'ssh-mitm' in system PATH..."
    ln -sf "${TARGET_DIR}/${APPIMAGE_NAME}" "${BIN_DIR}/ssh-mitm"
}

# --- Main Flow ---
main() {
    check_requirements
    install_hydra
    install_ssh_mitm
    
    echo -e "\n${GREEN}✔ Verification Complete!${NC}"
    echo -e "-> Hydra version: $(hydra -h | head -n 1)"
    echo -e "-> SSH-MITM path: /usr/local/bin/ssh-mitm"
    echo -e "\nYou can now run the tools globally using ${YELLOW}hydra${NC} or ${YELLOW}ssh-mitm${NC}."
}

main

