# MQTT Setup Guide

Quick guide to get MQTT functionality up and running.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure

```bash
cp config/config.yaml.example config/config.yaml
nano config/config.yaml
```

Edit the MQTT section:
```yaml
mqtt:
  enabled: true
  broker: localhost  # Change to your MQTT broker IP/hostname
  port: 1883
  username: null     # Optional: your MQTT username
  password: null     # Optional: your MQTT password
  base_topic: faac/gate
```

### 3. Run

```bash
python3 faac_gateway_mqtt.py -c config/config.yaml
```

## MQTT Topics

### Subscribe to status (read-only):

- `faac/gate/status` - Full status as JSON
- `faac/gate/state` - OPEN, CLOSED, MOVING, STOPPED, UNKNOWN
- `faac/gate/wing1` - Wing 1 position (0-100%)
- `faac/gate/wing2` - Wing 2 position (0-100%)
- `faac/gate/availability` - online/offline

### Publish commands (write):

- `faac/gate/command` - Send: `open`, `close`, or `stop`

## Testing

### Subscribe to all topics:
```bash
mosquitto_sub -h localhost -t 'faac/gate/#' -v
```

### Send commands:
```bash
# Open gate
mosquitto_pub -h localhost -t 'faac/gate/command' -m 'open'

# Close gate
mosquitto_pub -h localhost -t 'faac/gate/command' -m 'close'

# Stop gate
mosquitto_pub -h localhost -t 'faac/gate/command' -m 'stop'
```

### Test with Python:
```bash
python3 examples/mqtt_test.py
```

## Home Assistant Integration

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
```

## Docker Setup

```bash
# Edit docker-compose.yml to set your serial port
nano docker-compose.yml

# Start services
docker-compose up -d

# View logs
docker-compose logs -f
```

## Troubleshooting

### Can't connect to MQTT broker

1. Check if broker is running:
```bash
systemctl status mosquitto
```

2. Test connection:
```bash
mosquitto_pub -h localhost -t test -m "hello"
```

### Commands not working

1. Verify command format (lowercase):
   - ✓ `open`, `close`, `stop`
   - ✗ `OPEN`, `Open`, `opening`

2. Check logs:
```bash
python3 faac_gateway_mqtt.py -c config/config.yaml
```

### Serial port not found

1. Find your port:
```bash
ls /dev/ttyUSB* /dev/ttyACM*
```

2. Update config.yaml:
```yaml
serial:
  port: /dev/ttyUSB0  # Your actual port
```

## More Information

- [Full MQTT Documentation](docs/MQTT.md)
- [Installation Guide](docs/installation.md)
- [Protocol Documentation](docs/protocol.md)
