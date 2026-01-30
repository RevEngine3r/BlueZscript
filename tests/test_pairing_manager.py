#!/usr/bin/env python3
"""
Unit tests for pairing_manager.py
Tests device storage, encryption, and CRUD operations
"""

import unittest
import os
import sys
import tempfile
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from raspberry_pi.pairing_manager import PairingManager
from raspberry_pi.crypto_utils import CryptoUtils


class TestPairingManager(unittest.TestCase):
    """Test suite for PairingManager class"""
    
    def setUp(self):
        """Create temporary database for each test"""
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()
        self.manager = PairingManager(self.db_path)
    
    def tearDown(self):
        """Clean up after each test"""
        self.manager.close()
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
    
    def test_init(self):
        """Test manager initialization"""
        self.assertIsNotNone(self.manager)
        self.assertIsNotNone(self.manager.conn)
        self.assertIsNotNone(self.manager.cipher)
    
    def test_add_device(self):
        """Test adding a device"""
        device_id = CryptoUtils.generate_device_id()
        secret = CryptoUtils.generate_secret()
        
        result = self.manager.add_device(device_id, "Test Phone", secret)
        
        self.assertTrue(result)
        self.assertTrue(self.manager.device_exists(device_id))
    
    def test_add_duplicate_device(self):
        """Test adding duplicate device (should fail)"""
        device_id = CryptoUtils.generate_device_id()
        secret = CryptoUtils.generate_secret()
        
        # Add first time
        result1 = self.manager.add_device(device_id, "Phone 1", secret)
        self.assertTrue(result1)
        
        # Try to add again (should fail)
        result2 = self.manager.add_device(device_id, "Phone 2", secret)
        self.assertFalse(result2)
    
    def test_get_device(self):
        """Test retrieving a device"""
        device_id = CryptoUtils.generate_device_id()
        secret = CryptoUtils.generate_secret()
        device_name = "Test Phone"
        
        self.manager.add_device(device_id, device_name, secret)
        
        device = self.manager.get_device(device_id)
        
        self.assertIsNotNone(device)
        self.assertEqual(device['device_id'], device_id)
        self.assertEqual(device['device_name'], device_name)
        self.assertEqual(device['secret_key'], secret)  # Should be decrypted
        self.assertIsNotNone(device['paired_at'])
    
    def test_get_nonexistent_device(self):
        """Test getting device that doesn't exist"""
        device = self.manager.get_device("nonexistent_id")
        self.assertIsNone(device)
    
    def test_list_devices(self):
        """Test listing devices"""
        # Add multiple devices
        devices_data = []
        for i in range(3):
            device_id = CryptoUtils.generate_device_id()
            secret = CryptoUtils.generate_secret()
            name = f"Phone {i}"
            self.manager.add_device(device_id, name, secret)
            devices_data.append({'id': device_id, 'name': name})
        
        devices = self.manager.list_devices()
        
        self.assertEqual(len(devices), 3)
        
        # Secrets should not be in list view
        for device in devices:
            self.assertNotIn('secret_key', device)
            self.assertIn('device_id', device)
            self.assertIn('device_name', device)
    
    def test_list_devices_empty(self):
        """Test listing devices when none exist"""
        devices = self.manager.list_devices()
        self.assertEqual(len(devices), 0)
    
    def test_remove_device(self):
        """Test removing a device (soft delete)"""
        device_id = CryptoUtils.generate_device_id()
        secret = CryptoUtils.generate_secret()
        
        self.manager.add_device(device_id, "Test Phone", secret)
        self.assertTrue(self.manager.device_exists(device_id))
        
        result = self.manager.remove_device(device_id)
        
        self.assertTrue(result)
        self.assertFalse(self.manager.device_exists(device_id))
        
        # Device should not be in list
        devices = self.manager.list_devices()
        self.assertEqual(len(devices), 0)
    
    def test_remove_nonexistent_device(self):
        """Test removing device that doesn't exist"""
        result = self.manager.remove_device("nonexistent_id")
        self.assertFalse(result)
    
    def test_update_last_used(self):
        """Test updating last_used timestamp"""
        device_id = CryptoUtils.generate_device_id()
        secret = CryptoUtils.generate_secret()
        
        self.manager.add_device(device_id, "Test Phone", secret)
        
        # Initially last_used should be None
        device = self.manager.get_device(device_id)
        initial_last_used = device['last_used']
        
        # Wait a moment and update
        time.sleep(0.1)
        result = self.manager.update_last_used(device_id)
        
        self.assertTrue(result)
        
        # Verify it was updated
        device = self.manager.get_device(device_id)
        self.assertIsNotNone(device['last_used'])
        if initial_last_used:
            self.assertGreater(device['last_used'], initial_last_used)
    
    def test_device_exists(self):
        """Test checking if device exists"""
        device_id = CryptoUtils.generate_device_id()
        secret = CryptoUtils.generate_secret()
        
        # Should not exist initially
        self.assertFalse(self.manager.device_exists(device_id))
        
        # Add device
        self.manager.add_device(device_id, "Test Phone", secret)
        
        # Should exist now
        self.assertTrue(self.manager.device_exists(device_id))
        
        # Remove device
        self.manager.remove_device(device_id)
        
        # Should not exist after removal
        self.assertFalse(self.manager.device_exists(device_id))
    
    def test_get_device_count(self):
        """Test getting device count"""
        # Initially zero
        self.assertEqual(self.manager.get_device_count(), 0)
        
        # Add devices
        for i in range(5):
            device_id = CryptoUtils.generate_device_id()
            secret = CryptoUtils.generate_secret()
            self.manager.add_device(device_id, f"Phone {i}", secret)
        
        self.assertEqual(self.manager.get_device_count(), 5)
        
        # Remove one
        devices = self.manager.list_devices()
        self.manager.remove_device(devices[0]['device_id'])
        
        self.assertEqual(self.manager.get_device_count(), 4)
    
    def test_encryption(self):
        """Test that secrets are encrypted in database"""
        device_id = CryptoUtils.generate_device_id()
        secret = CryptoUtils.generate_secret()
        
        self.manager.add_device(device_id, "Test Phone", secret)
        
        # Read raw database value
        cursor = self.manager.conn.cursor()
        cursor.execute(
            "SELECT secret_key FROM paired_devices WHERE device_id=?", 
            (device_id,)
        )
        encrypted_secret = cursor.fetchone()[0]
        
        # Encrypted value should not match plain secret
        self.assertNotEqual(encrypted_secret, secret)
        
        # Encrypted value should be longer (due to Fernet format)
        self.assertGreater(len(encrypted_secret), len(secret))
        
        # But decrypted value should match
        device = self.manager.get_device(device_id)
        self.assertEqual(device['secret_key'], secret)
    
    def test_hard_delete(self):
        """Test permanent deletion of device"""
        device_id = CryptoUtils.generate_device_id()
        secret = CryptoUtils.generate_secret()
        
        self.manager.add_device(device_id, "Test Phone", secret)
        
        # Hard delete
        result = self.manager.hard_delete_device(device_id)
        self.assertTrue(result)
        
        # Should not exist at all (even in inactive records)
        cursor = self.manager.conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM paired_devices WHERE device_id=?",
            (device_id,)
        )
        count = cursor.fetchone()[0]
        self.assertEqual(count, 0)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
