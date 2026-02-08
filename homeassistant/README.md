# Home Assistant Integration for FAAC Gate

This directory contains Home Assistant configuration files for integrating your FAAC gate via MQTT.

## Architecture

```
┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐
│  FAAC Gateway   │◄──────►│  MQTT Broker    │◄──────►│ Home Assistant  │
│  (Publisher)    │        │  (mosquitto)    │        │  (Subscriber)   │
└─────────────────┘        └─────────────────┘        └─────────────────┘
```

The FAAC Gateway publishes status to MQTT topics, and Home Assistant subscribes to these topics. Commands from Home Assistant are published to the command topic which the gateway subscribes to.

## Prerequisites

1. **MQTT Broker** (Mosquitto) running and accessible
2. **FAAC Gateway** running with MQTT enabled
3. **Home Assistant** with MQTT integration configured

## Quick Start

### 1. Configure MQTT Integration in Home Assistant

If you haven't already, add MQTT integration:

**Settings → Devices & Services → Add Integration → MQTT**

Configure your MQTT broker settings (same broker used by FAAC Gateway).

### 2. Add Gate Configuration

Add the contents of `configuration.yaml` to your Home Assistant configuration file (usually `/config/configuration.yaml`).

You can either:
- Copy the entire `mqtt:` section into your config
- Use `!include` to include the file separately

### 3. Restart Home Assistant

**Settings → System → Restart**

### 4. Add Dashboard Card

The gate will appear as a Cover entity. Choose one of the provided dashboard card examples:

- `card_simple.yaml` - Basic tile with open/close/position controls
- `card_detailed.yaml` - Tile + detailed status entities
- `card_glance.yaml` - Compact glance view
- `card_picture.yaml` - Picture overlay with controls
- `card_button.yaml` - Custom styled button (requires HACS button-card)

## Files

### Configuration
- **configuration.yaml** - MQTT sensor and cover entity definitions

### Dashboard Cards (choose one or combine)
- **card_simple.yaml** - Basic tile card
- **card_detailed.yaml** - Detailed status card
- **card_glance.yaml** - Compact glance card
- **card_picture.yaml** - Picture overlay card
- **card_button.yaml** - Custom button card (requires HACS)

### Automations
- **automations_examples.yaml** - 10 example automations

### Documentation
- **SETUP.md** - Step-by-step setup guide
- **README.md** - This file

## MQTT Topics

The integration uses these topics (default base: `faac/gate`):

### Status Topics (Subscribe)
- `faac/gate/state` - Gate state (OPEN, CLOSED, OPENING, CLOSING, STOPPED, UNKNOWN)
- `faac/gate/wing1` - Wing 1 position (0-100%)
- `faac/gate/wing2` - Wing 2 position (0-100%)
- `faac/gate/availability` - Gateway availability (online/offline)
- `faac/gate/status` - Complete status as JSON

### Command Topic (Publish)
- `faac/gate/command` - Send commands: `open`, `close`, `stop`, or position `0-100`

## Entity Details

### Cover Entity: `cover.faac_gate`

The main gate control entity with these features:

- **Open/Close/Stop** buttons
- **Position slider** (0-100%)
- **Current state** (opening, closing, open, closed, stopped)
- **Availability tracking**

### Diagnostic Sensors

Additional sensors for monitoring:

- `sensor.faac_gate_state` - Detailed state
- `sensor.faac_gate_wing1` - Wing 1 position
- `sensor.faac_gate_wing2` - Wing 2 position
- `binary_sensor.faac_gateway_connection` - Gateway online status

## Usage Examples

### Basic Control

```yaml
# Open gate
service: cover.open_cover
target:
  entity_id: cover.faac_gate

# Close gate
service: cover.close_cover
target:
  entity_id: cover.faac_gate

# Stop gate
service: cover.stop_cover
target:
  entity_id: cover.faac_gate

# Set position to 50%
service: cover.set_cover_position
target:
  entity_id: cover.faac_gate
data:
  position: 50
```

### Automation Examples

See `automations_examples.yaml` for complete examples:

- Close gate at sunset
- Open gate when arriving home
- Send notification when gate is left open
- Close gate if left open for 10 minutes

## Troubleshooting

### Gate entity shows "unavailable"

1. Check MQTT broker is running: `sudo systemctl status mosquitto`
2. Check FAAC Gateway is connected: `sudo systemctl status faac-gateway`
3. Verify MQTT topics in Home Assistant Developer Tools → MQTT

### Commands not working

1. Test MQTT command manually:
   ```bash
   mosquitto_pub -h localhost -t faac/gate/command -m "open"
   ```
2. Check Home Assistant logs for MQTT errors
3. Verify topic names match your configuration

### Position not updating

1. Check `faac/gate/wing1` topic is publishing values
2. Verify template in cover configuration is correct
3. Check Home Assistant logs for template errors

## Advanced Configuration

### Custom Topics

If you changed the MQTT base topic in FAAC Gateway config, update all topic references in the configuration files:

```yaml
# Change from default 'faac/gate' to your custom topic
state_topic: "your/custom/topic/state"
command_topic: "your/custom/topic/command"
# ... etc
```

### Multiple Gates

To control multiple gates:

1. Run each FAAC Gateway with a different MQTT base topic
2. Duplicate the configuration for each gate with unique entity IDs
3. Example:
   ```yaml
   # Front gate
   - unique_id: faac_front_gate
     state_topic: "faac/front_gate/state"

   # Back gate
   - unique_id: faac_back_gate
     state_topic: "faac/back_gate/state"
   ```

## Integration with HomeKit

Home Assistant can expose the gate to Apple HomeKit:

1. Install HomeKit Bridge integration
2. Add gate to bridge:
   ```yaml
   homekit:
     filter:
       include_entities:
         - cover.faac_gate
   ```
3. Scan QR code in Home app on iOS device

The gate will appear as a garage door in HomeKit with open/close/stop controls.

## See Also

- [Home Assistant MQTT Cover Documentation](https://www.home-assistant.io/integrations/cover.mqtt/)
- [FAAC Gateway MQTT Documentation](../docs/MQTT.md)
- [OpenHAB Integration](../openhab/README.md)
