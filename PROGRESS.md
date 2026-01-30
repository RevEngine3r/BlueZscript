# BlueZscript Development Progress

## Active Feature
**Feature**: Secure Pairing System with TOTP Authentication
**Status**: Backend Complete - Mobile App in Progress
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
- ✅ **STEP 2: Pairing Manager** (Completed 2026-01-31)
  - PairingManager class with SQLite database
  - Fernet encryption for secrets at rest
  - CRUD operations with master key management
  - 14 comprehensive unit tests (all passing)
- ✅ **STEP 3: Flask WebUI** (Completed 2026-01-31)
  - Flask web application with Bootstrap 5 UI
  - QR code generation for device pairing
  - Admin dashboard with RESTful API
  - 12 comprehensive unit tests (all passing)
- ✅ **STEP 4: Enhanced BLE Listener** (Completed 2026-01-31)
  - Multi-layer TOTP validation
  - JSON message parsing over BLE
  - Comprehensive security logging
  - 10 comprehensive unit tests (all passing)
- ✅ **STEP 5: Android App Structure** (Completed 2026-01-31)
  - Kotlin + Jetpack Compose project setup
  - MVVM + Clean Architecture
  - Material 3 design system
  - Navigation graph (Home, Pairing, Settings)
  - Room database schema
  - Data models and repository interfaces
  - Dependency injection (Hilt)
  - Theme with dynamic colors

## Current Step
**STEP 6**: Android BLE Client and TOTP Integration

### Plan
- Implement ViewModels for all screens
- BLE service for communication with Raspberry Pi
- TOTP generation using kotlin-onetimepassword
- QR code scanner with CameraX + ML Kit
- Device pairing flow (scan QR → save device)
- Trigger button with BLE message sending
- Permission handling (Bluetooth, Camera)
- Repository implementation with Room

### Implementation Details
- **HomeViewModel**: Device list, trigger action
- **PairingViewModel**: QR scanning, device addition
- **SettingsViewModel**: App settings
- **BleService**: Connect, send messages, handle responses
- **TotpManager**: Generate TOTP codes
- **QrScanner**: CameraX preview + ML Kit detection
- **DeviceRepositoryImpl**: Room database operations

### Next Steps (After STEP 6)
7. STEP 7: Testing, documentation, and deployment scripts

## Technical Stack

### Backend (Raspberry Pi) ✅ Complete
- Python 3.9+
- PyOTP (TOTP), Fernet encryption
- SQLite3 with encrypted secrets
- Bleak (BLE library)
- Flask + Bootstrap 5

### Mobile (Android) 🔄 In Progress
- Kotlin 1.9.22
- Jetpack Compose + Material 3
- MVVM + Clean Architecture
- Room database
- Nordic BLE Library 2.7.0
- ML Kit + CameraX
- Hilt (DI)

## Security Model
- **Layer 1**: BLE Secure Connections
- **Layer 2**: TOTP (30s window, ±1 tolerance)
- **Layer 3**: Timestamp validation (5-min replay protection)
- **Storage**: Fernet encryption (Pi) + EncryptedSharedPreferences (Android)
- **Permissions**: 600 on sensitive files
- **Logging**: All auth attempts logged

## Test Coverage
- Crypto utilities: 16/16 tests ✅
- Pairing manager: 14/14 tests ✅
- Web UI: 12/12 tests ✅
- BLE listener: 10/10 tests ✅
- **Total Backend**: 52 unit tests passing ✅
- **Android Tests**: Coming in STEP 6

## Project Structure
```
BlueZscript/
├── raspberry-pi/          ✅ Complete
│   ├── crypto_utils.py
│   ├── pairing_manager.py
│   ├── web_ui.py
│   ├── ble_listener_secure.py
│   └── templates/
├── tests/                 ✅ 52 tests passing
├── android-app/           🔄 Structure complete, implementation next
│   ├── app/
│   │   └── src/main/java/com/revengine3r/bluezscript/
│   │       ├── data/
│   │       │   ├── local/ (Room DB)
│   │       │   ├── models/
│   │       │   └── repository/
│   │       ├── domain/ (next)
│   │       ├── presentation/
│   │       │   ├── home/
│   │       │   ├── pairing/
│   │       │   ├── settings/
│   │       │   ├── navigation/
│   │       │   └── theme/
│   │       ├── BlueZscriptApp.kt
│   │       └── MainActivity.kt
│   ├── build.gradle.kts
│   └── settings.gradle.kts
└── ROAD_MAP/
```

## Message Protocol

**BLE Message (JSON over characteristic):**
```json
{
  "device_id": "abc123def456",
  "totp": "123456",
  "timestamp": 1738267890,
  "action": "TRIGGER"
}
```

**QR Code Format:**
```json
{
  "device_id": "abc123def456",
  "secret": "JBSWY3DPEHPK3PXP...",
  "server_url": "http://raspberrypi:5000"
}
```

## Android App Screens

1. **Home Screen** ✅
   - List of paired devices
   - Big trigger button
   - Navigate to pairing/settings

2. **Pairing Screen** ✅
   - QR code scanner (next: camera implementation)
   - Device name input
   - Save paired device

3. **Settings Screen** ✅
   - App version
   - About info
   - Future: theme, notifications

4. **Device Detail** (structure ready)
   - Device info
   - Last used
   - Unpair button

## Deployment

**Raspberry Pi:**
```bash
# BLE Listener
sudo systemctl enable ble-listener-secure
sudo systemctl start ble-listener-secure

# Web UI (optional)
cd /opt/BlueZscript/raspberry-pi
sudo ../venv/bin/python3 web_ui.py
```

**Android:**
```bash
cd android-app
./gradlew assembleDebug
# Install APK to device
```

## Notes
- Raspberry Pi backend is production-ready
- Android app structure complete, ready for BLE/TOTP implementation
- All backend tests passing (52/52)
- Material 3 with dynamic colors on Android 12+
- Clean Architecture ensures testability and maintainability

---
*Last Updated*: 2026-01-31 00:20 +0330
