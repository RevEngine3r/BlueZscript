# 📦 Building Android App

> **Complete guide to building BlueZscript Android APK**

## Prerequisites

### System Requirements
- **Operating System**: Windows 10/11, macOS 10.14+, or Linux
- **RAM**: Minimum 8GB (16GB recommended)
- **Disk Space**: Minimum 10GB free
- **Java**: JDK 17 or newer

### Required Software

#### 1. Install Java Development Kit (JDK)

**Linux:**
```bash
sudo apt-get update
sudo apt-get install -y openjdk-17-jdk
java -version
```

**macOS:**
```bash
brew install openjdk@17
echo 'export PATH="/opt/homebrew/opt/openjdk@17/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
java -version
```

**Windows:**
- Download from [Oracle](https://www.oracle.com/java/technologies/downloads/) or [Adoptium](https://adoptium.net/)
- Install and add to PATH
- Verify: `java -version` in Command Prompt

#### 2. Install Android Studio (Optional but Recommended)

**Download:** [https://developer.android.com/studio](https://developer.android.com/studio)

**Installation:**
1. Run installer
2. Select "Standard" installation
3. Download Android SDK components
4. Configure virtual device (optional)

#### 3. Install Android SDK Command Line Tools (Alternative)

If not using Android Studio:

**Linux/macOS:**
```bash
# Download SDK command line tools
wget https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip
unzip commandlinetools-linux-9477386_latest.zip -d ~/android-sdk

# Set environment variables
export ANDROID_HOME=~/android-sdk
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools

# Install required SDK components
sdkmanager "platform-tools" "platforms;android-33" "build-tools;33.0.0"
```

**Windows:**
- Download from [Android Developer site](https://developer.android.com/studio#command-tools)
- Extract to `C:\Android\sdk`
- Set environment variables:
  ```
  ANDROID_HOME=C:\Android\sdk
  PATH=%PATH%;%ANDROID_HOME%\cmdline-tools\latest\bin;%ANDROID_HOME%\platform-tools
  ```

---

## Building from Command Line

### 1. Clone Repository

```bash
git clone https://github.com/RevEngine3r/BlueZscript.git
cd BlueZscript/android-app
```

### 2. Configure Build

**Check Gradle Wrapper:**
```bash
# Linux/macOS
chmod +x gradlew
./gradlew --version

# Windows
gradlew.bat --version
```

**Sync Dependencies:**
```bash
./gradlew build --refresh-dependencies
```

### 3. Build Debug APK

```bash
./gradlew assembleDebug
```

**Output location:**
```
app/build/outputs/apk/debug/app-debug.apk
```

**Install on connected device:**
```bash
adb install app/build/outputs/apk/debug/app-debug.apk
```

### 4. Build Release APK

#### Without Signing (Testing Only)

```bash
./gradlew assembleRelease
```

**Output:**
```
app/build/outputs/apk/release/app-release-unsigned.apk
```

#### With Signing (For Distribution)

**Generate Keystore:**
```bash
keytool -genkey -v -keystore bluezscript.keystore \
  -alias bluezscript \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000
```

**Enter details:**
- Keystore password (remember this!)
- Your name and organization
- Alias password

**Create `keystore.properties`:**
```bash
cat > keystore.properties << EOF
storeFile=../bluezscript.keystore
storePassword=YOUR_KEYSTORE_PASSWORD
keyAlias=bluezscript
keyPassword=YOUR_KEY_PASSWORD
EOF
```

**Update `app/build.gradle.kts`:**
```kotlin
android {
    signingConfigs {
        create("release") {
            val keystorePropertiesFile = rootProject.file("keystore.properties")
            if (keystorePropertiesFile.exists()) {
                val keystoreProperties = Properties()
                keystoreProperties.load(FileInputStream(keystorePropertiesFile))
                
                storeFile = file(keystoreProperties["storeFile"] as String)
                storePassword = keystoreProperties["storePassword"] as String
                keyAlias = keystoreProperties["keyAlias"] as String
                keyPassword = keystoreProperties["keyPassword"] as String
            }
        }
    }
    
    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")
            // ...
        }
    }
}
```

**Build signed APK:**
```bash
./gradlew assembleRelease
```

**Output:**
```
app/build/outputs/apk/release/app-release.apk
```

**Verify signature:**
```bash
jarsigner -verify -verbose -certs app/build/outputs/apk/release/app-release.apk
```

---

## Building with Android Studio

### 1. Open Project

1. Launch Android Studio
2. **File → Open**
3. Select `BlueZscript/android-app` directory
4. Wait for Gradle sync

### 2. Configure Build Variant

1. **View → Tool Windows → Build Variants**
2. Select:
   - **debug** for development
   - **release** for production

### 3. Build APK

**Debug:**
- **Build → Build Bundle(s) / APK(s) → Build APK(s)**
- Wait for build to complete
- Click "locate" in notification to find APK

**Release:**
- **Build → Generate Signed Bundle / APK**
- Select **APK**
- Choose existing keystore or create new
- Enter passwords
- Select release build variant
- Click **Finish**

### 4. Run on Device/Emulator

**Connect device:**
- Enable Developer Options on Android device
- Enable USB Debugging
- Connect via USB
- Allow USB debugging prompt

**Or create emulator:**
- **Tools → Device Manager**
- **Create Device**
- Select device definition (e.g., Pixel 6)
- Download system image (Android 8.0+)
- Finish and launch

**Run app:**
- Select device from dropdown
- Click **Run** button (green play icon)
- Or press `Shift+F10`

---

## Build Variants

### Debug

**Characteristics:**
- Debug symbols included
- Logging enabled
- Not optimized
- Allows debugging with Android Studio

**Use for:**
- Development
- Testing
- Debugging

**Build command:**
```bash
./gradlew assembleDebug
```

### Release

**Characteristics:**
- Optimized (ProGuard/R8)
- Debug symbols stripped
- Minimal logging
- Signed for distribution

**Use for:**
- Production deployment
- App store distribution
- End users

**Build command:**
```bash
./gradlew assembleRelease
```

---

## ProGuard / R8 Configuration

**ProGuard rules:** `app/proguard-rules.pro`

```proguard
# Keep Room database entities
-keep class com.revengine3r.bluezscript.data.local.** { *; }

# Keep Kotlin coroutines
-keepnames class kotlinx.coroutines.internal.MainDispatcherFactory {}
-keepnames class kotlinx.coroutines.CoroutineExceptionHandler {}

# Keep BLE library classes
-keep class no.nordicsemi.android.ble.** { *; }

# Keep TOTP library
-keep class dev.turingcomplete.kotlinonetimepassword.** { *; }

# Remove logging in release
-assumenosideeffects class android.util.Log {
    public static *** d(...);
    public static *** v(...);
    public static *** i(...);
}
```

**Enable R8 full mode:** `gradle.properties`
```properties
android.enableR8.fullMode=true
```

---

## Optimizing APK Size

### Enable Shrinking

**`app/build.gradle.kts`:**
```kotlin
android {
    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}
```

### Split APKs by ABI

```kotlin
android {
    splits {
        abi {
            isEnable = true
            reset()
            include("armeabi-v7a", "arm64-v8a", "x86", "x86_64")
            isUniversalApk = false
        }
    }
}
```

### Analyze APK Size

**Android Studio:**
- **Build → Analyze APK**
- Select APK file
- View size breakdown

**Command line:**
```bash
./gradlew :app:analyzeReleaseApkSize
```

---

## Troubleshooting

### Gradle Build Failed

**Error: "SDK location not found"**

**Solution:**
```bash
# Create local.properties
echo "sdk.dir=$ANDROID_HOME" > local.properties
```

### Dependency Resolution Failed

**Clear Gradle cache:**
```bash
./gradlew clean
rm -rf ~/.gradle/caches/
./gradlew build --refresh-dependencies
```

### Out of Memory

**Increase Gradle heap size:**

**`gradle.properties`:**
```properties
org.gradle.jvmargs=-Xmx4g -XX:MaxMetaspaceSize=512m
```

### Signing Failed

**Verify keystore:**
```bash
keytool -list -v -keystore bluezscript.keystore
```

**Check passwords in `keystore.properties`**

### APK Not Installing

**Check minimum SDK version:**
- App requires Android 8.0+ (API 26)
- Device must meet requirement

**Check architecture:**
- Ensure APK built for device architecture
- Use universal APK for testing

---

## CI/CD Integration

### GitHub Actions

**`.github/workflows/android.yml`:**
```yaml
name: Android Build

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up JDK 17
        uses: actions/setup-java@v3
        with:
          java-version: '17'
          distribution: 'temurin'
      
      - name: Grant execute permission for gradlew
        run: chmod +x android-app/gradlew
      
      - name: Build Debug APK
        run: |
          cd android-app
          ./gradlew assembleDebug
      
      - name: Upload APK
        uses: actions/upload-artifact@v3
        with:
          name: app-debug
          path: android-app/app/build/outputs/apk/debug/app-debug.apk
```

---

## Distribution

### Manual Distribution

1. Build signed release APK
2. Upload to GitHub Releases
3. Users download and install manually

### Google Play Store (Future)

**Required:**
- Google Play Developer account ($25 one-time)
- Privacy policy URL
- App store listing (description, screenshots)
- Content rating

**Build App Bundle (AAB):**
```bash
./gradlew bundleRelease
```

**Output:**
```
app/build/outputs/bundle/release/app-release.aab
```

---

## Version Management

### Update Version

**`app/build.gradle.kts`:**
```kotlin
android {
    defaultConfig {
        versionCode = 2  // Increment for each release
        versionName = "1.1.0"  // Semantic versioning
    }
}
```

**Versioning scheme:**
- **versionCode**: Integer, increments each release (1, 2, 3, ...)
- **versionName**: String, semantic version (1.0.0, 1.1.0, 2.0.0)

---

## Build Artifacts

### APK Files

**Debug APK:**
- `app/build/outputs/apk/debug/app-debug.apk`
- Size: ~15-20 MB
- Not optimized

**Release APK:**
- `app/build/outputs/apk/release/app-release.apk`
- Size: ~8-12 MB (optimized)
- Production-ready

### Build Reports

**Lint report:**
```bash
./gradlew lint
open app/build/reports/lint-results.html
```

**Test report:**
```bash
./gradlew test
open app/build/reports/tests/testDebugUnitTest/index.html
```

---

## Next Steps

1. Build APK following this guide
2. Test on real device
3. Report issues: [GitHub Issues](https://github.com/RevEngine3r/BlueZscript/issues)
4. See [README.md](../README.md) for usage instructions

---

**Happy building! 🚀**