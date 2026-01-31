# 🔧 Troubleshooting Guide

> **Solutions to common issues with BlueZscript**

## Table of Contents

- [Bluetooth Issues](#bluetooth-issues)
- [Service Issues](#service-issues)
- [Permission Errors](#permission-errors)
- [BLE Communication](#ble-communication)
- [Web UI Issues](#web-ui-issues)
- [Android App Issues](#android-app-issues)
- [Database Issues](#database-issues)
- [Performance Issues](#performance-issues)
- [Security Issues](#security-issues)

---

## Bluetooth Issues

### Bluetooth Not Working

**Symptoms:**
- `hciconfig: command not found`
- `No such device` error
- Bluetooth service not running

**Solutions:**

```bash
# 1. Install Bluetooth packages
sudo apt-get install -y bluetooth bluez libbluetooth-dev

# 2. Unblock Bluetooth (if blocked)
sudo rfkill unblock bluetooth

# 3. Enable and start Bluetooth service
sudo systemctl enable bluetooth
sudo systemctl start bluetooth

# 4. Bring up Bluetooth interface
sudo hciconfig hci0 up

# 5. Verify status
hciconfig -a
```

### Bluetooth Adapter Not Detected

**Check hardware:**
```bash
# List USB devices
lsusb | grep -i bluetooth

# Check kernel messages
sudo dmesg | grep -i bluetooth

# Check device status
rfkill list
```

**On Raspberry Pi:**
```bash
# Check if built-in BLE is enabled
sudo raspi-config
# Navigate to: Interface Options -> Bluetooth -> Enable
```

### BLE Advertisement Not Working

```bash
# Check if advertising is enabled
sudo hciconfig hci0 leadv

# Reset Bluetooth adapter
sudo hciconfig hci0 down
sudo hciconfig hci0 up

# Restart Bluetooth service
sudo systemctl restart bluetooth
```

---

## Service Issues

### Service Won't Start

**Check status:**
```bash
sudo systemctl status ble-listener-secure
```

**Common errors:**

#### 1. Python Module Not Found

**Error:**
```
ModuleNotFoundError: No module named 'bleak'
```

**Solution:**
```bash
cd /opt/BlueZscript
sudo ./venv/bin/pip install -r raspberry-pi/requirements.txt
```

#### 2. Permission Denied

**Error:**
```
Permission denied: '/opt/BlueZscript/raspberry-pi/data/pairing.db'
```

**Solution:**
```bash
sudo chmod 600 /opt/BlueZscript/raspberry-pi/data/pairing.db
sudo chown root:root /opt/BlueZscript/raspberry-pi/data/pairing.db
```

#### 3. Port Already in Use

**Error:**
```
OSError: [Errno 98] Address already in use
```

**Solution:**
```bash
# Find process using port 5000
sudo lsof -i :5000

# Kill process
sudo kill -9 <PID>

# Or change port in web_ui.py
sudo nano /opt/BlueZscript/raspberry-pi/web_ui.py
# Change: app.run(host="0.0.0.0", port=5001)
```

### Service Crashes/Restarts

**View recent crashes:**
```bash
sudo journalctl -u ble-listener-secure -p err -n 100
```

**Enable debug logging:**
```bash
# Edit service file
sudo nano /etc/systemd/system/ble-listener-secure.service

# Change ExecStart to:
ExecStart=/opt/BlueZscript/venv/bin/python3 /opt/BlueZscript/raspberry-pi/ble_listener_secure.py --debug

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart ble-listener-secure
```

### Service Not Auto-Starting on Boot

```bash
# Enable auto-start
sudo systemctl enable ble-listener-secure

# Verify enabled
sudo systemctl is-enabled ble-listener-secure

# Check boot logs
sudo journalctl -b | grep ble-listener
```

---

## Permission Errors

### Database Permission Denied

```bash
sudo chmod 600 /opt/BlueZscript/raspberry-pi/data/pairing.db
sudo chown root:root /opt/BlueZscript/raspberry-pi/data/pairing.db
```

### Action Script Not Executable

```bash
sudo chmod +x /opt/BlueZscript/raspberry-pi/action_script.sh
```

### Cannot Write to Log File

```bash
sudo mkdir -p /var/log
sudo touch /var/log/ble_listener.log
sudo chmod 644 /var/log/ble_listener.log
```

### Bluetooth Permission Denied

```bash
# Add user to bluetooth group
sudo usermod -a -G bluetooth $USER

# Or run service as root (already configured in systemd)
```

---

## BLE Communication

### Android Can't Find Raspberry Pi

**Check Raspberry Pi:**
```bash
# Verify BLE listener is running
sudo systemctl status ble-listener-secure

# Check if advertising
sudo hcitool lescan
```

**Check Android:**
- Enable Bluetooth
- Enable Location services (required for BLE scanning on Android)
- Grant app permissions (Bluetooth, Location)
- Ensure devices are within ~10 meters

### Connection Keeps Dropping

**Reduce interference:**
- Move away from WiFi routers (2.4GHz interferes with BLE)
- Reduce distance between devices
- Remove metal obstacles

**Check signal strength:**
```bash
# On Android (via logcat)
adb logcat | grep -i "rssi"
```

**Increase timeout:**
```python
# Edit raspberry-pi/ble_listener_secure.py
CONNECTION_TIMEOUT = 30  # Increase from default
```

### TOTP Validation Fails

**Check time synchronization:**
```bash
# On Raspberry Pi
sudo timedatectl set-ntp true
timedatectl status

# Sync time
sudo systemctl restart systemd-timesyncd
```

**On Android:**
- Settings → Date & Time → Enable "Automatic date & time"

**Time difference must be < 30 seconds for TOTP to work!**

### Message Not Received

**Check BLE service UUID:**
```python
# In ble_listener_secure.py
SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"

# Must match Android app configuration
```

**Enable verbose logging:**
```bash
# Run manually
sudo /opt/BlueZscript/venv/bin/python3 \
  /opt/BlueZscript/raspberry-pi/ble_listener_secure.py
```

---

## Web UI Issues

### Can't Access Web UI

**Check if running:**
```bash
# Check process
ps aux | grep web_ui

# Check port
sudo lsof -i :5000
```

**Test locally:**
```bash
curl http://localhost:5000
```

**Check firewall:**
```bash
# Allow port 5000
sudo ufw allow 5000/tcp

# Or disable firewall temporarily
sudo ufw disable
```

### QR Code Not Generating

**Check dependencies:**
```bash
./venv/bin/pip list | grep qrcode
./venv/bin/pip install qrcode[pil]
```

**Test manually:**
```python
import qrcode
qr = qrcode.make("test")
qr.save("test.png")
```

### 500 Internal Server Error

**Check logs:**
```bash
# Flask logs
sudo tail -f /var/log/bluezscript_webui.log

# Or run manually to see errors
cd /opt/BlueZscript/raspberry-pi
sudo ../venv/bin/python3 web_ui.py
```

**Check database:**
```bash
# Verify database exists and is writable
ls -la /opt/BlueZscript/raspberry-pi/data/pairing.db

# Test database connection
sqlite3 /opt/BlueZscript/raspberry-pi/data/pairing.db "SELECT * FROM devices;"
```

---

## Android App Issues

### App Won't Install

**Enable Unknown Sources:**
- Android 8+: Settings → Apps → Special Access → Install Unknown Apps → Enable for your file manager

**Check APK signature:**
```bash
# Verify APK integrity
jarsigner -verify -verbose app-release.apk
```

### App Crashes on Startup

**Check Android version:**
- Minimum: Android 8.0 (API 26)
- Check: Settings → About Phone → Android Version

**Check logs:**
```bash
# Connect phone via USB
adb logcat | grep -i "bluezscript"
```

### Permissions Not Granted

**Manually grant:**
- Settings → Apps → BlueZscript → Permissions
- Enable: Location, Bluetooth, Camera

**Location required for BLE scanning** (Android limitation)

### QR Scanner Not Working

**Check camera permission:**
- Settings → Apps → BlueZscript → Permissions → Camera

**Test camera:**
- Try other camera apps
- Restart device

**Clean camera lens:**
- Ensure QR code is well-lit and in focus

### Trigger Button Not Working

**Check Bluetooth:**
- Enable Bluetooth in Android settings
- Pair device first via QR code

**Check logs:**
```kotlin
// Enable verbose logging in app
Log.d("BlueZscript", "Trigger button pressed")
```

### Database Errors

**Clear app data:**
- Settings → Apps → BlueZscript → Storage → Clear Data
- Re-pair devices

**Reinstall app:**
```bash
adb uninstall com.revengine3r.bluezscript
adb install app-release.apk
```

---

## Database Issues

### Database Locked

```bash
# Check if database is in use
sudo lsof /opt/BlueZscript/raspberry-pi/data/pairing.db

# Stop service
sudo systemctl stop ble-listener-secure

# Remove lock file if exists
sudo rm /opt/BlueZscript/raspberry-pi/data/pairing.db-journal
```

### Database Corrupted

**Backup first:**
```bash
sudo cp /opt/BlueZscript/raspberry-pi/data/pairing.db \
  /opt/BlueZscript/raspberry-pi/data/pairing.db.backup
```

**Check integrity:**
```bash
sqlite3 /opt/BlueZscript/raspberry-pi/data/pairing.db "PRAGMA integrity_check;"
```

**Rebuild:**
```bash
# Export data
sqlite3 /opt/BlueZscript/raspberry-pi/data/pairing.db ".dump" > backup.sql

# Delete corrupted database
sudo rm /opt/BlueZscript/raspberry-pi/data/pairing.db

# Recreate
cd /opt/BlueZscript
sudo ./venv/bin/python3 -c "
from raspberry_pi.pairing_manager import PairingManager
pm = PairingManager()
print('Database recreated')
"

# Import data
sqlite3 /opt/BlueZscript/raspberry-pi/data/pairing.db < backup.sql
```

### Can't Read/Write Database

```bash
# Fix permissions
sudo chmod 600 /opt/BlueZscript/raspberry-pi/data/pairing.db
sudo chown root:root /opt/BlueZscript/raspberry-pi/data/pairing.db

# Fix directory permissions
sudo chmod 700 /opt/BlueZscript/raspberry-pi/data/
```

---

## Performance Issues

### High CPU Usage

```bash
# Check process
top -p $(pgrep -f ble_listener)

# Check for infinite loops in action script
sudo nano /opt/BlueZscript/raspberry-pi/action_script.sh
```

### High Memory Usage

```bash
# Check memory
free -h

# Monitor service
watch -n 1 'ps aux | grep ble_listener'

# Restart service
sudo systemctl restart ble-listener-secure
```

### Slow Response Time

**Check network latency:**
```bash
ping <raspberry-pi-ip>
```

**Reduce TOTP validation window:**
```python
# Edit crypto_utils.py
TOTP_WINDOW = 1  # Default: 1 (allows ±30s)
```

**Optimize action script:**
- Remove unnecessary delays
- Use background jobs for long-running tasks

---

## Security Issues

### Secrets Exposed in Logs

**Check logs:**
```bash
sudo journalctl -u ble-listener-secure | grep -i secret
```

**Should return nothing!**

**Fix if exposed:**
```bash
# Rotate logs
sudo journalctl --vacuum-time=1d

# Review code to ensure no secret logging
```

### Unauthorized Access

**Review paired devices:**
```bash
sqlite3 /opt/BlueZscript/raspberry-pi/data/pairing.db \
  "SELECT device_id, device_name, created_at FROM devices;"
```

**Remove suspicious devices:**
```bash
sqlite3 /opt/BlueZscript/raspberry-pi/data/pairing.db \
  "DELETE FROM devices WHERE device_id='<suspicious_id>';"
```

**Check authentication logs:**
```bash
sudo journalctl -u ble-listener-secure | grep -i "authentication"
```

### Master Key Lost

**Cannot recover encrypted secrets without master key!**

**If backed up:**
```bash
sudo cp /path/to/backup/master.key \
  /opt/BlueZscript/raspberry-pi/data/master.key
sudo chmod 600 /opt/BlueZscript/raspberry-pi/data/master.key
```

**If lost:**
- Delete database: `sudo rm /opt/BlueZscript/raspberry-pi/data/*`
- Re-pair all devices

---

## Common Error Messages

### "No BLE adapter found"

**Cause:** Bluetooth hardware not detected

**Solution:**
```bash
sudo systemctl restart bluetooth
sudo hciconfig hci0 up
```

### "TOTP validation failed"

**Cause:** Time mismatch between devices

**Solution:**
```bash
# Sync time on Raspberry Pi
sudo timedatectl set-ntp true

# Sync time on Android
# Settings → Date & Time → Automatic
```

### "Device not found in registry"

**Cause:** Device not paired or database issue

**Solution:**
- Re-pair device via QR code
- Check database:
  ```bash
  sqlite3 /opt/BlueZscript/raspberry-pi/data/pairing.db \
    "SELECT * FROM devices;"
  ```

### "Action script execution failed"

**Cause:** Script error or permission issue

**Solution:**
```bash
# Test script manually
sudo /opt/BlueZscript/raspberry-pi/action_script.sh

# Check permissions
sudo chmod +x /opt/BlueZscript/raspberry-pi/action_script.sh

# Check script syntax
sudo bash -n /opt/BlueZscript/raspberry-pi/action_script.sh
```

---

## Getting Help

### Collect Debug Information

```bash
#!/bin/bash
# debug_info.sh

echo "=== BlueZscript Debug Info ==="
echo

echo "--- System Info ---"
uname -a
cat /etc/os-release

echo
echo "--- Bluetooth Status ---"
sudo systemctl status bluetooth --no-pager
sudo hciconfig -a

echo
echo "--- Service Status ---"
sudo systemctl status ble-listener-secure --no-pager

echo
echo "--- Recent Logs ---"
sudo journalctl -u ble-listener-secure -n 50 --no-pager

echo
echo "--- Python Packages ---"
/opt/BlueZscript/venv/bin/pip list

echo
echo "--- Disk Space ---"
df -h

echo
echo "--- Permissions ---"
ls -la /opt/BlueZscript/raspberry-pi/data/
```

Run and save output:
```bash
chmod +x debug_info.sh
./debug_info.sh > debug_output.txt 2>&1
```

### Report Issues

1. Run debug script above
2. Create issue: [GitHub Issues](https://github.com/RevEngine3r/BlueZscript/issues)
3. Include:
   - Debug output
   - Expected behavior
   - Actual behavior
   - Steps to reproduce

### Community Support

- **GitHub Discussions**: [Start a discussion](https://github.com/RevEngine3r/BlueZscript/discussions)
- **Documentation**: [Wiki](https://github.com/RevEngine3r/BlueZscript/wiki)

---

## Still Having Issues?

1. Check [README.md](README.md) for basic setup
2. Review [INSTALL.md](INSTALL.md) for installation steps
3. Run tests: [TESTING.md](TESTING.md)
4. Search existing issues: [GitHub Issues](https://github.com/RevEngine3r/BlueZscript/issues)
5. Ask for help: [GitHub Discussions](https://github.com/RevEngine3r/BlueZscript/discussions)

---

**Most issues can be resolved by:**
1. Restarting the service
2. Checking Bluetooth status
3. Verifying file permissions
4. Syncing time between devices
5. Re-pairing devices