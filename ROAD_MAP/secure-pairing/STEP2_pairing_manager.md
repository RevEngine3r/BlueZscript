# STEP 2: Pairing Manager and Database

## Objective
Implement pairing manager with SQLite database for storing and managing paired devices.

## Scope
Create `raspberry-pi/pairing_manager.py` with secure device storage and management.

## Requirements

### Database Schema

**Table: `paired_devices`**
```sql
CREATE TABLE paired_devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT UNIQUE NOT NULL,
    device_name TEXT NOT NULL,
    secret_key TEXT NOT NULL,  -- Encrypted with Fernet
    paired_at INTEGER NOT NULL,  -- Unix timestamp
    last_used INTEGER,  -- Unix timestamp
    is_active BOOLEAN DEFAULT 1
);
```

### Functions to Implement

1. **`__init__(db_path: str = "paired_devices.db")`**
   - Initialize database connection
   - Create tables if not exist
   - Load or generate master encryption key

2. **`add_device(device_id: str, device_name: str, secret_key: str) -> bool`**
   - Add new paired device
   - Encrypt secret_key before storage
   - Store pairing timestamp
   - Return True on success

3. **`get_device(device_id: str) -> Optional[Dict]`**
   - Retrieve device by ID
   - Decrypt secret_key
   - Return device dict or None

4. **`list_devices() -> List[Dict]`**
   - Get all active paired devices
   - Return list without decrypted secrets (for display)

5. **`remove_device(device_id: str) -> bool`**
   - Soft delete (set is_active=0)
   - Return True on success

6. **`update_last_used(device_id: str) -> bool`**
   - Update last_used timestamp
   - Called after successful authentication

7. **`device_exists(device_id: str) -> bool`**
   - Check if device is paired and active

8. **`get_device_count() -> int`**
   - Return count of active devices

## Implementation Details

### Dependencies
```python
import sqlite3
import json
from typing import Dict, List, Optional
from datetime import datetime
from cryptography.fernet import Fernet
import os
import base64
```

### Encryption Strategy

**Master Key Management:**
- Generate master key on first run
- Store in `~/.bluezscript/master.key` (600 permissions)
- Use Fernet symmetric encryption
- Encrypt all secret_key values before DB storage

**Why Fernet:**
- Built on AES-128-CBC
- Authenticated encryption (prevents tampering)
- Timestamp support
- Standard library (cryptography package)

### Security Considerations

- Database file permissions: 600 (owner read/write only)
- Master key permissions: 600
- Never log decrypted secrets
- Use parameterized queries (prevent SQL injection)
- Soft delete for audit trail

## Code Structure

```python
class PairingManager:
    """
    Manages paired device storage with encrypted secrets.
    """
    
    def __init__(self, db_path: str = "paired_devices.db"):
        """Initialize database and encryption"""
        pass
    
    def _init_db(self):
        """Create database schema"""
        pass
    
    def _load_or_generate_key(self) -> bytes:
        """Load or generate master encryption key"""
        pass
    
    def _encrypt_secret(self, secret: str) -> str:
        """Encrypt secret with master key"""
        pass
    
    def _decrypt_secret(self, encrypted: str) -> str:
        """Decrypt secret with master key"""
        pass
    
    def add_device(self, device_id: str, device_name: str, secret_key: str) -> bool:
        """Add paired device"""
        pass
    
    def get_device(self, device_id: str) -> Optional[Dict]:
        """Get device with decrypted secret"""
        pass
    
    def list_devices(self) -> List[Dict]:
        """List all active devices (without secrets)"""
        pass
    
    def remove_device(self, device_id: str) -> bool:
        """Soft delete device"""
        pass
    
    def update_last_used(self, device_id: str) -> bool:
        """Update last used timestamp"""
        pass
    
    def device_exists(self, device_id: str) -> bool:
        """Check if device is paired"""
        pass
    
    def get_device_count(self) -> int:
        """Get active device count"""
        pass
    
    def close(self):
        """Close database connection"""
        pass
```

## Unit Tests

Create `tests/test_pairing_manager.py`:

```python
import unittest
import os
import tempfile
from raspberry_pi.pairing_manager import PairingManager
from raspberry_pi.crypto_utils import CryptoUtils

class TestPairingManager(unittest.TestCase):
    def setUp(self):
        # Use temporary database for tests
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.manager = PairingManager(self.temp_db.name)
    
    def tearDown(self):
        self.manager.close()
        os.unlink(self.temp_db.name)
    
    def test_add_device(self):
        device_id = CryptoUtils.generate_device_id()
        secret = CryptoUtils.generate_secret()
        result = self.manager.add_device(device_id, "Test Phone", secret)
        self.assertTrue(result)
    
    def test_get_device(self):
        device_id = CryptoUtils.generate_device_id()
        secret = CryptoUtils.generate_secret()
        self.manager.add_device(device_id, "Test Phone", secret)
        
        device = self.manager.get_device(device_id)
        self.assertIsNotNone(device)
        self.assertEqual(device['secret_key'], secret)  # Should be decrypted
    
    def test_list_devices(self):
        # Add multiple devices
        for i in range(3):
            device_id = CryptoUtils.generate_device_id()
            secret = CryptoUtils.generate_secret()
            self.manager.add_device(device_id, f"Phone {i}", secret)
        
        devices = self.manager.list_devices()
        self.assertEqual(len(devices), 3)
        
        # Secrets should not be in list view
        for device in devices:
            self.assertNotIn('secret_key', device)
    
    def test_remove_device(self):
        device_id = CryptoUtils.generate_device_id()
        secret = CryptoUtils.generate_secret()
        self.manager.add_device(device_id, "Test Phone", secret)
        
        result = self.manager.remove_device(device_id)
        self.assertTrue(result)
        
        # Device should not be found after removal
        self.assertFalse(self.manager.device_exists(device_id))
    
    def test_update_last_used(self):
        device_id = CryptoUtils.generate_device_id()
        secret = CryptoUtils.generate_secret()
        self.manager.add_device(device_id, "Test Phone", secret)
        
        result = self.manager.update_last_used(device_id)
        self.assertTrue(result)
        
        device = self.manager.get_device(device_id)
        self.assertIsNotNone(device['last_used'])
    
    def test_device_exists(self):
        device_id = CryptoUtils.generate_device_id()
        secret = CryptoUtils.generate_secret()
        
        self.assertFalse(self.manager.device_exists(device_id))
        
        self.manager.add_device(device_id, "Test Phone", secret)
        self.assertTrue(self.manager.device_exists(device_id))
    
    def test_encryption(self):
        """Test that secrets are encrypted in database"""
        device_id = CryptoUtils.generate_device_id()
        secret = CryptoUtils.generate_secret()
        self.manager.add_device(device_id, "Test Phone", secret)
        
        # Read raw database value
        cursor = self.manager.conn.cursor()
        cursor.execute("SELECT secret_key FROM paired_devices WHERE device_id=?", (device_id,))
        encrypted_secret = cursor.fetchone()[0]
        
        # Encrypted value should not match plain secret
        self.assertNotEqual(encrypted_secret, secret)
        
        # But decrypted value should match
        device = self.manager.get_device(device_id)
        self.assertEqual(device['secret_key'], secret)
```

## Files to Create

- `raspberry-pi/pairing_manager.py` (main implementation)
- `tests/test_pairing_manager.py` (unit tests)
- `~/.bluezscript/` directory (created at runtime)
- `~/.bluezscript/master.key` (generated at runtime)

## Success Criteria

- [ ] All functions implemented
- [ ] Database schema created correctly
- [ ] Secrets encrypted at rest
- [ ] All unit tests pass (8+ tests)
- [ ] Proper error handling
- [ ] File permissions set correctly (600)
- [ ] No SQL injection vulnerabilities
- [ ] Type hints for all functions
- [ ] Comprehensive docstrings

## Security Checklist

- [ ] Master key stored with 600 permissions
- [ ] Database file with 600 permissions
- [ ] Parameterized SQL queries only
- [ ] Secrets never logged
- [ ] Fernet encryption for secrets
- [ ] Soft delete for audit trail

## Estimated Time
2-3 hours

---
*Ready for implementation*
