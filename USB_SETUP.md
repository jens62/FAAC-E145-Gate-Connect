# USB Connection Setup Guide for FAAC E145 Controller Board

This guide explains how to setup the USB connection to access the FAAC E145 controller board via the faac-gateway on a Raspberry Pi.

## Table of Contents
1. [Hardware Requirements](#1-hardware-requirements)
2. [USB Device Identification](#2-usb-device-identification)
3. [Driver Installation & Configuration](#3-driver-installation--configuration)
4. [Persistent Configuration](#4-persistent-configuration-survives-reboot)
5. [Serial Port Setup & Permissions](#5-serial-port-setup--permissions)
6. [Testing the Connection](#6-testing-the-connection)
7. [Troubleshooting](#7-troubleshooting-tips)
8. [Protocol Information](#8-protocol-information)
9. [Quick Reference](#quick-reference-commands)

---

## 1. Hardware Requirements

### USB Adapters & Cables
- **FAAC EasyBoard (E145)**: Contains a Texas Instruments USB-to-Serial converter chip
- **USB Cable**: Standard USB Type-A to USB Type-B (or appropriate connector for your board)
- **Active USB Hub** (Recommended): For Raspberry Pi 1/2, an externally powered USB hub solves 90% of driver issues due to power limitations on the Pi's onboard USB port

### Target Hardware
- **Raspberry Pi 2 Model B** (or compatible single-board computer)
- Adequate power supply for the Pi and USB peripherals

---

## 2. USB Device Identification

### Vendor & Product IDs
```
Vendor ID (VID):  22d3
Product ID (PID): 0000
Description:      Texas Instruments Virtual COM Port
```

### Verification Command
```bash
lsusb
```

**Expected Output:**
```
Bus 001 Device 005: ID 22d3:0000 Texas Instruments Virtual COM Port
```

### Device Path on Raspberry Pi
Once properly configured, the device appears as:
```
/dev/ttyUSB1     (primary)
/dev/ttyACM0     (alternative if CDC-ACM is used)
/dev/ttyUSB0     (secondary alternative)
```

### USB Bus Location
The device typically connects at:
```
/sys/bus/usb/devices/1-1.5
```

With two interfaces:
- `1-1.5:1.0` (interface 0)
- `1-1.5:1.1` (interface 1)

---

## 3. Driver Installation & Configuration

### Initial Setup - Loading Kernel Modules

The FAAC board requires the `option` driver (robust serial-over-USB driver) to function on Linux. Here's the step-by-step process:

#### Step 1: Remove Previous Drivers
```bash
sudo modprobe -r usbserial cdc_acm
```

#### Step 2: Load the Option Driver
```bash
sudo modprobe option
```

#### Step 3: Register Hardware ID
```bash
echo "22d3 0000" | sudo tee /sys/bus/usb-serial/drivers/option1/new_id
```

#### Step 4: Bind Device to Driver
If the device doesn't appear automatically, manually bind it:
```bash
echo "1-1.5:1.0" | sudo tee /sys/bus/usb/drivers/option/bind
```

#### Step 5: Verify Device Creation
```bash
ls -l /dev/ttyUSB*
```

**Expected Output:**
```
crw-rw-rw- 1 root dialout 188, 1  4. Feb 09:11 /dev/ttyUSB1
```

---

## 4. Persistent Configuration (Survives Reboot)

To make the driver configuration survive system reboots, implement the following:

### 4.1 Load Modules at Boot

Edit `/etc/modules`:
```bash
sudo nano /etc/modules
```

Add these lines:
```
usbserial
option
```

### 4.2 Create udev Rule

Create file `/etc/udev/rules.d/99-faac.rules`:
```bash
sudo nano /etc/udev/rules.d/99-faac.rules
```

Add this line:
```
ACTION=="add", ATTRS{idVendor}=="22d3", ATTRS{idProduct}=="0000", RUN+="/sbin/modprobe option", RUN+="/bin/sh -c 'sleep 1; echo 22d3 0000 > /sys/bus/usb-serial/drivers/option1/new_id'", MODE="0666", GROUP="dialout"
```

**Key elements:**
- `ACTION=="add"`: Trigger when device is plugged in
- `ATTRS{idVendor}=="22d3"`: Match FAAC vendor ID
- `ATTRS{idProduct}=="0000"`: Match FAAC product ID
- `RUN+="/sbin/modprobe option"`: Load driver
- `RUN+="/bin/sh -c 'sleep 1; ...new_id'"`: Register hardware with 1-second delay
- `MODE="0666"`: Make device readable/writable by all users
- `GROUP="dialout"`: Assign to dialout group for serial access

### 4.3 Reload udev Rules

After creating the rule:
```bash
sudo udevadm control --reload-rules
```

Then replug the device or reboot:
```bash
sudo shutdown -r now
```

---

## 5. Serial Port Setup & Permissions

### Connection Parameters
- **Port**: `/dev/ttyUSB1` (or as identified in your system)
- **Baud Rate**: 115200
- **Data Bits**: 8
- **Stop Bits**: 1
- **Parity**: None
- **Timeout**: 1 second (for read operations)

### Permissions & Access Rights

#### User Access to Serial Port
Ensure your user is in the `dialout` group:
```bash
sudo usermod -a -G dialout $USER
```

Verify membership (requires logout/login):
```bash
groups
```

Should include: `dialout`

#### Device Permissions After Boot
```bash
ls -l /dev/ttyUSB1
```

**Expected:**
```
crw-rw-rw- 1 root dialout 188, 1  [date/time] /dev/ttyUSB1
```

The `rw-rw-rw-` permissions (mode 0666) allow any user to access the port.

---

## 6. Testing the Connection

### 6.1 Basic Connectivity Test

Create a Python test script (`test_faac.py`):

```python
#!/usr/bin/env python3
import serial
import time

PORT = '/dev/ttyUSB1'
BAUD = 115200

try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    print(f"Connected to {PORT}")

    # Status request command (from protocol analysis)
    cmd = bytes.fromhex("023035303030363330333033303330333303")

    print("Sending status request...")
    ser.write(cmd)
    time.sleep(0.1)

    response = ser.read(250)

    if response:
        print(f"Success! Received response:")
        print(f"  Hex: {response.hex().upper()}")
        print(f"  Length: {len(response)} bytes")
    else:
        print("No response received")

    ser.close()
except Exception as e:
    print(f"Error: {e}")
```

Run the test:
```bash
chmod +x test_faac.py
python3 test_faac.py
```

If `pyserial` is not installed:
```bash
pip install pyserial
```

### 6.2 Monitoring Kernel Messages

Watch the kernel log while connecting/disconnecting:
```bash
dmesg -w
```

**Expected output when device is plugged in:**
```
usb 1-1.5: GSM modem (1-port) converter now attached to ttyUSB1
```

### 6.3 Using the FAAC Gateway

Once the gateway is running:
```bash
# Start the gateway
python3 faac_gateway_mqtt.py -c config/config.yaml

# Or using systemd service
sudo systemctl start faac-gateway
```

Check the web interface:
```
http://[PI-IP]:5000
```

---

## 7. Troubleshooting Tips

### Problem: Device not appearing after `lsusb` shows it

**Solution:**
1. Unload conflicting drivers: `sudo modprobe -r cdc_acm usbserial`
2. Load the option driver: `sudo modprobe option`
3. Register the device: `echo "22d3 0000" | sudo tee /sys/bus/usb-serial/drivers/option1/new_id`

### Problem: "Device or resource is busy" error when binding

**Cause:** Another driver already has the interface.

**Solution:**
```bash
# Identify which driver is bound
ls -l /sys/bus/usb/devices/1-1.5:1.0/driver

# Unbind it (replace cdc_acm with actual driver name if different)
echo "1-1.5:1.0" | sudo tee /sys/bus/usb/drivers/cdc_acm/unbind

# Then bind to option
echo "1-1.5:1.0" | sudo tee /sys/bus/usb/drivers/option/bind
```

### Problem: Device disappears after reboot

**Cause:** udev rule or module loading failed during boot.

**Solution:**
1. Verify `/etc/modules` contains `usbserial` and `option`
2. Verify `/etc/udev/rules.d/99-faac.rules` is correct
3. Reload udev rules: `sudo udevadm control --reload-rules`
4. Replug the device or reboot: `sudo shutdown -r now`

### Problem: Permission denied when accessing `/dev/ttyUSB1`

**Solution:**
```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER

# Logout and login again for changes to take effect
```

### Problem: Port seems to work but no response to commands

**Possible causes:**
1. Wrong serial port selected (check `/dev/ttyUSB*` vs `/dev/ttyACM*`)
2. Another process is using the port
3. Wrong baud rate (should be 115200)

**Solution:**
```bash
# Check if port is in use
sudo lsof | grep ttyUSB1

# Verify serial port in config
cat config/config.yaml | grep port
```

### Problem: VirtualHere conflicts

If VirtualHere USB server is installed and conflicts:

**Solution:**
```bash
# Stop VirtualHere
sudo systemctl stop virtualhere

# Disable VirtualHere from starting at boot
sudo systemctl disable virtualhere
```

---

## 8. Protocol Information

### Communication Format
- **Protocol**: Hex-encoded ASCII over serial
- **Baud Rate**: 115200
- **Frame Format**:
  - STX (02) + ASCII-hex payload + ETX (03)

### Status Request Command
```
Hex: 02 30 35 30 30 30 36 33 30 33 30 33 30 33 30 33 38 03
ASCII: <STX>0500063030303038<ETX>
```

### Status Response
- Long ASCII-hex string (typically 200+ bytes)
- Begins with: `02 33 30 30 30 38 36...`
- Contains position data for both wings
- Ends with status indicator before ETX (03)

### Gate Status Codes
Status code appears in the response before ETX marker:
- **`A4`**: Gate is CLOSED (secure)
- **`A3`**: Gate is MOVING or OPEN
- **`A0`**: Alternative moving/open state

---

## Quick Reference Commands

```bash
# Identify device
lsusb | grep "22d3"

# Find serial port
ls -l /dev/ttyUSB*
ls -l /dev/ttyACM*

# Monitor kernel messages
dmesg | tail -20
dmesg | grep -i "attached to"

# Check driver status
ls -l /sys/bus/usb/devices/1-1.5:1.0/driver

# Load drivers manually
sudo modprobe -r cdc_acm usbserial
sudo modprobe option
echo "22d3 0000" | sudo tee /sys/bus/usb-serial/drivers/option1/new_id

# Check permissions
ls -l /dev/ttyUSB1
groups  # Should include 'dialout'

# Test connection
python3 test_faac.py

# Service management
sudo systemctl status faac-gateway
sudo systemctl start faac-gateway
sudo systemctl stop faac-gateway
```

---

## Related Documentation

- [Main README](README.md) - Project overview
- [Installation Guide](scripts/README.md) - Systemd service setup
- [MQTT Setup](MQTT_SETUP.md) - MQTT configuration
- [OpenHAB Integration](openhab/README.md) - OpenHAB setup

---

## Notes

### Why the `option` driver?

The FAAC E145 uses a Texas Instruments USB-to-Serial chip that requires the `option` kernel driver on Linux. This driver is designed for GSM modems and other serial devices that use similar USB chipsets. The default `cdc_acm` driver doesn't work reliably with this hardware.

### Powered USB Hub Recommendation

For Raspberry Pi models 1 and 2, the onboard USB ports have limited power output. Using an externally powered USB hub eliminates many driver and connection stability issues.

### VirtualHere Note

VirtualHere USB Server can be used to share the USB device over the network, but it must be stopped when using direct access via the FAAC gateway software.
