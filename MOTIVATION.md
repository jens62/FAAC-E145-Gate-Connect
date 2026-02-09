# Project Motivation

## Background

I have owned a two-wing entrance gate since 2004, controlled by a FAAC CONTROL BOARD E145 ("Electronic Control Card E145"). The E145 is a reliable but aging controller with limited integration capabilities.

**Documentation:** [FAAC E145 Manual (PDF)](https://www.faac.co.uk/productfiles/340_Manual_rad741B6.pdf)

## Initial Setup (2004)

### KNX Integration

My initial implementation in 2004 used a simple KNX-based approach:
- A button that shorts the corresponding terminals on the FAAC E145
- Single pulse control for all operations: open, close, stop
- The E145 controller handled all logic internally

**How it worked:**
- During gate movement → pulse stops the gate
- When stopped → pulse resumes movement in opposite direction
- When fully open → pulse closes the gate
- When fully closed → pulse opens the gate

This **stateless** approach was simple but had a critical limitation: the KNX system had no knowledge of the gate's current state.

## The Problem

### Voice Control Requirements

As smart home technology evolved, I began controlling my house by voice. I wanted to say commands like:

> "Open courtyard gate!"

For this to work reliably, the **gate status must be known**. The stateless pulse approach was no longer sufficient.

### The FAAC Response

I contacted FAAC to inquire about status monitoring capabilities. Their response was negative.

**I understand their position:**
- FAAC needs to focus on selling new products
- Supporting decades-old controllers is not commercially viable
- Liability concerns with unofficial integrations

However, I remained convinced that the controller had the necessary capabilities — they just weren't officially exposed.

## The Solution

### Reverse Engineering the Protocol

FAAC provides the **EasyBoard** software for the E145, which connects via USB. I decided to investigate:

1. **Captured USB traffic** between EasyBoard software and the E145
2. **Analyzed the communication patterns**
3. **Identified the key commands and responses**
4. **Reverse engineered the protocol**

### Implementation: FAAC Gateway

Using the reverse-engineered protocol, I developed **faac-gateway** — a Python application that provides:

✅ **Web GUI** - Real-time monitoring and control interface
✅ **MQTT Integration** - Publish gate status, subscribe to commands
✅ **Headless API** - RESTful API for programmatic access
✅ **State Monitoring** - Track gate position, status, and wing angles

### Hardware Setup

**Simple, Non-Invasive Installation:**

- **Raspberry Pi 2 Model B** (retired hardware, repurposed)
- **Placement:** Directly next to the E145 controller
- **Connection:** USB cable from Raspberry Pi to E145
- **Network:** Standard Ethernet cable to home network

**Key Advantages:**
- ❌ **No tinkering required**
- ❌ **No complex wiring**
- ❌ **No soldering**
- ✅ **Plug-and-play setup**
- ✅ **Uses existing hardware**

## Integration Success

### Home Automation Platforms

Via MQTT, I successfully integrated the E145 into:

**OpenHAB:**
- Rollershutter control with dynamic position icons
- Real-time status monitoring
- Sitemap integration with visual feedback

**Home Assistant:**
- Cover entity with full state tracking
- Dashboard cards with gate animation
- Voice control via Google Assistant/Alexa

### Benefits Achieved

✅ **Status Monitoring** - Always know if gate is open, closed, or moving
✅ **Voice Control** - "Open courtyard gate" works reliably
✅ **Position Tracking** - Monitor exact wing positions (0-100%)
✅ **Automation** - Trigger actions based on gate state
✅ **Remote Control** - Operate gate from anywhere via home automation
✅ **Visual Feedback** - Animated gate display in web interface

## Project Philosophy

This project demonstrates that:

1. **Old hardware can be modernized** without replacement
2. **Reverse engineering enables integration** when vendors won't help
3. **Open source solutions** provide flexibility proprietary systems lack
4. **Simple, non-invasive approaches** are often the best

## Technical Achievement

**What started as:**
- A simple pulse-based gate controller
- No state information
- No integration capabilities

**Became:**
- A fully monitored smart gate system
- Real-time position tracking
- Voice control integration
- Multiple home automation platform support

All achieved through software, without modifying the original FAAC hardware.

---

*This project brings modern smart home capabilities to a 20-year-old gate controller, proving that sometimes the best solution isn't buying new hardware — it's understanding and enhancing what you already have.*
