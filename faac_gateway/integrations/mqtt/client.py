"""
MQTT Client for FAAC Gate Connect
Handles publishing status updates and subscribing to commands
"""

import json
import logging
import paho.mqtt.client as mqtt
from typing import Callable, Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class MQTTClient:
    """MQTT client for gate control and monitoring"""

    def __init__(
        self,
        broker: str,
        port: int = 1883,
        username: Optional[str] = None,
        password: Optional[str] = None,
        client_id: str = "faac_gateway",
        base_topic: str = "faac/gate",
        use_tls: bool = False
    ):
        """
        Initialize MQTT client

        Args:
            broker: MQTT broker hostname or IP
            port: MQTT broker port (default: 1883)
            username: MQTT username (optional)
            password: MQTT password (optional)
            client_id: MQTT client ID
            base_topic: Base topic for all messages (default: faac/gate)
            use_tls: Enable TLS encryption
        """
        self.broker = broker
        self.port = port
        self.client_id = client_id
        self.base_topic = base_topic.rstrip('/')

        # Topics
        self.status_topic = f"{self.base_topic}/status"
        self.wing1_topic = f"{self.base_topic}/wing1"
        self.wing2_topic = f"{self.base_topic}/wing2"
        self.state_topic = f"{self.base_topic}/state"
        self.availability_topic = f"{self.base_topic}/availability"
        self.server_heartbeat_topic = f"{self.base_topic}/server_heartbeat"
        self.gate_last_seen_topic = f"{self.base_topic}/gate_last_seen"
        self.command_topic = f"{self.base_topic}/command"

        # Callback for commands
        self.command_callback: Optional[Callable[[str], None]] = None

        # Initialize MQTT client
        self.client = mqtt.Client(client_id=client_id)

        # Set authentication if provided
        if username and password:
            self.client.username_pw_set(username, password)

        # Enable TLS if requested
        if use_tls:
            self.client.tls_set()

        # Set up callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message

        # Set last will and testament
        self.client.will_set(
            self.availability_topic,
            payload="offline",
            qos=1,
            retain=True
        )

        self.connected = False

    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker"""
        if rc == 0:
            logger.info(f"Connected to MQTT broker at {self.broker}:{self.port}")
            self.connected = True

            # Subscribe to command topic
            client.subscribe(self.command_topic, qos=1)
            logger.info(f"Subscribed to {self.command_topic}")

            # Publish availability
            self.publish_availability("online")
        else:
            logger.error(f"Failed to connect to MQTT broker, return code: {rc}")
            self.connected = False

    def _on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from MQTT broker"""
        self.connected = False
        if rc != 0:
            logger.warning(f"Unexpected disconnection from MQTT broker (rc: {rc})")
            logger.info("Will automatically reconnect (paho-mqtt handles this)")
        else:
            logger.info("Disconnected from MQTT broker")

    def _on_message(self, client, userdata, msg):
        """Callback when message is received"""
        try:
            if msg.topic == self.command_topic:
                command = msg.payload.decode('utf-8').strip()
                logger.info(f"Received command: {command}")

                # Try to parse as position (0-100)
                try:
                    position = int(command)
                    if 0 <= position <= 100:
                        # Map extreme positions to text commands for limit switch accuracy
                        # This ensures HomeKit/voice "Open" and "Close" commands
                        # run the gate to limit switches instead of stopping at ~99% or ~1%
                        if position == 0:
                            command = "close"
                            logger.info(f"Position 0 mapped to 'close' command")
                        elif position == 100:
                            command = "open"
                            logger.info(f"Position 100 mapped to 'open' command")
                        else:
                            # Partial position (1-99%) - use position control
                            if self.command_callback:
                                self.command_callback(str(position))
                            else:
                                logger.warning("No command callback registered")
                            return
                except (ValueError, TypeError):
                    pass

                # Handle text commands (including mapped positions)
                command_lower = command.lower()
                if command_lower in ['open', 'close', 'stop']:
                    if self.command_callback:
                        self.command_callback(command_lower)
                    else:
                        logger.warning("No command callback registered")
                else:
                    logger.warning(f"Invalid command received: {command}")
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")

    def connect(self):
        """
        Connect to MQTT broker with automatic reconnection

        Note: If initial connection fails, loop_start() will keep trying to
        reconnect indefinitely in the background. This handles scenarios where
        the MQTT broker is down at startup or goes down during operation.
        """
        try:
            logger.info(f"Connecting to MQTT broker at {self.broker}:{self.port}")
            self.client.connect(self.broker, self.port, keepalive=60)
            self.client.loop_start()
            logger.info("MQTT client started (will auto-reconnect if connection lost)")
        except Exception as e:
            logger.warning(f"Initial MQTT connection failed: {e}")
            logger.info("Starting MQTT loop anyway - will keep trying to reconnect...")
            self.client.loop_start()
            # Don't raise - let loop_start() handle reconnection attempts

    def disconnect(self):
        """Disconnect from MQTT broker"""
        self.publish_availability("offline")
        self.client.loop_stop()
        self.client.disconnect()

    def register_command_callback(self, callback: Callable[[str], None]):
        """
        Register callback for command messages

        Args:
            callback: Function to call when command is received
        """
        self.command_callback = callback

    def publish_status(self, status: Dict[str, Any]):
        """
        Publish complete gate status and update heartbeat timestamps

        Args:
            status: Dictionary with keys: wing1, wing2, state, online
        """
        if not self.connected:
            return

        try:
            timestamp = datetime.now().isoformat()

            # Publish complete status as JSON
            self.client.publish(
                self.status_topic,
                payload=json.dumps(status),
                qos=1,
                retain=True
            )

            # Publish individual values for easier consumption
            self.client.publish(
                self.wing1_topic,
                payload=str(status.get('wing1', 0)),
                qos=1,
                retain=True
            )

            self.client.publish(
                self.wing2_topic,
                payload=str(status.get('wing2', 0)),
                qos=1,
                retain=True
            )

            self.client.publish(
                self.state_topic,
                payload=status.get('state', 'UNKNOWN'),
                qos=1,
                retain=True
            )

            # Server heartbeat - shows server is alive and publishing
            self.client.publish(
                self.server_heartbeat_topic,
                payload=timestamp,
                qos=1,
                retain=True
            )

            # Gate last seen - shows when gate (USB) last responded
            # Only update if gate is online (has valid data)
            if status.get('online', False):
                self.client.publish(
                    self.gate_last_seen_topic,
                    payload=timestamp,
                    qos=1,
                    retain=True
                )

        except Exception as e:
            logger.error(f"Error publishing status: {e}")

    def publish_availability(self, status: str):
        """
        Publish availability status and server heartbeat

        Args:
            status: "online" or "offline"
        """
        try:
            timestamp = datetime.now().isoformat()

            # Publish availability status
            self.client.publish(
                self.availability_topic,
                payload=status,
                qos=1,
                retain=True
            )

            # Publish server heartbeat (shows server is alive)
            self.client.publish(
                self.server_heartbeat_topic,
                payload=timestamp,
                qos=1,
                retain=True
            )
        except Exception as e:
            logger.error(f"Error publishing availability: {e}")
