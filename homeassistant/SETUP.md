# Home Assistant Setup Guide for FAAC Gate

Quick setup guide to integrate your FAAC gate with Home Assistant via MQTT.

## Prerequisites

✅ MQTT Broker (Mosquitto) running
✅ FAAC Gateway running with MQTT enabled
✅ Home Assistant installed and accessible

## Step-by-Step Setup

### Step 1: Configure MQTT in Home Assistant

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "MQTT" and select it
4. Enter your MQTT broker details:
   - **Broker**: `localhost` (or your MQTT broker IP)
   - **Port**: `1883`
   - **Username/Password**: (if configured on broker)
5. Click **Submit**

### Step 2: Add Gate Configuration

Edit your Home Assistant configuration file:

```bash
# Access Home Assistant terminal or SSH
cd /config
nano configuration.yaml
```

Add the MQTT configuration from `configuration.yaml` in this directory.

Alternatively, use includes for cleaner organization:

```yaml
# In configuration.yaml
mqtt: !include mqtt.yaml
```

Then create `mqtt.yaml` with the contents of `configuration.yaml`.

### Step 3: Verify MQTT Topics

Before restarting, verify the MQTT topics are publishing:

1. In Home Assistant, go to **Developer Tools** → **MQTT**
2. Subscribe to `faac/gate/#` to see all topics
3. You should see messages on:
   - `faac/gate/state`
   - `faac/gate/wing1`
   - `faac/gate/wing2`
   - `faac/gate/availability`

### Step 4: Restart Home Assistant

```bash
# Via UI
Settings → System → Restart

# Or via terminal
ha core restart
```

### Step 5: Verify Entities

After restart, check that entities are created:

1. Go to **Settings** → **Devices & Services** → **Entities**
2. Search for "faac"
3. You should see:
   - `cover.faac_gate` (main control)
   - `sensor.faac_gate_state`
   - `sensor.faac_gate_wing1`
   - `sensor.faac_gate_wing2`
   - `binary_sensor.faac_gateway_connection`

### Step 6: Add to Dashboard

1. Go to your dashboard
2. Click **Edit Dashboard** (three dots menu)
3. Click **+ Add Card**
4. Choose one of these options:
   - **Easy**: Select "Cover" card type, then choose `cover.faac_gate`
   - **Custom**: Switch to YAML mode and paste from one of:
     - `card_simple.yaml` - Basic control
     - `card_detailed.yaml` - With status info
     - `card_glance.yaml` - Compact view
     - `card_picture.yaml` - With image
     - `card_button.yaml` - Custom styled (requires HACS)
5. Click **Save**

### Step 7: Test Control

Test the gate control:

1. Click the gate card
2. Try **Open** → gate should open
3. Try **Stop** → gate should stop
4. Try **Close** → gate should close
5. Try position slider → gate should move to that position

## Verification Checklist

- [ ] MQTT integration shows "connected"
- [ ] Gate cover entity appears in entities list
- [ ] Entity shows current state (not "unavailable")
- [ ] Opening gate from HA changes state to "opening"
- [ ] Gate responds to commands from Home Assistant
- [ ] Position slider updates as gate moves

## Troubleshooting

### Entity shows "unavailable"

**Check MQTT connection:**
```bash
# On MQTT broker machine
mosquitto_sub -v -t "faac/gate/#"
```

You should see status messages. If not:
- Check FAAC Gateway is running: `systemctl status faac-gateway`
- Check MQTT broker: `systemctl status mosquitto`

**Check Home Assistant MQTT connection:**
- Settings → Devices & Services → MQTT
- Should show "Connected"
- If not, reconfigure with correct broker address

### Commands don't work

**Test MQTT publishing:**
```bash
# From any machine that can reach MQTT broker
mosquitto_pub -h BROKER_IP -t faac/gate/command -m "open"
```

If this works but HA doesn't:
- Check HA logs: Settings → System → Logs
- Verify command topic in configuration matches FAAC Gateway

### Position doesn't update

**Check wing1 topic:**
```bash
mosquitto_sub -t "faac/gate/wing1"
```

Should show 0-100 values. If not:
- FAAC Gateway might not be connected to gate
- Check gateway logs

If topic publishes but HA doesn't update:
- Check `value_template` in cover configuration
- Verify template syntax in HA Template Editor

### State stuck on "unknown"

**Check state topic:**
```bash
mosquitto_sub -t "faac/gate/state"
```

Should show: OPEN, CLOSED, OPENING, CLOSING, STOPPED

If not publishing:
- FAAC Gateway might be offline
- Check `faac/gate/availability` topic

## Advanced Configuration

### Custom MQTT Topic

If you changed the MQTT base topic in FAAC Gateway:

1. Edit all topic references in `configuration.yaml`
2. Change `faac/gate` to your custom topic
3. Example: `my/custom/gate/topic`

### Multiple Gates

To add multiple gates:

1. Duplicate the cover section in configuration
2. Change `unique_id` and entity names
3. Update topics to match each gateway
4. Example:
   ```yaml
   # Front gate
   - name: "Front Gate"
     unique_id: front_gate_cover
     state_topic: "faac/front/state"

   # Back gate
   - name: "Back Gate"
     unique_id: back_gate_cover
     state_topic: "faac/back/state"
   ```

### HomeKit Bridge

Expose gate to Apple Home:

```yaml
# In configuration.yaml
homekit:
  filter:
    include_entities:
      - cover.faac_gate
```

Restart HA, then scan QR code in Home app.

## Next Steps

- Add automations (see `automations_examples.yaml`)
- Customize dashboard card (see `dashboard_card.yaml`)
- Set up notifications for gate events
- Integrate with other Home Assistant features

## Support

For issues:
1. Check FAAC Gateway logs: `journalctl -u faac-gateway -f`
2. Check Home Assistant logs: Settings → System → Logs
3. Test MQTT manually with `mosquitto_sub` and `mosquitto_pub`
4. Review [FAAC Gateway MQTT docs](../docs/MQTT.md)

## See Also

- [Home Assistant MQTT Cover Documentation](https://www.home-assistant.io/integrations/cover.mqtt/)
- [FAAC Gateway Documentation](../README.md)
- [OpenHAB Integration](../openhab/README.md)
