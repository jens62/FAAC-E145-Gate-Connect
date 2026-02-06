#!/usr/bin/env python3
"""
Simple MQTT example - just subscribe to status
"""

import paho.mqtt.client as mqtt
import json

BROKER = "localhost"
BASE_TOPIC = "faac/gate"

def on_connect(client, userdata, flags, rc):
    print(f"Connected to {BROKER}")
    client.subscribe(f"{BASE_TOPIC}/status")

def on_message(client, userdata, msg):
    status = json.loads(msg.payload.decode())
    print(f"Gate Status: {status['state']} - Wing1: {status['wing1']}% - Wing2: {status['wing2']}%")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, 1883)
print("Listening for gate status updates...")
print("Press Ctrl+C to exit")

try:
    client.loop_forever()
except KeyboardInterrupt:
    print("\nExiting...")
    client.disconnect()
