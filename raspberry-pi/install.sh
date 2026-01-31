#!/bin/bash

################################################################################
# BlueZscript Automated Installation Script
# Author: RevEngine3r
# Description: Automated setup for Raspberry Pi BLE listener and web UI
# Requirements: Raspberry Pi OS (Bullseye+), Python 3.9+, root privileges
################################################################################

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/opt/BlueZscript"
REPO_URL="https://github.com/RevEngine3r/BlueZscript.git"
SERVICE_NAME="ble-listener-secure"
PYTHON_VERSION="3.9"

################################################################################
# Helper Functions
################################################################################

print_status() {
    echo -e "${GREEN}[*]${NC} $1"
}

print_error() {
    echo -e "${RED}[!]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

check_os() {
    if [[ ! -f /etc/os-release ]]; then
        print_error "Cannot determine OS version"
        exit 1
    fi
    
    . /etc/os-release
    if [[ "$ID" != "raspbian" ]] && [[ "$ID" != "debian" ]]; then
        print_warning "This script is designed for Raspberry Pi OS/Debian"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    
    PYTHON_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    print_status "Detected Python $PYTHON_VER"
    
    if awk "BEGIN {exit !($PYTHON_VER >= $PYTHON_VERSION)}"; then
        print_status "Python version is compatible"
    else
        print_error "Python $PYTHON_VERSION or higher is required (found $PYTHON_VER)"
        exit 1
    fi
}

################################################################################
# Installation Steps
################################################################################

install_system_dependencies() {
    print_status "Updating package lists..."
    apt-get update -qq
    
    print_status "Installing system dependencies..."
    apt-get install -y \
        python3-pip \
        python3-venv \
        python3-dev \
        bluetooth \
        bluez \
        libbluetooth-dev \
        libglib2.0-dev \
        git \
        sqlite3 \
        curl \
        > /dev/null 2>&1
    
    print_status "System dependencies installed successfully"
}

enable_bluetooth() {
    print_status "Configuring Bluetooth..."
    
    # Unblock Bluetooth
    rfkill unblock bluetooth || true
    
    # Enable and start Bluetooth service
    systemctl enable bluetooth
    systemctl start bluetooth
    
    # Check if Bluetooth is available
    if ! hciconfig hci0 &> /dev/null; then
        print_warning "Bluetooth adapter not detected. Please ensure BLE is supported."
    else
        print_status "Bluetooth adapter detected and configured"
    fi
}

clone_repository() {
    print_status "Cloning BlueZscript repository..."
    
    # Remove existing directory if present
    if [[ -d "$INSTALL_DIR" ]]; then
        print_warning "Existing installation found at $INSTALL_DIR"
        read -p "Remove and reinstall? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$INSTALL_DIR"
        else
            print_error "Installation aborted"
            exit 1
        fi
    fi
    
    # Clone repository
    git clone "$REPO_URL" "$INSTALL_DIR" > /dev/null 2>&1
    cd "$INSTALL_DIR"
    
    print_status "Repository cloned successfully"
}

setup_python_environment() {
    print_status "Setting up Python virtual environment..."
    
    cd "$INSTALL_DIR"
    
    # Create virtual environment
    python3 -m venv venv
    
    # Activate and install dependencies
    print_status "Installing Python dependencies (this may take a few minutes)..."
    ./venv/bin/pip install --upgrade pip > /dev/null 2>&1
    ./venv/bin/pip install -r raspberry-pi/requirements.txt > /dev/null 2>&1
    
    print_status "Python environment configured successfully"
}

setup_directories() {
    print_status "Creating data directories..."
    
    cd "$INSTALL_DIR/raspberry-pi"
    
    # Create necessary directories
    mkdir -p data logs templates/static
    
    # Set secure permissions
    chmod 700 data
    chmod 755 logs
    chmod 755 templates
    
    # Create action script if not exists
    if [[ ! -f action_script.sh ]]; then
        cat > action_script.sh << 'EOF'
#!/bin/bash
################################################################################
# BlueZscript Action Script
# This script is executed when a valid BLE trigger is received
# Customize this to perform your desired actions
################################################################################

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Action triggered" >> /opt/BlueZscript/raspberry-pi/logs/actions.log

# Example: Blink LED on GPIO 17
# Uncomment and modify as needed
# echo "17" > /sys/class/gpio/export 2>/dev/null || true
# echo "out" > /sys/class/gpio/gpio17/direction
# echo "1" > /sys/class/gpio/gpio17/value
# sleep 2
# echo "0" > /sys/class/gpio/gpio17/value

# Example: Take a photo with PiCamera
# raspistill -o /opt/BlueZscript/raspberry-pi/logs/capture_$(date +%s).jpg

# Example: Send notification
# curl -X POST https://your-webhook-url.com/notify -d "action=triggered"

echo "Action completed successfully"
EOF
        chmod +x action_script.sh
    fi
    
    print_status "Directories created and configured"
}

install_systemd_service() {
    print_status "Installing systemd service..."
    
    cd "$INSTALL_DIR/raspberry-pi"
    
    # Copy service file
    cp ble-listener-secure.service /etc/systemd/system/
    
    # Reload systemd
    systemctl daemon-reload
    
    # Enable service (but don't start yet)
    systemctl enable "$SERVICE_NAME"
    
    print_status "Systemd service installed and enabled"
}

generate_master_key() {
    print_status "Generating master encryption key..."
    
    cd "$INSTALL_DIR"
    
    # Generate master key using Python
    ./venv/bin/python3 -c "
import os
from cryptography.fernet import Fernet

key_file = 'raspberry-pi/data/master.key'
if not os.path.exists(key_file):
    key = Fernet.generate_key()
    with open(key_file, 'wb') as f:
        f.write(key)
    os.chmod(key_file, 0o600)
    print('Master key generated successfully')
else:
    print('Master key already exists, skipping...')
"
    
    # Set secure permissions
    chmod 600 raspberry-pi/data/master.key
    chown root:root raspberry-pi/data/master.key
    
    print_status "Master encryption key secured"
}

run_tests() {
    print_status "Running unit tests to verify installation..."
    
    cd "$INSTALL_DIR"
    
    if ./venv/bin/python3 -m pytest tests/ -q > /dev/null 2>&1; then
        print_status "All tests passed ✓"
    else
        print_warning "Some tests failed. Installation may still work, but please check logs."
    fi
}

print_summary() {
    cat << EOF

${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}
${GREEN}    BlueZscript Installation Complete! 🎉${NC}
${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}

${YELLOW}Installation Directory:${NC} $INSTALL_DIR

${YELLOW}Next Steps:${NC}

1. ${GREEN}Start the BLE Listener Service:${NC}
   sudo systemctl start $SERVICE_NAME
   sudo systemctl status $SERVICE_NAME

2. ${GREEN}Start the Web UI (optional):${NC}
   cd $INSTALL_DIR/raspberry-pi
   ../venv/bin/python3 web_ui.py
   
   Access at: http://$(hostname -I | awk '{print $1}'):5000

3. ${GREEN}Pair Your Android Device:${NC}
   - Open Web UI
   - Click "Pair New Device"
   - Scan QR code with Android app

4. ${GREEN}Customize Action Script:${NC}
   sudo nano $INSTALL_DIR/raspberry-pi/action_script.sh

${YELLOW}Useful Commands:${NC}

- Check service status:  ${GREEN}sudo systemctl status $SERVICE_NAME${NC}
- View logs:            ${GREEN}sudo journalctl -u $SERVICE_NAME -f${NC}
- Restart service:      ${GREEN}sudo systemctl restart $SERVICE_NAME${NC}
- Run tests:            ${GREEN}cd $INSTALL_DIR && ./venv/bin/pytest tests/ -v${NC}

${YELLOW}Documentation:${NC}
- Installation Guide:   $INSTALL_DIR/INSTALL.md
- Troubleshooting:      $INSTALL_DIR/TROUBLESHOOTING.md
- Testing Guide:        $INSTALL_DIR/TESTING.md

${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}

For support, visit: https://github.com/RevEngine3r/BlueZscript

EOF
}

################################################################################
# Main Installation Flow
################################################################################

main() {
    clear
    echo -e "${GREEN}"
    cat << "EOF"
 ____  _             ______            _       _   
|  _ \| |           |___  /           (_)     | |  
| |_) | |_   _  ___    / / ___  ___ _ __ _ __| |_ 
|  _ <| | | | |/ _ \  / / / __|/ __| '__| '_ \ __|
| |_) | | |_| |  __/ / /__\__ \ (__| |  | |_) | |_ 
|____/|_|\__,_|\___/_____/___/\___|_|  | .__/ \__|
                                       | |        
                                       |_|        
EOF
    echo -e "${NC}"
    echo "Automated Installation Script"
    echo "Version 1.0.0"
    echo ""
    
    # Pre-flight checks
    print_status "Running pre-flight checks..."
    check_root
    check_os
    check_python
    
    echo ""
    read -p "Proceed with installation? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Installation cancelled"
        exit 1
    fi
    
    echo ""
    print_status "Starting installation..."
    echo ""
    
    # Installation steps
    install_system_dependencies
    enable_bluetooth
    clone_repository
    setup_python_environment
    setup_directories
    generate_master_key
    install_systemd_service
    run_tests
    
    # Summary
    print_summary
}

# Trap errors
trap 'print_error "Installation failed at line $LINENO. Check logs for details."' ERR

# Run main installation
main "$@"