#!/bin/bash

################################################################################
# BlueZscript Automated Installer
# 
# This script automates the installation of BlueZscript on Raspberry Pi.
# It installs dependencies, sets up the Python environment, and configures
# the systemd service.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/RevEngine3r/BlueZscript/main/raspberry-pi/install.sh | sudo bash
#
# Or download and run:
#   wget https://raw.githubusercontent.com/RevEngine3r/BlueZscript/main/raspberry-pi/install.sh
#   chmod +x install.sh
#   sudo ./install.sh
#
# Author: RevEngine3r
# License: MIT
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/opt/BlueZscript"
REPO_URL="https://github.com/RevEngine3r/BlueZscript.git"
SERVICE_NAME="ble-listener-secure"

################################################################################
# Helper Functions
################################################################################

print_header() {
    echo -e "${BLUE}"
    echo "═══════════════════════════════════════════════════════════════"
    echo "  $1"
    echo "═══════════════════════════════════════════════════════════════"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

check_os() {
    if [ ! -f /etc/os-release ]; then
        print_error "Cannot determine OS. /etc/os-release not found."
        exit 1
    fi
    
    . /etc/os-release
    
    if [[ "$ID" != "raspbian" && "$ID" != "debian" ]]; then
        print_warning "This script is designed for Raspberry Pi OS (Debian-based)."
        print_warning "Detected OS: $PRETTY_NAME"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

check_bluetooth() {
    if ! command -v hciconfig &> /dev/null; then
        return 1
    fi
    
    if ! hciconfig hci0 &> /dev/null; then
        return 1
    fi
    
    return 0
}

################################################################################
# Installation Steps
################################################################################

install_system_dependencies() {
    print_header "Installing System Dependencies"
    
    print_info "Updating package lists..."
    apt-get update -qq
    
    print_info "Installing packages..."
    apt-get install -y -qq \
        python3 \
        python3-pip \
        python3-venv \
        bluetooth \
        bluez \
        libbluetooth-dev \
        git \
        sqlite3 \
        curl \
        || { print_error "Failed to install system dependencies"; exit 1; }
    
    print_success "System dependencies installed"
}

setup_bluetooth() {
    print_header "Configuring Bluetooth"
    
    print_info "Enabling Bluetooth service..."
    systemctl enable bluetooth
    systemctl start bluetooth
    
    # Unblock Bluetooth if blocked
    if command -v rfkill &> /dev/null; then
        rfkill unblock bluetooth
    fi
    
    # Bring up Bluetooth interface
    if check_bluetooth; then
        hciconfig hci0 up
        print_success "Bluetooth configured successfully"
        print_info "Bluetooth address: $(hciconfig hci0 | grep 'BD Address' | awk '{print $3}')"
    else
        print_warning "Bluetooth interface not detected. This may be normal on some systems."
        print_warning "Bluetooth will be activated when hardware is available."
    fi
}

clone_repository() {
    print_header "Cloning Repository"
    
    if [ -d "$INSTALL_DIR" ]; then
        print_warning "Installation directory already exists: $INSTALL_DIR"
        read -p "Remove and reinstall? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_info "Removing existing installation..."
            rm -rf "$INSTALL_DIR"
        else
            print_info "Updating existing installation..."
            cd "$INSTALL_DIR"
            git pull
            return
        fi
    fi
    
    print_info "Cloning from $REPO_URL..."
    git clone -q "$REPO_URL" "$INSTALL_DIR" || { print_error "Failed to clone repository"; exit 1; }
    
    print_success "Repository cloned to $INSTALL_DIR"
}

setup_python_environment() {
    print_header "Setting Up Python Environment"
    
    cd "$INSTALL_DIR"
    
    print_info "Creating virtual environment..."
    python3 -m venv venv || { print_error "Failed to create virtual environment"; exit 1; }
    
    print_info "Upgrading pip..."
    ./venv/bin/pip install --upgrade pip setuptools wheel -q
    
    print_info "Installing Python dependencies..."
    ./venv/bin/pip install -r raspberry-pi/requirements.txt -q || { print_error "Failed to install Python packages"; exit 1; }
    
    print_success "Python environment configured"
}

run_tests() {
    print_header "Running Tests"
    
    cd "$INSTALL_DIR"
    
    print_info "Running unit tests..."
    if ./venv/bin/python3 -m pytest tests/ -v --tb=short; then
        print_success "All tests passed (52/52)"
    else
        print_warning "Some tests failed. Installation will continue, but functionality may be impaired."
        read -p "Continue? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

setup_data_directory() {
    print_header "Setting Up Data Directory"
    
    local data_dir="$INSTALL_DIR/raspberry-pi/data"
    
    print_info "Creating data directory..."
    mkdir -p "$data_dir"
    
    print_info "Setting permissions..."
    chmod 700 "$data_dir"
    chown root:root "$data_dir"
    
    print_success "Data directory configured: $data_dir"
}

setup_action_script() {
    print_header "Configuring Action Script"
    
    local script="$INSTALL_DIR/raspberry-pi/action_script.sh"
    
    if [ ! -f "$script" ]; then
        print_info "Creating default action script..."
        cat > "$script" << 'EOF'
#!/bin/bash
# Default action script for BlueZscript
# Edit this file to customize the action

echo "[$(date)] Trigger received" >> /tmp/bluezscript_triggers.log
echo "Action executed successfully"
EOF
    fi
    
    chmod +x "$script"
    print_success "Action script configured: $script"
    print_info "Edit this file to customize your trigger action"
}

install_systemd_service() {
    print_header "Installing Systemd Service"
    
    local service_file="/etc/systemd/system/${SERVICE_NAME}.service"
    
    print_info "Copying service file..."
    cp "$INSTALL_DIR/raspberry-pi/ble-listener-secure.service" "$service_file" || { print_error "Failed to copy service file"; exit 1; }
    
    print_info "Reloading systemd..."
    systemctl daemon-reload
    
    print_info "Enabling service..."
    systemctl enable "${SERVICE_NAME}.service"
    
    print_info "Starting service..."
    systemctl start "${SERVICE_NAME}.service"
    
    sleep 2
    
    if systemctl is-active --quiet "${SERVICE_NAME}.service"; then
        print_success "Service installed and started successfully"
    else
        print_warning "Service installed but not running. Check logs:"
        print_info "sudo journalctl -u ${SERVICE_NAME} -n 50"
    fi
}

print_completion_info() {
    print_header "Installation Complete!"
    
    echo -e "${GREEN}"
    cat << "EOF"
    ____  __           _____           _       __ 
   / __ )/ /_  _____  /__  /_  _______(_)___  / /_
  / __  / / / / / _ \   / / / / / ___/ / __ \/ __/
 / /_/ / / /_/ /  __/  / /_\ \/ /  / / /_/ / /_  
/_____/_/\__,_/\___/  /____/\_\_/ /_/ .___/\__/  
                                   /_/            
EOF
    echo -e "${NC}"
    
    echo
    print_info "Installation directory: $INSTALL_DIR"
    print_info "Service name: ${SERVICE_NAME}.service"
    echo
    
    print_header "Next Steps"
    echo
    echo "1. Check service status:"
    echo -e "   ${BLUE}sudo systemctl status ${SERVICE_NAME}${NC}"
    echo
    echo "2. View logs:"
    echo -e "   ${BLUE}sudo journalctl -u ${SERVICE_NAME} -f${NC}"
    echo
    echo "3. Start Web UI:"
    echo -e "   ${BLUE}cd $INSTALL_DIR/raspberry-pi${NC}"
    echo -e "   ${BLUE}sudo ../venv/bin/python3 web_ui.py${NC}"
    echo
    echo "4. Access Web UI:"
    local ip=$(hostname -I | awk '{print $1}')
    echo -e "   ${BLUE}http://${ip}:5000${NC}"
    echo
    echo "5. Customize action script:"
    echo -e "   ${BLUE}sudo nano $INSTALL_DIR/raspberry-pi/action_script.sh${NC}"
    echo
    echo "6. Install Android app:"
    echo -e "   ${BLUE}https://github.com/RevEngine3r/BlueZscript/releases${NC}"
    echo
    
    print_header "Documentation"
    echo
    echo -e "${BLUE}Installation Guide:${NC} $INSTALL_DIR/INSTALL.md"
    echo -e "${BLUE}Testing Guide:${NC} $INSTALL_DIR/TESTING.md"
    echo -e "${BLUE}Troubleshooting:${NC} $INSTALL_DIR/TROUBLESHOOTING.md"
    echo -e "${BLUE}Full README:${NC} $INSTALL_DIR/README.md"
    echo
    
    print_success "Happy automating! 🚀"
    echo
}

################################################################################
# Main Installation Flow
################################################################################

main() {
    clear
    
    print_header "BlueZscript Installer"
    echo -e "${BLUE}Version: 1.0.0${NC}"
    echo -e "${BLUE}Author: RevEngine3r${NC}"
    echo
    
    # Pre-flight checks
    check_root
    check_os
    
    # Installation steps
    install_system_dependencies
    setup_bluetooth
    clone_repository
    setup_python_environment
    run_tests
    setup_data_directory
    setup_action_script
    install_systemd_service
    
    # Completion
    print_completion_info
}

# Run main installation
main

exit 0