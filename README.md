# BlueZscript

Raspberry Pi 4 BLE (Bluetooth Low Energy) listener that executes custom actions when receiving signals from your phone.

## Features

- 🔵 Listens for BLE notifications from your phone
- ⚡ Executes custom scripts when triggered
- 🔄 Auto-reconnects on disconnect
- 📝 Comprehensive logging
- 🚀 Systemd service for auto-start on boot
- 🔧 Easy configuration

## Prerequisites

- Raspberry Pi 4 (or Pi 3 with BLE support)
- Raspberry Pi OS (Bullseye or newer recommended)
- Python 3.7+
- Bluetooth hardware enabled

## Installation

### 1. Install System Dependencies

```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv bluetooth bluez libbluetooth-dev
```

### 2. Enable Bluetooth

```bash
sudo systemctl enable bluetooth
sudo systemctl start bluetooth
```

### 3. Clone Repository

```bash
cd /opt
sudo git clone https://github.com/RevEngine3r/BlueZscript.git
cd BlueZscript
```

### 4. Set Up Python Environment

```bash
sudo python3 -m venv venv
sudo ./venv/bin/pip install -r requirements.txt
```

### 5. Configure the Script

Edit `ble_listener.py` and update these constants:

```python
CUSTOM_SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"  # Your BLE service UUID
CUSTOM_CHARACTERISTIC_UUID = "12345678-1234-5678-1234-56789abcdef1"  # Your characteristic UUID
TARGET_DEVICE_NAME = "MyPhone"  # Your phone's BLE advertised name
TRIGGER_VALUE = b"TRIGGER"  # The value that triggers the action
```

### 6. Create Your Action Script

Edit `action_script.sh` to define what happens when the trigger is received:

```bash
sudo nano action_script.sh
```

### 7. Test Manually

```bash
sudo ./venv/bin/python3 ble_listener.py
```

## Setting Up as a System Service

### 1. Install the Service

```bash
sudo cp ble-listener.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ble-listener.service
sudo systemctl start ble-listener.service
```

### 2. Check Status

```bash
sudo systemctl status ble-listener.service
```

### 3. View Logs

```bash
sudo journalctl -u ble-listener.service -f
# or
sudo tail -f /var/log/ble_listener.log
```

## Phone App Setup

You'll need a BLE app on your phone to send signals. Recommended apps:

### Android
- **nRF Connect** (Nordic Semiconductor)
- **BLE Scanner**
- **LightBlue**

### iOS
- **LightBlue**
- **nRF Connect**

### Steps to Send Trigger

1. Open your BLE app
2. Create a custom service with the UUID you configured
3. Add a characteristic with notify/write properties
4. Send the trigger value (e.g., "TRIGGER") to activate the script

### Alternative: Create Your Own App

You can create a simple app using:
- **React Native**: `react-native-ble-plx`
- **Flutter**: `flutter_blue_plus`
- **Swift (iOS)**: CoreBluetooth framework
- **Kotlin (Android)**: Android BLE APIs

## Configuration Examples

### Example 1: Control GPIO LED

```bash
#!/bin/bash
# action_script.sh
echo "17" > /sys/class/gpio/export
echo "out" > /sys/class/gpio/gpio17/direction
echo "1" > /sys/class/gpio/gpio17/value
sleep 2
echo "0" > /sys/class/gpio/gpio17/value
```

### Example 2: Run Home Automation Command

```bash
#!/bin/bash
# action_script.sh
curl -X POST http://192.168.1.100:8123/api/services/light/toggle \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "light.living_room"}'
```

### Example 3: Trigger a Python Script

```bash
#!/bin/bash
# action_script.sh
/opt/BlueZscript/venv/bin/python3 /home/pi/my_custom_script.py
```

## Troubleshooting

### Bluetooth Not Working

```bash
sudo rfkill unblock bluetooth
sudo hciconfig hci0 up
```

### Permission Denied

```bash
sudo usermod -a -G bluetooth $USER
sudo chmod +x action_script.sh
```

### Can't Find Device

- Ensure Bluetooth is enabled on your phone
- Check that your phone's BLE name matches `TARGET_DEVICE_NAME`
- Try setting `TARGET_DEVICE_NAME = None` to accept any device
- Verify your phone is advertising the correct service UUID

### Script Not Executing

- Check logs: `sudo tail -f /var/log/ble_listener.log`
- Verify trigger value matches exactly
- Ensure action_script.sh is executable
- Test action_script.sh manually: `./action_script.sh`

## Security Considerations

- Change default UUIDs to custom values
- Use BLE pairing/bonding for secure connections
- Restrict action_script.sh permissions
- Consider implementing authentication in your phone app
- Use firewall rules to limit network access if scripts make network calls

## Advanced Usage

### Multiple Triggers

Modify `notification_handler()` to handle different trigger values:

```python
def notification_handler(self, sender, data):
    if data == b"TRIGGER1":
        self.execute_action("./action1.sh")
    elif data == b"TRIGGER2":
        self.execute_action("./action2.sh")
```

### Read Sensor Data

Instead of just listening, you can also send data back to your phone by writing to characteristics.

## Contributing

Feel free to submit issues and pull requests!

## License

MIT License - Feel free to use and modify for your projects.

## Author

**RevEngine3r**
- GitHub: [@RevEngine3r](https://github.com/RevEngine3r)
- Website: [RevEngine3r.iR](https://www.RevEngine3r.iR)

---

**Made with ❤️ for IoT and Home Automation Projects**
