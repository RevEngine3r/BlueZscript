#!/usr/bin/env python3
"""
Pairing Manager for Secure Device Storage
Manages paired devices with encrypted secret storage using SQLite
"""

import sqlite3
import os
import stat
from typing import Dict, List, Optional
from datetime import datetime
from cryptography.fernet import Fernet
import time
import logging

logger = logging.getLogger(__name__)

# Configuration
DEFAULT_DB_PATH = "/opt/BlueZscript/data/paired_devices.db"
KEY_DIR = os.path.expanduser("~/.bluezscript")
KEY_FILE = os.path.join(KEY_DIR, "master.key")


class PairingManager:
    """
    Manages paired device storage with encrypted secrets.
    
    Features:
    - SQLite database for persistent storage
    - Fernet symmetric encryption for secrets at rest
    - Soft delete for audit trail
    - Automatic key generation and management
    """
    
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        """
        Initialize pairing manager.
        
        Args:
            db_path: Path to SQLite database file
            
        Example:
            >>> manager = PairingManager()
            >>> manager.get_device_count()
            0
        """
        self.db_path = db_path
        
        # Ensure database directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Load or generate encryption key
        self.cipher = self._load_or_generate_key()
        
        # Initialize database
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
        self._init_db()
        
        # Set secure permissions on database
        self._set_secure_permissions(db_path)
        
        logger.info(f"PairingManager initialized with database: {db_path}")
    
    def _init_db(self):
        """Create database schema if it doesn't exist."""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS paired_devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT UNIQUE NOT NULL,
                device_name TEXT NOT NULL,
                secret_key TEXT NOT NULL,
                paired_at INTEGER NOT NULL,
                last_used INTEGER,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        # Create index for faster lookups
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_device_id 
            ON paired_devices(device_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_active 
            ON paired_devices(is_active)
        """)
        
        self.conn.commit()
        logger.debug("Database schema initialized")
    
    def _load_or_generate_key(self) -> Fernet:
        """
        Load existing master key or generate new one.
        
        Returns:
            Fernet: Cipher instance for encryption/decryption
        """
        # Create key directory if it doesn't exist
        os.makedirs(KEY_DIR, exist_ok=True)
        
        if os.path.exists(KEY_FILE):
            # Load existing key
            with open(KEY_FILE, 'rb') as f:
                key = f.read()
            logger.info("Loaded existing master key")
        else:
            # Generate new key
            key = Fernet.generate_key()
            
            # Save key with secure permissions
            with open(KEY_FILE, 'wb') as f:
                f.write(key)
            
            # Set file permissions to 600 (owner read/write only)
            self._set_secure_permissions(KEY_FILE)
            logger.info(f"Generated new master key: {KEY_FILE}")
        
        return Fernet(key)
    
    def _set_secure_permissions(self, filepath: str):
        """Set file permissions to 600 (owner read/write only)."""
        try:
            os.chmod(filepath, stat.S_IRUSR | stat.S_IWUSR)  # 600
            logger.debug(f"Set secure permissions (600) on {filepath}")
        except Exception as e:
            logger.warning(f"Could not set permissions on {filepath}: {e}")
    
    def _encrypt_secret(self, secret: str) -> str:
        """
        Encrypt secret with master key.
        
        Args:
            secret: Plain text secret
            
        Returns:
            str: Encrypted secret (base64 encoded)
        """
        encrypted = self.cipher.encrypt(secret.encode('utf-8'))
        return encrypted.decode('utf-8')
    
    def _decrypt_secret(self, encrypted: str) -> str:
        """
        Decrypt secret with master key.
        
        Args:
            encrypted: Encrypted secret (base64 encoded)
            
        Returns:
            str: Plain text secret
        """
        decrypted = self.cipher.decrypt(encrypted.encode('utf-8'))
        return decrypted.decode('utf-8')
    
    def add_device(self, device_id: str, device_name: str, secret_key: str) -> bool:
        """
        Add a new paired device.
        
        Args:
            device_id: Unique device identifier
            device_name: Human-readable device name
            secret_key: TOTP shared secret
            
        Returns:
            bool: True if added successfully, False otherwise
            
        Example:
            >>> manager = PairingManager()
            >>> manager.add_device("abc123", "My Phone", "JBSWY3DPEHPK3PXP")
            True
        """
        try:
            # Encrypt secret before storage
            encrypted_secret = self._encrypt_secret(secret_key)
            
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO paired_devices 
                (device_id, device_name, secret_key, paired_at, is_active)
                VALUES (?, ?, ?, ?, 1)
            """, (device_id, device_name, encrypted_secret, int(time.time())))
            
            self.conn.commit()
            logger.info(f"Added device: {device_id} ({device_name})")
            return True
        
        except sqlite3.IntegrityError:
            logger.warning(f"Device already exists: {device_id}")
            return False
        except Exception as e:
            logger.error(f"Error adding device: {e}")
            return False
    
    def get_device(self, device_id: str) -> Optional[Dict]:
        """
        Get device details with decrypted secret.
        
        Args:
            device_id: Device identifier
            
        Returns:
            Dict with device details or None if not found
            
        Example:
            >>> device = manager.get_device("abc123")
            >>> device['device_name']
            'My Phone'
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT * FROM paired_devices 
                WHERE device_id = ? AND is_active = 1
            """, (device_id,))
            
            row = cursor.fetchone()
            
            if row:
                device = dict(row)
                # Decrypt secret
                device['secret_key'] = self._decrypt_secret(device['secret_key'])
                return device
            
            return None
        
        except Exception as e:
            logger.error(f"Error getting device: {e}")
            return None
    
    def list_devices(self) -> List[Dict]:
        """
        List all active paired devices (without secrets).
        
        Returns:
            List of device dicts (secrets excluded for security)
            
        Example:
            >>> devices = manager.list_devices()
            >>> len(devices)
            3
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT id, device_id, device_name, paired_at, last_used
                FROM paired_devices 
                WHERE is_active = 1
                ORDER BY paired_at DESC
            """)
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        
        except Exception as e:
            logger.error(f"Error listing devices: {e}")
            return []
    
    def remove_device(self, device_id: str) -> bool:
        """
        Soft delete a device (maintains audit trail).
        
        Args:
            device_id: Device identifier
            
        Returns:
            bool: True if removed successfully
            
        Example:
            >>> manager.remove_device("abc123")
            True
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE paired_devices 
                SET is_active = 0 
                WHERE device_id = ?
            """, (device_id,))
            
            self.conn.commit()
            
            if cursor.rowcount > 0:
                logger.info(f"Removed device: {device_id}")
                return True
            else:
                logger.warning(f"Device not found: {device_id}")
                return False
        
        except Exception as e:
            logger.error(f"Error removing device: {e}")
            return False
    
    def update_last_used(self, device_id: str) -> bool:
        """
        Update last used timestamp for a device.
        
        Args:
            device_id: Device identifier
            
        Returns:
            bool: True if updated successfully
            
        Example:
            >>> manager.update_last_used("abc123")
            True
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE paired_devices 
                SET last_used = ? 
                WHERE device_id = ? AND is_active = 1
            """, (int(time.time()), device_id))
            
            self.conn.commit()
            return cursor.rowcount > 0
        
        except Exception as e:
            logger.error(f"Error updating last_used: {e}")
            return False
    
    def device_exists(self, device_id: str) -> bool:
        """
        Check if a device is paired and active.
        
        Args:
            device_id: Device identifier
            
        Returns:
            bool: True if device exists and is active
            
        Example:
            >>> manager.device_exists("abc123")
            True
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM paired_devices 
                WHERE device_id = ? AND is_active = 1
            """, (device_id,))
            
            count = cursor.fetchone()[0]
            return count > 0
        
        except Exception as e:
            logger.error(f"Error checking device existence: {e}")
            return False
    
    def get_device_count(self) -> int:
        """
        Get count of active paired devices.
        
        Returns:
            int: Number of active devices
            
        Example:
            >>> manager.get_device_count()
            5
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM paired_devices 
                WHERE is_active = 1
            """)
            
            return cursor.fetchone()[0]
        
        except Exception as e:
            logger.error(f"Error getting device count: {e}")
            return 0
    
    def hard_delete_device(self, device_id: str) -> bool:
        """
        Permanently delete a device from database.
        
        WARNING: This is irreversible. Use remove_device() for soft delete.
        
        Args:
            device_id: Device identifier
            
        Returns:
            bool: True if deleted successfully
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                DELETE FROM paired_devices 
                WHERE device_id = ?
            """, (device_id,))
            
            self.conn.commit()
            
            if cursor.rowcount > 0:
                logger.info(f"Hard deleted device: {device_id}")
                return True
            else:
                return False
        
        except Exception as e:
            logger.error(f"Error hard deleting device: {e}")
            return False
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")


if __name__ == "__main__":
    # Demo usage
    import tempfile
    from crypto_utils import CryptoUtils
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    print("=== BlueZscript Pairing Manager Demo ===")
    print()
    
    # Use temporary database for demo
    temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    manager = PairingManager(temp_db.name)
    
    # Generate test data
    device_id = CryptoUtils.generate_device_id()
    device_name = "Test Phone"
    secret = CryptoUtils.generate_secret()
    
    print(f"Generated Device ID: {device_id}")
    print(f"Device Name: {device_name}")
    print(f"Secret: {secret}")
    print()
    
    # Add device
    print("Adding device...")
    success = manager.add_device(device_id, device_name, secret)
    print(f"Result: {'✓ Success' if success else '✗ Failed'}")
    print()
    
    # List devices
    print("Listing devices:")
    devices = manager.list_devices()
    for device in devices:
        print(f"  - {device['device_name']} (ID: {device['device_id']})")
    print()
    
    # Get device
    print("Getting device details...")
    device = manager.get_device(device_id)
    if device:
        print(f"  Name: {device['device_name']}")
        print(f"  Secret: {device['secret_key']}")
        print(f"  Paired at: {datetime.fromtimestamp(device['paired_at'])}")
    print()
    
    # Update last used
    print("Updating last used timestamp...")
    manager.update_last_used(device_id)
    print("✓ Updated")
    print()
    
    # Device count
    count = manager.get_device_count()
    print(f"Total paired devices: {count}")
    print()
    
    # Remove device
    print("Removing device...")
    manager.remove_device(device_id)
    print("✓ Removed")
    print()
    
    # Verify removal
    exists = manager.device_exists(device_id)
    print(f"Device still exists: {exists}")
    print()
    
    # Cleanup
    manager.close()
    os.unlink(temp_db.name)
    print("Demo complete!")
