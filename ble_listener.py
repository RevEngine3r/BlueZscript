#!/usr/bin/env python3
"""
Bluetooth Low Energy (BLE) Listener for Raspberry Pi 4
Listens for signals from a phone and executes a custom script
"""

import asyncio
import subprocess
import logging
from bleak import BleakScanner, BleakClient
import sys
import os

# Configuration
CUSTOM_SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"  # Change this to your service UUID
CUSTOM_CHARACTERISTIC_UUID = "12345678-1234-5678-1234-56789abcdef1"  # Change this to your characteristic UUID
TARGET_DEVICE_NAME = "MyPhone"  # Change to your phone's BLE name (or set to None to accept any device)
ACTION_SCRIPT = "./action_script.sh"  # Script to execute when signal is received
TRIGGER_VALUE = b"TRIGGER"  # The value that triggers the action

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/ble_listener.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class BLEListener:
    def __init__(self):
        self.client = None
        self.target_address = None
        self.running = True

    async def scan_for_device(self):
        """Scan for the target BLE device"""
        logger.info(f"Scanning for device: {TARGET_DEVICE_NAME or 'Any device'}...")
        
        devices = await BleakScanner.discover(timeout=10.0)
        
        for device in devices:
            logger.debug(f"Found device: {device.name} ({device.address})")
            
            # Match by name if specified, otherwise accept first device with our service
            if TARGET_DEVICE_NAME is None or device.name == TARGET_DEVICE_NAME:
                logger.info(f"Target device found: {device.name} ({device.address})")
                return device.address
        
        logger.warning("Target device not found")
        return None

    def notification_handler(self, sender, data):
        """Handle notifications from the BLE characteristic"""
        logger.info(f"Received notification from {sender}: {data}")
        
        if data == TRIGGER_VALUE:
            logger.info("Trigger value received! Executing action script...")
            self.execute_action()
        else:
            logger.debug(f"Received non-trigger value: {data}")

    def execute_action(self):
        """Execute the custom action script"""
        try:
            if not os.path.exists(ACTION_SCRIPT):
                logger.error(f"Action script not found: {ACTION_SCRIPT}")
                return
            
            # Make script executable if it isn't
            os.chmod(ACTION_SCRIPT, 0o755)
            
            result = subprocess.run(
                [ACTION_SCRIPT],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"Action script executed successfully: {result.stdout}")
            else:
                logger.error(f"Action script failed: {result.stderr}")
        
        except subprocess.TimeoutExpired:
            logger.error("Action script timed out")
        except Exception as e:
            logger.error(f"Error executing action script: {e}")

    async def connect_and_listen(self, address):
        """Connect to device and listen for notifications"""
        try:
            async with BleakClient(address) as client:
                self.client = client
                logger.info(f"Connected to {address}")
                
                # List available services
                services = await client.get_services()
                logger.info("Available services:")
                for service in services:
                    logger.info(f"  Service: {service.uuid}")
                    for char in service.characteristics:
                        logger.info(f"    Characteristic: {char.uuid} - Properties: {char.properties}")
                
                # Subscribe to notifications
                try:
                    await client.start_notify(CUSTOM_CHARACTERISTIC_UUID, self.notification_handler)
                    logger.info(f"Subscribed to notifications on {CUSTOM_CHARACTERISTIC_UUID}")
                    
                    # Keep connection alive
                    while self.running and client.is_connected:
                        await asyncio.sleep(1)
                
                except Exception as e:
                    logger.error(f"Error subscribing to characteristic: {e}")
                    logger.info("Make sure the characteristic UUID is correct and supports notifications")
                
        except Exception as e:
            logger.error(f"Connection error: {e}")

    async def run(self):
        """Main loop"""
        logger.info("BLE Listener started")
        
        while self.running:
            try:
                # Scan for device
                address = await self.scan_for_device()
                
                if address:
                    # Connect and listen
                    await self.connect_and_listen(address)
                    logger.info("Disconnected. Will rescan...")
                else:
                    logger.info("Device not found. Retrying in 10 seconds...")
                
                await asyncio.sleep(10)
            
            except KeyboardInterrupt:
                logger.info("Shutting down...")
                self.running = False
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                await asyncio.sleep(10)


def main():
    """Entry point"""
    listener = BLEListener()
    
    try:
        asyncio.run(listener.run())
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    finally:
        logger.info("BLE Listener stopped")


if __name__ == "__main__":
    main()
