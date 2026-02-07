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

# Setup logging (configured after loading config)
logger = logging.getLogger(__name__)


def setup_logging(config):
    """Configure logging based on config file"""
    from logging.handlers import RotatingFileHandler

    handlers = []

    # Console handler (for systemd journal)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%H:%M:%S'
    ))
    handlers.append(console_handler)

    # File handler (optional)
    log_config = config.get('logging', {})
    log_file = log_config.get('file')
    if log_file:
        try:
            # Create log directory if needed
            import os
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, mode=0o755)

            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=log_config.get('max_bytes', 10485760),  # 10MB default
                backupCount=log_config.get('backup_count', 5)
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            ))
            handlers.append(file_handler)
            logger.info(f"File logging enabled: {log_file}")
        except Exception as e:
            logger.error(f"Failed to setup file logging: {e}")

    # Configure root logger
    log_level = getattr(logging, log_config.get('level', 'INFO').upper())
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=handlers
    )

    # Minimize Flask logs
    logging.getLogger('werkzeug').setLevel(logging.ERROR)

    # Filter out harmless client disconnect errors
    # These occur when web browsers/clients disconnect while server is sending data
    # Common with SSE (Server-Sent Events) connections in the web interface
    class ClientDisconnectFilter(logging.Filter):
        """Suppress expected client disconnect errors"""
        def filter(self, record):
            msg = str(record.msg)
            # Suppress timeout/disconnect errors (expected when clients close browsers)
            suppress_patterns = [
                'Connection timed out',  # errno 110 - client didn't respond
                'Broken pipe',            # errno 32 - client closed connection
                'Connection reset by peer' # errno 104 - client forcibly closed
            ]
            return not any(pattern in msg for pattern in suppress_patterns)

    logging.getLogger('werkzeug').addFilter(ClientDisconnectFilter())


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

    # Setup logging (console + optional file)
    setup_logging(config._data)

    # Keep using the Config object (has properties for all settings)

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
    print("Commands: OPEN, CLOSE, STOP, 0-100 (position)")

    if config.mqtt_enabled:
        print()
        print("MQTT Topics:")
        print(f"  Publish commands to: {config.mqtt_base_topic}/command")
        print(f"    - Text commands: open, close, stop")
        print(f"    - Position: 0-100 (0=fully closed, 100=fully open)")
        print()
        print(f"  Subscribe to status:")
        print(f"    - {config.mqtt_base_topic}/status (JSON with all fields)")
        print(f"    - {config.mqtt_base_topic}/state (OPEN, CLOSED, MOVING, STOPPED, UNKNOWN)")
        print(f"    - {config.mqtt_base_topic}/wing1 (0-100%)")
        print(f"    - {config.mqtt_base_topic}/wing2 (0-100%)")
        print(f"    - {config.mqtt_base_topic}/availability (online/offline)")
        print(f"    - {config.mqtt_base_topic}/server_heartbeat (ISO 8601 timestamp)")
        print(f"    - {config.mqtt_base_topic}/gate_last_seen (ISO 8601 timestamp)")

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
        app = create_app(controller, mqtt_enabled=config.mqtt_enabled, config=config._data)

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
