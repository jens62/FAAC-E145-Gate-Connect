# FAAC EasyBoard Software Guide

This guide explains how to access the official FAAC EasyBoard Windows software and the different deployment options when using a Raspberry Pi gateway.

## Table of Contents

1. [Downloading FAAC EasyBoard Software](#downloading-faac-easyboard-software)
2. [Deployment Options](#deployment-options)
3. [Option A: Direct USB Access (faac-gateway)](#option-a-direct-usb-access-faac-gateway)
4. [Option B: VirtualHere USB over Network](#option-b-virtualhere-usb-over-network)
5. [Option C: Advanced USB Traffic Capture](#option-c-advanced-usb-traffic-capture)
6. [Switching Between Modes](#switching-between-modes)

---

## Downloading FAAC EasyBoard Software

### Official Download

The FAAC EasyBoard Windows application is available from FAAC's official support site:

1. Visit the [FAAC Support Page](https://www.faac.biz/support/manuals-and-certificates)
2. Click on **"Software"** in the categories
3. You'll be directed to a Dropbox folder with the EasyBoard software
4. Download the appropriate version for your Windows system

**Direct link** (may change, use official page if broken):
- [FAAC EasyBoard on Dropbox](https://www.dropbox.com/scl/fo/2um9pp2enr4odt6g89hbq/AJo2MRIotBLcW7ytdhavGR4/EasyBoard?dl=0&rlkey=2e6b63it7r81ztf7flp35apm0)

> **Note**: The Dropbox link is provided by FAAC and may change. If the direct link doesn't work, use the official FAAC support page navigation.

### System Requirements

- **OS**: Windows 7/8/10/11
- **USB**: Standard USB port for direct connection, or network access for VirtualHere
- **.NET Framework**: May be required (typically pre-installed on modern Windows)

---

## Deployment Options

When using a Raspberry Pi as a gateway, you have several options for accessing the FAAC E145 controller:

| Option | Use Case | Pros | Cons |
|--------|----------|------|------|
| **A: Direct USB** | Home automation via MQTT | ✅ MQTT/OpenHAB/HA integration<br>✅ Automatic control<br>✅ No Windows needed | ❌ Can't use FAAC software simultaneously |
| **B: VirtualHere** | Remote access to FAAC software | ✅ Run official FAAC software remotely<br>✅ Good for configuration/diagnostics | ❌ Requires Windows PC<br>❌ Can't run faac-gateway simultaneously |
| **C: USB Traffic Capture** | Advanced monitoring | ✅ Record and replay USB traffic<br>✅ Protocol analysis | ❌ Complex setup<br>❌ Requires additional tools |

**Important**: The USB port can only be used by **one application at a time**. You must choose between faac-gateway and VirtualHere, or use the advanced USB traffic capture method.

---

## Option A: Direct USB Access (faac-gateway)

This is the **recommended option** for home automation and MQTT integration.

### Overview

The Raspberry Pi connects directly to the FAAC E145 controller via USB and runs the faac-gateway software. This provides:
- MQTT integration for Home Assistant, OpenHAB, etc.
- Web interface for manual control
- Real-time status updates
- Position control (0-100%)

### Setup

See the main documentation:
- [USB Setup Guide](../USB_SETUP.md) - USB driver configuration
- [Installation Guide](../scripts/README.md) - Systemd service setup
- [MQTT Setup](../MQTT_SETUP.md) - MQTT configuration
- [OpenHAB Integration](../openhab/README.md) - OpenHAB setup

### When to Use

✅ You want home automation integration
✅ You want automatic gate control via MQTT
✅ You don't need the official FAAC software regularly
✅ You want 24/7 monitoring and control

---

## Option B: VirtualHere USB over Network

VirtualHere allows you to share the USB device over the network, making it accessible to the FAAC EasyBoard Windows software running on a remote PC.

### Overview

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│  FAAC E145      │  USB    │  Raspberry Pi    │ Network │  Windows PC     │
│  Controller     ├────────►│  VirtualHere     ├────────►│  FAAC EasyBoard │
│                 │         │  Server          │         │  VirtualHere    │
└─────────────────┘         └──────────────────┘         │  Client         │
                                                          └─────────────────┘
```

### VirtualHere Server Setup (Raspberry Pi)

1. **Download VirtualHere USB Server**
   ```bash
   wget https://www.virtualhere.com/sites/default/files/usbserver/vhusbdarm
   chmod +x vhusbdarm
   sudo mv vhusbdarm /usr/local/bin/
   ```

2. **Create systemd service** (`/etc/systemd/system/virtualhere.service`):
   ```ini
   [Unit]
   Description=VirtualHere USB Server
   After=network.target

   [Service]
   Type=simple
   ExecStart=/usr/local/bin/vhusbdarm -b
   Restart=always
   User=root

   [Install]
   WantedBy=multi-user.target
   ```

3. **Enable and start service**:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable virtualhere
   sudo systemctl start virtualhere
   ```

### VirtualHere Client Setup (Windows)

1. **Download VirtualHere Client** from [virtualhere.com](https://www.virtualhere.com/usb_client_software)
2. **Install and run** the client
3. **Find Raspberry Pi** - should appear in the client automatically
4. **Right-click** the FAAC device and select **"Use this device"**
5. **Launch FAAC EasyBoard** - it will see the device as if locally connected

### When to Use VirtualHere

✅ You need to configure gate parameters (one-time or occasional)
✅ You need to diagnose issues with official FAAC software
✅ You want to update gate controller firmware
✅ You prefer using the official FAAC GUI

### Important Limitation

⚠️ **Mutual Exclusivity**: When VirtualHere is using the USB device, the faac-gateway **cannot** access it.

You must choose one or the other, or switch between them (see [Switching Between Modes](#switching-between-modes)).

---

## Option C: Advanced USB Traffic Capture

For advanced users who want to monitor, record, and replay USB traffic, or need to use both FAAC software and faac-gateway simultaneously.

### Overview

This approach involves:
- Capturing USB traffic between FAAC software and the controller
- Recording commands and responses
- Replaying traffic for analysis or testing
- Potentially running both systems with careful orchestration

### More Information

See this detailed guide on USB traffic recording and playback:
- [USB Traffic Capture with VirtualHere](https://claude.ai/share/b309c5b5-a132-4d2d-9479-ee54c71fb2c7)

### When to Use

✅ You're reverse-engineering the FAAC protocol
✅ You need to debug communication issues
✅ You want to understand how FAAC commands work
✅ You're developing new features for faac-gateway

---

## Switching Between Modes

Since the USB port can only be used by one application at a time, you need to stop one service before starting the other.

### Switch to VirtualHere (from faac-gateway)

```bash
# Stop faac-gateway
sudo systemctl stop faac-gateway

# Start VirtualHere
sudo systemctl start virtualhere

# On Windows: Open VirtualHere Client and connect to device
```

### Switch to faac-gateway (from VirtualHere)

```bash
# On Windows: Disconnect device in VirtualHere Client

# Stop VirtualHere on Raspberry Pi
sudo systemctl stop virtualhere

# Start faac-gateway
sudo systemctl start faac-gateway
```

### Check Current Status

```bash
# Check which service is running
sudo systemctl status faac-gateway
sudo systemctl status virtualhere

# Check which process has the USB port
sudo lsof | grep ttyUSB
```

### Automatic Startup Configuration

Choose which service should start automatically at boot:

**For faac-gateway (home automation)**:
```bash
sudo systemctl enable faac-gateway
sudo systemctl disable virtualhere
```

**For VirtualHere (manual configuration)**:
```bash
sudo systemctl disable faac-gateway
sudo systemctl enable virtualhere
```

---

## Troubleshooting

### Problem: VirtualHere shows "In use by another process"

**Cause**: faac-gateway or another application is using the USB port.

**Solution**:
```bash
# Stop faac-gateway
sudo systemctl stop faac-gateway

# Check what's using the port
sudo lsof | grep ttyUSB

# Kill any remaining processes if needed
sudo pkill -f faac_gateway
```

### Problem: faac-gateway can't open serial port

**Cause**: VirtualHere has claimed the USB device.

**Solution**:
```bash
# Stop VirtualHere
sudo systemctl stop virtualhere

# Verify device is available
ls -l /dev/ttyUSB*

# Start faac-gateway
sudo systemctl start faac-gateway
```

### Problem: FAAC EasyBoard can't find device via VirtualHere

**Cause**: USB driver not bound correctly, or device not shared.

**Solution**:
1. Check VirtualHere server is running: `sudo systemctl status virtualhere`
2. In VirtualHere Client, ensure device is "Used by this client"
3. Try disconnecting and reconnecting the device in VirtualHere Client
4. Check Windows Device Manager for USB errors

### Problem: Both services start at boot and conflict

**Cause**: Both `faac-gateway` and `virtualhere` are enabled.

**Solution**:
```bash
# Choose one to disable
sudo systemctl disable virtualhere
# OR
sudo systemctl disable faac-gateway

# Reboot to test
sudo reboot
```

---

## Recommendations

### For Most Users (Home Automation Focus)

**Primary**: Use faac-gateway (Option A)
- Run 24/7 for MQTT/OpenHAB/Home Assistant integration
- Enable at boot: `sudo systemctl enable faac-gateway`

**Occasional**: Use VirtualHere (Option B)
- Keep installed but disabled
- Enable manually when you need FAAC software: `sudo systemctl start virtualhere`
- Switch back when done: `sudo systemctl stop virtualhere && sudo systemctl start faac-gateway`

### For Configuration/Diagnostics Focus

**Primary**: Use VirtualHere (Option B)
- If you frequently use the official FAAC software
- Enable at boot: `sudo systemctl enable virtualhere`

**Add**: faac-gateway for automation
- Install but keep disabled
- Enable when you want automation: `sudo systemctl start faac-gateway`

### For Developers

**Use**: USB Traffic Capture (Option C)
- For protocol analysis and reverse engineering
- See the [detailed guide](https://claude.ai/share/b309c5b5-a132-4d2d-9479-ee54c71fb2c7)

---

## Related Documentation

- [Main README](../README.md) - Project overview
- [USB Setup Guide](../USB_SETUP.md) - USB driver configuration
- [Installation Guide](../scripts/README.md) - Systemd service setup
- [MQTT Setup](../MQTT_SETUP.md) - MQTT configuration
- [OpenHAB Integration](../openhab/README.md) - OpenHAB setup

---

## External Resources

- [FAAC Official Support](https://www.faac.biz/support/manuals-and-certificates) - Official software and manuals
- [VirtualHere](https://www.virtualhere.com/) - USB over network software
- [USB Traffic Capture Guide](https://claude.ai/share/b309c5b5-a132-4d2d-9479-ee54c71fb2c7) - Advanced USB monitoring
