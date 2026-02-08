#!/usr/bin/env python3
"""
Simple MQTT test script
Subscribe to status and send test commands
"""

import paho.mqtt.client as mqtt
import time
import sys

# Configuration
BROKER = "localhost"
PORT = 1883
BASE_TOPIC = "faac/gate"

def on_connect(client, userdata, flags, rc):
    """Callback when connected to broker"""
    if rc == 0:
        print(f"✓ Connected to MQTT broker at {BROKER}:{PORT}")
        print(f"✓ Subscribing to {BASE_TOPIC}/#")
        client.subscribe(f"{BASE_TOPIC}/#")
        print()
    else:
        print(f"✗ Connection failed with code {rc}")
        sys.exit(1)

def on_message(client, userdata, msg):
    """Callback when message is received"""
    topic = msg.topic.replace(f"{BASE_TOPIC}/", "")
    payload = msg.payload.decode('utf-8')

    # Format output based on topic
    if topic == "status":
        print(f"📊 {topic:20s} = {payload}")
    elif topic == "state":
        emoji = {
            "OPEN": "🟢",
            "CLOSED": "🔴",
            "OPENING": "🟡",
            "CLOSING": "🟠",
            "STOPPED": "🔵",
            "UNKNOWN": "⚪"
        }.get(payload, "⚪")
        print(f"{emoji} {topic:20s} = {payload}")
    elif topic == "availability":
        emoji = "✓" if payload == "online" else "✗"
        print(f"{emoji} {topic:20s} = {payload}")
    elif topic in ["wing1", "wing2"]:
        bar_length = int(int(payload) / 5)  # Scale to 20 chars
        bar = "█" * bar_length + "░" * (20 - bar_length)
        print(f"  {topic:20s} = {payload:>3s}% [{bar}]")
    else:
        print(f"  {topic:20s} = {payload}")

def send_command(client, command):
    """Send a command to the gate"""
    print(f"\n▶ Sending command: {command.upper()}")
    client.publish(f"{BASE_TOPIC}/command", command)

def main():
    """Main function"""
    print("=" * 60)
    print("FAAC MQTT Test Script")
    print("=" * 60)
    print(f"Broker: {BROKER}:{PORT}")
    print(f"Topics: {BASE_TOPIC}/#")
    print("=" * 60)
    print()

    # Create MQTT client
    client = mqtt.Client("faac_test_client")
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        # Connect to broker
        client.connect(BROKER, PORT, 60)
        client.loop_start()

        print("Press Ctrl+C to exit")
        print()
        print("Commands:")
        print("  o - Open gate")
        print("  c - Close gate")
        print("  s - Stop gate")
        print()

        # Interactive command loop
        import select
        import tty
        import termios

        # Save terminal settings
        old_settings = termios.tcgetattr(sys.stdin)

        try:
            tty.setcbreak(sys.stdin.fileno())

            while True:
                # Check for keyboard input (non-blocking)
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    key = sys.stdin.read(1).lower()

                    if key == 'o':
                        send_command(client, "open")
                    elif key == 'c':
                        send_command(client, "close")
                    elif key == 's':
                        send_command(client, "stop")
                    elif key == 'q':
                        break

                time.sleep(0.1)

        finally:
            # Restore terminal settings
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\n✗ Error: {e}")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == '__main__':
    main()
