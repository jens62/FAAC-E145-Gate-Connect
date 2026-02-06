"""
MQTT Client for FAAC Gate Connect
Handles publishing status updates and subscribing to commands
"""

import json
import logging
import paho.mqtt.client as mqtt
from typing import Callable, Optional, Dict, Any

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
        else:
            logger.info("Disconnected from MQTT broker")

    def _on_message(self, client, userdata, msg):
        """Callback when message is received"""
        try:
            if msg.topic == self.command_topic:
                command = msg.payload.decode('utf-8').lower().strip()
                logger.info(f"Received command: {command}")

                # Validate command
                if command in ['open', 'close', 'stop']:
                    if self.command_callback:
                        self.command_callback(command)
                    else:
                        logger.warning("No command callback registered")
                else:
                    logger.warning(f"Invalid command received: {command}")
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")

    def connect(self):
        """Connect to MQTT broker"""
        try:
            logger.info(f"Connecting to MQTT broker at {self.broker}:{self.port}")
            self.client.connect(self.broker, self.port, keepalive=60)
            self.client.loop_start()
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            raise

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
        Publish complete gate status

        Args:
            status: Dictionary with keys: wing1, wing2, state, online
        """
        if not self.connected:
            return

        try:
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

        except Exception as e:
            logger.error(f"Error publishing status: {e}")

    def publish_availability(self, status: str):
        """
        Publish availability status

        Args:
            status: "online" or "offline"
        """
        try:
            self.client.publish(
                self.availability_topic,
                payload=status,
                qos=1,
                retain=True
            )
        except Exception as e:
            logger.error(f"Error publishing availability: {e}")
