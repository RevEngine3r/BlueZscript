# 📦 Installation Guide

> **Complete setup guide for BlueZscript on Raspberry Pi and Android**

This guide covers both automated and manual installation methods.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Install (Automated)](#quick-install-automated)
- [Manual Installation](#manual-installation)
  - [Raspberry Pi Setup](#raspberry-pi-setup)
  - [Android App Installation](#android-app-installation)
- [Configuration](#configuration)
- [Verification](#verification)
- [Next Steps](#next-steps)

---

## Prerequisites

### Raspberry Pi
- **Hardware**: Raspberry Pi 4 Model B (or Pi 3B+ with BLE support)
- **OS**: Raspberry Pi OS (Bullseye or newer, 64-bit recommended)
- **Memory**: Minimum 1GB RAM
- **Storage**: Minimum 4GB available
- **Network**: WiFi or Ethernet for initial setup
- **Bluetooth**: Built-in BLE 4.0+ (included in Pi 4/3B+)

### Android Device
- **OS**: Android 8.0 (Oreo) or newer (API level 26+)
- **Bluetooth**: BLE 4.0+ support
- **Camera**: Required for QR code scanning
- **Storage**: 50MB available space
- **Permissions**: Location, Camera, Bluetooth

### Network Requirements
- Raspberry Pi and Android device on same network (for initial pairing)
- Port 5000 open for Web UI access (optional, can be changed)

---

## Quick Install (Automated)

### Raspberry Pi One-Line Installer

```bash
curl -fsSL https://raw.githubusercontent.com/RevEngine3r/BlueZscript/main/raspberry-pi/install.sh | sudo bash
```

**What it does:**
1. Installs system dependencies (Python, Bluetooth, etc.)
2. Clones repository to `/opt/BlueZscript`
3. Creates Python virtual environment
4. Installs Python packages
5. Sets up systemd service
6. Configures file permissions
7. Starts BLE listener service

**Installation time:** ~5-10 minutes (depending on network)

### Verify Installation

```bash
# Check service status
sudo systemctl status ble-listener-secure

# View logs
sudo journalctl -u ble-listener-secure -n 50 -f
```

You should see:
```
✓ BLE listener started successfully
✓ Waiting for BLE connections...
```

---

## Manual Installation

### Raspberry Pi Setup

#### 1. Update System

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

#### 2. Install System Dependencies

```bash
sudo apt-get install -y \
  python3 \
  python3-pip \
  python3-venv \
  bluetooth \
  bluez \
  libbluetooth-dev \
  git \
  sqlite3
```

#### 3. Enable Bluetooth Service

```bash
sudo systemctl enable bluetooth
sudo systemctl start bluetooth

# Verify Bluetooth is working
sudo hciconfig hci0 up
hciconfig -a
```

Expected output:
```
hci0:   Type: Primary  Bus: UART
        BD Address: XX:XX:XX:XX:XX:XX  ACL MTU: 1021:8  SCO MTU: 64:1
        UP RUNNING
```

#### 4. Clone Repository

```bash
sudo mkdir -p /opt
cd /opt
sudo git clone https://github.com/RevEngine3r/BlueZscript.git
cd BlueZscript
```

#### 5. Create Python Virtual Environment

```bash
sudo python3 -m venv venv
sudo ./venv/bin/pip install --upgrade pip setuptools wheel
```

#### 6. Install Python Dependencies

```bash
sudo ./venv/bin/pip install -r raspberry-pi/requirements.txt
```

**Dependencies installed:**
- `bleak` - BLE communication
- `pyotp` - TOTP generation
- `cryptography` - Fernet encryption
- `flask` - Web UI framework
- `qrcode` - QR code generation
- `pytest` - Testing framework

#### 7. Create Data Directory

```bash
sudo mkdir -p /opt/BlueZscript/raspberry-pi/data
sudo chmod 700 /opt/BlueZscript/raspberry-pi/data
```

#### 8. Run Initial Tests

```bash
cd /opt/BlueZscript
sudo ./venv/bin/python3 -m pytest tests/ -v
```

Expected: **52 tests passed** ✅

#### 9. Install Systemd Service

```bash
# Copy service file
sudo cp raspberry-pi/ble-listener-secure.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable auto-start on boot
sudo systemctl enable ble-listener-secure

# Start service
sudo systemctl start ble-listener-secure
```

#### 10. Verify Service Status

```bash
sudo systemctl status ble-listener-secure
```

Expected output:
```
● ble-listener-secure.service - BlueZscript Secure BLE Listener
   Loaded: loaded (/etc/systemd/system/ble-listener-secure.service; enabled)
   Active: active (running) since ...
```

#### 11. Start Web UI (Optional)

```bash
cd /opt/BlueZscript/raspberry-pi
sudo ../venv/bin/python3 web_ui.py
```

Access at: `http://<raspberry-pi-ip>:5000`

**Find Raspberry Pi IP:**
```bash
hostname -I
```

---

### Android App Installation

#### Option 1: Download Pre-built APK

1. Go to [Releases](https://github.com/RevEngine3r/BlueZscript/releases)
2. Download latest `BlueZscript-vX.X.X.apk`
3. On Android device:
   - Enable "Install from Unknown Sources" (Settings → Security)
   - Open APK file
   - Tap "Install"
   - Grant permissions when prompted

#### Option 2: Build from Source

See [android-app/BUILDING.md](android-app/BUILDING.md) for detailed build instructions.

**Quick build:**
```bash
cd android-app
./gradlew assembleRelease

# APK output at:
# app/build/outputs/apk/release/app-release.apk
```

---

## Configuration

### Customize Action Script

Edit the action script that executes when triggered:

```bash
sudo nano /opt/BlueZscript/raspberry-pi/action_script.sh
```

**Example 1: GPIO LED Control**
```bash
#!/bin/bash
echo "Triggering GPIO 17"
echo "17" > /sys/class/gpio/export
echo "out" > /sys/class/gpio/gpio17/direction
echo "1" > /sys/class/gpio/gpio17/value
sleep 2
echo "0" > /sys/class/gpio/gpio17/value
```

**Example 2: Home Assistant Integration**
```bash
#!/bin/bash
curl -X POST http://homeassistant.local:8123/api/services/light/toggle \
  -H "Authorization: Bearer YOUR_LONG_LIVED_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "light.living_room"}'
```

**Example 3: System Command**
```bash
#!/bin/bash
# Take a photo with Pi Camera
raspistill -o /home/pi/photos/capture_$(date +%s).jpg
```

**Make executable:**
```bash
sudo chmod +x /opt/BlueZscript/raspberry-pi/action_script.sh
```

### Web UI Port Configuration

Edit `raspberry-pi/web_ui.py` to change port (default: 5000):

```python
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
```

### Database Location

Default: `/opt/BlueZscript/raspberry-pi/data/pairing.db`

To change, edit `raspberry-pi/pairing_manager.py`:
```python
db_path = "/custom/path/pairing.db"
```

---

## Verification

### Test BLE Listener

```bash
# Stop service temporarily
sudo systemctl stop ble-listener-secure

# Run manually to see output
cd /opt/BlueZscript
sudo ./venv/bin/python3 raspberry-pi/ble_listener_secure.py
```

Expected output:
```
[INFO] BLE Listener started
[INFO] Advertising as: BlueZscript-XXXX
[INFO] Waiting for connections...
```

Press `Ctrl+C` to stop, then restart service:
```bash
sudo systemctl start ble-listener-secure
```

### Test Web UI

```bash
# Start web UI
cd /opt/BlueZscript/raspberry-pi
sudo ../venv/bin/python3 web_ui.py
```

Open browser: `http://<raspberry-pi-ip>:5000`

You should see:
- Device management dashboard
- "Pair New Device" button
- Empty device list (no devices paired yet)

### Test Action Script

```bash
# Run manually
sudo /opt/BlueZscript/raspberry-pi/action_script.sh
```

Verify your custom action executes correctly.

### Android App Verification

1. Open app
2. Grant required permissions:
   - ✅ Location (for BLE scanning)
   - ✅ Bluetooth
   - ✅ Camera (for QR scanning)
3. You should see empty device list
4. Tap "+" button - QR scanner should open

---

## Next Steps

### 1. Pair Your First Device

**On Raspberry Pi:**
1. Open Web UI: `http://<raspberry-pi-ip>:5000`
2. Click "Pair New Device"
3. QR code is displayed

**On Android:**
1. Open BlueZscript app
2. Tap "+" button
3. Scan QR code
4. Enter device name (e.g., "My Phone")
5. Tap "Save"

### 2. Test Trigger

1. Select device from list
2. Press "Trigger" button
3. Watch action execute on Raspberry Pi
4. Check logs:
   ```bash
   sudo journalctl -u ble-listener-secure -n 20
   ```

### 3. Monitoring and Logs

**Real-time logs:**
```bash
sudo journalctl -u ble-listener-secure -f
```

**Recent errors:**
```bash
sudo journalctl -u ble-listener-secure -p err -n 50
```

**Service restart:**
```bash
sudo systemctl restart ble-listener-secure
```

### 4. Security Hardening

```bash
# Restrict database permissions
sudo chmod 600 /opt/BlueZscript/raspberry-pi/data/pairing.db

# Restrict master key
sudo chmod 600 /opt/BlueZscript/raspberry-pi/data/master.key

# Set ownership
sudo chown root:root /opt/BlueZscript/raspberry-pi/data/*
```

### 5. Backup Configuration

```bash
# Backup database and keys
sudo tar -czf bluezscript-backup-$(date +%Y%m%d).tar.gz \
  /opt/BlueZscript/raspberry-pi/data/

# Store securely off-device
scp bluezscript-backup-*.tar.gz user@backup-server:/backups/
```

---

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.

**Quick checks:**

```bash
# Bluetooth status
sudo systemctl status bluetooth
sudo hciconfig hci0

# Service status
sudo systemctl status ble-listener-secure

# Disk space
df -h

# Python packages
/opt/BlueZscript/venv/bin/pip list
```

---

## Uninstallation

```bash
# Stop and disable service
sudo systemctl stop ble-listener-secure
sudo systemctl disable ble-listener-secure
sudo rm /etc/systemd/system/ble-listener-secure.service

# Remove files
sudo rm -rf /opt/BlueZscript

# Reload systemd
sudo systemctl daemon-reload
```

---

## Support

- **Issues**: [GitHub Issues](https://github.com/RevEngine3r/BlueZscript/issues)
- **Discussions**: [GitHub Discussions](https://github.com/RevEngine3r/BlueZscript/discussions)
- **Documentation**: [Project Wiki](https://github.com/RevEngine3r/BlueZscript/wiki)

---

**Installation complete! 🎉**

Return to [README.md](README.md) for usage instructions.