#!/bin/bash

# Example action script that gets executed when BLE signal is received
# Customize this script to perform any action you want

echo "[$(date)] BLE trigger received!" >> /var/log/ble_actions.log

# Example actions:

# 1. Turn on an LED (GPIO example)
# echo "1" > /sys/class/gpio/gpio17/value

# 2. Run a command
# espeak "Hello, signal received"

# 3. Control a smart device
# curl -X POST http://192.168.1.100/api/switch/turn_on

# 4. Send a notification
# notify-send "BLE Signal" "Trigger received from phone"

# 5. Execute another Python script
# python3 /home/pi/custom_action.py

# 6. Toggle a service
# systemctl restart some-service

echo "Action completed successfully"
exit 0
