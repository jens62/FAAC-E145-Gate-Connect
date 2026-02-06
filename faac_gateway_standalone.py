#!/usr/bin/env python3
"""
FAAC Gate Control - Standalone Version
Simple web interface without MQTT
"""

import sys
import logging
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from faac_gateway.core import GateController
from faac_gateway.web import create_app

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
        description='FAAC Gate Control - Standalone Version',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('-p', '--port', default='/dev/ttyUSB1',
                        help='Serial port (default: /dev/ttyUSB1)')
    parser.add_argument('--web-port', type=int, default=5000,
                        help='Web interface port (default: 5000)')
    parser.add_argument('--web-host', default='0.0.0.0',
                        help='Web interface host (default: 0.0.0.0)')
    parser.add_argument('-tx', action='store_true',
                        help='Show transmitted commands')
    parser.add_argument('-rx', action='store_true',
                        help='Show received raw data')
    parser.add_argument('--parser', action='store_true',
                        help='Show parsed position data')

    args = parser.parse_args()

    print("=" * 80)
    print("FAAC GATE CONTROL - STANDALONE")
    print("=" * 80)
    print()
    print("Commands: OPEN, CLOSE, STOP")
    print(f"Serial port: {args.port}")
    print(f"Web UI: http://{args.web_host}:{args.web_port}")
    print()
    print("Keyboard shortcuts:")
    print("  [O] - Open")
    print("  [C] - Close")
    print("  [S] or [SPACE] - Stop")
    print("=" * 80)
    print()

    # Create gate controller
    controller = GateController(
        serial_port=args.port,
        show_tx=args.tx,
        show_rx=args.rx,
        show_parser=args.parser
    )

    # Start controller
    controller.start()

    # Create Flask app
    app = create_app(controller, mqtt_enabled=False)

    # Run web server
    try:
        app.run(
            host=args.web_host,
            port=args.web_port,
            threaded=True
        )
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        controller.stop()


if __name__ == '__main__':
    main()
