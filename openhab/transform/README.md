# MQTT Transformation Scripts

## Purpose

These transformation scripts handle the value inversion between the FAAC gate hardware and OpenHAB's rollershutter convention.

## The Problem

**Gate Hardware:**
- 0% = CLOSED
- 100% = OPEN

**OpenHAB Rollershutter Convention:**
- 0 = UP/OPEN (for blinds/shutters)
- 100 = DOWN/CLOSED

These are **opposite**, causing status display and control issues.

## The Solution

Transform values at the **MQTT channel level** (not at item level):

### invert.js

Inverts position values bidirectionally:

**Incoming (from gate → OpenHAB):**
- Gate sends 0 (CLOSED) → Transform to 100 → OpenHAB sees 100 (CLOSED ✓)
- Gate sends 100 (OPEN) → Transform to 0 → OpenHAB sees 0 (OPEN ✓)

**Outgoing (OpenHAB → gate):**
- User says "Close" → OpenHAB sends 100 → Transform to 0 → Gate closes ✓
- User says "Open" → OpenHAB sends 0 → Transform to 100 → Gate opens ✓

## Installation

```bash
# Copy transformation script to OpenHAB
sudo mkdir -p /etc/openhab/transform
sudo cp invert.js /etc/openhab/transform/
sudo chown openhab:openhab /etc/openhab/transform/invert.js
```

## Usage in Things File

```java
Type rollershutter : position "Gate Position" [
    commandTopic="faac/gate/command",
    stateTopic="faac/gate/wing1",
    transformationPattern="JS:invert.js",      // Incoming transformation
    transformationPatternOut="JS:invert.js",   // Outgoing transformation
    on="0",    // OpenHAB 0 = OPEN → transform → gate receives 100
    off="100", // OpenHAB 100 = CLOSED → transform → gate receives 0
    retained=false
]
```

## Benefits

✅ **OpenHAB UI works correctly**
- Down button closes gate
- Up button opens gate
- Position display matches reality

✅ **HomeKit works correctly**
- No `inverted=true` needed
- Status displays correctly
- Stop command works

✅ **Google Assistant works correctly**
- No `inverted=true` needed
- Commands work naturally

✅ **Alexa works correctly**
- No special configuration needed

✅ **One transformation handles everything**
- All interfaces aligned
- Simple to maintain

## Verification

After applying:

1. **OpenHAB UI:** Click UP → Gate should OPEN
2. **HomeKit:** Say "Open" → Gate should OPEN, status shows OPEN
3. **Google:** Say "Close" → Gate should CLOSE, status shows CLOSED
4. **Position:** Send 50% → Gate goes to 50%, all interfaces show 50%

## Alternative Approach (Not Recommended)

You could invert at the item level:
```java
ga="Rollershutter" [lang="de", inverted=true],
homekit="WindowCovering" [inverted=true]
```

**Why channel-level is better:**
- Fixes OpenHAB UI too (not just voice assistants)
- One transformation handles all interfaces
- Cleaner, more maintainable
- Matches OpenHAB best practices

## Troubleshooting

### Status still inverted?

1. Verify transformation is installed:
```bash
ls -l /etc/openhab/transform/invert.js
```

2. Check OpenHAB logs:
```bash
tail -f /var/log/openhab/openhab.log | grep -i transform
```

3. Test transformation manually:
```bash
# Should output: 0
echo "100" | /etc/openhab/transform/invert.js

# Should output: 100
echo "0" | /etc/openhab/transform/invert.js
```

### OpenHAB not applying transformation?

Restart OpenHAB:
```bash
sudo systemctl restart openhab
```

### Want to verify values?

Enable debug logging:
```bash
log:set DEBUG org.openhab.binding.mqtt
```

Then watch the logs while sending commands.
