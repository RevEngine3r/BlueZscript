# BlueZscript Android App

Secure BLE authentication app for Raspberry Pi triggers.

## Architecture

### Clean Architecture + MVVM
```
Presentation Layer (UI)
    ↓
Domain Layer (Business Logic)
    ↓
Data Layer (Repository, Database, BLE)
```

### Technology Stack
- **UI**: Jetpack Compose + Material 3
- **Architecture**: MVVM + Clean Architecture
- **DI**: Hilt
- **Database**: Room
- **BLE**: Nordic BLE Library
- **QR Scanning**: ML Kit Barcode Scanning + CameraX
- **TOTP**: kotlin-onetimepassword
- **Security**: EncryptedSharedPreferences

## Package Structure

```
com.revengine3r.bluezscript/
├── data/
│   ├── local/
│   │   ├── AppDatabase.kt
│   │   ├── dao/
│   │   │   └── PairedDeviceDao.kt
│   │   └── entity/
│   │       └── PairedDeviceEntity.kt
│   ├── models/
│   │   ├── PairingData.kt
│   │   ├── BleMessage.kt
│   │   └── PairedDevice.kt
│   └── repository/
│       └── DeviceRepository.kt
│
├── domain/
│   └── usecases/  (Next step)
│
├── presentation/
│   ├── home/
│   │   └── HomeScreen.kt
│   ├── pairing/
│   │   └── PairingScreen.kt
│   ├── settings/
│   │   └── SettingsScreen.kt
│   ├── navigation/
│   │   ├── Screen.kt
│   │   └── BlueZscriptNavigation.kt
│   └── theme/
│       ├── Color.kt
│       ├── Theme.kt
│       └── Type.kt
│
├── BlueZscriptApp.kt
└── MainActivity.kt
```

## Features (Step 5 - Structure)

- ✅ Project structure with Clean Architecture
- ✅ MVVM architecture setup
- ✅ Jetpack Compose UI with Material 3
- ✅ Navigation graph
- ✅ Room database schema
- ✅ Data models and repositories
- ✅ Dependency injection setup (Hilt)
- ✅ Theme with dynamic colors

## Next Steps (Step 6)

- Implement ViewModels
- BLE service integration
- TOTP generation
- QR code scanning
- Camera permission handling
- Device pairing flow
- Trigger button functionality

## Building

```bash
./gradlew assembleDebug
```

## Dependencies

See `app/build.gradle.kts` for full dependency list.

Key libraries:
- Jetpack Compose BOM 2024.01.00
- Hilt 2.50
- Room 2.6.1
- Nordic BLE 2.7.0
- ML Kit Barcode Scanning
- CameraX

## Minimum Requirements

- Android 8.0 (API 26)
- Bluetooth LE support
- Camera (for QR scanning)
