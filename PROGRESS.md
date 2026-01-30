# BlueZscript Development Progress

## Active Feature
**Feature**: Secure Pairing System with TOTP Authentication
**Status**: Backend Complete - Ready for Mobile App Development
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
- ✅ **STEP 4: Enhanced BLE Listener** (Completed 2026-01-31)
  - Rewrote ble_listener.py with TOTP authentication
  - Multi-layer validation: device exists, TOTP valid, timestamp fresh
  - JSON message parsing over BLE characteristic
  - Update last_used timestamp on successful auth
  - Comprehensive security logging (all auth attempts)
  - Statistics tracking (attempts, success, failures)
  - 10 comprehensive unit tests (all passing)
  - Updated systemd service file

## Current Step
**STEP 5**: Kotlin Compose Android App Structure

### Plan
- Create Android app with Kotlin + Jetpack Compose
- Material 3 design system
- Project structure: MVVM architecture
- Screens: Home, Pairing, Settings
- Navigation with Compose Navigation
- Dependency injection with Hilt

### Implementation Details
- **Package Structure**:
  ```
  com.revengine3r.bluezscript/
  ├── data/
  │   ├── local/      (Room database)
  │   ├── models/     (Data classes)
  │   └── repository/ (Repository pattern)
  ├── domain/
  │   └── usecases/   (Business logic)
  ├── presentation/
  │   ├── home/       (HomeScreen, HomeViewModel)
  │   ├── pairing/    (PairingScreen, PairingViewModel)
  │   ├── settings/   (SettingsScreen, SettingsViewModel)
  │   └── theme/      (Material 3 theme)
  └── utils/          (Helpers, extensions)
  ```
- **Dependencies**:
  - Jetpack Compose (UI)
  - Room (Local database)
  - Hilt (Dependency injection)
  - CameraX (QR scanning)
  - Accompanist (Permissions)
  - Material 3

### Next Steps (After STEP 5)
6. STEP 6: Android BLE client and TOTP integration
7. STEP 7: Testing, documentation, and deployment scripts

## Technical Stack

### Backend (Raspberry Pi)
- **Language**: Python 3.9+
- **Crypto**: PyOTP (TOTP), HMAC-SHA256, Fernet encryption
- **Database**: SQLite3 with encrypted secrets
- **BLE**: Bleak (async BLE library)
- **Web**: Flask + QR codes + Bootstrap 5

### Mobile (Android)
- **Language**: Kotlin
- **UI**: Jetpack Compose + Material 3
- **Architecture**: MVVM + Clean Architecture
- **BLE**: Android BLE APIs
- **Storage**: Room + Encrypted SharedPreferences

## Security Model
- **Layer 1**: BLE Secure Connections with bonding
- **Layer 2**: TOTP (30s window, ±1 period tolerance)
- **Layer 3**: Timestamp validation (5-minute replay protection)
- **Storage**: Fernet symmetric encryption for secrets at rest
- **Files**: 600 permissions on sensitive files
- **Web**: CSRF protection, rate limiting, secure headers
- **Logging**: All authentication attempts logged

## Test Coverage
- Crypto utilities: 16/16 tests passing
- Pairing manager: 14/14 tests passing
- Web UI: 12/12 tests passing
- BLE listener: 10/10 tests passing
- **Total**: 52 unit tests passing ✅

## Project Structure
```
BlueZscript/
├── raspberry-pi/
│   ├── crypto_utils.py            ✅ TOTP, HMAC, keys
│   ├── pairing_manager.py         ✅ Device storage
│   ├── web_ui.py                  ✅ Flask web interface
│   ├── ble_listener_secure.py     ✅ Secure BLE listener
│   ├── ble-listener-secure.service ✅ Systemd service
│   ├── requirements.txt           ✅
│   └── templates/                 ✅ HTML templates
├── tests/
│   ├── test_crypto_utils.py       ✅ 16 tests
│   ├── test_pairing_manager.py    ✅ 14 tests
│   ├── test_web_ui.py             ✅ 12 tests
│   └── test_ble_listener_secure.py ✅ 10 tests
├── android-app/                    🔜 Next
├── action_script.sh               ✅
└── ROAD_MAP/                       ✅
```

## Message Protocol

**BLE Message Format (JSON over characteristic):**
```json
{
  "device_id": "abc123def456",
  "totp": "123456",
  "timestamp": 1738267890,
  "action": "TRIGGER"
}
```

**Validation Flow:**
1. Parse JSON from BLE
2. Check device is paired (database lookup)
3. Validate TOTP against stored secret (±30s window)
4. Verify timestamp is fresh (< 5 minutes old)
5. Execute action if all checks pass
6. Update last_used timestamp
7. Log all attempts (success/failure)

## Deployment

**Raspberry Pi Services:**
- `ble-listener-secure.service` - BLE listener with auth
- `web-ui.service` - Flask web interface (optional)

**Configuration Files:**
- `~/.bluezscript/master.key` - Fernet master key (600)
- `/opt/BlueZscript/data/paired_devices.db` - SQLite (600)
- `/var/log/ble_listener_secure.log` - Security log

## Notes
- Backend (Raspberry Pi) is complete and ready for testing
- Web UI accessible at http://raspberry-pi:5000
- BLE listener validates all authentications before executing actions
- All secrets encrypted at rest using Fernet (AES-128-CBC)
- Comprehensive logging for security auditing
- Ready to begin Android app development

---
*Last Updated*: 2026-01-31 00:18 +0330
