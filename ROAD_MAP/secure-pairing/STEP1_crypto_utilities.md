# STEP 1: Crypto Utilities

## Objective
Implement cryptographic utilities for TOTP generation/validation, HMAC signing, and secure key generation.

## Scope
Create `raspberry-pi/crypto_utils.py` with all cryptographic functions needed for secure authentication.

## Requirements

### Functions to Implement

1. **`generate_secret() -> str`**
   - Generate cryptographically secure 32-byte base32-encoded secret
   - Use `secrets` module for CSPRNG
   - Return base32 string compatible with PyOTP

2. **`generate_totp(secret: str) -> str`**
   - Generate current 6-digit TOTP code
   - Use SHA-1 algorithm (TOTP standard)
   - 30-second time step

3. **`verify_totp(secret: str, token: str, window: int = 1) -> bool`**
   - Validate TOTP token against secret
   - Allow ±1 time window (30 seconds tolerance)
   - Return True if valid, False otherwise

4. **`sign_message(secret: str, message: str) -> str`**
   - Create HMAC-SHA256 signature
   - Return base64-encoded signature
   - Use secret as HMAC key

5. **`verify_signature(secret: str, message: str, signature: str) -> bool`**
   - Verify HMAC-SHA256 signature
   - Use constant-time comparison
   - Return True if valid

6. **`validate_timestamp(timestamp: int, tolerance: int = 300) -> bool`**
   - Check if timestamp is within tolerance (default 5 minutes)
   - Prevent replay attacks
   - Return True if fresh

## Implementation Details

### Dependencies
```python
import pyotp
import hmac
import hashlib
import base64
import secrets
import time
from typing import Optional
```

### TOTP Configuration
- **Algorithm**: SHA-1 (RFC 6238 standard)
- **Digits**: 6
- **Interval**: 30 seconds
- **Window**: ±1 period (±30 seconds)

### HMAC Configuration
- **Algorithm**: SHA-256
- **Encoding**: Base64
- **Comparison**: Constant-time (prevent timing attacks)

### Security Notes
- Use `secrets.token_bytes()` for key generation (not `random`)
- Use `hmac.compare_digest()` for signature verification
- Log validation failures for security monitoring
- Never log secrets or tokens

## Testing Checklist

- [ ] `generate_secret()` returns 32-character base32 string
- [ ] Generated secrets are unique (test 1000 generations)
- [ ] `generate_totp()` produces 6-digit code
- [ ] `verify_totp()` accepts valid current code
- [ ] `verify_totp()` accepts code from ±30 seconds ago
- [ ] `verify_totp()` rejects code from 2+ minutes ago
- [ ] `sign_message()` produces consistent signatures
- [ ] `verify_signature()` accepts valid signatures
- [ ] `verify_signature()` rejects tampered signatures
- [ ] `validate_timestamp()` accepts current time
- [ ] `validate_timestamp()` rejects old timestamps

## Code Structure

```python
# Constants
TOTP_INTERVAL = 30
TOTP_DIGITS = 6
TIMESTAMP_TOLERANCE = 300  # 5 minutes

class CryptoUtils:
    """Cryptographic utilities for secure BLE authentication"""
    
    @staticmethod
    def generate_secret() -> str:
        """Generate secure random secret"""
        pass
    
    @staticmethod
    def generate_totp(secret: str) -> str:
        """Generate TOTP code"""
        pass
    
    @staticmethod
    def verify_totp(secret: str, token: str, window: int = 1) -> bool:
        """Verify TOTP code"""
        pass
    
    @staticmethod
    def sign_message(secret: str, message: str) -> str:
        """Sign message with HMAC-SHA256"""
        pass
    
    @staticmethod
    def verify_signature(secret: str, message: str, signature: str) -> bool:
        """Verify HMAC-SHA256 signature"""
        pass
    
    @staticmethod
    def validate_timestamp(timestamp: int, tolerance: int = TIMESTAMP_TOLERANCE) -> bool:
        """Validate timestamp freshness"""
        pass
```

## Unit Tests

Create `tests/test_crypto_utils.py`:

```python
import unittest
import time
from raspberry_pi.crypto_utils import CryptoUtils

class TestCryptoUtils(unittest.TestCase):
    def test_generate_secret(self):
        secret = CryptoUtils.generate_secret()
        self.assertEqual(len(secret), 32)
        self.assertTrue(secret.isalnum())
    
    def test_totp_generation(self):
        secret = CryptoUtils.generate_secret()
        totp = CryptoUtils.generate_totp(secret)
        self.assertEqual(len(totp), 6)
        self.assertTrue(totp.isdigit())
    
    def test_totp_validation(self):
        secret = CryptoUtils.generate_secret()
        totp = CryptoUtils.generate_totp(secret)
        self.assertTrue(CryptoUtils.verify_totp(secret, totp))
    
    def test_hmac_signature(self):
        secret = "TESTSECRET123"
        message = "test message"
        signature = CryptoUtils.sign_message(secret, message)
        self.assertTrue(CryptoUtils.verify_signature(secret, message, signature))
    
    def test_timestamp_validation(self):
        now = int(time.time())
        self.assertTrue(CryptoUtils.validate_timestamp(now))
        self.assertFalse(CryptoUtils.validate_timestamp(now - 600))
```

## Files to Create

- `raspberry-pi/crypto_utils.py` (main implementation)
- `tests/test_crypto_utils.py` (unit tests)
- Update `raspberry-pi/requirements.txt`:
  ```
  pyotp>=2.9.0
  cryptography>=41.0.0
  ```

## Success Criteria

- [ ] All functions implemented
- [ ] All unit tests pass
- [ ] Code follows PEP 8 style
- [ ] Docstrings for all public methods
- [ ] No security vulnerabilities (secrets logged, timing attacks, etc.)
- [ ] Type hints for all function signatures

## Estimated Time
1-2 hours

---
*Ready for implementation*
