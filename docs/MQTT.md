# MQTT Integration Guide

This guide explains how to use the MQTT functionality with FAAC Gate Connect.

## Overview

The MQTT integration allows you to:
- **Subscribe** to gate status changes (wing positions, state, availability)
- **Publish** commands to control the gate (open, close, stop)
- Integrate with Home Assistant, OpenHAB, Node-RED, and other MQTT-based systems

## Quick Start

### 1. Configure MQTT

Copy the example configuration:
```bash
cp config/config.yaml.example config/config.yaml
```

Edit `config/config.yaml` and configure the MQTT section:
```yaml
mqtt:
  enabled: true
  broker: localhost  # Your MQTT broker hostname/IP
  port: 1883
  username: null     # Optional
  password: null     # Optional
  client_id: faac_gateway
  base_topic: faac/gate
  use_tls: false
```

### 2. Run with MQTT

```bash
python3 faac_gateway_mqtt.py -c config/config.yaml
```

## MQTT Topics

All topics are prefixed with the `base_topic` (default: `faac/gate`):

### Status Topics (Subscribe)

| Topic | Description | Example Value | Retained |
|-------|-------------|---------------|----------|
| `faac/gate/status` | Complete status (JSON) | `{"wing1": 100, "wing2": 95, "state": "OPEN", "online": true}` | Yes |
| `faac/gate/state` | Current gate state | `OPEN`, `CLOSED`, `MOVING`, `STOPPED`, `UNKNOWN` | Yes |
| `faac/gate/wing1` | Wing 1 position (%) | `0` to `100` | Yes |
| `faac/gate/wing2` | Wing 2 position (%) | `0` to `100` | Yes |
| `faac/gate/availability` | Connection status | `online` or `offline` | Yes |

### Command Topic (Publish)

| Topic | Description | Valid Values |
|-------|-------------|--------------|
| `faac/gate/command` | Send gate commands | `open`, `close`, `stop` |

## Usage Examples

### Using mosquitto_pub/sub

**Subscribe to all topics:**
```bash
mosquitto_sub -h localhost -t 'faac/gate/#' -v
```

**Subscribe to state only:**
```bash
mosquitto_sub -h localhost -t 'faac/gate/state'
```

**Send commands:**
```bash
# Open gate
mosquitto_pub -h localhost -t 'faac/gate/command' -m 'open'

# Close gate
mosquitto_pub -h localhost -t 'faac/gate/command' -m 'close'

# Stop gate
mosquitto_pub -h localhost -t 'faac/gate/command' -m 'stop'
```

### Using Python (paho-mqtt)

```python
import paho.mqtt.client as mqtt

def on_message(client, userdata, msg):
    print(f"Topic: {msg.topic}, Value: {msg.payload.decode()}")

client = mqtt.Client()
client.on_message = on_message
client.connect("localhost", 1883)

# Subscribe to status updates
client.subscribe("faac/gate/#")

# Send command
client.publish("faac/gate/command", "open")

client.loop_forever()
```

### Using Node-RED

1. Add an **MQTT In** node:
   - Server: Your MQTT broker
   - Topic: `faac/gate/state`

2. Add an **MQTT Out** node for commands:
   - Server: Your MQTT broker
   - Topic: `faac/gate/command`

3. Add a **Function** node to format commands:
```javascript
msg.payload = "open";  // or "close", "stop"
return msg;
```

## Home Assistant Integration

### Manual Configuration

Add to your `configuration.yaml`:

```yaml
mqtt:
  cover:
    - name: "FAAC Gate"
      command_topic: "faac/gate/command"
      state_topic: "faac/gate/state"
      availability_topic: "faac/gate/availability"
      payload_open: "open"
      payload_close: "close"
      payload_stop: "stop"
      state_open: "OPEN"
      state_closed: "CLOSED"
      state_opening: "MOVING"
      state_closing: "MOVING"
      optimistic: false
      retain: false

  sensor:
    - name: "FAAC Gate Wing 1"
      state_topic: "faac/gate/wing1"
      unit_of_measurement: "%"
      icon: mdi:gate

    - name: "FAAC Gate Wing 2"
      state_topic: "faac/gate/wing2"
      unit_of_measurement: "%"
      icon: mdi:gate
```

Restart Home Assistant to see the new entities.

### Using MQTT Discovery (Coming Soon)

Automatic discovery will be added in a future version.

## OpenHAB Integration

### Things Configuration

Create a file `faac_gate.things`:

```
Bridge mqtt:broker:mosquitto "Mosquitto Broker" [ host="localhost", port=1883 ] {
    Thing topic faac_gate "FAAC Gate" {
        Channels:
            Type string : state "Gate State" [ stateTopic="faac/gate/state" ]
            Type string : command "Gate Command" [ commandTopic="faac/gate/command" ]
            Type number : wing1 "Wing 1 Position" [ stateTopic="faac/gate/wing1" ]
            Type number : wing2 "Wing 2 Position" [ stateTopic="faac/gate/wing2" ]
            Type string : availability "Availability" [ stateTopic="faac/gate/availability" ]
    }
}
```

### Items Configuration

Create a file `faac_gate.items`:

```
String FaacGate_State "Gate State [%s]" { channel="mqtt:topic:mosquitto:faac_gate:state" }
String FaacGate_Command "Gate Command" { channel="mqtt:topic:mosquitto:faac_gate:command" }
Number FaacGate_Wing1 "Wing 1 [%d %%]" { channel="mqtt:topic:mosquitto:faac_gate:wing1" }
Number FaacGate_Wing2 "Wing 2 [%d %%]" { channel="mqtt:topic:mosquitto:faac_gate:wing2" }
String FaacGate_Availability "Availability [%s]" { channel="mqtt:topic:mosquitto:faac_gate:availability" }
```

### Sitemap

```
Frame label="Gate Control" {
    Text item=FaacGate_State
    Switch item=FaacGate_Command mappings=[open="Open", close="Close", stop="Stop"]
    Text item=FaacGate_Wing1
    Text item=FaacGate_Wing2
}
```

## Security

### TLS Encryption

Enable TLS in your configuration:

```yaml
mqtt:
  use_tls: true
  port: 8883  # Standard MQTT TLS port
```

Note: You may need to configure certificates depending on your broker setup.

### Authentication

Configure username and password:

```yaml
mqtt:
  username: your_username
  password: your_password
```

### Best Practices

1. Use TLS encryption for production deployments
2. Use strong passwords and change default credentials
3. Limit MQTT broker access to trusted networks
4. Consider using client certificates for additional security
5. Use ACLs (Access Control Lists) on your MQTT broker to restrict topic access

## Troubleshooting

### Connection Issues

1. Check if MQTT broker is running:
```bash
mosquitto_sub -h localhost -t '$SYS/#' -C 1
```

2. Verify configuration:
   - Correct broker hostname/IP
   - Correct port (1883 for non-TLS, 8883 for TLS)
   - Valid credentials if authentication is enabled

3. Check logs:
```bash
python3 faac_gateway_mqtt.py -c config/config.yaml
```

### Commands Not Working

1. Verify command format (lowercase: `open`, `close`, `stop`)
2. Check QoS settings
3. Monitor the command topic:
```bash
mosquitto_sub -h localhost -t 'faac/gate/command' -v
```

### Status Not Updating

1. Check if serial connection is working
2. Verify gate is powered on
3. Check logs for errors

## Advanced Configuration

### Custom Topics

You can customize the base topic:

```yaml
mqtt:
  base_topic: home/garage/gate
```

This will create topics like:
- `home/garage/gate/state`
- `home/garage/gate/command`
- etc.

### Multiple Gates

Run multiple instances with different configurations:

```bash
# Gate 1
python3 faac_gateway_mqtt.py -c config/gate1.yaml

# Gate 2
python3 faac_gateway_mqtt.py -c config/gate2.yaml
```

Configure different serial ports and MQTT topics:

**gate1.yaml:**
```yaml
serial:
  port: /dev/ttyUSB0
mqtt:
  base_topic: faac/gate1
```

**gate2.yaml:**
```yaml
serial:
  port: /dev/ttyUSB1
mqtt:
  base_topic: faac/gate2
```

## State Definitions

| State | Description |
|-------|-------------|
| `OPEN` | Gate is fully open (position ≥ 95%) |
| `CLOSED` | Gate is fully closed (position = 0%) |
| `MOVING` | Gate is actively moving |
| `STOPPED` | Gate has stopped at an intermediate position |
| `UNKNOWN` | Initial state or no data received |

## Retained Messages

Status messages are published with the `retain` flag set to `true`. This means:
- New MQTT clients will immediately receive the last known state
- Status is persisted across broker restarts (if broker supports persistence)
- Useful for ensuring Home Assistant and other systems have current state after restart

## QoS Levels

The integration uses QoS 1 (at least once delivery) for:
- Command messages
- Status updates
- Availability messages

This ensures reliable message delivery while maintaining good performance.
