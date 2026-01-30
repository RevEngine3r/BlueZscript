# Secure Pairing System Feature

## Overview
Implement a secure, TOTP-based authentication system for BLE communication between Raspberry Pi and Android devices.

## Goals
- Enable secure device pairing via QR code
- Implement TOTP (Time-based One-Time Password) authentication
- Provide WebUI for pairing management
- Create Kotlin Compose Android app for control
- Ensure defense-in-depth security (BLE bonding + TOTP)

## Security Model

### Layers
1. **BLE Security**: Bonding with encryption (BLE Secure Connections)
2. **Application Security**: TOTP validation (30-second window)
3. **Replay Protection**: Timestamp validation (±5 minutes)
4. **Signature Verification**: HMAC-SHA256 message authentication

### Threat Model Protection
- ✅ Unauthorized device connection (BLE bonding)
- ✅ Signal replay attacks (timestamp + TOTP)
- ✅ Man-in-the-middle (HMAC signature)
- ✅ Brute force (TOTP + rate limiting)
- ✅ Device theft (revocation via admin panel)

## Architecture

### Pairing Flow
```
[Raspberry Pi WebUI] 
       ↓ Generates
   [QR Code: device_id + secret]
       ↓ Scans
 [Android App]
       ↓ Stores in
 [EncryptedSharedPreferences]
       ↓ Initiates
   [BLE Bonding]
       ↓ Establishes
 [Trusted Connection]
```

### Trigger Flow
```
[Android App]
   ↓ Generates TOTP
   ↓ Creates signed command
   ↓ Sends via BLE
[Raspberry Pi]
   ↓ Validates bonding
   ↓ Validates TOTP
   ↓ Validates signature
   ↓ Checks timestamp
   ↓ Executes action if valid
```

### Data Format
```json
{
  "device_id": "550e8400-e29b-41d4-a716-446655440000",
  "action": "TRIGGER",
  "totp": "123456",
  "timestamp": 1738267890,
  "signature": "base64-hmac-sha256"
}
```

## Implementation Steps

### STEP 1: Crypto Utilities
**File**: `raspberry-pi/crypto_utils.py`
- TOTP generation and validation (PyOTP)
- HMAC-SHA256 signing and verification
- Secure random key generation
- Time drift tolerance (±1 period)

### STEP 2: Pairing Manager
**File**: `raspberry-pi/pairing_manager.py`
- SQLite database for paired devices
- Device registration and revocation
- Secret storage and retrieval
- Pairing data model (device_id, name, secret, created_at)

### STEP 3: Flask WebUI
**Files**: `raspberry-pi/web_ui/`
- Pairing page with QR code generation
- Admin panel (list/revoke devices)
- REST API for pairing operations
- Responsive Material Design UI

### STEP 4: Enhanced BLE Listener
**File**: `raspberry-pi/ble_listener_secure.py`
- Parse JSON commands from BLE
- Validate TOTP against device secret
- Verify HMAC signature
- Check timestamp freshness
- Rate limiting (prevent brute force)

### STEP 5: Android App Structure
**Files**: `android-app/`
- Gradle setup with dependencies
- Package structure (ui, ble, crypto, data)
- Navigation (Splash → Pairing → Control)
- Material 3 theme

### STEP 6: Android Core Features
- QR scanner (CameraX + ML Kit)
- BLE client (Kable library)
- TOTP generation (OTP library)
- Secure storage (EncryptedSharedPreferences)
- Trigger UI with confirmation

### STEP 7: Testing & Deployment
- Unit tests (crypto, pairing logic)
- Integration tests (BLE communication)
- Installation scripts
- Updated documentation
- APK build configuration

## Technical Specifications

### Raspberry Pi
- **Language**: Python 3.9+
- **BLE**: Bleak 0.21+
- **Web**: Flask 3.0+
- **Database**: SQLite 3
- **Crypto**: PyOTP, cryptography

### Android App
- **Language**: Kotlin 1.9+
- **Min SDK**: 26 (Android 8.0)
- **Target SDK**: 34 (Android 14)
- **UI**: Jetpack Compose + Material 3
- **BLE**: Kable 0.30+
- **QR**: ML Kit Barcode Scanning

## Dependencies

### Python Requirements
```
bleak>=0.21.1
flask>=3.0.0
pyotp>=2.9.0
cryptography>=41.0.0
qrcode[pil]>=7.4.2
sqlite3 (built-in)
```

### Android Dependencies
```kotlin
// Compose BOM
androidx.compose.bom:2024.02.00
// BLE
com.juul.kable:kable-core:0.30.0
// QR Scanning
com.google.mlkit:barcode-scanning:17.2.0
// TOTP
dev.turingcomplete:kotlin-onetimepassword:2.4.0
// Crypto
androidx.security:security-crypto:1.1.0-alpha06
```

## Security Considerations

### Best Practices Implemented
- ✅ Secrets never transmitted in plaintext
- ✅ QR code shown only once during pairing
- ✅ Device revocation immediately invalidates access
- ✅ Rate limiting prevents brute force attacks
- ✅ TOTP window prevents replay attacks
- ✅ HMAC signature prevents tampering
- ✅ BLE bonding prevents unauthorized connections

### User Responsibilities
- Keep Raspberry Pi physically secure
- Don't share QR codes
- Revoke lost/stolen devices immediately
- Use strong WiFi/network security

## Testing Plan

### Unit Tests
- TOTP generation/validation
- HMAC signature verification
- Timestamp validation logic
- Pairing manager CRUD operations

### Integration Tests
- End-to-end pairing flow
- Command transmission and validation
- Error handling and edge cases
- Multi-device scenarios

### Manual Testing
- QR code scanning from various distances
- BLE connection stability
- UI responsiveness
- Permission handling

## Success Criteria

- [ ] User can pair device via QR code scan
- [ ] Only paired devices can trigger actions
- [ ] TOTP validation works within 30-second window
- [ ] Invalid/expired commands are rejected
- [ ] Admin can revoke devices via WebUI
- [ ] Android app works on SDK 26-34
- [ ] No security vulnerabilities found in review
- [ ] Documentation covers all setup steps

## Estimated Timeline

- STEP 1-2: 2-3 hours (Backend crypto & database)
- STEP 3: 2-3 hours (WebUI)
- STEP 4: 2 hours (Enhanced BLE listener)
- STEP 5-6: 4-6 hours (Android app)
- STEP 7: 2 hours (Testing & docs)

**Total**: ~12-16 hours of development

---
*Created*: 2026-01-30
