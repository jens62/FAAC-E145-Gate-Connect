# Installation Scripts

System integration files for running FAAC Gateway as a service.

## 📁 Files

- **`faac-gateway.service`** - Systemd service unit file
- **`faac-gateway.logrotate`** - Logrotate configuration (optional)
- **`README.md`** - This file

## 🚀 Quick Installation

### 1. Install as Systemd Service

```bash
# Copy service file
sudo cp faac-gateway.service /etc/systemd/system/

# Edit service file to match your installation
sudo nano /etc/systemd/system/faac-gateway.service
# Adjust: User, WorkingDirectory, ExecStart paths

# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable faac-gateway

# Start service
sudo systemctl start faac-gateway

# Check status
sudo systemctl status faac-gateway
```

### 2. Configure Logging (Optional)

**Option A: Systemd Journal Only (Default)**
```bash
# View logs
journalctl -u faac-gateway -f

# No additional configuration needed!
```

**Option B: Systemd Journal + File Logging**
```bash
# Create log directory
sudo mkdir -p /var/log/faac-gateway
sudo chown pi:pi /var/log/faac-gateway  # Adjust user as needed

# Enable in config.yaml
sudo nano /opt/faac-gateway/config/config.yaml
```

Edit the logging section:
```yaml
logging:
  file: /var/log/faac-gateway/faac-gateway.log
  level: INFO
  max_bytes: 10485760  # 10MB
  backup_count: 5
```

```bash
# Restart service
sudo systemctl restart faac-gateway

# View file logs
tail -f /var/log/faac-gateway/faac-gateway.log
```

**Option C: Add System Logrotate (Optional)**

Python's RotatingFileHandler already handles rotation, but if you want system-level logrotate:

```bash
# Install logrotate config
sudo cp faac-gateway.logrotate /etc/logrotate.d/faac-gateway

# Test logrotate
sudo logrotate -d /etc/logrotate.d/faac-gateway
```

## 🔧 Service Configuration

### Systemd Service File

**Key settings in `faac-gateway.service`:**

```ini
[Unit]
Description=FAAC E145 Gate Connect with MQTT
After=network-online.target
Wants=network-online.target
```

**Why `network-online.target`?**
- ✅ Waits for network to be fully configured
- ✅ Perfect for remote MQTT brokers
- ✅ Ensures network is ready before starting

**If you need it:**
```bash
# Enable network-online.target
sudo systemctl enable systemd-networkd-wait-online.service
```

### Service Settings

```ini
[Service]
Type=simple
User=pi                                    # ← Change to your user
WorkingDirectory=/opt/faac-gateway         # ← Adjust path
ExecStart=/usr/bin/python3 /opt/faac-gateway/faac_gateway_mqtt.py -c /opt/faac-gateway/config/config.yaml
Restart=always                             # Auto-restart on crash
RestartSec=10                              # Wait 10s before restart
```

**Security settings:**
```ini
NoNewPrivileges=true    # Prevent privilege escalation
PrivateTmp=true         # Private /tmp directory
SupplementaryGroups=dialout  # Access to serial port
```

## 📊 Service Management

### Basic Commands

```bash
# Start service
sudo systemctl start faac-gateway

# Stop service
sudo systemctl stop faac-gateway

# Restart service
sudo systemctl restart faac-gateway

# Reload configuration (no downtime)
sudo systemctl reload faac-gateway

# Check status
sudo systemctl status faac-gateway

# Enable (start on boot)
sudo systemctl enable faac-gateway

# Disable (don't start on boot)
sudo systemctl disable faac-gateway
```

### View Logs

```bash
# Follow live logs
journalctl -u faac-gateway -f

# Last 100 lines
journalctl -u faac-gateway -n 100

# Logs from today
journalctl -u faac-gateway --since today

# Logs from last hour
journalctl -u faac-gateway --since "1 hour ago"

# Logs with timestamps
journalctl -u faac-gateway -o short-iso

# Search for errors
journalctl -u faac-gateway | grep -i error
```

### File Logs (if enabled)

```bash
# Follow live
tail -f /var/log/faac-gateway/faac-gateway.log

# View all logs (including rotated)
cat /var/log/faac-gateway/faac-gateway.log*

# Search for patterns
grep -i "mqtt" /var/log/faac-gateway/faac-gateway.log
```

## 🐛 Troubleshooting

### Service Won't Start

```bash
# Check status and recent logs
sudo systemctl status faac-gateway
journalctl -u faac-gateway -n 50

# Check if config file exists
ls -l /opt/faac-gateway/config/config.yaml

# Check if serial port exists
ls -l /dev/ttyUSB1

# Check if user has dialout group
groups pi  # Should include "dialout"
```

### Add User to dialout Group

```bash
sudo usermod -a -G dialout pi
# Logout and login for changes to take effect
```

### MQTT Connection Issues

```bash
# Check if MQTT broker is reachable
mosquitto_sub -h 192.168.0.194 -t 'faac/gate/#' -v

# Check logs for MQTT errors
journalctl -u faac-gateway | grep -i mqtt

# Test connection manually
telnet 192.168.0.194 1883
```

### Service Crashes/Restarts

```bash
# View crash logs
journalctl -u faac-gateway --since "10 minutes ago"

# Check restart count
systemctl show faac-gateway | grep NRestarts

# Disable auto-restart temporarily for debugging
sudo systemctl edit faac-gateway
# Add: Restart=no
```

## 🔄 MQTT Reconnection

The service automatically handles MQTT broker issues:

| Scenario | Behavior |
|----------|----------|
| **Broker down at startup** | ✅ Service starts anyway, keeps trying to connect |
| **Broker goes down** | ✅ Automatically reconnects when broker returns |
| **Broker down for days** | ✅ Keeps trying, reconnects when available |
| **Network outage** | ✅ Reconnects when network returns |

No manual intervention needed!

## 📈 Log Rotation

### Python RotatingFileHandler (Automatic)

When file logging is enabled, Python automatically:
- Rotates at 10MB (default, configurable)
- Keeps 5 backup files (default, configurable)
- Names: `faac-gateway.log`, `faac-gateway.log.1`, `faac-gateway.log.2`, etc.

**No logrotate needed!**

### System Logrotate (Optional)

If you prefer system-level logrotate:

```bash
# Install config
sudo cp faac-gateway.logrotate /etc/logrotate.d/faac-gateway

# Edit if needed
sudo nano /etc/logrotate.d/faac-gateway

# Test without making changes
sudo logrotate -d /etc/logrotate.d/faac-gateway

# Force rotation (for testing)
sudo logrotate -f /etc/logrotate.d/faac-gateway

# Check logrotate status
cat /var/lib/logrotate/status | grep faac
```

## 🔐 Permissions

### Serial Port Access

```bash
# Check serial port permissions
ls -l /dev/ttyUSB1
# Should show: crw-rw---- 1 root dialout

# Add user to dialout group
sudo usermod -a -G dialout pi

# Verify
groups pi
# Should include: dialout
```

### Log Directory Access

```bash
# Create log directory
sudo mkdir -p /var/log/faac-gateway

# Set ownership (if running as pi user)
sudo chown pi:pi /var/log/faac-gateway

# Set permissions
sudo chmod 755 /var/log/faac-gateway
```

## 📝 Configuration Files

### Main Config

**Location:** `/opt/faac-gateway/config/config.yaml`

Key sections:
```yaml
serial:
  port: /dev/ttyUSB1

mqtt:
  enabled: true
  broker: 192.168.0.194  # ← Your MQTT broker IP
  port: 1883

logging:
  file: /var/log/faac-gateway/faac-gateway.log  # ← Enable file logging
  level: INFO

web:
  enabled: true
  host: 0.0.0.0
  port: 5000
```

### Systemd Service Override

To customize without editing the original:

```bash
# Create override file
sudo systemctl edit faac-gateway

# Add overrides (example)
[Service]
Environment="PYTHONUNBUFFERED=1"
RestartSec=30
```

## 🎯 Best Practices

### Logging Strategy

**For Production:**
```yaml
logging:
  file: /var/log/faac-gateway/faac-gateway.log
  level: INFO
  max_bytes: 10485760
  backup_count: 7  # One week of 10MB logs
```

**For Development/Debugging:**
```yaml
logging:
  file: /var/log/faac-gateway/faac-gateway.log
  level: DEBUG  # More verbose
  max_bytes: 52428800  # 50MB
  backup_count: 3
```

**Minimal (Production):**
```yaml
logging:
  file: null  # Only systemd journal
  level: WARNING  # Only warnings and errors
```

### Service Reliability

The service configuration ensures reliability:
- ✅ `Restart=always` - Auto-restart on any failure
- ✅ `RestartSec=10` - Wait 10s between restarts (prevent tight restart loop)
- ✅ `network-online.target` - Wait for network before starting
- ✅ MQTT auto-reconnect - Handles broker outages gracefully

### Monitoring

```bash
# Check if service is running
systemctl is-active faac-gateway

# Check if service is enabled
systemctl is-enabled faac-gateway

# Check recent restarts
systemctl show faac-gateway | grep -E "NRestarts|RestartCount"

# Monitor logs live
journalctl -u faac-gateway -f | grep -E "ERROR|WARNING"
```

## 📚 Related Documentation

- [Main README](../README.md) - Project overview
- [MQTT Setup Guide](../MQTT_SETUP.md) - MQTT configuration
- [OpenHAB Integration](../openhab/README.md) - OpenHAB setup
- [Configuration Example](../config/config.yaml.example) - Config reference

## 🆘 Getting Help

If you encounter issues:

1. Check service status: `sudo systemctl status faac-gateway`
2. View recent logs: `journalctl -u faac-gateway -n 100`
3. Verify config: `cat /opt/faac-gateway/config/config.yaml`
4. Check serial port: `ls -l /dev/ttyUSB1`
5. Test MQTT: `mosquitto_sub -h <broker> -t 'faac/gate/#'`

For more help, check the [project issues](https://github.com/jens62/FAAC-E145-Gate-Connect/issues).
