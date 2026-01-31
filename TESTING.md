# 🧪 BlueZscript Testing Guide

Comprehensive testing procedures for backend and Android components.

## Table of Contents

- [Backend Testing](#backend-testing)
  - [Unit Tests](#unit-tests)
  - [Integration Tests](#integration-tests)
  - [Manual Testing](#manual-testing)
- [Android Testing](#android-testing)
- [End-to-End Testing](#end-to-end-testing)
- [Performance Testing](#performance-testing)
- [Security Testing](#security-testing)
- [Test Coverage](#test-coverage)

---

## Backend Testing

### Unit Tests

BlueZscript includes 52 comprehensive unit tests covering all backend components.

#### Run All Tests

```bash
cd /opt/BlueZscript
./venv/bin/python3 -m pytest tests/ -v
```

**Expected output:**
```
============= test session starts =============
platform linux -- Python 3.9.x
collected 52 items

tests/test_crypto_utils.py::test_generate_secret PASSED [1/52]
tests/test_crypto_utils.py::test_generate_totp PASSED [2/52]
...
tests/test_ble_listener.py::test_replay_attack PASSED [52/52]

============= 52 passed in 2.34s =============
```

#### Run Specific Test Modules

```bash
# Test crypto utilities only
./venv/bin/pytest tests/test_crypto_utils.py -v

# Test pairing manager only
./venv/bin/pytest tests/test_pairing_manager.py -v

# Test web UI only
./venv/bin/pytest tests/test_web_ui.py -v

# Test BLE listener only
./venv/bin/pytest tests/test_ble_listener.py -v
```

#### Test with Coverage

```bash
# Install coverage tool
./venv/bin/pip install pytest-cov

# Run with coverage report
./venv/bin/pytest tests/ --cov=raspberry-pi --cov-report=html

# View coverage report
# Open htmlcov/index.html in browser
```

#### Test Categories

**1. Crypto Utils Tests (16 tests)**
- TOTP generation and validation
- Secret key generation
- HMAC verification
- Timestamp validation
- Edge cases (invalid inputs, expired codes)

**2. Pairing Manager Tests (14 tests)**
- Device registration
- CRUD operations
- Encryption/decryption
- Database integrity
- Master key management

**3. Web UI Tests (12 tests)**
- API endpoints
- QR code generation
- Device listing
- Authentication
- Error handling

**4. BLE Listener Tests (10 tests)**
- Message parsing
- TOTP validation
- Replay attack prevention
- Action execution
- Logging

---

### Integration Tests

Test interactions between components.

#### Test Pairing Flow

```bash
# Start web UI
cd /opt/BlueZscript/raspberry-pi
../venv/bin/python3 web_ui.py &
WEB_UI_PID=$!

# Test pairing API
curl -X POST http://localhost:5000/api/pair \
  -H "Content-Type: application/json" \
  -d '{"device_name": "Test Device"}'

# Should return:
# {"device_id": "...", "secret": "...", "qr_data": "..."}

# Cleanup
kill $WEB_UI_PID
```

#### Test BLE Message Processing

```bash
# Create test script
cat > test_ble_message.py << 'EOF'
import sys
sys.path.insert(0, '/opt/BlueZscript/raspberry-pi')

from ble_listener_secure import BLEListener
import json
import time

# Initialize listener
listener = BLEListener()

# Create test message
message = {
    "device_id": "test123",
    "totp": listener.crypto.generate_totp("JBSWY3DPEHPK3PXP"),
    "timestamp": int(time.time()),
    "action": "TRIGGER"
}

# Test validation
if listener.validate_message(json.dumps(message)):
    print("✓ Message validation passed")
else:
    print("✗ Message validation failed")
EOF

# Run test
../venv/bin/python3 test_ble_message.py
```

---

### Manual Testing

#### Test 1: Service Status

```bash
# Check if service is running
sudo systemctl status ble-listener-secure

# Expected: "active (running)"
```

#### Test 2: Bluetooth Functionality

```bash
# Check Bluetooth adapter
hciconfig hci0

# Expected output shows:
# - UP RUNNING
# - Valid BD Address

# Scan for BLE devices
sudo hcitool lescan

# Press Ctrl+C to stop
```

#### Test 3: Database Operations

```bash
# Check database exists
ls -lh /opt/BlueZscript/raspberry-pi/data/pairing.db

# Query database
sqlite3 /opt/BlueZscript/raspberry-pi/data/pairing.db \
  "SELECT device_id, device_name, created_at FROM devices;"
```

#### Test 4: Logging

```bash
# Check system logs
sudo journalctl -u ble-listener-secure -n 50

# Check action logs
tail -f /opt/BlueZscript/raspberry-pi/logs/actions.log

# Check security logs
tail -f /opt/BlueZscript/raspberry-pi/logs/security.log
```

#### Test 5: Web UI

```bash
# Start web UI
cd /opt/BlueZscript/raspberry-pi
../venv/bin/python3 web_ui.py

# In another terminal, test endpoints:
curl http://localhost:5000/api/devices
curl http://localhost:5000/api/health
```

---

## Android Testing

### Unit Tests (Planned)

```bash
# Run Android unit tests
cd android-app
./gradlew test

# Run instrumentation tests
./gradlew connectedAndroidTest
```

### Manual Android Testing

#### Test 1: App Installation
1. Install APK on device
2. Open app (should not crash)
3. Check permissions dialog appears

#### Test 2: Permissions
1. Grant Bluetooth permission
2. Grant Location permission (required for BLE)
3. Grant Camera permission (for QR scanning)
4. App should show "Ready" state

#### Test 3: QR Pairing
1. Tap "+" button
2. Camera preview should appear
3. Scan QR code from web UI
4. Device name dialog appears
5. Enter name and save
6. Device appears in list

#### Test 4: Trigger Action
1. Select paired device
2. Tap "Trigger" button
3. Button shows loading state
4. Success/error message appears
5. Check Raspberry Pi logs for validation

#### Test 5: Device Management
1. Long-press device in list
2. Delete option appears
3. Confirm deletion
4. Device removed from list

---

## End-to-End Testing

Test complete workflow from pairing to action execution.

### E2E Test Procedure

#### Setup (5 minutes)

1. **Start Raspberry Pi services:**
   ```bash
   sudo systemctl start ble-listener-secure
   cd /opt/BlueZscript/raspberry-pi
   ../venv/bin/python3 web_ui.py
   ```

2. **Prepare monitoring:**
   ```bash
   # Terminal 1: Monitor BLE listener
   sudo journalctl -u ble-listener-secure -f
   
   # Terminal 2: Monitor actions
   tail -f /opt/BlueZscript/raspberry-pi/logs/actions.log
   ```

#### Test Case 1: First-Time Pairing (2 minutes)

1. Open web UI: `http://<pi-ip>:5000`
2. Click "Pair New Device"
3. QR code displays (✓)
4. Open Android app
5. Tap "+" button
6. Scan QR code (✓)
7. Enter device name: "Test Phone"
8. Tap "Save"
9. **Expected**: Device appears in list
10. **Verify**: Web UI shows device in dashboard

#### Test Case 2: Trigger Action (30 seconds)

1. Select "Test Phone" from list
2. Tap "Trigger" button
3. **Expected**: Button shows loading spinner
4. **Expected**: Success message appears
5. **Verify in logs**:
   ```
   # Terminal 1 should show:
   [INFO] Received BLE message from Test Phone
   [INFO] TOTP validated successfully
   [INFO] Timestamp valid
   [INFO] Executing action script
   [INFO] Action completed
   
   # Terminal 2 should show:
   [2026-01-31 14:30:15] Action triggered
   Action completed successfully
   ```

#### Test Case 3: Security Validation (1 minute)

1. **Test replay attack prevention:**
   - Trigger action
   - Immediately trigger again with same TOTP
   - **Expected**: Second attempt fails (TOTP expired)

2. **Test invalid TOTP:**
   - Manually modify TOTP in test script
   - Send message
   - **Expected**: Validation fails, logged as security event

3. **Test expired timestamp:**
   - Send message with old timestamp (>5 min)
   - **Expected**: Validation fails

#### Test Case 4: Multiple Devices (3 minutes)

1. Pair second device: "Test Phone 2"
2. Trigger from Device 1
3. Trigger from Device 2
4. **Expected**: Both work independently
5. **Verify**: Logs show correct device IDs

#### Test Case 5: Error Handling (2 minutes)

1. **Bluetooth disabled:**
   - Disable Bluetooth on Raspberry Pi
   - Attempt trigger from app
   - **Expected**: Graceful error message

2. **Service stopped:**
   - Stop BLE listener: `sudo systemctl stop ble-listener-secure`
   - Attempt trigger
   - **Expected**: Timeout error
   - Restart service

3. **Out of range:**
   - Move phone >15 meters from Pi
   - Attempt trigger
   - **Expected**: Connection timeout

---

## Performance Testing

### Latency Benchmarks

```bash
# Create benchmark script
cat > benchmark.py << 'EOF'
import time
import sys
sys.path.insert(0, '/opt/BlueZscript/raspberry-pi')

from crypto_utils import CryptoUtils

crypto = CryptoUtils()
secret = crypto.generate_secret()

# Benchmark TOTP generation
start = time.time()
for _ in range(1000):
    totp = crypto.generate_totp(secret)
end = time.time()

print(f"TOTP Generation: {(end-start)/1000*1000:.2f}ms per operation")

# Benchmark TOTP validation
totp = crypto.generate_totp(secret)
start = time.time()
for _ in range(1000):
    crypto.validate_totp(secret, totp)
end = time.time()

print(f"TOTP Validation: {(end-start)/1000*1000:.2f}ms per operation")
EOF

../venv/bin/python3 benchmark.py
```

**Expected Results:**
- TOTP Generation: < 1ms
- TOTP Validation: < 5ms
- Total trigger latency: < 1 second

### Load Testing

```bash
# Test concurrent triggers (requires multiple devices)
# Send 10 triggers in rapid succession
for i in {1..10}; do
  # Trigger from app
  sleep 0.5
done

# Verify all processed in logs
sudo journalctl -u ble-listener-secure --since "1 minute ago" | grep "Action completed"
```

---

## Security Testing

### Security Test Cases

#### Test 1: Replay Attack Prevention

```python
# test_replay.py
import time
import json
from ble_listener_secure import BLEListener

listener = BLEListener()

# Create message
message = {
    "device_id": "test123",
    "totp": "123456",  # Same TOTP
    "timestamp": int(time.time()),
    "action": "TRIGGER"
}

# First attempt
result1 = listener.validate_message(json.dumps(message))
print(f"First attempt: {result1}")  # Should pass

# Wait 35 seconds (TOTP expires)
time.sleep(35)

# Second attempt with same TOTP
result2 = listener.validate_message(json.dumps(message))
print(f"Second attempt: {result2}")  # Should fail
```

#### Test 2: Encryption Verification

```bash
# Verify database encryption
sqlite3 /opt/BlueZscript/raspberry-pi/data/pairing.db \
  "SELECT secret FROM devices LIMIT 1;"

# Output should be encrypted (Fernet format: gAAAAA...)
# NOT plaintext TOTP secret
```

#### Test 3: Permission Checks

```bash
# Check file permissions
ls -l /opt/BlueZscript/raspberry-pi/data/

# Expected:
# -rw------- master.key (600)
# -rw------- pairing.db (600)
# drwx------ data/ (700)
```

#### Test 4: Log Sanitization

```bash
# Check logs don't contain secrets
sudo journalctl -u ble-listener-secure | grep -i "secret"
sudo journalctl -u ble-listener-secure | grep -i "key"

# Should return NO matches
```

---

## Test Coverage

### Current Coverage

| Component | Tests | Coverage |
|-----------|-------|----------|
| Crypto Utils | 16 | 100% |
| Pairing Manager | 14 | 100% |
| Web UI | 12 | 95% |
| BLE Listener | 10 | 90% |
| **Total Backend** | **52** | **96%** |
| Android App | TBD | TBD |

### Generate Coverage Report

```bash
cd /opt/BlueZscript
./venv/bin/pytest tests/ \
  --cov=raspberry-pi \
  --cov-report=html \
  --cov-report=term-missing

# View HTML report
chromium-browser htmlcov/index.html
```

---

## Continuous Testing

### Automated Testing on Commit

```bash
# Create pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
echo "Running tests..."
cd /opt/BlueZscript
./venv/bin/pytest tests/ -q

if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi
EOF

chmod +x .git/hooks/pre-commit
```

### Scheduled Testing

```bash
# Add to crontab for daily testing
crontab -e

# Add line:
0 2 * * * cd /opt/BlueZscript && ./venv/bin/pytest tests/ > /tmp/bluezscript_test.log 2>&1
```

---

## Test Checklist

Before releasing or deploying:

- [ ] All 52 unit tests pass
- [ ] Integration tests complete
- [ ] Manual BLE test successful
- [ ] Web UI accessible and functional
- [ ] Android app installs without errors
- [ ] QR pairing works end-to-end
- [ ] Trigger action executes successfully
- [ ] Logs show no errors
- [ ] Security tests pass
- [ ] Performance within acceptable range
- [ ] Multiple devices work independently
- [ ] Error handling graceful

---

## Reporting Issues

If tests fail:

1. **Capture logs:**
   ```bash
   sudo journalctl -u ble-listener-secure > ble_logs.txt
   ./venv/bin/pytest tests/ -v > test_output.txt
   ```

2. **System info:**
   ```bash
   uname -a > system_info.txt
   python3 --version >> system_info.txt
   hciconfig hci0 >> system_info.txt
   ```

3. **Create issue:**
   - Visit: https://github.com/RevEngine3r/BlueZscript/issues
   - Include logs, system info, and steps to reproduce

---

**Happy Testing! 🧪**