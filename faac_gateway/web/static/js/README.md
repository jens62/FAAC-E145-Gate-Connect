# FAAC Gate Animation Web Component

A reusable, self-contained gate animation component that can be embedded in any web application.

## Features

- ✅ **Zero dependencies** - Pure vanilla JavaScript Web Component
- ✅ **Framework agnostic** - Works in any HTML context
- ✅ **Single source of truth** - Update once, works everywhere
- ✅ **Shadow DOM** - Encapsulated styles, no conflicts
- ✅ **Reactive** - Automatically updates when attributes change
- ✅ **Simple API** - Easy to use programmatically or declaratively

## Usage

### Basic HTML

```html
<!DOCTYPE html>
<html>
<head>
    <script type="module" src="gate-animation.js"></script>
</head>
<body>
    <!-- Declarative: Set initial positions via attributes -->
    <gate-animation wing1="50" wing2="45"></gate-animation>
</body>
</html>
```

### Programmatic API

```javascript
// Get reference to the component
const gate = document.querySelector('gate-animation');

// Set wing positions (0-100)
gate.setWingPosition(1, 75);  // Wing 1 to 75%
gate.setWingPosition(2, 80);  // Wing 2 to 80%

// Get current positions
const wing1Pos = gate.getWingPosition(1);
const wing2Pos = gate.getWingPosition(2);
```

### Reactive Attributes

The component automatically updates when attributes change:

```javascript
const gate = document.querySelector('gate-animation');

// These will trigger visual updates automatically
gate.setAttribute('wing1', '90');
gate.setAttribute('wing2', '85');
```

## Integration Examples

### Flask (Current Implementation)

```python
# Flask automatically serves from static folder
app = Flask(__name__, static_folder='static', static_url_path='/static')
```

```html
<script type="module" src="/static/js/gate-animation.js"></script>
<gate-animation id="gate" wing1="0" wing2="0"></gate-animation>

<script>
    const gate = document.getElementById('gate');

    // Update from SSE
    source.onmessage = function(e) {
        const data = JSON.parse(e.data);
        gate.setWingPosition(1, data.wing1);
        gate.setWingPosition(2, data.wing2);
    };
</script>
```

### Home Assistant (Lovelace Custom Card)

```javascript
// custom-card/gate-card.js
import './gate-animation.js';

class GateCard extends HTMLElement {
    setConfig(config) {
        this.innerHTML = `<gate-animation wing1="0" wing2="0"></gate-animation>`;
        this.gateAnimation = this.querySelector('gate-animation');
    }

    set hass(hass) {
        // Update from Home Assistant entity states
        const wing1 = hass.states['sensor.faac_gate_wing1'].state;
        const wing2 = hass.states['sensor.faac_gate_wing2'].state;

        this.gateAnimation.setWingPosition(1, parseFloat(wing1));
        this.gateAnimation.setWingPosition(2, parseFloat(wing2));
    }
}

customElements.define('gate-card', GateCard);
```

### OpenHAB (HABPanel Widget)

```html
<!-- HABPanel custom widget -->
<script src="gate-animation.js"></script>

<gate-animation id="gate" wing1="0" wing2="0"></gate-animation>

<script>
    const gate = document.getElementById('gate');

    // Subscribe to OpenHAB item updates
    smarthome.subscribe('Hoftor_Wing1', function(item) {
        gate.setWingPosition(1, parseFloat(item.state));
    });

    smarthome.subscribe('Hoftor_Wing2', function(item) {
        gate.setWingPosition(2, parseFloat(item.state));
    });
</script>
```

### MQTT (Direct Subscription)

```html
<script src="https://unpkg.com/mqtt/dist/mqtt.min.js"></script>
<script type="module" src="gate-animation.js"></script>

<gate-animation id="gate" wing1="0" wing2="0"></gate-animation>

<script>
    const gate = document.getElementById('gate');
    const client = mqtt.connect('ws://broker:9001');

    client.on('connect', function() {
        client.subscribe('faac/gate/wing1');
        client.subscribe('faac/gate/wing2');
    });

    client.on('message', function(topic, message) {
        const value = parseInt(message.toString());

        if (topic === 'faac/gate/wing1') {
            gate.setWingPosition(1, value);
        } else if (topic === 'faac/gate/wing2') {
            gate.setWingPosition(2, value);
        }
    });
</script>
```

## Component API

### Attributes

| Attribute | Type | Description | Default |
|-----------|------|-------------|---------|
| `wing1` | number | Wing 1 position (0-100) | 0 |
| `wing2` | number | Wing 2 position (0-100) | 0 |

### Methods

#### `setWingPosition(wingId, position)`

Set wing position programmatically.

- **wingId** (number): Wing identifier (1 or 2)
- **position** (number): Position percentage (0-100)

```javascript
gate.setWingPosition(1, 75);
```

#### `getWingPosition(wingId)`

Get current wing position.

- **wingId** (number): Wing identifier (1 or 2)
- **Returns** (number): Current position (0-100)

```javascript
const position = gate.getWingPosition(1);
```

## Styling

The component uses Shadow DOM, so internal styles are encapsulated. To style the container:

```css
gate-animation {
    display: block;
    width: 100%;
    max-width: 800px;
    margin: 0 auto;
}
```

## Browser Compatibility

- ✅ Chrome/Edge (88+)
- ✅ Firefox (63+)
- ✅ Safari (14+)
- ✅ All modern browsers with Web Components support

## Maintenance

**This is the single source of truth for the gate animation.**

When you update `gate-animation.js`:
- The Flask web UI automatically uses the new version
- Home Assistant cards automatically use the new version (after copying the file)
- OpenHAB widgets automatically use the new version (after copying the file)

No need to maintain multiple implementations!

## Technical Details

### Gate Geometry

- Rotation axis: x=125 (hinge center)
- Frame closed position: left=150, right=1725
- Frame stroke: 15mm (closed) to 40mm (open)
- 12 vertical bars with equal 121.15mm spacing

### Animation Physics

The component calculates foreshortening based on rotation angle (0-90°):
- 0% (closed): Full width, narrow stroke
- 100% (open): Compressed width (edge-on view), wide stroke

Position is converted to angle: `angle = (position / 100) * (π / 2)`

All frame and bar positions are calculated using trigonometry (cos/sin) for smooth, realistic rotation.
