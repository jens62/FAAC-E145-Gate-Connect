# Gate SVG Icons for OpenHAB

Static SVG icons showing the gate at different positions for use in OpenHAB sitemap.

## Files

**Base icon (required by OpenHAB):**
- `gate.svg` - Gate at 50% position (placeholder/default icon)

**Position icons (match transformed Rollershutter state):**
- `gate-0.svg` - Gate fully **OPEN** (Rollershutter 0 = physical 100%)
- `gate-10.svg` - Gate 90% open (Rollershutter 10 = physical 90%)
- `gate-20.svg` - Gate 80% open (Rollershutter 20 = physical 80%)
- `gate-30.svg` - Gate 70% open (Rollershutter 30 = physical 70%)
- `gate-40.svg` - Gate 60% open (Rollershutter 40 = physical 60%)
- `gate-50.svg` - Gate 50% open (Rollershutter 50 = physical 50%)
- `gate-60.svg` - Gate 40% open (Rollershutter 60 = physical 40%)
- `gate-70.svg` - Gate 30% open (Rollershutter 70 = physical 30%)
- `gate-80.svg` - Gate 20% open (Rollershutter 80 = physical 20%)
- `gate-90.svg` - Gate 10% open (Rollershutter 90 = physical 10%)
- `gate-100.svg` - Gate fully **CLOSED** (Rollershutter 100 = physical 0%)

## Icon Selection: Transformed Rollershutter State

OpenHAB selects icons based on the **transformed Rollershutter item state**, not the raw MQTT value.

The OpenHAB things file uses `invert.js` to transform the gate position:

```
transformationPattern="JS:invert.js",
transformationPatternOut="JS:invert.js",
```

**How it works:**
1. MQTT publishes physical gate position: `wing1=0` (closed) to `wing1=100` (open)
2. `invert.js` transforms to Rollershutter convention: `0` (open) to `100` (closed)
3. OpenHAB Rollershutter item displays transformed state
4. **Icon selection uses the transformed state**

Therefore, icon naming matches the Rollershutter state after transformation:
- `gate-0.svg` shows a physically **open** gate (Rollershutter 0 = open convention)
- `gate-100.svg` shows a physically **closed** gate (Rollershutter 100 = closed convention)

This ensures the correct icon is displayed for the Rollershutter state.

## Installation

Copy the SVG files to your OpenHAB classic icons directory:

```bash
# Copy all gate icons
cp openhab/icons/*.svg $OPENHAB_CONF/icons/classic/

# Or specify path explicitly (adjust for your system)
cp openhab/icons/*.svg /etc/openhab/icons/classic/

# Or on Docker installations
cp openhab/icons/*.svg /openhab/conf/icons/classic/
```

## Usage in Sitemap

OpenHAB will automatically select the appropriate icon based on the item state.

For a `Rollershutter` item representing the gate position:

```
Slider item=FAAC_Gate icon="gate"
```

OpenHAB icon selection (based on transformed Rollershutter state):
- `gate.svg` = default/fallback
- `gate-0.svg` = shown when Rollershutter state=0-9 (gate open)
- `gate-10.svg` = shown when Rollershutter state=10-19
- `gate-20.svg` = shown when Rollershutter state=20-29
- etc.
- `gate-100.svg` = shown when Rollershutter state=100 (gate closed)

## Browser Compatibility

**Known Issue:** The dynamic icon display has a rendering issue in **Firefox on macOS** (tested in private browsing mode). Icons may appear to "flip" or display incorrectly during gate movement.

**Working browsers:**
- ✅ Chrome (macOS, Windows, Linux)
- ✅ Safari (macOS)
- ✅ OpenHAB iOS App (iPhone)
- ⚠️ Firefox on macOS - visual glitches during icon updates

If you experience icon flipping in Firefox, try using Chrome or the OpenHAB mobile app instead.

## Regenerating Icons

If you need to regenerate the icons (e.g., after changing gate geometry):

```bash
python3 scripts/generate_openhab_gate_icons.py
```

The script:
1. Generates `gate.svg` (50% position as placeholder)
2. Generates 11 position icons with inverted naming
3. Uses the same geometry as `docs/gate_animation_2d.html` for consistency

## Icon Details

- **Format**: SVG (Scalable Vector Graphics)
- **Size**: 3480 x 1330 viewBox
- **Background**: Light blue gradient (matches web animation)
- **Gate elements**: Posts, hinges, frame, reinforcements, bars
- **Colors**: Dark grey (#555) for gate, light blue gradient background
- **Total files**: 12 (gate.svg + gate-0 through gate-100)

## See Also

- [OpenHAB Integration README](../README.md)
- [Gate Animation](../../docs/gate_animation_2d.html)
- [Icon generation script](../../scripts/generate_openhab_gate_icons.py)
- [OpenHAB Classic Icons Documentation](https://www.openhab.org/docs/configuration/iconsets/classic/)
