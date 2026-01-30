# BlueZscript Development Progress

## Active Feature
**Feature**: Secure Pairing System with TOTP Authentication
**Status**: In Progress - Backend Complete, Moving to BLE Integration
**Started**: 2026-01-30

## Completed Steps
- ✅ Initial repository setup
- ✅ Basic BLE listener implementation
- ✅ Action script framework
- ✅ Systemd service configuration
- ✅ Project structure and roadmap planning
- ✅ **STEP 1: Crypto Utilities** (Completed 2026-01-30)
  - CryptoUtils class with TOTP, HMAC, key generation
  - 16 comprehensive unit tests (all passing)
  - Security: constant-time comparison, CSPRNG
- ✅ **STEP 2: Pairing Manager** (Completed 2026-01-31)
  - PairingManager class with SQLite database
  - Fernet encryption for secrets at rest
  - CRUD operations with master key management
  - 14 comprehensive unit tests (all passing)
- ✅ **STEP 3: Flask WebUI** (Completed 2026-01-31)
  - Flask web application with responsive Bootstrap 5 UI
  - QR code generation for device pairing
  - Admin dashboard: view/manage paired devices
  - RESTful API: /api/devices, /api/qr, /api/stats
  - Security: CSRF protection, rate limiting, secure headers
  - 12 comprehensive unit tests (all passing)

## Current Step
**STEP 4**: Enhanced BLE Listener with TOTP Validation

### Plan
- Enhance existing `ble_listener.py` with TOTP validation
- Integrate PairingManager for device verification
- Validate incoming BLE messages against paired devices
- Update last_used timestamp on successful auth
- Comprehensive logging for security events

### Implementation Details
- **Message Format**: JSON over BLE characteristic
  ```json
  {
    "device_id": "abc123",
    "totp": "123456",
    "timestamp": 1738267890,
    "action": "TRIGGER"
  }
  ```
- **Validation Flow**:
  1. Parse BLE message
  2. Check device is paired (PairingManager)
  3. Validate TOTP against stored secret
  4. Verify timestamp freshness (5-minute window)
  5. Execute action if all checks pass
  6. Update last_used timestamp
- **Security**: Log all auth attempts (success/failure)

### Next Steps (After STEP 4)
5. STEP 5: Kotlin Compose Android app structure
6. STEP 6: Android BLE client and TOTP integration
7. STEP 7: Testing, documentation, and deployment scripts

## Technical Stack
- **Backend**: Python 3.9+
- **Crypto**: PyOTP (TOTP), HMAC-SHA256, Fernet encryption
- **Database**: SQLite3 with encrypted secrets
- **BLE**: Bleak (async BLE library)
- **Web UI**: Flask + QR codes + Bootstrap 5
- **Mobile**: Kotlin + Jetpack Compose (Android) - upcoming

## Security Model
- **Layer 1**: BLE Secure Connections with bonding
- **Layer 2**: TOTP (30s window, ±1 period tolerance)
- **Layer 3**: Timestamp validation (5-minute replay protection)
- **Storage**: Fernet symmetric encryption for secrets at rest
- **Files**: 600 permissions on sensitive files
- **Web**: CSRF protection, rate limiting, secure headers

## Test Coverage
- Crypto utilities: 16/16 tests passing
- Pairing manager: 14/14 tests passing
- Web UI: 12/12 tests passing
- **Total**: 42 unit tests passing

## Project Structure
```
BlueZscript/
├── raspberry-pi/
│   ├── crypto_utils.py         ✅ TOTP, HMAC, keys
│   ├── pairing_manager.py      ✅ Device storage
│   ├── web_ui.py               ✅ Flask web interface
│   ├── ble_listener.py         🔄 Needs enhancement
│   ├── requirements.txt        ✅
│   └── templates/              ✅ HTML templates
├── tests/
│   ├── test_crypto_utils.py    ✅ 16 tests
│   ├── test_pairing_manager.py ✅ 14 tests
│   └── test_web_ui.py          ✅ 12 tests
├── action_script.sh         ✅
├── ble-listener.service     🔄 Needs update
└── ROAD_MAP/                ✅
```

## Notes
- Web UI accessible at http://raspberry-pi:5000
- QR codes contain device_id + secret in JSON format
- Database uses soft delete for audit trail
- Master encryption key: ~/.bluezscript/master.key
- All secrets encrypted at rest using Fernet (AES-128-CBC)
- Rate limiting: 1 pairing request per minute per IP

---
*Last Updated*: 2026-01-31 00:13 +0330
