# BlueZscript Project Map

## Overview
Secure BLE listener system for Raspberry Pi 4 with TOTP-based authentication and device pairing via QR codes.

## Project Structure

```
BlueZscript/
├── raspberry-pi/              # Raspberry Pi components
│   ├── ble_listener.py       # Main BLE listener with TOTP validation
│   ├── web_ui/               # Flask pairing WebUI
│   │   ├── app.py
│   │   ├── templates/
│   │   └── static/
│   ├── pairing_manager.py    # Device pairing & secret management
│   ├── crypto_utils.py       # TOTP & encryption utilities
│   └── requirements.txt
├── android-app/              # Kotlin Compose Android app
│   ├── app/
│   │   ├── src/main/
│   │   │   ├── java/com/revengine3r/bluezcontrol/
│   │   │   │   ├── ui/          # Compose UI
│   │   │   │   ├── ble/         # BLE client
│   │   │   │   ├── crypto/      # TOTP generation
│   │   │   │   └── data/        # Local storage
│   │   │   └── res/
│   │   └── build.gradle.kts
│   └── gradle/
├── action_script.sh
├── ble-listener.service
└── README.md
```

## Architecture

### Security Layers
1. **BLE Layer**: Bonding + encryption (BLE 4.2+ Secure Connections)
2. **Application Layer**: TOTP validation (30s window)
3. **Replay Protection**: Timestamp validation

### Pairing Flow
1. Raspberry Pi WebUI generates QR code (device_id + shared_secret)
2. Android app scans QR code
3. App stores secret in EncryptedSharedPreferences
4. BLE bonding establishes trusted connection
5. Every trigger: app sends TOTP-signed command
6. Raspberry Pi validates TOTP + bonding before executing action

### Communication Protocol
```json
{
  "device_id": "uuid-here",
  "action": "TRIGGER",
  "totp": "123456",
  "timestamp": 1738267890,
  "signature": "hmac-sha256-here"
}
```

## Technology Stack

### Raspberry Pi
- Python 3.9+
- Flask (WebUI)
- Bleak (BLE)
- PyOTP (TOTP)
- cryptography (HMAC)
- SQLite (pairing database)
- QRCode generation

### Android App
- Kotlin 1.9+
- Jetpack Compose
- Material 3 Design
- Accompanist (permissions)
- ZXing (QR scanning)
- Kable (BLE client)
- Security Crypto (EncryptedSharedPreferences)
- Kotlinx Serialization

## Current Status

See [PROGRESS.md](PROGRESS.md) for implementation status.

## Features

- [x] Basic BLE listener
- [x] Action script execution
- [x] Systemd service
- [ ] Secure pairing system
- [ ] TOTP authentication
- [ ] WebUI for pairing
- [ ] Android app
- [ ] Device management panel

## Development Roadmap

See [ROAD_MAP/README.md](ROAD_MAP/README.md) for detailed feature roadmap.
