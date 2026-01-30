#!/usr/bin/env python3
"""
Unit tests for ble_listener_secure.py
Tests message parsing, authentication, and action execution
"""

import unittest
import os
import sys
import tempfile
import json
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from raspberry_pi.ble_listener_secure import SecureBLEListener
from raspberry_pi.pairing_manager import PairingManager
from raspberry_pi.crypto_utils import CryptoUtils


class TestSecureBLEListener(unittest.TestCase):
    """Test suite for SecureBLEListener class"""
    
    def setUp(self):
        """Set up test environment"""
        # Use temporary database
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.db_path = self.temp_db.name
        self.temp_db.close()
        
        # Create listener with test database
        self.listener = SecureBLEListener()
        self.listener.pairing_manager = PairingManager(self.db_path)
        
        # Add test device
        self.device_id = CryptoUtils.generate_device_id()
        self.secret = CryptoUtils.generate_secret()
        self.device_name = "Test Phone"
        self.listener.pairing_manager.add_device(self.device_id, self.device_name, self.secret)
    
    def tearDown(self):
        """Clean up after tests"""
        self.listener.pairing_manager.close()
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)
    
    def test_parse_message_valid(self):
        """Test parsing valid BLE message"""
        message = {
            'device_id': self.device_id,
            'totp': '123456',
            'timestamp': int(time.time()),
            'action': 'TRIGGER'
        }
        
        data = json.dumps(message).encode('utf-8')
        parsed = self.listener.parse_message(data)
        
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed['device_id'], self.device_id)
        self.assertEqual(parsed['action'], 'TRIGGER')
    
    def test_parse_message_invalid_json(self):
        """Test parsing invalid JSON"""
        data = b"not valid json"
        parsed = self.listener.parse_message(data)
        
        self.assertIsNone(parsed)
    
    def test_parse_message_missing_fields(self):
        """Test parsing message with missing fields"""
        message = {
            'device_id': self.device_id,
            'totp': '123456'
            # Missing timestamp and action
        }
        
        data = json.dumps(message).encode('utf-8')
        parsed = self.listener.parse_message(data)
        
        self.assertIsNone(parsed)
    
    def test_validate_authentication_success(self):
        """Test successful authentication"""
        # Generate valid TOTP
        totp = CryptoUtils.generate_totp(self.secret)
        
        message = {
            'device_id': self.device_id,
            'totp': totp,
            'timestamp': int(time.time()),
            'action': 'TRIGGER'
        }
        
        result = self.listener.validate_authentication(message)
        
        self.assertTrue(result)
        self.assertEqual(self.listener.stats['successful_auth'], 1)
        self.assertEqual(self.listener.stats['failed_auth'], 0)
    
    def test_validate_authentication_unknown_device(self):
        """Test authentication with unknown device"""
        totp = CryptoUtils.generate_totp(self.secret)
        
        message = {
            'device_id': 'unknown_device',
            'totp': totp,
            'timestamp': int(time.time()),
            'action': 'TRIGGER'
        }
        
        result = self.listener.validate_authentication(message)
        
        self.assertFalse(result)
        self.assertEqual(self.listener.stats['failed_auth'], 1)
    
    def test_validate_authentication_invalid_totp(self):
        """Test authentication with invalid TOTP"""
        message = {
            'device_id': self.device_id,
            'totp': '000000',  # Invalid TOTP
            'timestamp': int(time.time()),
            'action': 'TRIGGER'
        }
        
        result = self.listener.validate_authentication(message)
        
        self.assertFalse(result)
        self.assertEqual(self.listener.stats['failed_auth'], 1)
    
    def test_validate_authentication_stale_timestamp(self):
        """Test authentication with stale timestamp"""
        totp = CryptoUtils.generate_totp(self.secret)
        
        message = {
            'device_id': self.device_id,
            'totp': totp,
            'timestamp': int(time.time()) - 600,  # 10 minutes ago
            'action': 'TRIGGER'
        }
        
        result = self.listener.validate_authentication(message)
        
        self.assertFalse(result)
        self.assertEqual(self.listener.stats['failed_auth'], 1)
    
    def test_validate_authentication_updates_last_used(self):
        """Test that successful auth updates last_used"""
        totp = CryptoUtils.generate_totp(self.secret)
        
        message = {
            'device_id': self.device_id,
            'totp': totp,
            'timestamp': int(time.time()),
            'action': 'TRIGGER'
        }
        
        # Get initial last_used
        device = self.listener.pairing_manager.get_device(self.device_id)
        initial_last_used = device['last_used']
        
        # Authenticate
        time.sleep(0.1)
        result = self.listener.validate_authentication(message)
        
        # Check last_used was updated
        device = self.listener.pairing_manager.get_device(self.device_id)
        new_last_used = device['last_used']
        
        self.assertTrue(result)
        if initial_last_used:
            self.assertGreater(new_last_used, initial_last_used)
        else:
            self.assertIsNotNone(new_last_used)
    
    def test_execute_action_trigger(self):
        """Test action execution"""
        # Create a temporary action script
        temp_script = tempfile.NamedTemporaryFile(mode='w', suffix=".sh", delete=False)
        temp_script.write("#!/bin/bash\necho 'Action executed'\nexit 0")
        temp_script.close()
        os.chmod(temp_script.name, 0o755)
        
        # Override action script path
        original_script = self.listener.__class__.__module__
        import raspberry_pi.ble_listener_secure as ble_module
        original_path = ble_module.ACTION_SCRIPT
        ble_module.ACTION_SCRIPT = temp_script.name
        
        try:
            # Execute action
            self.listener.execute_action('TRIGGER', self.device_name)
            
            # Check stats
            self.assertEqual(self.listener.stats['actions_executed'], 1)
        
        finally:
            # Restore original path and cleanup
            ble_module.ACTION_SCRIPT = original_path
            os.unlink(temp_script.name)
    
    def test_stats_tracking(self):
        """Test that statistics are tracked correctly"""
        totp = CryptoUtils.generate_totp(self.secret)
        
        # Successful auth
        message1 = {
            'device_id': self.device_id,
            'totp': totp,
            'timestamp': int(time.time()),
            'action': 'TRIGGER'
        }
        self.listener.validate_authentication(message1)
        
        # Failed auth (invalid TOTP)
        message2 = {
            'device_id': self.device_id,
            'totp': '000000',
            'timestamp': int(time.time()),
            'action': 'TRIGGER'
        }
        self.listener.validate_authentication(message2)
        
        # Check stats
        self.assertEqual(self.listener.stats['total_attempts'], 2)
        self.assertEqual(self.listener.stats['successful_auth'], 1)
        self.assertEqual(self.listener.stats['failed_auth'], 1)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
