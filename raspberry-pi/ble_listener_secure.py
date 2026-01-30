#!/usr/bin/env python3
"""
Secure BLE Listener for BlueZscript
Listens for authenticated BLE signals and executes actions
"""

import asyncio
import subprocess
import logging
import json
import sys
import os
from bleak import BleakScanner, BleakClient
from typing import Optional, Dict
import time

from pairing_manager import PairingManager
from crypto_utils import CryptoUtils

# Configuration
BLE_SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"
BLE_CHARACTERISTIC_UUID = "12345678-1234-5678-1234-56789abcdef1"
ACTION_SCRIPT = "/opt/BlueZscript/action_script.sh"
SCAN_TIMEOUT = 10.0  # seconds
RECONNECT_DELAY = 10  # seconds

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/ble_listener_secure.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class SecureBLEListener:
    """
    Secure BLE listener with TOTP authentication.
    
    Features:
    - Device pairing verification
    - TOTP validation (30-second window)
    - Timestamp validation (replay protection)
    - Comprehensive security logging
    - Auto-reconnect on disconnect
    """
    
    def __init__(self):
        self.pairing_manager = PairingManager()
        self.running = True
        self.client: Optional[BleakClient] = None
        self.stats = {
            'total_attempts': 0,
            'successful_auth': 0,
            'failed_auth': 0,
            'actions_executed': 0
        }
    
    def parse_message(self, data: bytes) -> Optional[Dict]:
        """
        Parse BLE message.
        
        Expected format:
        {
            "device_id": "abc123",
            "totp": "123456",
            "timestamp": 1738267890,
            "action": "TRIGGER"
        }
        
        Args:
            data: Raw BLE data
            
        Returns:
            Parsed message dict or None if invalid
        """
        try:
            message_str = data.decode('utf-8')
            message = json.loads(message_str)
            
            # Validate required fields
            required_fields = ['device_id', 'totp', 'timestamp', 'action']
            if not all(field in message for field in required_fields):
                logger.warning(f"Missing required fields in message: {message.keys()}")
                return None
            
            return message
        
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON in BLE message: {data}")
            return None
        except UnicodeDecodeError:
            logger.warning(f"Invalid UTF-8 in BLE message")
            return None
        except Exception as e:
            logger.error(f"Error parsing message: {e}")
            return None
    
    def validate_authentication(self, message: Dict) -> bool:
        """
        Validate BLE message authentication.
        
        Multi-layer validation:
        1. Device is paired
        2. TOTP is valid
        3. Timestamp is fresh
        
        Args:
            message: Parsed message dict
            
        Returns:
            True if authenticated, False otherwise
        """
        device_id = message['device_id']
        totp = message['totp']
        timestamp = message['timestamp']
        
        self.stats['total_attempts'] += 1
        
        # Layer 1: Check if device is paired
        if not self.pairing_manager.device_exists(device_id):
            logger.warning(f"Authentication failed: Unknown device {device_id}")
            self.stats['failed_auth'] += 1
            return False
        
        # Get device details (including secret)
        device = self.pairing_manager.get_device(device_id)
        if not device:
            logger.error(f"Device {device_id} exists but could not retrieve details")
            self.stats['failed_auth'] += 1
            return False
        
        secret = device['secret_key']
        device_name = device['device_name']
        
        # Layer 2: Validate TOTP
        if not CryptoUtils.verify_totp(secret, totp):
            logger.warning(f"Authentication failed: Invalid TOTP from {device_name} ({device_id})")
            self.stats['failed_auth'] += 1
            return False
        
        # Layer 3: Validate timestamp (replay protection)
        if not CryptoUtils.validate_timestamp(timestamp):
            logger.warning(f"Authentication failed: Stale timestamp from {device_name} ({device_id})")
            self.stats['failed_auth'] += 1
            return False
        
        # All checks passed
        logger.info(f"Authentication successful: {device_name} ({device_id})")
        self.stats['successful_auth'] += 1
        
        # Update last_used timestamp
        self.pairing_manager.update_last_used(device_id)
        
        return True
    
    def execute_action(self, action: str, device_name: str):
        """
        Execute the specified action.
        
        Args:
            action: Action to execute (currently only TRIGGER supported)
            device_name: Name of device that triggered action
        """
        try:
            if action != "TRIGGER":
                logger.warning(f"Unknown action requested: {action}")
                return
            
            if not os.path.exists(ACTION_SCRIPT):
                logger.error(f"Action script not found: {ACTION_SCRIPT}")
                return
            
            # Make script executable if it isn't
            os.chmod(ACTION_SCRIPT, 0o755)
            
            logger.info(f"Executing action '{action}' triggered by {device_name}")
            
            result = subprocess.run(
                [ACTION_SCRIPT],
                capture_output=True,
                text=True,
                timeout=30,
                env={**os.environ, 'TRIGGER_DEVICE': device_name}
            )
            
            if result.returncode == 0:
                logger.info(f"Action executed successfully: {result.stdout.strip()}")
                self.stats['actions_executed'] += 1
            else:
                logger.error(f"Action script failed: {result.stderr.strip()}")
        
        except subprocess.TimeoutExpired:
            logger.error("Action script timed out (30s)")
        except Exception as e:
            logger.error(f"Error executing action: {e}")
    
    def notification_handler(self, sender, data: bytes):
        """
        Handle BLE notifications.
        
        Args:
            sender: BLE characteristic handle
            data: Raw notification data
        """
        logger.debug(f"Received notification from {sender}: {len(data)} bytes")
        
        # Parse message
        message = self.parse_message(data)
        if not message:
            return
        
        logger.info(f"Received message: action={message['action']}, device={message['device_id']}")
        
        # Authenticate
        if not self.validate_authentication(message):
            return
        
        # Get device name for logging
        device = self.pairing_manager.get_device(message['device_id'])
        device_name = device['device_name'] if device else 'Unknown'
        
        # Execute action
        self.execute_action(message['action'], device_name)
    
    async def scan_for_devices(self) -> list:
        """
        Scan for BLE devices.
        
        Returns:
            List of discovered devices
        """
        logger.info("Scanning for BLE devices...")
        
        try:
            devices = await BleakScanner.discover(timeout=SCAN_TIMEOUT)
            logger.info(f"Found {len(devices)} BLE devices")
            
            for device in devices:
                logger.debug(f"  - {device.name or 'Unknown'} ({device.address})")
            
            return devices
        
        except Exception as e:
            logger.error(f"Error scanning for devices: {e}")
            return []
    
    async def connect_and_listen(self, address: str):
        """
        Connect to BLE device and listen for notifications.
        
        Args:
            address: BLE device address
        """
        try:
            async with BleakClient(address, timeout=15.0) as client:
                self.client = client
                logger.info(f"Connected to {address}")
                
                # List available services (for debugging)
                services = await client.get_services()
                logger.debug("Available services:")
                for service in services:
                    logger.debug(f"  Service: {service.uuid}")
                    for char in service.characteristics:
                        logger.debug(f"    Characteristic: {char.uuid} - {char.properties}")
                
                # Subscribe to notifications
                try:
                    await client.start_notify(BLE_CHARACTERISTIC_UUID, self.notification_handler)
                    logger.info(f"Subscribed to notifications on {BLE_CHARACTERISTIC_UUID}")
                    
                    # Keep connection alive
                    while self.running and client.is_connected:
                        await asyncio.sleep(1)
                
                except Exception as e:
                    logger.error(f"Error subscribing to characteristic: {e}")
                    logger.info("Make sure the characteristic UUID is correct and supports notifications")
        
        except asyncio.TimeoutError:
            logger.warning(f"Connection timeout to {address}")
        except Exception as e:
            logger.error(f"Connection error: {e}")
    
    async def run(self):
        """
        Main event loop.
        """
        logger.info("=== Secure BLE Listener Started ===")
        logger.info(f"Paired devices: {self.pairing_manager.get_device_count()}")
        logger.info(f"BLE Service UUID: {BLE_SERVICE_UUID}")
        logger.info(f"BLE Characteristic UUID: {BLE_CHARACTERISTIC_UUID}")
        logger.info(f"Action script: {ACTION_SCRIPT}")
        
        while self.running:
            try:
                # Scan for devices
                devices = await self.scan_for_devices()
                
                # Try to connect to first available device
                # In production, you'd filter by service UUID
                if devices:
                    for device in devices:
                        if self.running:
                            await self.connect_and_listen(device.address)
                            logger.info("Disconnected. Rescanning...")
                else:
                    logger.info("No devices found. Retrying...")
                
                # Wait before next scan
                await asyncio.sleep(RECONNECT_DELAY)
            
            except KeyboardInterrupt:
                logger.info("Shutting down...")
                self.running = False
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                await asyncio.sleep(RECONNECT_DELAY)
        
        # Print final stats
        logger.info("=== Final Statistics ===")
        logger.info(f"Total auth attempts: {self.stats['total_attempts']}")
        logger.info(f"Successful authentications: {self.stats['successful_auth']}")
        logger.info(f"Failed authentications: {self.stats['failed_auth']}")
        logger.info(f"Actions executed: {self.stats['actions_executed']}")
    
    def stop(self):
        """Stop the listener."""
        self.running = False
        if self.client and self.client.is_connected:
            asyncio.create_task(self.client.disconnect())


def main():
    """Entry point."""
    listener = SecureBLEListener()
    
    try:
        asyncio.run(listener.run())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    finally:
        listener.stop()
        logger.info("Secure BLE Listener stopped")


if __name__ == "__main__":
    main()
