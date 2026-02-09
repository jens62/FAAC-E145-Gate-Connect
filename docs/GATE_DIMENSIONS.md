# FAAC Gate Physical Dimensions

Physical dimensions extracted from the gate SVG technical drawings.

## Overall Structure

| Dimension | Measurement |
|-----------|-------------|
| **Total Width** | 3480 mm (both wings + posts) |
| **Total Height** | 1330 mm |
| **Single Wing Width** | 1575 mm (closed position) |
| **Wing Height** | 1215 mm |

## Posts (Left and Right)

| Component | Measurement |
|-----------|-------------|
| **Width** | 100 mm (square profile) |
| **Height** | 1330 mm |
| **Material** | Steel (implied from structure) |
| **Position** | x = 0 mm (left), x = 3480 mm (right, mirrored) |

## Hinges

| Component | Measurement |
|-----------|-------------|
| **Width** | 32 mm |
| **Height** | 105 mm |
| **Position (horizontal)** | x = 105.25 mm from post edge |
| **Position (vertical)** | Top: y = 10 mm, Bottom: y = 1100 mm |
| **Quantity** | 2 per wing (top and bottom) |

### Hinge Geometry Details

- **Rotation axis**: x = 125 mm from post edge
  - Calculated as: Post edge (100 mm) + gap (9 mm) + hinge radius (16 mm)
- **Gap between post and hinge**: 9 mm (105.25 - 100 + 4 = calculated)

## Wing Frame (Closed Position)

### Frame Dimensions

| Component | Measurement |
|-----------|-------------|
| **Outer Width** | 1575 mm |
| **Outer Height** | 1215 mm |
| **Frame Profile** | 15 mm (when closed) |
| **Frame Profile** | 40 mm (when fully open - edge view) |

### Frame Position

| Element | Position |
|---------|----------|
| **Wing offset from hinge** | x = 142.5 mm (frame starts at x=150 mm absolute) |
| **Left edge** | x = 150 mm |
| **Right edge** | x = 1725 mm |
| **Top edge** | y = 7.5 mm |
| **Bottom edge** | y = 1207.5 mm |

## Vertical Bars

### Bar Specifications

| Property | Value |
|----------|-------|
| **Diameter** | 15 mm (round bars) |
| **Quantity** | 12 bars per wing |
| **Height** | 1200 mm (from y=15 to y=1215) |

### Bar Positions (X-coordinates from hinge axis)

| Bar # | Position (mm) | Distance from Hinge (mm) |
|-------|---------------|--------------------------|
| 1 | 128.65 | 3.65 |
| 2 | 249.81 | 124.81 |
| 3 | 370.96 | 245.96 |
| 4 | 492.12 | 367.12 |
| 5 | 613.27 | 488.27 |
| 6 | 734.42 | 609.42 |
| 7 | 855.58 | 730.58 |
| 8 | 976.73 | 851.73 |
| 9 | 1097.88 | 972.88 |
| 10 | 1219.04 | 1094.04 |
| 11 | 1340.19 | 1215.19 |
| 12 | 1461.35 | 1336.35 |

**Note:** Bars are spaced approximately 121.15 mm apart (measured from center to center).

### Adjusted Bar Positions (Used in Animation)

The animation uses slightly different bar positions for equal spacing:

| Bar # | Animation Position (mm) |
|-------|-------------------------|
| 1 | 271.15 |
| 2 | 392.31 |
| 3 | 513.46 |
| 4 | 634.62 |
| 5 | 755.77 |
| 6 | 876.92 |
| 7 | 998.08 |
| 8 | 1119.23 |
| 9 | 1240.38 |
| 10 | 1361.54 |
| 11 | 1482.69 |
| 12 | 1603.85 |

**Spacing:** Exactly 121.15 mm between each bar center.

## Horizontal Reinforcements

| Element | Position | Dimensions |
|---------|----------|------------|
| **Top reinforcement** | y = 250 mm | 15 mm diameter, spans full wing width |
| **Bottom reinforcement** | y = 1100 mm | 15 mm diameter, spans full wing width |

## Gate Operation Geometry

### Rotation

| Property | Value |
|----------|-------|
| **Rotation Axis** | x = 125 mm (hinge center) |
| **Rotation Range** | 0° (closed) to 90° (fully open) |
| **Closed Position** | Frame perpendicular to opening |
| **Open Position** | Frame parallel to opening (edge-on view) |

### Foreshortening Effect

When the gate rotates from closed (0°) to open (90°):

| State | Frame Appearance | Profile Width |
|-------|------------------|---------------|
| **Closed (0°)** | Full width visible (1575 mm) | 15 mm |
| **Open (90°)** | Edge-on view (40 mm visible) | 40 mm |

**Physics:**
- As rotation angle increases, the visible width compresses
- Frame profile appears wider when viewed edge-on
- Calculated using: `cos(angle)` for compression, `sin(angle)` for profile visibility

## Calculated Dimensions

### Wing Center of Mass (Closed Position)

- **Horizontal**: ~937.5 mm from hinge axis
- **Vertical**: ~612.5 mm from top

### Maximum Opening Width

When both wings are fully open (90°):
- Each wing extends approximately 40 mm from hinge axis
- Total opening width: ~3230 mm (3480 - 2×125 mm hinge positions)

## Material Specifications (Inferred)

| Component | Material | Profile Type |
|-----------|----------|--------------|
| **Posts** | Steel | 100×100 mm square |
| **Hinges** | Steel | 32 mm diameter |
| **Frame** | Steel strip | 40×15 mm rectangular |
| **Bars** | Steel | 15 mm diameter round |
| **Reinforcements** | Steel | 15 mm diameter round |

## Notes

- All dimensions are in millimeters (mm)
- Measurements extracted from SVG technical drawings
- Animation uses rotation axis at x=125 mm (hinge center)
- The gate design is symmetrical - right wing is a mirror of the left wing
- Frame profile thickness changes visually from 15 mm (closed) to 40 mm (open) due to viewing angle

## Reference Files

- **Closed position**: `docs/images/swing-leaf-gate-closed.svg`
- **Open position**: `docs/images/swing-leaf-gate-opened.svg`
- **Animation component**: `faac_gateway/web/static/js/gate-animation.js`
