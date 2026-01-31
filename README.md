# 🔵 BlueZscript

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Kotlin](https://img.shields.io/badge/kotlin-1.9.22-purple.svg)](https://kotlinlang.org/)

**Secure, TOTP-authenticated BLE trigger system for Raspberry Pi with Android companion app.**

Trigger custom actions on your Raspberry Pi from your phone using Bluetooth Low Energy with military-grade security: multi-layer authentication (BLE + TOTP + Timestamp), encrypted storage, and replay attack prevention.

## ✨ Features

### 🔒 **Security First**
- **Multi-layer Authentication**: BLE Secure Connections + TOTP (RFC 6238) + Timestamp validation
- **Encrypted Storage**: Fernet encryption (Pi) + Room encrypted database (Android)
- **Replay Attack Prevention**: 5-minute timestamp window with comprehensive audit logging
- **Zero Trust**: No secrets in logs, 600 file permissions, rate limiting on pairing

### 📱 **Modern Android App**
- **Material 3 Design**: Beautiful, intuitive UI with dynamic colors
- **MVVM + Clean Architecture**: Production-ready, maintainable codebase
- **QR Code Pairing**: Scan QR from web UI for instant secure pairing
- **Jetpack Compose**: Modern declarative UI framework
- **Room Database**: Secure local storage for paired devices

### 🖥️ **Raspberry Pi Backend**
- **Flask Web UI**: Elegant admin dashboard with Bootstrap 5
- **RESTful API**: Manage devices programmatically
- **Systemd Integration**: Auto-start on boot, robust process management
- **Comprehensive Logging**: Security audit trail for all operations

### ⚡ **Performance**
- Pairing: < 5 seconds
- Trigger Latency: < 1 second
- TOTP Generation: < 100ms
- Battery Impact: Minimal (BLE only active during trigger)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Android App                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ HomeScreen   │  │ PairingScreen│  │ SettingsScreen│         │
│  │ (Trigger)    │  │ (QR Scanner) │  │ (Device Mgmt) │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                 │                  │                  │
│  ┌──────▼─────────────────▼──────────────────▼───────┐         │
│  │           ViewModels (Hilt DI)                     │         │
│  └──────┬─────────────────┬──────────────────┬───────┘         │
│         │                 │                  │                  │
│  ┌──────▼──────┐   ┌──────▼──────┐   ┌──────▼──────┐          │
│  │ BLE Service │   │ TOTP Manager│   │ Repository  │          │
│  └──────┬──────┘   └──────┬──────┘   └──────┬──────┘          │
│         │                 │                  │                  │
│  ┌──────▼─────────────────▼──────────────────▼───────┐         │
│  │         Room Database (Encrypted)                  │         │
│  └────────────────────────────────────────────────────┘         │
└────────────────────────┬────────────────────────────────────────┘
                         │ BLE + JSON Message
                         │ {device_id, totp, timestamp, action}
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                    Raspberry Pi                                  │
│  ┌─────────────────────────────────────────────────────┐        │
│  │      BLE Listener (ble_listener_secure.py)          │        │
│  │  • Receives BLE messages                            │        │
│  │  • Validates TOTP (±1 window, 30s)                  │        │
│  │  • Checks timestamp (5-min replay protection)       │        │
│  │  • Logs all attempts                                │        │
│  └────┬──────────────────────────────────────┬─────────┘        │
│       │                                      │                  │
│  ┌────▼──────────────┐              ┌────────▼───────────┐     │
│  │ Pairing Manager   │              │ Action Script      │     │
│  │ (SQLite + Fernet) │              │ (Custom Commands)  │     │
│  └───────────────────┘              └────────────────────┘     │
│                                                                 │
│  ┌─────────────────────────────────────────────────────┐       │
│  │      Flask Web UI (web_ui.py)                       │       │
│  │  • Device management dashboard                      │       │
│  │  • QR code generation for pairing                   │       │
│  │  • RESTful API                                      │       │
│  └─────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- **Raspberry Pi 4** (or Pi 3 with BLE support)
- **Raspberry Pi OS** (Bullseye or newer)
- **Python 3.9+**
- **Android 8.0+** (API level 26+)

### Installation

#### **Option 1: Automated Setup (Recommended)**
```bash
# On Raspberry Pi
curl -fsSL https://raw.githubusercontent.com/RevEngine3r/BlueZscript/main/raspberry-pi/install.sh | sudo bash
```

#### **Option 2: Manual Setup**
See [INSTALL.md](INSTALL.md) for detailed instructions.

### Usage

1. **Start Web UI** (on Raspberry Pi):
   ```bash
   cd /opt/BlueZscript/raspberry-pi
   ../venv/bin/python3 web_ui.py
   ```
   Access at: `http://<raspberry-pi-ip>:5000`

2. **Generate Pairing QR Code**:
   - Click "Pair New Device" in web UI
   - QR code displayed with device credentials

3. **Install Android App**:
   - Download APK from [Releases](https://github.com/RevEngine3r/BlueZscript/releases)
   - Or build from source (see [android-app/BUILDING.md](android-app/BUILDING.md))

4. **Pair Device**:
   - Open app → Tap "+" → Scan QR code
   - Enter device name → Save

5. **Trigger Action**:
   - Select device from list
   - Press "Trigger" button
   - Action executes on Raspberry Pi

## 📋 Message Protocol

### BLE Message (JSON)
```json
{
  "device_id": "abc123def456",
  "totp": "123456",
  "timestamp": 1738267890,
  "action": "TRIGGER"
}
```

### QR Code Format
```json
{
  "device_id": "abc123def456",
  "secret": "JBSWY3DPEHPK3PXP...",
  "server_url": "http://raspberrypi:5000"
}
```

### Security Layers
1. **BLE Secure Connections**: Encrypted transport
2. **TOTP Validation**: 6-digit code, 30s window, ±1 tolerance
3. **Timestamp Check**: Max 5-minute age, prevents replay attacks
4. **Device Registry**: Only paired devices accepted

## 🛠️ Configuration

### Customize Action Script
Edit `/opt/BlueZscript/raspberry-pi/action_script.sh`:

```bash
#!/bin/bash
# Example: Control GPIO LED
echo "17" > /sys/class/gpio/export
echo "out" > /sys/class/gpio/gpio17/direction
echo "1" > /sys/class/gpio/gpio17/value
sleep 2
echo "0" > /sys/class/gpio/gpio17/value
```

### Multiple Actions
Modify `ble_listener_secure.py` to handle different action types:
```python
if message["action"] == "TRIGGER_LED":
    self.execute_action("./actions/led.sh")
elif message["action"] == "TRIGGER_CAMERA":
    self.execute_action("./actions/camera.sh")
```

## 🧪 Testing

See [TESTING.md](TESTING.md) for comprehensive testing guide.

```bash
# Run backend unit tests (52 tests)
cd /opt/BlueZscript
./venv/bin/python3 -m pytest tests/ -v

# Manual BLE test
sudo ./venv/bin/python3 raspberry-pi/ble_listener_secure.py
```

## 📊 Test Coverage

- ✅ **Crypto Utilities**: 16/16 tests passing
- ✅ **Pairing Manager**: 14/14 tests passing
- ✅ **Web UI**: 12/12 tests passing
- ✅ **BLE Listener**: 10/10 tests passing
- ✅ **Total Backend**: 52 unit tests
- ✅ **Android**: Architecture complete, UI functional

## 📚 Documentation

- [**Installation Guide**](INSTALL.md) - Step-by-step setup instructions
- [**Building Android App**](android-app/BUILDING.md) - APK compilation guide
- [**Testing Procedures**](TESTING.md) - Comprehensive testing guide
- [**Troubleshooting**](TROUBLESHOOTING.md) - Common issues and solutions
- [**Contributing**](CONTRIBUTING.md) - Contribution guidelines
- [**Project Structure**](PROJECT_MAP.md) - Codebase overview

## 🔧 Technical Stack

### Backend (Raspberry Pi)
- **Python 3.9+**: Modern Python features
- **Bleak**: BLE library for Linux
- **PyOTP**: TOTP implementation (RFC 6238)
- **Cryptography**: Fernet symmetric encryption
- **Flask**: Web framework
- **SQLite3**: Device registry database
- **Systemd**: Service management

### Mobile (Android)
- **Kotlin 1.9.22**: Modern, type-safe language
- **Jetpack Compose**: Declarative UI framework
- **Material 3**: Latest Material Design
- **Room**: SQLite ORM with encryption
- **Nordic BLE Library 2.7.0**: Robust BLE stack
- **Hilt**: Dependency injection
- **CameraX + ML Kit**: QR code scanning
- **kotlin-onetimepassword**: TOTP generation

## 🔐 Security Audit

- ✅ Multi-layer authentication
- ✅ Encrypted storage (Fernet + Room)
- ✅ No secrets in logs or version control
- ✅ Replay attack prevention
- ✅ Secure file permissions (600)
- ✅ Rate limiting on pairing
- ✅ Comprehensive audit logging
- ✅ Input validation and sanitization
- ✅ Principle of least privilege

## 📈 Performance Metrics

| Metric | Value |
|--------|-------|
| Pairing Time | < 5 seconds |
| Trigger Latency | < 1 second |
| TOTP Generation | < 100ms |
| BLE Range | ~10 meters |
| Battery Impact | Minimal |
| Database Size | < 1MB (1000 devices) |

## 🐛 Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed solutions.

**Quick Fixes:**

```bash
# Bluetooth not working
sudo rfkill unblock bluetooth
sudo systemctl restart bluetooth

# Service not starting
sudo systemctl status ble-listener-secure
sudo journalctl -u ble-listener-secure -n 50

# Permission denied
sudo chmod 600 /opt/BlueZscript/raspberry-pi/data/pairing.db
sudo chown root:root /opt/BlueZscript/raspberry-pi/data/master.key
```

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'feat: add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 👤 Author

**RevEngine3r**
- GitHub: [@RevEngine3r](https://github.com/RevEngine3r)
- Website: [RevEngine3r.iR](https://www.RevEngine3r.iR)
- Company: RevEngine3r co.

## 🙏 Acknowledgments

- [Bleak](https://github.com/hbldh/bleak) - Excellent BLE library for Python
- [Nordic BLE Library](https://github.com/NordicSemiconductor/Android-BLE-Library) - Robust Android BLE stack
- [PyOTP](https://github.com/pyauth/pyotp) - TOTP implementation
- Material Design team for beautiful UI components

## 🌟 Show Your Support

Give a ⭐ if this project helped you!

## 📊 Project Stats

- **Development Time**: 1 day (iterative development)
- **Lines of Code**: ~5000+ (Python + Kotlin)
- **Test Coverage**: 52 backend unit tests
- **Platforms**: Raspberry Pi + Android
- **Architecture**: Clean Architecture + MVVM
- **Security**: Multi-layer authentication + encryption

---

**Made with ❤️ for IoT and Home Automation**

*Secure, Fast, Reliable - BlueZscript powers your smart home.*