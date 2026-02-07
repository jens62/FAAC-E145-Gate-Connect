# REST API Documentation

The FAAC Gateway includes a RESTful API for gate control and status monitoring. This provides an alternative to MQTT for systems that prefer HTTP-based integration.

## Table of Contents

1. [Overview](#overview)
2. [Base URL](#base-url)
3. [Authentication](#authentication)
4. [Endpoints](#endpoints)
5. [Examples](#examples)
6. [Error Handling](#error-handling)
7. [CORS Support](#cors-support)
8. [When to Use REST vs MQTT](#when-to-use-rest-vs-mqtt)

---

## Overview

The REST API provides simple HTTP endpoints for:
- **Reading** gate status (position, state, connection status)
- **Sending** commands (open, close, stop, position)
- **Health checks** for monitoring and load balancers

**Key Features**:
- ✅ Simple HTTP GET/POST requests
- ✅ JSON request/response format
- ✅ Optional API key authentication
- ✅ CORS support for web applications
- ✅ Works alongside MQTT (not a replacement)

---

## Base URL

All API endpoints are prefixed with `/api`:

```
http://<gateway-ip>:5000/api
```

Default: `http://localhost:5000/api`

---

## Authentication

### API Key (Optional)

API key authentication can be enabled via configuration. If no API key is configured, all endpoints are accessible without authentication (except `/api/health` which is always public).

#### Configure API Key

Edit `config/config.yaml`:

```yaml
api:
  enabled: true
  key: "your-secret-api-key-here"  # Set your API key
```

#### Providing API Key

**Method 1: HTTP Header (Recommended)**
```bash
curl -H "X-API-Key: your-secret-api-key-here" \
     http://localhost:5000/api/status
```

**Method 2: Query Parameter**
```bash
curl "http://localhost:5000/api/status?api_key=your-secret-api-key-here"
```

#### No Authentication

If `api.key` is `null` or not set, authentication is disabled:

```yaml
api:
  enabled: true
  key: null  # No authentication required
```

---

## Endpoints

### 1. GET /api/status

Get current gate status including position, state, and connection status.

**Authentication**: Required (if configured)

**Response**:
```json
{
  "wing1": 0,
  "wing2": 0,
  "state": "CLOSED",
  "online": true
}
```

**Fields**:
- `wing1` (integer): Position of wing 1 (0-100%)
- `wing2` (integer): Position of wing 2 (0-100%)
- `state` (string): Gate state - one of:
  - `OPEN` - Fully open
  - `CLOSED` - Fully closed
  - `MOVING` - In motion
  - `STOPPED` - Stopped mid-position
  - `UNKNOWN` - Status unknown or offline
- `online` (boolean): Connection status to gate controller

**Example**:
```bash
curl http://localhost:5000/api/status
```

---

### 2. POST /api/command

Send command to gate (open, close, stop, or position).

**Authentication**: Required (if configured)

**Request Body** (JSON):
```json
{
  "command": "open"
}
```

**Commands**:
- `"open"` - Open gate (run to open limit)
- `"close"` - Close gate (run to close limit)
- `"stop"` - Stop gate movement
- `0-100` - Set position (0=closed, 100=open)

**Special Behavior**:
- Position `0` is mapped to `"close"` command (ensures limit switch accuracy)
- Position `100` is mapped to `"open"` command (ensures limit switch accuracy)
- Positions `1-99` use precise positioning

**Response** (Success):
```json
{
  "status": "ok",
  "command": "open"
}
```

If position was mapped to a command:
```json
{
  "status": "ok",
  "command": "100",
  "sent": "open"
}
```

**Examples**:

```bash
# Open gate
curl -X POST http://localhost:5000/api/command \
     -H "Content-Type: application/json" \
     -d '{"command": "open"}'

# Close gate
curl -X POST http://localhost:5000/api/command \
     -H "Content-Type: application/json" \
     -d '{"command": "close"}'

# Stop gate
curl -X POST http://localhost:5000/api/command \
     -H "Content-Type: application/json" \
     -d '{"command": "stop"}'

# Set position to 50%
curl -X POST http://localhost:5000/api/command \
     -H "Content-Type: application/json" \
     -d '{"command": "50"}'

# With API key
curl -X POST http://localhost:5000/api/command \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your-secret-api-key-here" \
     -d '{"command": "open"}'
```

---

### 3. GET /api/health

Health check endpoint for monitoring and load balancers.

**Authentication**: None (always public)

**Response**:
```json
{
  "status": "ok",
  "service": "faac-gateway",
  "online": true,
  "mqtt_enabled": true
}
```

**Fields**:
- `status` (string): Always `"ok"` if service is responding
- `service` (string): Service identifier (`"faac-gateway"`)
- `online` (boolean): Gate controller connection status
- `mqtt_enabled` (boolean): Whether MQTT integration is enabled

**Example**:
```bash
curl http://localhost:5000/api/health
```

**Use Cases**:
- Monitoring systems (Nagios, Zabbix, etc.)
- Load balancer health checks
- Service discovery
- Quick status verification

---

## Examples

### Python

```python
import requests

BASE_URL = "http://localhost:5000/api"
API_KEY = "your-secret-api-key-here"  # Optional

headers = {}
if API_KEY:
    headers["X-API-Key"] = API_KEY

# Get status
response = requests.get(f"{BASE_URL}/status", headers=headers)
status = response.json()
print(f"Gate state: {status['state']}")
print(f"Wing 1: {status['wing1']}%")
print(f"Wing 2: {status['wing2']}%")

# Send command
response = requests.post(
    f"{BASE_URL}/command",
    json={"command": "open"},
    headers=headers
)
result = response.json()
print(f"Command result: {result['status']}")

# Health check
response = requests.get(f"{BASE_URL}/health")
health = response.json()
print(f"Service: {health['service']}, Online: {health['online']}")
```

### Shell Script

```bash
#!/bin/bash

API_URL="http://localhost:5000/api"
API_KEY="your-secret-api-key-here"  # Optional

# Function to call API with optional auth
api_call() {
    local method=$1
    local endpoint=$2
    local data=$3

    if [ -n "$API_KEY" ]; then
        if [ "$method" = "GET" ]; then
            curl -H "X-API-Key: $API_KEY" "$API_URL/$endpoint"
        else
            curl -X POST -H "Content-Type: application/json" \
                 -H "X-API-Key: $API_KEY" \
                 -d "$data" "$API_URL/$endpoint"
        fi
    else
        if [ "$method" = "GET" ]; then
            curl "$API_URL/$endpoint"
        else
            curl -X POST -H "Content-Type: application/json" \
                 -d "$data" "$API_URL/$endpoint"
        fi
    fi
}

# Get status
echo "Current status:"
api_call GET status | jq

# Open gate
echo "Opening gate..."
api_call POST command '{"command":"open"}'

# Wait 5 seconds
sleep 5

# Check status again
echo "Status after opening:"
api_call GET status | jq
```

### JavaScript (Node.js)

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:5000/api';
const API_KEY = 'your-secret-api-key-here';  // Optional

const headers = API_KEY ? { 'X-API-Key': API_KEY } : {};

// Get status
async function getStatus() {
    const response = await axios.get(`${BASE_URL}/status`, { headers });
    console.log('Status:', response.data);
    return response.data;
}

// Send command
async function sendCommand(command) {
    const response = await axios.post(
        `${BASE_URL}/command`,
        { command },
        { headers }
    );
    console.log('Result:', response.data);
    return response.data;
}

// Health check
async function checkHealth() {
    const response = await axios.get(`${BASE_URL}/health`);
    console.log('Health:', response.data);
    return response.data;
}

// Usage
(async () => {
    await checkHealth();
    await getStatus();
    await sendCommand('open');
})();
```

### Home Assistant REST Command

Add to `configuration.yaml`:

```yaml
rest_command:
  faac_gate_open:
    url: http://192.168.1.100:5000/api/command
    method: POST
    headers:
      Content-Type: application/json
      X-API-Key: your-secret-api-key-here  # If using authentication
    payload: '{"command": "open"}'

  faac_gate_close:
    url: http://192.168.1.100:5000/api/command
    method: POST
    headers:
      Content-Type: application/json
      X-API-Key: your-secret-api-key-here
    payload: '{"command": "close"}'

  faac_gate_stop:
    url: http://192.168.1.100:5000/api/command
    method: POST
    headers:
      Content-Type: application/json
      X-API-Key: your-secret-api-key-here
    payload: '{"command": "stop"}'

# RESTful sensor for gate status
sensor:
  - platform: rest
    name: FAAC Gate Status
    resource: http://192.168.1.100:5000/api/status
    headers:
      X-API-Key: your-secret-api-key-here
    value_template: "{{ value_json.state }}"
    json_attributes:
      - wing1
      - wing2
      - online
    scan_interval: 5
```

---

## Error Handling

### Error Response Format

All errors return JSON with consistent format:

```json
{
  "error": "Error type",
  "message": "Detailed error message"
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| `200` | OK | Request successful |
| `400` | Bad Request | Invalid request format or parameters |
| `401` | Unauthorized | Invalid or missing API key |
| `404` | Not Found | Endpoint does not exist |
| `405` | Method Not Allowed | Wrong HTTP method for endpoint |
| `500` | Internal Server Error | Server error |
| `503` | Service Unavailable | Gate controller not initialized |

### Common Errors

**401 Unauthorized**:
```json
{
  "error": "Unauthorized",
  "message": "Invalid or missing API key"
}
```

**400 Bad Request** (missing command):
```json
{
  "error": "Bad request",
  "message": "Missing \"command\" field"
}
```

**400 Bad Request** (invalid command):
```json
{
  "error": "Bad request",
  "message": "Invalid command. Use \"open\", \"close\", \"stop\", or position 0-100"
}
```

**400 Bad Request** (invalid position):
```json
{
  "error": "Bad request",
  "message": "Position must be between 0 and 100"
}
```

**503 Service Unavailable**:
```json
{
  "error": "Service unavailable",
  "message": "Gate controller not initialized"
}
```

---

## CORS Support

CORS (Cross-Origin Resource Sharing) allows web applications from other domains to call the API.

### Enable CORS

Edit `config/config.yaml`:

```yaml
api:
  enabled: true
  cors_enabled: true
  cors_origins: "*"  # Allow all origins (or specify domain)
```

### Restrict to Specific Domain

```yaml
api:
  cors_enabled: true
  cors_origins: "https://example.com"
```

### Security Note

⚠️ **Only enable CORS if needed**. Allowing all origins (`*`) means any website can call your API. Combine with API key authentication for security.

---

## When to Use REST vs MQTT

### Use REST API when:
✅ You need simple request/response interactions
✅ You're writing shell scripts or cron jobs
✅ Your system doesn't support MQTT well
✅ You want stateless operations
✅ You need webhook-based integrations

### Use MQTT when:
✅ You want real-time push updates
✅ You're integrating with home automation (HA, OpenHAB)
✅ You need efficient bandwidth usage
✅ You want pub/sub pattern
✅ Multiple systems need to monitor status

### Use Both:
- **REST** for manual control and scripting
- **MQTT** for automation and real-time monitoring

They work perfectly together! For example:
- Home Assistant uses MQTT for real-time status updates
- Cron job uses REST API to close gate at night
- Monitoring system uses REST `/api/health` for health checks

---

## Security Best Practices

### 1. Use API Key Authentication

```yaml
api:
  enabled: true
  key: "generate-a-long-random-key-here"
```

Generate a secure key:
```bash
openssl rand -base64 32
```

### 2. Use HTTPS (Reverse Proxy)

For external access, use nginx or Apache with Let's Encrypt:

```nginx
server {
    listen 443 ssl;
    server_name gate.example.com;

    ssl_certificate /etc/letsencrypt/live/gate.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/gate.example.com/privkey.pem;

    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. Firewall Rules

If only local access needed:
```bash
# Only allow from local network
sudo ufw allow from 192.168.1.0/24 to any port 5000
```

### 4. Rate Limiting (Optional)

For production, consider adding rate limiting with nginx or Flask-Limiter.

---

## Testing the API

### Quick Test

```bash
# Health check (no auth needed)
curl http://localhost:5000/api/health

# Get status
curl http://localhost:5000/api/status

# Send command
curl -X POST http://localhost:5000/api/command \
     -H "Content-Type: application/json" \
     -d '{"command": "open"}'
```

### Test with jq (Pretty JSON)

```bash
# Install jq
sudo apt install jq

# Get status with pretty formatting
curl -s http://localhost:5000/api/status | jq

# Monitor status continuously
watch -n 1 'curl -s http://localhost:5000/api/status | jq'
```

### Test Script

```bash
#!/bin/bash
# test_api.sh - Complete API test

API_URL="http://localhost:5000/api"

echo "=== Testing FAAC Gateway REST API ==="
echo

echo "1. Health Check:"
curl -s "$API_URL/health" | jq
echo

echo "2. Get Status:"
curl -s "$API_URL/status" | jq
echo

echo "3. Send OPEN command:"
curl -s -X POST "$API_URL/command" \
     -H "Content-Type: application/json" \
     -d '{"command":"open"}' | jq
echo

sleep 2

echo "4. Get Status (should be MOVING or OPEN):"
curl -s "$API_URL/status" | jq
echo

echo "5. Send STOP command:"
curl -s -X POST "$API_URL/command" \
     -H "Content-Type: application/json" \
     -d '{"command":"stop"}' | jq
echo

echo "=== Test Complete ==="
```

---

## Related Documentation

- [Main README](../README.md) - Project overview
- [MQTT Setup](../MQTT_SETUP.md) - MQTT integration
- [OpenHAB Integration](../openhab/README.md) - OpenHAB setup
- [Installation Guide](../scripts/README.md) - Service setup

---

## Support

For issues or questions:
- [GitHub Issues](https://github.com/jens62/FAAC-E145-Gate-Connect/issues)
- [Project Repository](https://github.com/jens62/FAAC-E145-Gate-Connect)
