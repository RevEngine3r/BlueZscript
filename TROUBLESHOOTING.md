# 🔧 BlueZscript Troubleshooting Guide

Common issues and their solutions.

## Table of Contents

- [Quick Diagnostics](#quick-diagnostics)
- [Installation Issues](#installation-issues)
- [Bluetooth Problems](#bluetooth-problems)
- [Service Issues](#service-issues)
- [Pairing Problems](#pairing-problems)
- [Android App Issues](#android-app-issues)
- [Performance Issues](#performance-issues)
- [Security Issues](#security-issues)
- [Advanced Debugging](#advanced-debugging)

---

## Quick Diagnostics

Run this comprehensive diagnostic script to identify common issues:

```bash
#!/bin/bash
echo "=== BlueZscript Diagnostics ==="
echo ""

echo "1. System Info:"
uname -a
cat /etc/os-release | grep PRETTY_NAME
echo ""

echo "2. Python Version:"
python3 --version
echo ""

echo "3. Bluetooth Status:"
hciconfig hci0 2>&1 || echo "Bluetooth adapter not found"
systemctl status bluetooth --no-pager -l
echo ""

echo "4. Service Status:"
systemctl status ble-listener-secure --no-pager -l
echo ""

echo "5. File Permissions:"
ls -la /opt/BlueZscript/raspberry-pi/data/ 2>/dev/null || echo "Data directory not found"
echo ""

echo "6. Recent Logs:"
journalctl -u ble-listener-secure -n 20 --no-pager
echo ""

echo "7. Network:"
hostname -I
echo ""

echo "=== End Diagnostics ==="
```

Save as `diagnose.sh`, make executable, and run:
```bash
chmod +x diagnose.sh
sudo ./diagnose.sh > diagnostic_report.txt
```

---

## Installation Issues

### Issue: "Permission Denied" During Installation

**Symptoms:**
```
bash: ./install.sh: Permission denied
```

**Solution:**
```bash
# Make script executable
chmod +x install.sh

# Run with sudo
sudo ./install.sh
```

---

### Issue: Python Version Too Old

**Symptoms:**
```
ERROR: Python 3.9 or higher is required (found 3.7)
```

**Solution:**
```bash
# Update Raspberry Pi OS first
sudo apt-get update
sudo apt-get upgrade -y

# If still old, install Python 3.9+
sudo apt-get install -y python3.9 python3.9-venv python3.9-dev

# Update alternatives
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1
```

---

### Issue: pip Install Fails

**Symptoms:**
```
ERROR: Could not build wheels for cryptography
```

**Solution:**
```bash
# Install build dependencies
sudo apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    cargo

# Retry installation
cd /opt/BlueZscript
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r raspberry-pi/requirements.txt
```

---

### Issue: Git Clone Fails

**Symptoms:**
```
fatal: unable to access 'https://github.com/...': Could not resolve host
```

**Solution:**
```bash
# Check network connectivity
ping -c 3 github.com

# If network is down, check Wi-Fi/Ethernet
sudo ifconfig

# Try alternative clone method
git clone https://github.com/RevEngine3r/BlueZscript.git
```

---

## Bluetooth Problems

### Issue: Bluetooth Adapter Not Found

**Symptoms:**
```
hciconfig: command not found
# OR
Can't get device info: No such device
```

**Solution:**
```bash
# Install Bluetooth tools
sudo apt-get install -y bluetooth bluez bluez-tools

# Check if adapter is blocked
sudo rfkill list

# Unblock Bluetooth
sudo rfkill unblock bluetooth

# Restart Bluetooth service
sudo systemctl restart bluetooth

# Verify adapter
hciconfig hci0 up
hciconfig hci0
```

---

### Issue: Bluetooth Service Won't Start

**Symptoms:**
```
Failed to start bluetooth.service: Unit bluetooth.service not found
```

**Solution:**
```bash
# Reinstall Bluetooth stack
sudo apt-get remove --purge bluez
sudo apt-get install -y bluez bluetooth

# Enable and start service
sudo systemctl enable bluetooth
sudo systemctl start bluetooth

# Check status
sudo systemctl status bluetooth
```

---

### Issue: "Resource Busy" Error

**Symptoms:**
```
Can't init device hci0: Device or resource busy (16)
```

**Solution:**
```bash
# Kill processes using Bluetooth
sudo killall bluetoothd

# Restart Bluetooth
sudo systemctl restart bluetooth

# Reset adapter
sudo hciconfig hci0 down
sudo hciconfig hci0 up
```

---

## Service Issues

### Issue: Service Fails to Start

**Symptoms:**
```
Job for ble-listener-secure.service failed
```

**Solution 1: Check Logs**
```bash
# View detailed error
sudo journalctl -u ble-listener-secure -n 50 --no-pager

# Common errors and fixes:
# - "Permission denied": Check file permissions
# - "Module not found": Reinstall dependencies
# - "Bluetooth adapter not found": Fix Bluetooth (see above)
```

**Solution 2: Fix Permissions**
```bash
cd /opt/BlueZscript/raspberry-pi

# Fix data directory
sudo chmod 700 data
sudo chmod 600 data/*
sudo chown root:root data/master.key

# Fix executable
chmod +x ble_listener_secure.py
chmod +x action_script.sh
```

**Solution 3: Reinstall Service**
```bash
# Stop service
sudo systemctl stop ble-listener-secure

# Reinstall service file
sudo cp /opt/BlueZscript/raspberry-pi/ble-listener-secure.service \
     /etc/systemd/system/

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl start ble-listener-secure
```

---

### Issue: Service Starts But Doesn't Work

**Symptoms:**
```
service is active (running) but triggers don't work
```

**Solution:**
```bash
# Check if service is actually listening
sudo journalctl -u ble-listener-secure -f

# Should see:
# "BLE Listener started..."
# "Waiting for connections..."

# If not, check Python errors:
sudo systemctl status ble-listener-secure -l

# Test manually
cd /opt/BlueZscript/raspberry-pi
sudo ../venv/bin/python3 ble_listener_secure.py

# Watch for errors
```

---

## Pairing Problems

### Issue: QR Code Not Displaying

**Symptoms:**
Web UI shows error when generating QR code

**Solution:**
```bash
# Check if qrcode library is installed
cd /opt/BlueZscript
./venv/bin/pip show qrcode

# If not found, install:
./venv/bin/pip install qrcode[pil]

# Restart web UI
pkill -f web_ui.py
./venv/bin/python3 raspberry-pi/web_ui.py
```

---

### Issue: Web UI Not Accessible

**Symptoms:**
```
Cannot connect to http://raspberrypi:5000
```

**Solution:**
```bash
# Check if web UI is running
ps aux | grep web_ui.py

# If not running, start it:
cd /opt/BlueZscript/raspberry-pi
../venv/bin/python3 web_ui.py

# Check firewall
sudo ufw status
sudo ufw allow 5000/tcp  # If firewall is active

# Find IP address
hostname -I

# Access using IP instead of hostname:
# http://<IP-ADDRESS>:5000
```

---

### Issue: "Device Already Exists" Error

**Symptoms:**
Cannot pair new device with same name

**Solution:**
```bash
# List existing devices
sqlite3 /opt/BlueZscript/raspberry-pi/data/pairing.db \
  "SELECT device_id, device_name FROM devices;"

# Delete old device
sqlite3 /opt/BlueZscript/raspberry-pi/data/pairing.db \
  "DELETE FROM devices WHERE device_name='OLD_NAME';"

# Or use web UI to delete device
```

---

## Android App Issues

### Issue: App Won't Install

**Symptoms:**
```
App not installed
# OR
Parsing error
```

**Solution:**
1. **Enable Unknown Sources:**
   - Settings → Security → Unknown Sources → Enable
   - Or: Settings → Apps → Special Access → Install Unknown Apps

2. **Check Android Version:**
   - Requires Android 8.0+ (API 26+)
   - Settings → About Phone → Android Version

3. **Re-download APK:**
   - File may be corrupted
   - Download again from releases

4. **Clear Package Installer Cache:**
   - Settings → Apps → Package Installer → Storage → Clear Cache

---

### Issue: "Bluetooth Permission Denied"

**Symptoms:**
App crashes when trying to scan or connect

**Solution:**
```
1. Open Settings
2. Apps → BlueZscript → Permissions
3. Enable:
   - Bluetooth
   - Location (REQUIRED for BLE scanning)
   - Camera (for QR scanning)
4. Restart app
```

**Note:** Location permission is required by Android for BLE scanning, even though the app doesn't use GPS.

---

### Issue: QR Scanner Not Working

**Symptoms:**
Camera preview is black or doesn't scan QR code

**Solution:**
1. **Grant Camera Permission:**
   - Settings → Apps → BlueZscript → Permissions → Camera → Allow

2. **Check Camera Access:**
   - Close other apps using camera
   - Restart device

3. **Manual Entry (Workaround):**
   - Copy device_id and secret from web UI
   - Enter manually in app (if feature available)

---

### Issue: "Cannot Connect to Device"

**Symptoms:**
App shows "Connection failed" when triggering

**Solution:**
1. **Check Bluetooth:**
   - Enable Bluetooth on phone
   - Settings → Bluetooth → On

2. **Check Distance:**
   - Move closer to Raspberry Pi (<10 meters)
   - Remove obstacles

3. **Check BLE Service:**
   ```bash
   # On Raspberry Pi
   sudo systemctl status ble-listener-secure
   sudo journalctl -u ble-listener-secure -f
   ```

4. **Restart Bluetooth:**
   - Toggle Bluetooth off/on
   - Or reboot phone

5. **Re-pair Device:**
   - Delete device in app
   - Scan QR code again

---

### Issue: TOTP Validation Fails

**Symptoms:**
Logs show "Invalid TOTP" errors

**Solution:**
1. **Check Time Sync:**
   ```bash
   # On Raspberry Pi
   date
   
   # On Android
   # Settings → Date & Time → Use network-provided time
   ```

2. **Synchronize Time:**
   ```bash
   # On Raspberry Pi
   sudo apt-get install -y ntpdate
   sudo ntpdate -s time.nist.gov
   
   # Enable automatic time sync
   sudo timedatectl set-ntp true
   ```

3. **Verify TOTP Window:**
   - Default is 30 seconds with ±1 window tolerance
   - Time difference must be < 60 seconds

---

## Performance Issues

### Issue: Slow Trigger Response

**Symptoms:**
Trigger takes >5 seconds to execute

**Solution:**
1. **Check CPU Load:**
   ```bash
   top
   # If CPU >80%, identify and kill heavy processes
   ```

2. **Check BLE Range:**
   - Move closer to Raspberry Pi
   - Optimal range: <5 meters

3. **Optimize Action Script:**
   ```bash
   # Time your action script
   time /opt/BlueZscript/raspberry-pi/action_script.sh
   
   # Should complete in <1 second
   # If slow, optimize script
   ```

4. **Check Logs for Delays:**
   ```bash
   sudo journalctl -u ble-listener-secure | grep -i "delay\|timeout"
   ```

---

### Issue: High CPU Usage

**Symptoms:**
```
ble_listener_secure.py using >50% CPU constantly
```

**Solution:**
```bash
# Check for infinite loops in logs
sudo journalctl -u ble-listener-secure -n 100

# Restart service
sudo systemctl restart ble-listener-secure

# If persists, check for BLE interference:
sudo hcitool lescan  # Should not show thousands of devices

# If many devices found, filter in code or change location
```

---

## Security Issues

### Issue: Master Key Missing

**Symptoms:**
```
FileNotFoundError: data/master.key
```

**Solution:**
```bash
cd /opt/BlueZscript/raspberry-pi

# Generate new master key
python3 -c "
from cryptography.fernet import Fernet
import os

key = Fernet.generate_key()
os.makedirs('data', exist_ok=True)
with open('data/master.key', 'wb') as f:
    f.write(key)
os.chmod('data/master.key', 0o600)
print('Master key generated')
"

# Secure permissions
sudo chmod 600 data/master.key
sudo chown root:root data/master.key
```

**Warning:** This will invalidate all existing pairings. Re-pair all devices.

---

### Issue: Database Corruption

**Symptoms:**
```
sqlite3.DatabaseError: database disk image is malformed
```

**Solution:**
```bash
cd /opt/BlueZscript/raspberry-pi/data

# Backup corrupted database
sudo cp pairing.db pairing.db.backup

# Attempt repair
sqlite3 pairing.db "PRAGMA integrity_check;"

# If repair fails, recreate:
sudo rm pairing.db
sudo systemctl restart ble-listener-secure

# Note: All devices will need to be re-paired
```

---

### Issue: Replay Attack Detected

**Symptoms:**
Logs show repeated "Replay attack detected" warnings

**Solution:**
This is normal security behavior. If you see this:

1. **Legitimate Re-triggers:**
   - Wait 30+ seconds between triggers
   - TOTP codes expire every 30 seconds

2. **Clock Skew:**
   ```bash
   # Sync time on both devices
   sudo ntpdate -s time.nist.gov
   ```

3. **Actual Attack:**
   - Check logs for suspicious device IDs
   - Remove compromised devices
   - Regenerate master key

---

## Advanced Debugging

### Enable Debug Logging

```bash
# Edit service file
sudo nano /etc/systemd/system/ble-listener-secure.service

# Change ExecStart line to:
ExecStart=/opt/BlueZscript/venv/bin/python3 -u /opt/BlueZscript/raspberry-pi/ble_listener_secure.py --debug

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart ble-listener-secure

# View verbose logs
sudo journalctl -u ble-listener-secure -f
```

---

### Packet Capture

```bash
# Capture BLE packets (requires btmon)
sudo apt-get install -y bluez-tools

# Start monitoring
sudo btmon > ble_capture.log

# In another terminal, trigger action

# Stop capture (Ctrl+C)
# Analyze ble_capture.log
```

---

### Database Inspection

```bash
# Open database
sqlite3 /opt/BlueZscript/raspberry-pi/data/pairing.db

# Useful queries:
.schema devices
SELECT * FROM devices;
SELECT device_id, device_name, created_at FROM devices;

# Check for duplicates
SELECT device_name, COUNT(*) FROM devices GROUP BY device_name HAVING COUNT(*) > 1;

# Exit
.quit
```

---

### Python Interactive Debugging

```bash
cd /opt/BlueZscript/raspberry-pi

# Start Python REPL
../venv/bin/python3

# Test components:
>>> from crypto_utils import CryptoUtils
>>> crypto = CryptoUtils()
>>> secret = crypto.generate_secret()
>>> totp = crypto.generate_totp(secret)
>>> print(f"TOTP: {totp}")
>>> crypto.validate_totp(secret, totp)
True
>>> quit()
```

---

## Getting Help

If none of these solutions work:

1. **Gather Information:**
   ```bash
   # Run diagnostics
   sudo /opt/BlueZscript/diagnose.sh > report.txt
   
   # Capture logs
   sudo journalctl -u ble-listener-secure > service_logs.txt
   
   # System info
   uname -a > system_info.txt
   ```

2. **Create GitHub Issue:**
   - Visit: https://github.com/RevEngine3r/BlueZscript/issues
   - Use issue template
   - Attach report.txt and logs
   - Describe steps to reproduce

3. **Community Support:**
   - GitHub Discussions: https://github.com/RevEngine3r/BlueZscript/discussions
   - Include error messages and context

---

## Security Hardening (Optional)

### Recommended Security Practices

```bash
# 1. Change default port for web UI
cd /opt/BlueZscript/raspberry-pi
nano web_ui.py
# Change: app.run(host='0.0.0.0', port=5000)
# To:     app.run(host='0.0.0.0', port=8443)

# 2. Enable firewall
sudo apt-get install -y ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 8443/tcp  # Web UI port
sudo ufw enable

# 3. Restrict web UI to local network
nano web_ui.py
# Change: app.run(host='0.0.0.0', ...)
# To:     app.run(host='127.0.0.1', ...)  # Local only

# 4. Regular updates
sudo apt-get update && sudo apt-get upgrade -y
cd /opt/BlueZscript && git pull
./venv/bin/pip install --upgrade -r raspberry-pi/requirements.txt

# 5. Monitor logs for suspicious activity
sudo journalctl -u ble-listener-secure | grep -i "failed\|invalid\|attack"
```

---

**Still stuck? We're here to help! 💚**