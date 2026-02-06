#!/usr/bin/env python3
"""
FAAC Gate Control - MQTT Version
Web interface with MQTT integration
"""

import sys
import logging
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from faac_gateway.core import GateController
from faac_gateway.web import create_app
from faac_gateway.integrations.mqtt import MQTTClient
from faac_gateway.config import load_config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%H:%M:%S'
)

# Minimize Flask logs
logging.getLogger('werkzeug').setLevel(logging.ERROR)

logger = logging.getLogger(__name__)


def main():
    """Main entry point"""
    # Parse arguments
    parser = argparse.ArgumentParser(
        description='FAAC Gate Control with MQTT Support',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('-c', '--config', default='config/config.yaml',
                        help='Configuration file path')
    parser.add_argument('-tx', action='store_true',
                        help='Show transmitted commands')
    parser.add_argument('-rx', action='store_true',
                        help='Show received raw data')
    parser.add_argument('--parser', action='store_true',
                        help='Show parsed position data')

    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)

    # Apply logging level
    log_level = getattr(logging, config.log_level.upper())
    logging.getLogger().setLevel(log_level)

    # Override with command line arguments
    show_tx = args.tx or config.show_tx
    show_rx = args.rx or config.show_rx
    show_parser = args.parser or config.show_parser

    print("=" * 80)
    print("FAAC GATE CONTROL WITH MQTT")
    print("=" * 80)
    print()

    # Initialize MQTT client if enabled
    mqtt_client = None
    if config.mqtt_enabled:
        try:
            mqtt_client = MQTTClient(
                broker=config.mqtt_broker,
                port=config.mqtt_port,
                username=config.mqtt_username,
                password=config.mqtt_password,
                client_id=config.mqtt_client_id,
                base_topic=config.mqtt_base_topic,
                use_tls=config.mqtt_use_tls
            )

            logger.info("MQTT enabled")
            logger.info(f"  Broker: {config.mqtt_broker}:{config.mqtt_port}")
            logger.info(f"  Base topic: {config.mqtt_base_topic}")
            logger.info(f"  Command topic: {config.mqtt_base_topic}/command")
            print()
        except Exception as e:
            logger.error(f"Failed to initialize MQTT: {e}")
            logger.info("Continuing without MQTT")
            mqtt_client = None
            print()
    else:
        logger.info("MQTT disabled")
        print()

    # Status callback for MQTT publishing
    def status_callback(status):
        if mqtt_client and mqtt_client.connected:
            mqtt_client.publish_status(status)

    # Create gate controller
    controller = GateController(
        serial_port=config.serial_port,
        status_callback=status_callback,
        show_tx=show_tx,
        show_rx=show_rx,
        show_parser=show_parser
    )

    # Register MQTT command callback
    if mqtt_client:
        mqtt_client.register_command_callback(controller.send_command)

    logger.info(f"Serial port: {config.serial_port}")

    if config.web_enabled:
        logger.info(f"Web UI: http://{config.web_host}:{config.web_port}")

    print()
    print("Commands: OPEN, CLOSE, STOP")

    if config.mqtt_enabled:
        print()
        print("MQTT Topics:")
        print(f"  Publish commands to: {config.mqtt_base_topic}/command")
        print(f"  Subscribe to status: {config.mqtt_base_topic}/status")
        print(f"  Subscribe to state: {config.mqtt_base_topic}/state")
        print(f"  Subscribe to wing1: {config.mqtt_base_topic}/wing1")
        print(f"  Subscribe to wing2: {config.mqtt_base_topic}/wing2")

    print("=" * 80)
    print()

    # Start controller
    controller.start()

    # Connect MQTT
    if mqtt_client:
        try:
            mqtt_client.connect()
            mqtt_client.publish_availability("online")
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")

    # Create Flask app if enabled
    if config.web_enabled:
        app = create_app(controller, mqtt_enabled=config.mqtt_enabled)

        try:
            app.run(
                host=config.web_host,
                port=config.web_port,
                threaded=True
            )
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        finally:
            controller.stop()
            if mqtt_client:
                mqtt_client.publish_availability("offline")
                mqtt_client.disconnect()
    else:
        # If web is disabled, just keep running
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            controller.stop()
            if mqtt_client:
                mqtt_client.publish_availability("offline")
                mqtt_client.disconnect()


if __name__ == '__main__':
    main()
