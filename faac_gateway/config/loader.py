"""
Configuration loader
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any
import yaml

logger = logging.getLogger(__name__)


class Config:
    """Configuration container"""

    def __init__(self, data: Dict[str, Any]):
        self._data = data

    def get(self, *keys, default=None):
        """Get nested configuration value"""
        value = self._data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default
        return value if value is not None else default

    @property
    def serial_port(self) -> str:
        """Get serial port"""
        return self.get('serial', 'port', default='/dev/ttyUSB1')

    @property
    def mqtt_enabled(self) -> bool:
        """Check if MQTT is enabled"""
        return self.get('mqtt', 'enabled', default=False)

    @property
    def mqtt_broker(self) -> str:
        """Get MQTT broker"""
        return self.get('mqtt', 'broker', default='localhost')

    @property
    def mqtt_port(self) -> int:
        """Get MQTT port"""
        return self.get('mqtt', 'port', default=1883)

    @property
    def mqtt_username(self) -> Optional[str]:
        """Get MQTT username"""
        return self.get('mqtt', 'username')

    @property
    def mqtt_password(self) -> Optional[str]:
        """Get MQTT password"""
        return self.get('mqtt', 'password')

    @property
    def mqtt_client_id(self) -> str:
        """Get MQTT client ID"""
        return self.get('mqtt', 'client_id', default='faac_gateway')

    @property
    def mqtt_base_topic(self) -> str:
        """Get MQTT base topic"""
        return self.get('mqtt', 'base_topic', default='faac/gate')

    @property
    def mqtt_use_tls(self) -> bool:
        """Check if MQTT TLS is enabled"""
        return self.get('mqtt', 'use_tls', default=False)

    @property
    def web_enabled(self) -> bool:
        """Check if web interface is enabled"""
        return self.get('web', 'enabled', default=True)

    @property
    def web_host(self) -> str:
        """Get web interface host"""
        return self.get('web', 'host', default='0.0.0.0')

    @property
    def web_port(self) -> int:
        """Get web interface port"""
        return self.get('web', 'port', default=5000)

    @property
    def log_level(self) -> str:
        """Get logging level"""
        return self.get('logging', 'level', default='INFO')

    @property
    def show_tx(self) -> bool:
        """Check if TX logging is enabled"""
        return self.get('logging', 'show_tx', default=False)

    @property
    def show_rx(self) -> bool:
        """Check if RX logging is enabled"""
        return self.get('logging', 'show_rx', default=False)

    @property
    def show_parser(self) -> bool:
        """Check if parser logging is enabled"""
        return self.get('logging', 'show_parser', default=False)


def load_config(config_path: Optional[str] = None) -> Config:
    """
    Load configuration from YAML file

    Args:
        config_path: Path to configuration file

    Returns:
        Config object with configuration data
    """
    default_config = {
        'serial': {'port': '/dev/ttyUSB1'},
        'mqtt': {'enabled': False},
        'web': {'enabled': True, 'host': '0.0.0.0', 'port': 5000},
        'logging': {'level': 'INFO'}
    }

    if not config_path:
        logger.info("No config file specified, using defaults")
        return Config(default_config)

    config_file = Path(config_path)

    if not config_file.exists():
        logger.warning(f"Config file not found: {config_path}")
        logger.info("Using default configuration")
        return Config(default_config)

    try:
        with open(config_file, 'r') as f:
            data = yaml.safe_load(f)
            if data:
                logger.info(f"Loaded configuration from {config_path}")
                return Config(data)
            else:
                logger.warning("Config file is empty, using defaults")
                return Config(default_config)
    except Exception as e:
        logger.error(f"Error loading config file: {e}")
        logger.info("Using default configuration")
        return Config(default_config)
