# OpenHAB Integration for FAAC Gate

Complete OpenHAB configuration for controlling the FAAC E145 gate via MQTT with HomeKit support.

## 🎯 Key Features

- ✅ **Direct position control (0-100%)** - NO RULES NEEDED!
- ✅ **HomeKit/Siri integration** for voice control in German
- ✅ **HomeKit-style stop** - Say "Open" while opening to stop (like professional blinds)
- ✅ **Real-time position feedback** from both wings
- ✅ **Alexa & Google Assistant** support included
- ✅ **Simple configuration** - just things, items, and sitemap

## 📁 Files

- **`faac_gate.things`** - MQTT broker and gate device configuration
- **`faac_gate.items`** - Item definitions with HomeKit GarageDoorOpener
- **`faac_gate_windowcovering.items`** - Alternative: HomeKit WindowCovering ⭐ **Recommended!**
- **`faac_gate.sitemap`** - Visual interface with position slider
- **`README.md`** - This file

**🎉 NO RULES FILE NEEDED!** Position control is handled automatically by the FAAC gateway.

### 🔄 Two HomeKit Variants

**Option 1: GarageDoorOpener** (`faac_gate.items`)
- Shows as "Garage Door" in Home app
- Has security confirmation prompts when opening
- Good if you want extra security

**Option 2: WindowCovering** (`faac_gate_windowcovering.items`) ⭐ **Recommended**
- Shows as "Rolladen/Blind" in Home app
- No security prompts - direct control
- Better for rollershutter-style voice commands
- Simpler and faster to use

## 🚀 Quick Setup

### 1. Install OpenHAB Bindings

Via OpenHAB UI:
```
Settings → Bindings → Install:
- MQTT Binding
- HomeKit Integration (optional, for Siri)
```

### 2. Copy Configuration Files

**Choose your HomeKit variant:**

**Option A: WindowCovering** ⭐ **Recommended - No security prompts**
```bash
sudo cp faac_gate.things /etc/openhab/things/
sudo cp faac_gate_windowcovering.items /etc/openhab/items/faac_gate.items
sudo cp faac_gate.sitemap /etc/openhab/sitemaps/

sudo chown openhab:openhab /etc/openhab/things/faac_gate.things
sudo chown openhab:openhab /etc/openhab/items/faac_gate.items
sudo chown openhab:openhab /etc/openhab/sitemaps/faac_gate.sitemap
```

**Option B: GarageDoorOpener** (with security confirmation prompts)
```bash
sudo cp faac_gate.things /etc/openhab/things/
sudo cp faac_gate.items /etc/openhab/items/
sudo cp faac_gate.sitemap /etc/openhab/sitemaps/

sudo chown openhab:openhab /etc/openhab/things/faac_gate.things
sudo chown openhab:openhab /etc/openhab/items/faac_gate.items
sudo chown openhab:openhab /etc/openhab/sitemaps/faac_gate.sitemap
```

### 3. Configure MQTT Broker

Edit `/etc/openhab/things/faac_gate.things`:

```java
Bridge mqtt:broker:mosquitto "MQTT Broker" [
    host="192.168.1.100",  // Your MQTT broker IP
    port=1883
    // username="your_username",
    // password="your_password"
]
```

### 4. Create Groups

Add to `/etc/openhab/items/groups.items`:

```java
Group gGarage "Garage/Hof" <garage>
```

### 5. Restart OpenHAB

```bash
sudo systemctl restart openhab
```

## 🎤 Voice Commands (German)

### Siri/HomeKit

**With WindowCovering** ⭐ (Recommended - No security prompts):
- **"Hey Siri, öffne Hoftor"** - Opens gate to 100%
- **"Hey Siri, schließe Hoftor"** - Closes gate to 0%
- **"Hey Siri, stoppe Hoftor"** - Stops gate movement
- **"Hey Siri, öffne Hoftor zu 30%"** - Opens to exactly 30%! ✨
- **"Hey Siri, stelle Hoftor auf 50%"** - Sets to 50%
- **"Hey Siri, fahre Hoftor hoch"** - Opens (rollershutter style)
- **"Hey Siri, fahre Hoftor runter"** - Closes (rollershutter style)
- **"Hey Siri, wie weit ist Hoftor geöffnet?"** - Checks position

**🎯 HomeKit-Style Stop** (Like Eve, Somfy, Shelly, Fibaro):
- **Gate is opening** → Say **"Öffne Hoftor"** again → **Stops!** 🛑
- **Gate is closing** → Say **"Schließe Hoftor"** again → **Stops!** 🛑
- **In Home app:** Tap "Open" while opening → Stops
- **In Home app:** Tap "Close" while closing → Stops

**With GarageDoorOpener:**
- Same commands work
- **But:** Security confirmation prompt appears when opening
- Shows as "Garage Door" in Home app

### Alexa

- **"Alexa, öffne Hoftor"**
- **"Alexa, schließe Hoftor"**
- **"Alexa, stelle Hoftor auf 25%"**

## 📊 How Position Control Works

### Without Rules (New Way!) ✅

```
1. You say: "Öffne Hoftor zu 30%"
2. OpenHAB Rollershutter → sends "30" to MQTT
3. FAAC Gateway receives "30"
4. Gateway opens gate and monitors position in real-time
5. When position reaches 30% (±2%), gateway sends STOP
6. Gate stops at exactly 30%!
```

### HomeKit-Style Stop 🎯

Professional HomeKit blinds (Eve, Somfy, Shelly, Fibaro) don't have a separate "Stop" command in HomeKit. Instead, they stop by **repeating the same command**:

```
1. You say: "Öffne Hoftor" → Gate starts opening
2. You say: "Öffne Hoftor" again → Gate stops!
```

**How it works:**
- Gateway tracks the last command ("open" or "close")
- When gate is MOVING and same command sent → Converts to STOP
- Works across all interfaces: HomeKit, OpenHAB, MQTT, Web GUI

**Examples:**
- Gate opening → "Open" again → STOPS ✅
- Gate closing → "Close" again → STOPS ✅
- Gate stopped at 50% → "Open" → Resumes opening ✅
- Gate moving → Opposite command → Changes direction ✅

### Why No Rules Needed?

The FAAC gateway firmware now includes intelligent control:
- Accepts position commands (0-100)
- Monitors current position continuously
- Automatically sends STOP when target reached
- HomeKit-style stop by repeating commands
- Works just like any other OpenHAB rollershutter!

This is much simpler than the old approach with complex rules.

## 🎛️ Control Options

### In OpenHAB Sitemap

- **UP/STOP/DOWN buttons** - Quick open/close/stop
- **Position slider** - Drag to any position 0-100%
- **Current position display** - See both wing positions in real-time
- **Status indicator** - Color-coded state (OPEN/CLOSED/MOVING/STOPPED)
- **History charts** - View position over time

### Via HomeKit App

- Tap to open/close
- Long press for position slider
- Appears as "Garage Door" type
- Shows OPEN/CLOSED/OPENING/CLOSING status

### Via Voice

Just say any of the commands listed above!

## 🔧 MQTT Topics

| Topic | Direction | Content | Purpose |
|-------|-----------|---------|---------|
| `faac/gate/command` | → Gate | "30" or "open"/"close"/"stop" | Send position (0-100) or command |
| `faac/gate/wing1` | ← Gate | "45" | Current Wing 1 position (0-100%) |
| `faac/gate/wing2` | ← Gate | "42" | Current Wing 2 position (0-100%) |
| `faac/gate/state` | ← Gate | "MOVING" | State: OPEN/CLOSED/MOVING/STOPPED |
| `faac/gate/availability` | ← Gate | "online" | Connection status |
| `faac/gate/server_heartbeat` | ← Gate | "2026-02-06T20:45:30" | Server alive timestamp (ISO 8601) |
| `faac/gate/gate_last_seen` | ← Gate | "2026-02-06T20:45:29" | Gate (USB) last response timestamp |

**Heartbeat monitoring** (updates every 5 seconds):
- Compare `server_heartbeat` vs `gate_last_seen` to diagnose connection issues
- If both frozen → OpenHAB ↔ MQTT connection broken
- If only gate frozen → Server alive, but USB/gate connection broken

## ✨ Advantages Over Rules-Based Approach

### ❌ Old Way (With Rules)
```
OpenHAB → Rule transforms UP to "open" → MQTT → Gate
Position 30% didn't work properly
Complex rule logic needed
Manual position synchronization
```

### ✅ New Way (No Rules!)
```
OpenHAB → Directly sends "30" → MQTT → Gate moves to 30%
Simple, clean, works like any rollershutter
Position control in gateway firmware
Automatic position feedback
```

## 📱 HomeKit Setup

1. OpenHAB UI → **Settings** → **Add-ons** → **HomeKit Integration**
2. Note the PIN code displayed
3. iPhone: **Home** app → **+** → **Add Accessory** → **OpenHAB**
4. Enter PIN code
5. Gate appears as "Hoftor"
6. Start using voice commands immediately!

## 🧪 Testing

### Test Position Control

```bash
# Open to 50%
mosquitto_pub -h localhost -t 'faac/gate/command' -m '50'

# Watch it move to 50% and stop automatically!

# Close to 0%
mosquitto_pub -h localhost -t 'faac/gate/command' -m '0'

# Open to 100%
mosquitto_pub -h localhost -t 'faac/gate/command' -m '100'
```

### Test OpenHAB

```bash
# Check thing status
openhab-cli console
> openhab:status mqtt:topic:mosquitto:faac_hoftor
# Should show: ONLINE
```

### Test Voice

1. Say "Hey Siri, öffne Hoftor zu 25%"
2. Watch OpenHAB sitemap - position updates in real-time
3. Gate moves to 25% and stops automatically!

## 🐛 Troubleshooting

### Gate doesn't respond to position commands

```bash
# 1. Check MQTT connection
mosquitto_sub -h localhost -t 'faac/gate/availability'
# Should show "online"

# 2. Test direct MQTT command
mosquitto_pub -h localhost -t 'faac/gate/command' -m '40'

# 3. Check FAAC gateway logs
journalctl -u faac-gateway -f | grep -i position
```

### OpenHAB shows wrong position

```bash
# Check if gateway is publishing position
mosquitto_sub -h localhost -t 'faac/gate/wing1' -v

# Verify thing channels are linked
# OpenHAB UI → Settings → Things → FAAC Gate → Check channels
```

### Voice commands don't work

1. Ensure HomeKit integration is enabled in OpenHAB
2. Verify "Hoftor" appears in Home app
3. Check iPhone language is set to German for German commands

## 🔐 Security

- **MQTT authentication**: Uncomment username/password in things file
- **TLS**: Set `secure=true` and configure certificates
- **HomeKit**: Uses encrypted communication automatically
- **Network**: Consider VLAN isolation for IoT devices

## 📖 Related Documentation

- [FAAC Gateway MQTT Guide](../docs/MQTT.md)
- [FAAC Gateway Setup](../MQTT_SETUP.md)
- [OpenHAB MQTT Binding](https://www.openhab.org/addons/bindings/mqtt/)
- [OpenHAB HomeKit Integration](https://www.openhab.org/addons/integrations/homekit/)

## 🎯 Summary

This OpenHAB integration provides:
- Native position control (0-100%)
- No complex rules needed
- Works like any other rollershutter
- Full HomeKit/Siri support with professional-grade stop behavior
- HomeKit-style stop: repeat command to stop (like Eve, Somfy, Shelly, Fibaro)
- Real-time position feedback with dual heartbeat monitoring
- Clean, simple configuration

Just copy 3 files, configure MQTT broker, and you're done! 🎉
