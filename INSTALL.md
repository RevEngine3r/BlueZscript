# 📦 BlueZscript Installation Guide

Comprehensive step-by-step installation instructions for Raspberry Pi and Android.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Raspberry Pi Installation](#raspberry-pi-installation)
  - [Automated Installation](#automated-installation-recommended)
  - [Manual Installation](#manual-installation)
- [Android App Installation](#android-app-installation)
- [Initial Configuration](#initial-configuration)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Raspberry Pi Requirements

- **Hardware**: Raspberry Pi 4 (recommended) or Pi 3 with BLE support
- **OS**: Raspberry Pi OS (Bullseye or newer)
- **Python**: Version 3.9 or higher
- **RAM**: Minimum 1GB
- **Storage**: At least 500MB free space
- **Network**: Wi-Fi or Ethernet connection
- **Bluetooth**: Built-in BLE or USB BLE adapter

### Android Requirements

- **OS**: Android 8.0 (Oreo) or higher (API level 26+)
- **Bluetooth**: BLE support (standard on modern devices)
- **Permissions**: Location, Bluetooth, Camera (for QR scanning)
- **Storage**: ~10MB for app installation

### Network Requirements

- Both devices should be on the same network for initial setup
- Raspberry Pi should have a static IP (recommended) or mDNS enabled
- Firewall: Port 5000 open for web UI access (optional)

---

## Raspberry Pi Installation

### Automated Installation (Recommended)

The fastest way to get started. The installation script handles everything automatically.

#### Step 1: Download and Run Installer

```bash
# One-line installation
curl -fsSL https://raw.githubusercontent.com/RevEngine3r/BlueZscript/main/raspberry-pi/install.sh | sudo bash
```

**Or download first, then run:**

```bash
# Download script
curl -fsSL https://raw.githubusercontent.com/RevEngine3r/BlueZscript/main/raspberry-pi/install.sh -o install.sh

# Review script (recommended)
less install.sh

# Make executable and run
chmod +x install.sh
sudo ./install.sh
```

#### Step 2: Follow Prompts

The installer will:
- ✅ Check system requirements
- ✅ Install dependencies (Python, Bluetooth, etc.)
- ✅ Clone repository to `/opt/BlueZscript`
- ✅ Set up Python virtual environment
- ✅ Install Python packages
- ✅ Generate encryption keys
- ✅ Configure systemd service
- ✅ Run verification tests

#### Step 3: Start Services

After installation completes:

```bash
# Start BLE listener
sudo systemctl start ble-listener-secure

# Check status
sudo systemctl status ble-listener-secure

# Enable auto-start on boot (optional)
sudo systemctl enable ble-listener-secure
```

#### Step 4: Start Web UI (Optional)

```bash
cd /opt/BlueZscript/raspberry-pi
../venv/bin/python3 web_ui.py
```

Access at: `http://<raspberry-pi-ip>:5000`

**To find your Raspberry Pi IP:**
```bash
hostname -I
# Or use mDNS:
# http://raspberrypi.local:5000
```

---

### Manual Installation

For advanced users who prefer manual control.

#### Step 1: Update System

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

#### Step 2: Install System Dependencies

```bash
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    python3-dev \
    bluetooth \
    bluez \
    libbluetooth-dev \
    libglib2.0-dev \
    git \
    sqlite3 \
    curl
```

#### Step 3: Configure Bluetooth

```bash
# Unblock Bluetooth
sudo rfkill unblock bluetooth

# Enable and start service
sudo systemctl enable bluetooth
sudo systemctl start bluetooth

# Verify adapter is detected
hciconfig hci0
```

**Expected output:**
```
hci0:   Type: Primary  Bus: UART
        BD Address: XX:XX:XX:XX:XX:XX  ACL MTU: 1021:8  SCO MTU: 64:1
        UP RUNNING
```

#### Step 4: Clone Repository

```bash
# Navigate to installation directory
cd /opt

# Clone repository
sudo git clone https://github.com/RevEngine3r/BlueZscript.git

# Change ownership (optional)
sudo chown -R $USER:$USER BlueZscript

cd BlueZscript
```

#### Step 5: Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r raspberry-pi/requirements.txt
```

#### Step 6: Create Data Directories

```bash
cd raspberry-pi

# Create directories
mkdir -p data logs templates/static

# Set permissions
chmod 700 data
chmod 755 logs
```

#### Step 7: Generate Master Encryption Key

```bash
# Generate key using Python
python3 -c "
import os
from cryptography.fernet import Fernet

key_file = 'data/master.key'
if not os.path.exists(key_file):
    key = Fernet.generate_key()
    with open(key_file, 'wb') as f:
        f.write(key)
    os.chmod(key_file, 0o600)
    print('Master key generated')
"

# Secure the key
sudo chmod 600 data/master.key
sudo chown root:root data/master.key
```

#### Step 8: Configure Action Script

```bash
# Make action script executable
chmod +x action_script.sh

# Edit to customize actions
nano action_script.sh
```

**Example action script:**
```bash
#!/bin/bash
echo "[$(date)] Action triggered" >> logs/actions.log

# Your custom action here
# Example: Control GPIO, capture image, send notification, etc.
```

#### Step 9: Install Systemd Service

```bash
# Copy service file
sudo cp ble-listener-secure.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable ble-listener-secure
sudo systemctl start ble-listener-secure

# Check status
sudo systemctl status ble-listener-secure
```

#### Step 10: Start Web UI

```bash
# From raspberry-pi directory
../venv/bin/python3 web_ui.py
```

**For production deployment, consider using gunicorn:**
```bash
../venv/bin/pip install gunicorn
../venv/bin/gunicorn -w 2 -b 0.0.0.0:5000 web_ui:app
```

---

## Android App Installation

### Option 1: Install Pre-built APK

1. **Download APK**:
   - Visit [Releases](https://github.com/RevEngine3r/BlueZscript/releases)
   - Download latest `BlueZscript-v1.0.0.apk`

2. **Enable Unknown Sources** (if needed):
   - Settings → Security → Unknown Sources → Enable
   - Or: Settings → Apps → Special Access → Install Unknown Apps

3. **Install APK**:
   - Open downloaded APK file
   - Tap "Install"
   - Grant requested permissions

### Option 2: Build from Source

See [android-app/BUILDING.md](android-app/BUILDING.md) for detailed build instructions.

**Quick build:**
```bash
cd android-app
./gradlew assembleRelease

# APK location:
# app/build/outputs/apk/release/app-release.apk
```

---

## Initial Configuration

### 1. Access Web UI

Open browser and navigate to:
```
http://<raspberry-pi-ip>:5000
```

### 2. Generate Pairing QR Code

1. Click **"Pair New Device"** button
2. QR code will be displayed with device credentials
3. Keep this screen open for scanning

### 3. Pair Android Device

1. **Open BlueZscript app** on Android
2. **Tap "+" button** in bottom-right corner
3. **Grant permissions** when prompted:
   - Bluetooth
   - Location (required for BLE scanning)
   - Camera (for QR scanning)
4. **Scan QR code** displayed on web UI
5. **Enter device name** (e.g., "My Phone")
6. **Tap "Save"**

### 4. Test Connection

1. **Select paired device** from list
2. **Tap "Trigger" button**
3. **Check Raspberry Pi logs**:
   ```bash
   sudo journalctl -u ble-listener-secure -f
   ```
4. **Verify action executed**:
   ```bash
   cat /opt/BlueZscript/raspberry-pi/logs/actions.log
   ```

---

## Verification

### Check Services

```bash
# BLE listener status
sudo systemctl status ble-listener-secure

# View live logs
sudo journalctl -u ble-listener-secure -f

# Check Bluetooth
hciconfig hci0
bluetooth -v
```

### Run Unit Tests

```bash
cd /opt/BlueZscript
./venv/bin/python3 -m pytest tests/ -v
```

**Expected output:**
```
============= test session starts =============
collected 52 items

tests/test_crypto_utils.py ............ [16]
tests/test_pairing_manager.py ........... [14]
tests/test_web_ui.py .............. [12]
tests/test_ble_listener.py .......... [10]

============= 52 passed in 2.34s =============
```

### Manual BLE Test

```bash
# Run listener in foreground for debugging
cd /opt/BlueZscript/raspberry-pi
sudo ../venv/bin/python3 ble_listener_secure.py

# Should see:
# BLE Listener started...
# Waiting for connections...
```

### Check Web UI

```bash
# Test web UI endpoints
curl http://localhost:5000/api/devices

# Should return JSON array of paired devices
```

---

## Troubleshooting

For comprehensive troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

### Quick Fixes

#### Bluetooth Not Working
```bash
sudo rfkill unblock bluetooth
sudo systemctl restart bluetooth
sudo hciconfig hci0 up
```

#### Service Won't Start
```bash
# Check logs
sudo journalctl -u ble-listener-secure -n 50

# Check permissions
sudo chmod 600 /opt/BlueZscript/raspberry-pi/data/*.db
sudo chmod 600 /opt/BlueZscript/raspberry-pi/data/master.key
```

#### Python Dependencies Missing
```bash
cd /opt/BlueZscript
./venv/bin/pip install --force-reinstall -r raspberry-pi/requirements.txt
```

#### Android App Won't Connect
1. Check Bluetooth is enabled
2. Grant location permission (required for BLE)
3. Ensure Raspberry Pi BLE listener is running
4. Check devices are within range (~10 meters)

---

## Next Steps

- ✅ **Customize Actions**: Edit `action_script.sh` for your use case
- ✅ **Security**: Review [TROUBLESHOOTING.md](TROUBLESHOOTING.md#security-hardening)
- ✅ **Testing**: Follow [TESTING.md](TESTING.md) for comprehensive testing
- ✅ **Updates**: Star the repo for updates: [github.com/RevEngine3r/BlueZscript](https://github.com/RevEngine3r/BlueZscript)

---

## Support

- **Issues**: [GitHub Issues](https://github.com/RevEngine3r/BlueZscript/issues)
- **Discussions**: [GitHub Discussions](https://github.com/RevEngine3r/BlueZscript/discussions)
- **Author**: [@RevEngine3r](https://github.com/RevEngine3r)

---

**Installation complete! 🎉 Enjoy your secure BLE trigger system.**