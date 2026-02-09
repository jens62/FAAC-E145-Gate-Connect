#!/usr/bin/env python3
"""
Generate static gate SVG icons for OpenHAB

Creates 12 SVG files:
- gate.svg (50% position - required by OpenHAB as placeholder)
- gate-0.svg to gate-100.svg (matches Rollershutter state after invert.js transformation)

IMPORTANT: OpenHAB selects icons based on the transformed Rollershutter item state.
With invert.js transformation: Rollershutter 0=OPEN, 100=CLOSED
Therefore: gate-0.svg shows physically open gate, gate-100.svg shows physically closed gate

For use in OpenHAB sitemap icons ($OPENHAB_CONF/icons/classic/)
"""

import math
import os

# Gate geometry constants (from gate_animation_2d.html)
ROTATION_X = 125
FRAME_LEFT_CLOSED = 150
FRAME_RIGHT_CLOSED = 1725
FRAME_LEFT_DX = FRAME_LEFT_CLOSED - ROTATION_X   # 25
FRAME_RIGHT_DX = FRAME_RIGHT_CLOSED - ROTATION_X  # 1600
FRAME_STROKE_CLOSED = 15
FRAME_STROKE_OPEN = 40

# Bar positions when closed (absolute x coordinates)
BAR_POSITIONS = [271.15, 392.31, 513.46, 634.62, 755.77, 876.92,
                 998.08, 1119.23, 1240.38, 1361.54, 1482.69, 1603.85]
BAR_DX = [x - ROTATION_X for x in BAR_POSITIONS]

# Post and hinge positions
POST_X = 0
POST_Y = -7.5
HINGE_X = 105.25
HINGE_Y_TOP = 10
HINGE_Y_BOTTOM = 1100


def calculate_wing_geometry(position_percent):
    """
    Calculate wing geometry for a given position percentage

    Args:
        position_percent: Gate position (0 = closed, 100 = open)

    Returns:
        Dictionary with wing geometry data
    """
    angle = (position_percent / 100) * (math.pi / 2)
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)

    # Frame positions
    frame_left_x = ROTATION_X + FRAME_LEFT_DX * cos_a
    frame_right_x = ROTATION_X + FRAME_RIGHT_DX * cos_a

    # Frame stroke width
    vert_stroke = FRAME_STROKE_CLOSED * cos_a + FRAME_STROKE_OPEN * sin_a
    half_vs = vert_stroke / 2

    # Horizontal frame extents
    h_left = frame_left_x - half_vs
    h_right = frame_right_x + half_vs

    # Bar positions
    bar_positions = [ROTATION_X + dx * cos_a for dx in BAR_DX]

    return {
        'frame_left_x': frame_left_x,
        'frame_right_x': frame_right_x,
        'vert_stroke': vert_stroke,
        'h_left': h_left,
        'h_right': h_right,
        'bar_positions': bar_positions
    }


def generate_svg(position_percent, output_path):
    """
    Generate SVG file for gate at specific position

    Args:
        position_percent: Gate position (0-100)
        output_path: Output file path
    """
    geom = calculate_wing_geometry(position_percent)

    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="3480" height="1330" viewBox="-7.5 -7.5 3480 1330" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- Hinge symbol -->
    <symbol id="hinge" width="32" height="105">
      <rect width="32" height="105" fill="#555" />
      <line x1="0" y1="35" x2="32" y2="35" stroke="#888" stroke-width="1" />
      <line x1="0" y1="70" x2="32" y2="70" stroke="#888" stroke-width="1" />
    </symbol>

    <!-- Post symbol -->
    <symbol id="post">
      <line x1="50" y1="0" x2="50" y2="1330" stroke="#555" stroke-width="100" />
    </symbol>
  </defs>

  <!-- Background (light blue gradient) -->
  <rect x="-7.5" y="-7.5" width="3480" height="1330" fill="url(#bg-gradient)" />
  <defs>
    <linearGradient id="bg-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#d4e6f1;stop-opacity:1" />
      <stop offset="50%" style="stop-color:#e8f4f8;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#d0d8dc;stop-opacity:1" />
    </linearGradient>
  </defs>

  <!-- Left side -->
  <use href="#post" x="{POST_X}" y="{POST_Y}" />
  <use href="#hinge" x="{HINGE_X}" y="{HINGE_Y_TOP}" />
  <use href="#hinge" x="{HINGE_X}" y="{HINGE_Y_BOTTOM}" />

  <!-- Left wing -->
  <g id="wing1">
    <!-- Frame horizontal edges -->
    <line x1="{geom['h_left']:.2f}" y1="7.5" x2="{geom['h_right']:.2f}" y2="7.5" stroke="#555" stroke-width="15" />
    <line x1="{geom['h_left']:.2f}" y1="1207.5" x2="{geom['h_right']:.2f}" y2="1207.5" stroke="#555" stroke-width="15" />

    <!-- Frame vertical edges -->
    <line x1="{geom['frame_left_x']:.2f}" y1="7.5" x2="{geom['frame_left_x']:.2f}" y2="1207.5" stroke="#555" stroke-width="{geom['vert_stroke']:.2f}" />
    <line x1="{geom['frame_right_x']:.2f}" y1="7.5" x2="{geom['frame_right_x']:.2f}" y2="1207.5" stroke="#555" stroke-width="{geom['vert_stroke']:.2f}" />

    <!-- Horizontal reinforcements -->
    <line x1="{geom['frame_left_x']:.2f}" y1="242.5" x2="{geom['frame_right_x']:.2f}" y2="242.5" stroke="#555" stroke-width="15" />
    <line x1="{geom['frame_left_x']:.2f}" y1="1092.5" x2="{geom['frame_right_x']:.2f}" y2="1092.5" stroke="#555" stroke-width="15" />

    <!-- Vertical bars -->'''

    for i, bar_x in enumerate(geom['bar_positions'], 1):
        svg_content += f'''
    <line x1="{bar_x:.2f}" y1="7.5" x2="{bar_x:.2f}" y2="1207.5" stroke="#555" stroke-width="15" />'''

    svg_content += '''
  </g>

  <!-- Right side (mirrored) -->
  <g transform="translate(3480, 0) scale(-1, 1)">
    <use href="#post" x="''' + str(POST_X) + '''" y="''' + str(POST_Y) + '''" />
    <use href="#hinge" x="''' + str(HINGE_X) + '''" y="''' + str(HINGE_Y_TOP) + '''" />
    <use href="#hinge" x="''' + str(HINGE_X) + '''" y="''' + str(HINGE_Y_BOTTOM) + '''" />

    <!-- Right wing -->
    <g id="wing2">
      <!-- Frame horizontal edges -->
      <line x1="''' + f"{geom['h_left']:.2f}" + '''" y1="7.5" x2="''' + f"{geom['h_right']:.2f}" + '''" y2="7.5" stroke="#555" stroke-width="15" />
      <line x1="''' + f"{geom['h_left']:.2f}" + '''" y1="1207.5" x2="''' + f"{geom['h_right']:.2f}" + '''" y2="1207.5" stroke="#555" stroke-width="15" />

      <!-- Frame vertical edges -->
      <line x1="''' + f"{geom['frame_left_x']:.2f}" + '''" y1="7.5" x2="''' + f"{geom['frame_left_x']:.2f}" + '''" y2="1207.5" stroke="#555" stroke-width="''' + f"{geom['vert_stroke']:.2f}" + '''" />
      <line x1="''' + f"{geom['frame_right_x']:.2f}" + '''" y1="7.5" x2="''' + f"{geom['frame_right_x']:.2f}" + '''" y2="1207.5" stroke="#555" stroke-width="''' + f"{geom['vert_stroke']:.2f}" + '''" />

      <!-- Horizontal reinforcements -->
      <line x1="''' + f"{geom['frame_left_x']:.2f}" + '''" y1="242.5" x2="''' + f"{geom['frame_right_x']:.2f}" + '''" y2="242.5" stroke="#555" stroke-width="15" />
      <line x1="''' + f"{geom['frame_left_x']:.2f}" + '''" y1="1092.5" x2="''' + f"{geom['frame_right_x']:.2f}" + '''" y2="1092.5" stroke="#555" stroke-width="15" />

      <!-- Vertical bars -->'''

    for i, bar_x in enumerate(geom['bar_positions'], 1):
        svg_content += f'''
      <line x1="{bar_x:.2f}" y1="7.5" x2="{bar_x:.2f}" y2="1207.5" stroke="#555" stroke-width="15" />'''

    svg_content += '''
    </g>
  </g>
</svg>
'''

    with open(output_path, 'w') as f:
        f.write(svg_content)

    print(f"Generated: {output_path}")


def main():
    """Generate all 11 gate icon SVG files"""
    # Create output directory
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'openhab', 'icons')
    os.makedirs(output_dir, exist_ok=True)

    # Generate gate.svg (50% position - required by OpenHAB as placeholder)
    gate_svg_path = os.path.join(output_dir, 'gate.svg')
    generate_svg(50, gate_svg_path)
    print(f"Generated base icon: {gate_svg_path}")

    # Generate icons for 0%, 10%, 20%, ..., 100%
    # OpenHAB selects icons based on the TRANSFORMED Rollershutter state (after invert.js)
    # Rollershutter convention: 0=OPEN, 100=CLOSED
    # So gate-X.svg must show what the gate looks like when Rollershutter state = X
    # gate-0.svg = Rollershutter OPEN = physically 100% (open gate)
    # gate-100.svg = Rollershutter CLOSED = physically 0% (closed gate)
    for rollershutter_state in range(0, 101, 10):
        physical_position = 100 - rollershutter_state  # Invert: Rollershutter 0=open → physical 100
        filename = f"gate-{rollershutter_state}.svg"
        output_path = os.path.join(output_dir, filename)
        generate_svg(physical_position, output_path)

    print(f"\nGenerated 12 SVG icons (gate.svg + gate-0 to gate-100) in: {output_dir}")
    print("\nIcon naming (matches OpenHAB Rollershutter state after transformation):")
    print("  gate-0.svg   = Rollershutter OPEN (physical 100% open)")
    print("  gate-100.svg = Rollershutter CLOSED (physical 0% closed)")
    print("\nOpenHAB selects icons based on transformed Rollershutter item state.")
    print("\nTo install in OpenHAB:")
    print(f"  cp {output_dir}/*.svg $OPENHAB_CONF/icons/classic/")
    print("\nThen use in sitemap:")
    print('  Slider item=FAAC_Gate icon="gate"')


if __name__ == '__main__':
    main()
