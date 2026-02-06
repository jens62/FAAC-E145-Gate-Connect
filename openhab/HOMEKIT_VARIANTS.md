# HomeKit Configuration Variants

Two HomeKit accessory types are available for your FAAC gate in OpenHAB.

## 📋 Comparison

| Feature | WindowCovering ⭐ | GarageDoorOpener |
|---------|-------------------|------------------|
| **File** | `faac_gate_windowcovering.items` | `faac_gate.items` |
| **HomeKit Type** | Blind/Rollershutter | Garage Door |
| **Security Prompts** | ❌ None | ✅ Yes, when opening |
| **Voice Commands** | Natural rollershutter commands | Garage door commands |
| **Icon in Home App** | Blind/Shutter icon | Garage door icon |
| **Position Control** | ✅ Direct | ✅ Direct |
| **Speed** | Fast (no prompts) | Slower (confirmation needed) |
| **Best For** | Daily use, convenience | Extra security |

## 🎯 Recommended: WindowCovering

### Why?

1. **No Security Prompts** - Instant control without confirmation
2. **Better Voice Commands** - Uses rollershutter vocabulary
3. **Faster** - No delays from security prompts
4. **More Natural** - Gate behaves like a blind/shutter

### Voice Commands with WindowCovering

```
"Öffne Hoftor zu 30%"        → Opens to 30% immediately
"Fahre Hoftor hoch"           → Opens (rollershutter style)
"Fahre Hoftor runter"         → Closes (rollershutter style)
"Stelle Hoftor auf 50%"       → Sets to 50%
"Wie weit ist Hoftor offen?"  → Asks position
```

### HomeKit App Display

- Shows as blind/shutter icon
- Position slider visible
- Tap to open/close
- No confirmation dialogs

## 🚪 Alternative: GarageDoorOpener

### Why Use This?

1. **Extra Security** - Confirmation prompt prevents accidental opening
2. **Semantic Clarity** - Clearly shows it's a gate/door
3. **Security Features** - HomeKit treats it as secured accessory

### Voice Commands with GarageDoorOpener

```
"Öffne Hoftor"               → Prompts: "Are you sure?"
"Schließe Hoftor"            → Closes immediately
"Stelle Hoftor auf 30%"      → Prompts, then opens to 30%
```

### HomeKit App Display

- Shows as garage door icon
- Security badge visible
- Tap requires confirmation for opening
- Extra security notifications

## 🔄 Switching Between Variants

### To Use WindowCovering (Recommended)

```bash
sudo cp faac_gate_windowcovering.items /etc/openhab/items/faac_gate.items
sudo chown openhab:openhab /etc/openhab/items/faac_gate.items
sudo systemctl restart openhab
```

### To Use GarageDoorOpener

```bash
sudo cp faac_gate.items /etc/openhab/items/
sudo chown openhab:openhab /etc/openhab/items/faac_gate.items
sudo systemctl restart openhab
```

### Reconnect HomeKit

After switching:
1. Open Home app on iPhone
2. Remove "Hoftor" accessory
3. Add accessory again with OpenHAB PIN
4. Test with voice commands

## 📱 Real-World Examples

### WindowCovering Experience

```
You: "Hey Siri, öffne Hoftor zu 30%"
Siri: "OK"
[Gate immediately starts opening to 30%]
[No prompts, no delays]
```

### GarageDoorOpener Experience

```
You: "Hey Siri, öffne Hoftor"
Siri: "To open your garage door, you need to confirm in the Home app"
[Opens Home app]
[Tap to confirm]
[Gate starts opening]
```

## 🎨 Home App Icons

### WindowCovering
```
┌─────────────┐
│   Hoftor    │
│  ▓▓▓▓▓▓▓░░  │ ← Shutter icon with position
│    50%      │
└─────────────┘
```

### GarageDoorOpener
```
┌─────────────┐
│   Hoftor    │
│    [🚪]     │ ← Garage door icon
│   🔒 Open   │ ← Security indicator
└─────────────┘
```

## 💡 Configuration Details

### WindowCovering Metadata

```java
homekit="WindowCovering" [
    WindowCovering.CurrentPosition="wing1",
    WindowCovering.TargetPosition="CONTROL",
    WindowCovering.PositionState="DYNAMIC"
]
```

**What this means:**
- `CurrentPosition`: Uses wing1 position as feedback
- `TargetPosition`: Allows setting target position
- `PositionState`: Shows if moving/stopped

### GarageDoorOpener Metadata

```java
homekit="GarageDoorOpener" [
    inverted=false
]
```

**What this means:**
- Treated as garage door accessory
- Security features enabled
- Requires confirmation for opening

## 🔍 Technical Differences

### MQTT Communication

Both variants send the same MQTT messages:
- Position commands: `"0"` to `"100"`
- Simple commands: `"open"`, `"close"`, `"stop"`

The only difference is the HomeKit accessory type and user experience.

### OpenHAB Binding

Both use the same:
- MQTT topic: `faac/gate/command`
- Rollershutter item type
- Position feedback: `faac/gate/wing1`

## ✅ Recommendation Summary

**Use WindowCovering if:**
- You want fast, convenient daily control ⭐
- You don't need security prompts
- You prefer rollershutter voice commands
- You want the simplest user experience

**Use GarageDoorOpener if:**
- You want extra security confirmation
- You prefer gate shown as garage door
- You're okay with confirmation delays
- Security is more important than convenience

**For most users: WindowCovering is the better choice!**
