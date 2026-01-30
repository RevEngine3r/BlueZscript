#!/usr/bin/env python3
"""
Cryptographic Utilities for Secure BLE Authentication
Provides TOTP generation/validation, HMAC signing, and secure key generation
"""

import pyotp
import hmac
import hashlib
import base64
import secrets
import time
from typing import Optional

# Configuration constants
TOTP_INTERVAL = 30  # 30-second time step
TOTP_DIGITS = 6     # 6-digit codes
TIMESTAMP_TOLERANCE = 300  # 5 minutes tolerance for replay protection


class CryptoUtils:
    """
    Cryptographic utilities for secure BLE authentication.
    
    Provides:
    - TOTP (Time-based One-Time Password) generation and validation
    - HMAC-SHA256 message signing and verification
    - Secure random key generation
    - Timestamp validation for replay attack prevention
    """
    
    @staticmethod
    def generate_secret() -> str:
        """
        Generate a cryptographically secure random secret.
        
        Uses Python's secrets module (CSPRNG) to generate a 32-byte
        random value encoded as base32 for TOTP compatibility.
        
        Returns:
            str: 32-character base32-encoded secret string
            
        Example:
            >>> secret = CryptoUtils.generate_secret()
            >>> len(secret)
            32
            >>> secret.isalnum()
            True
        """
        # Generate 20 random bytes (160 bits of entropy)
        random_bytes = secrets.token_bytes(20)
        # Encode as base32 for TOTP compatibility
        secret = base64.b32encode(random_bytes).decode('utf-8')
        return secret
    
    @staticmethod
    def generate_totp(secret: str) -> str:
        """
        Generate a TOTP code from a secret.
        
        Creates a 6-digit time-based one-time password using the
        current timestamp and the provided secret key.
        
        Args:
            secret: Base32-encoded secret string
            
        Returns:
            str: 6-digit TOTP code
            
        Example:
            >>> secret = "JBSWY3DPEHPK3PXP"
            >>> code = CryptoUtils.generate_totp(secret)
            >>> len(code)
            6
            >>> code.isdigit()
            True
        """
        totp = pyotp.TOTP(secret, interval=TOTP_INTERVAL, digits=TOTP_DIGITS)
        return totp.now()
    
    @staticmethod
    def verify_totp(secret: str, token: str, window: int = 1) -> bool:
        """
        Verify a TOTP token against a secret.
        
        Validates the provided token against the secret, allowing for
        clock skew by checking adjacent time windows.
        
        Args:
            secret: Base32-encoded secret string
            token: 6-digit TOTP code to validate
            window: Number of time steps to check before/after (default: 1)
                   window=1 allows ±30 seconds tolerance
                   
        Returns:
            bool: True if token is valid, False otherwise
            
        Example:
            >>> secret = CryptoUtils.generate_secret()
            >>> token = CryptoUtils.generate_totp(secret)
            >>> CryptoUtils.verify_totp(secret, token)
            True
        """
        try:
            totp = pyotp.TOTP(secret, interval=TOTP_INTERVAL, digits=TOTP_DIGITS)
            # Verify with time window tolerance
            return totp.verify(token, valid_window=window)
        except Exception:
            # Invalid secret format or other error
            return False
    
    @staticmethod
    def sign_message(secret: str, message: str) -> str:
        """
        Sign a message using HMAC-SHA256.
        
        Creates a cryptographic signature of the message using the
        provided secret as the HMAC key.
        
        Args:
            secret: Secret key for HMAC
            message: Message to sign
            
        Returns:
            str: Base64-encoded HMAC-SHA256 signature
            
        Example:
            >>> secret = "my_secret_key"
            >>> message = "important data"
            >>> sig = CryptoUtils.sign_message(secret, message)
            >>> isinstance(sig, str)
            True
        """
        # Encode inputs to bytes
        key_bytes = secret.encode('utf-8')
        msg_bytes = message.encode('utf-8')
        
        # Create HMAC-SHA256 signature
        signature = hmac.new(key_bytes, msg_bytes, hashlib.sha256).digest()
        
        # Return base64-encoded signature
        return base64.b64encode(signature).decode('utf-8')
    
    @staticmethod
    def verify_signature(secret: str, message: str, signature: str) -> bool:
        """
        Verify an HMAC-SHA256 signature.
        
        Uses constant-time comparison to prevent timing attacks.
        
        Args:
            secret: Secret key used for signing
            message: Original message that was signed
            signature: Base64-encoded signature to verify
            
        Returns:
            bool: True if signature is valid, False otherwise
            
        Example:
            >>> secret = "my_secret_key"
            >>> message = "important data"
            >>> sig = CryptoUtils.sign_message(secret, message)
            >>> CryptoUtils.verify_signature(secret, message, sig)
            True
        """
        try:
            # Generate expected signature
            expected_signature = CryptoUtils.sign_message(secret, message)
            
            # Constant-time comparison to prevent timing attacks
            return hmac.compare_digest(expected_signature, signature)
        except Exception:
            return False
    
    @staticmethod
    def validate_timestamp(timestamp: int, tolerance: int = TIMESTAMP_TOLERANCE) -> bool:
        """
        Validate that a timestamp is recent.
        
        Checks if the provided timestamp is within the tolerance window
        of the current time. Used to prevent replay attacks.
        
        Args:
            timestamp: Unix timestamp (seconds since epoch)
            tolerance: Maximum age in seconds (default: 300 = 5 minutes)
            
        Returns:
            bool: True if timestamp is fresh, False if too old or in future
            
        Example:
            >>> import time
            >>> now = int(time.time())
            >>> CryptoUtils.validate_timestamp(now)
            True
            >>> CryptoUtils.validate_timestamp(now - 600)  # 10 minutes ago
            False
        """
        current_time = int(time.time())
        time_diff = abs(current_time - timestamp)
        return time_diff <= tolerance
    
    @staticmethod
    def generate_device_id() -> str:
        """
        Generate a unique device identifier.
        
        Creates a random 16-character hex string for device identification.
        
        Returns:
            str: 16-character hexadecimal device ID
            
        Example:
            >>> device_id = CryptoUtils.generate_device_id()
            >>> len(device_id)
            16
        """
        return secrets.token_hex(8)  # 8 bytes = 16 hex characters


if __name__ == "__main__":
    # Demo usage
    print("=== BlueZscript Crypto Utilities Demo ===")
    print()
    
    # Generate a secret
    secret = CryptoUtils.generate_secret()
    print(f"Generated Secret: {secret}")
    print(f"Secret Length: {len(secret)} characters")
    print()
    
    # Generate TOTP
    totp_code = CryptoUtils.generate_totp(secret)
    print(f"Current TOTP Code: {totp_code}")
    print()
    
    # Verify TOTP
    is_valid = CryptoUtils.verify_totp(secret, totp_code)
    print(f"TOTP Verification: {'✓ Valid' if is_valid else '✗ Invalid'}")
    print()
    
    # Sign a message
    message = "TRIGGER_ACTION"
    signature = CryptoUtils.sign_message(secret, message)
    print(f"Message: {message}")
    print(f"Signature: {signature}")
    print()
    
    # Verify signature
    sig_valid = CryptoUtils.verify_signature(secret, message, signature)
    print(f"Signature Verification: {'✓ Valid' if sig_valid else '✗ Invalid'}")
    print()
    
    # Timestamp validation
    current_ts = int(time.time())
    is_fresh = CryptoUtils.validate_timestamp(current_ts)
    print(f"Current Timestamp: {current_ts}")
    print(f"Timestamp Valid: {'✓ Fresh' if is_fresh else '✗ Stale'}")
    print()
    
    # Generate device ID
    device_id = CryptoUtils.generate_device_id()
    print(f"Device ID: {device_id}")
