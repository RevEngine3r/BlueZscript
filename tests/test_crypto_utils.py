#!/usr/bin/env python3
"""
Unit tests for crypto_utils.py
Tests TOTP generation/validation, HMAC signing, and key generation
"""

import unittest
import time
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from raspberry_pi.crypto_utils import CryptoUtils


class TestCryptoUtils(unittest.TestCase):
    """Test suite for CryptoUtils class"""
    
    def test_generate_secret(self):
        """Test secret generation produces valid base32 strings"""
        secret = CryptoUtils.generate_secret()
        
        # Should be 32 characters
        self.assertEqual(len(secret), 32)
        
        # Should be alphanumeric (base32)
        self.assertTrue(secret.isalnum())
        
        # Should be uppercase (base32 standard)
        self.assertTrue(secret.isupper())
    
    def test_secret_uniqueness(self):
        """Test that generated secrets are unique"""
        secrets = [CryptoUtils.generate_secret() for _ in range(100)]
        
        # All secrets should be unique
        self.assertEqual(len(secrets), len(set(secrets)))
    
    def test_totp_generation(self):
        """Test TOTP code generation"""
        secret = CryptoUtils.generate_secret()
        totp = CryptoUtils.generate_totp(secret)
        
        # Should be 6 digits
        self.assertEqual(len(totp), 6)
        
        # Should be numeric
        self.assertTrue(totp.isdigit())
    
    def test_totp_validation_valid(self):
        """Test TOTP validation with valid code"""
        secret = CryptoUtils.generate_secret()
        totp = CryptoUtils.generate_totp(secret)
        
        # Current code should validate
        self.assertTrue(CryptoUtils.verify_totp(secret, totp))
    
    def test_totp_validation_invalid(self):
        """Test TOTP validation with invalid code"""
        secret = CryptoUtils.generate_secret()
        
        # Random code should not validate
        self.assertFalse(CryptoUtils.verify_totp(secret, "999999"))
        self.assertFalse(CryptoUtils.verify_totp(secret, "000000"))
    
    def test_totp_time_window(self):
        """Test TOTP validation with time window tolerance"""
        secret = "JBSWY3DPEHPK3PXP"  # Fixed secret for reproducibility
        
        # Generate code and verify it validates with window
        totp = CryptoUtils.generate_totp(secret)
        self.assertTrue(CryptoUtils.verify_totp(secret, totp, window=1))
    
    def test_hmac_signature_generation(self):
        """Test HMAC signature generation"""
        secret = "test_secret_key"
        message = "test message"
        
        signature = CryptoUtils.sign_message(secret, message)
        
        # Should return a string
        self.assertIsInstance(signature, str)
        
        # Should be base64 encoded (only valid base64 chars)
        self.assertTrue(all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=' for c in signature))
    
    def test_hmac_signature_verification_valid(self):
        """Test HMAC signature verification with valid signature"""
        secret = "test_secret_key"
        message = "test message"
        
        signature = CryptoUtils.sign_message(secret, message)
        
        # Signature should verify
        self.assertTrue(CryptoUtils.verify_signature(secret, message, signature))
    
    def test_hmac_signature_verification_invalid(self):
        """Test HMAC signature verification with tampered data"""
        secret = "test_secret_key"
        message = "test message"
        
        signature = CryptoUtils.sign_message(secret, message)
        
        # Modified message should fail verification
        self.assertFalse(CryptoUtils.verify_signature(secret, "tampered message", signature))
        
        # Different secret should fail verification
        self.assertFalse(CryptoUtils.verify_signature("wrong_secret", message, signature))
        
        # Random signature should fail
        self.assertFalse(CryptoUtils.verify_signature(secret, message, "invalid_signature"))
    
    def test_hmac_signature_consistency(self):
        """Test that same input produces same signature"""
        secret = "test_secret_key"
        message = "test message"
        
        sig1 = CryptoUtils.sign_message(secret, message)
        sig2 = CryptoUtils.sign_message(secret, message)
        
        # Should be deterministic
        self.assertEqual(sig1, sig2)
    
    def test_timestamp_validation_current(self):
        """Test timestamp validation with current time"""
        now = int(time.time())
        
        # Current timestamp should be valid
        self.assertTrue(CryptoUtils.validate_timestamp(now))
    
    def test_timestamp_validation_recent(self):
        """Test timestamp validation with recent time"""
        # 2 minutes ago should be valid (within 5 minute tolerance)
        two_minutes_ago = int(time.time()) - 120
        self.assertTrue(CryptoUtils.validate_timestamp(two_minutes_ago))
    
    def test_timestamp_validation_old(self):
        """Test timestamp validation with old time"""
        # 10 minutes ago should be invalid (outside 5 minute tolerance)
        ten_minutes_ago = int(time.time()) - 600
        self.assertFalse(CryptoUtils.validate_timestamp(ten_minutes_ago))
    
    def test_timestamp_validation_future(self):
        """Test timestamp validation with future time"""
        # 10 minutes in future should be invalid
        ten_minutes_future = int(time.time()) + 600
        self.assertFalse(CryptoUtils.validate_timestamp(ten_minutes_future))
    
    def test_timestamp_validation_custom_tolerance(self):
        """Test timestamp validation with custom tolerance"""
        # 2 minutes ago with 1 minute tolerance should fail
        two_minutes_ago = int(time.time()) - 120
        self.assertFalse(CryptoUtils.validate_timestamp(two_minutes_ago, tolerance=60))
        
        # 30 seconds ago with 1 minute tolerance should pass
        thirty_seconds_ago = int(time.time()) - 30
        self.assertTrue(CryptoUtils.validate_timestamp(thirty_seconds_ago, tolerance=60))
    
    def test_device_id_generation(self):
        """Test device ID generation"""
        device_id = CryptoUtils.generate_device_id()
        
        # Should be 16 characters
        self.assertEqual(len(device_id), 16)
        
        # Should be hexadecimal
        self.assertTrue(all(c in '0123456789abcdef' for c in device_id))
    
    def test_device_id_uniqueness(self):
        """Test that device IDs are unique"""
        ids = [CryptoUtils.generate_device_id() for _ in range(100)]
        
        # All IDs should be unique
        self.assertEqual(len(ids), len(set(ids)))


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
