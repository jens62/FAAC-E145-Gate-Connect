"""
Gate Controller
Handles serial communication and gate state management
"""

import os
import time
import threading
import queue
import logging
from typing import Optional, Callable, Dict, Any

from .protocol import FaacProtocol

logger = logging.getLogger(__name__)


class GateController:
    """Controls FAAC gate via serial connection"""

    def __init__(
        self,
        serial_port: str,
        status_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        show_tx: bool = False,
        show_rx: bool = False,
        show_parser: bool = False
    ):
        """
        Initialize gate controller

        Args:
            serial_port: Serial port path (e.g., /dev/ttyUSB1)
            status_callback: Callback function called when status changes
            show_tx: Show transmitted commands in logs
            show_rx: Show received raw data in logs
            show_parser: Show parsed position data in logs
        """
        self.serial_port = serial_port
        self.status_callback = status_callback
        self.show_tx = show_tx
        self.show_rx = show_rx
        self.show_parser = show_parser

        # Gate status
        self.status = {
            "wing1": 0,
            "wing2": 0,
            "state": "UNKNOWN",
            "online": False
        }

        # Track last status publish time for periodic heartbeat
        self.last_status_publish = 0
        self.heartbeat_interval = 5  # Publish status every 5 seconds even if unchanged

        # Track last command for HomeKit-style stop (send same command to stop)
        self.last_command = None

        # Command queue
        self.command_queue = queue.Queue()

        # Position control
        self.target_position = None
        self.position_control_active = False
        self.position_tolerance = 2  # Stop within ±2% of target

        # Control flags
        self._running = False
        self._thread = None

    def start(self):
        """Start the gate controller thread"""
        if self._running:
            logger.warning("Gate controller already running")
            return

        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        logger.info("Gate controller started")

    def stop(self):
        """Stop the gate controller thread"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Gate controller stopped")

    def send_command(self, command: str):
        """
        Queue a command to be sent to the gate

        Args:
            command: Command to send (open, close, stop) or position (0-100)
        """
        # Check if it's a position command (numeric 0-100)
        try:
            position = int(command)
            if 0 <= position <= 100:
                self.send_position(position)
                return
        except (ValueError, TypeError):
            pass

        # HomeKit-style stop: If gate is MOVING and same command sent again, treat as STOP
        command_lower = command.lower()
        if self.status['state'] == "MOVING" and command_lower == self.last_command:
            logger.info(f"HomeKit-style stop: '{command_lower}' sent while already moving in that direction")
            command_lower = "stop"

        # It's a regular command
        if FaacProtocol.validate_command(command_lower):
            # Cancel any active position control
            self.position_control_active = False
            self.target_position = None
            self.command_queue.put(command_lower)

            # Track last command (but not 'stop' itself)
            if command_lower != "stop":
                self.last_command = command_lower
        else:
            logger.warning(f"Invalid command: {command}")

    def send_position(self, position: int):
        """
        Move gate to specific position (0-100%)

        Args:
            position: Target position (0=closed, 100=open)
        """
        if not 0 <= position <= 100:
            logger.warning(f"Invalid position: {position}. Must be 0-100.")
            return

        self.target_position = position
        self.position_control_active = True
        logger.info(f"Moving gate to position {position}%")

    def get_status(self) -> Dict[str, Any]:
        """Get current gate status"""
        return self.status.copy()

    def _update_status(self, **kwargs):
        """Update status and trigger callback if changed or heartbeat interval elapsed"""
        changed = False
        for key, value in kwargs.items():
            if key in self.status and self.status[key] != value:
                self.status[key] = value
                changed = True

        # Check if heartbeat interval has elapsed (force publish even if unchanged)
        current_time = time.time()
        heartbeat_due = (current_time - self.last_status_publish) >= self.heartbeat_interval

        # Trigger callback if status changed OR heartbeat is due
        if (changed or heartbeat_due) and self.status_callback:
            self.status_callback(self.status.copy())
            self.last_status_publish = current_time

    def _run(self):
        """Main control loop"""
        last_w1, last_w2 = -1, -1
        still_count = 0

        while self._running:
            fd = None
            try:
                # Check if serial port exists
                if not os.path.exists(self.serial_port):
                    if self.status["online"]:
                        logger.warning(f"Serial port not available: {self.serial_port}")
                        self._update_status(online=False)
                    time.sleep(5)
                    continue

                # Open serial port
                fd = os.open(self.serial_port, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
                logger.info(f"✓ Connected to FAAC gate on {self.serial_port}")
                self._update_status(online=True)

                while self._running:
                    # 1. SEND (TX) - Process commands from queue
                    if not self.command_queue.empty():
                        cmd_type = self.command_queue.get()
                        full_cmd = FaacProtocol.COMMANDS.get(cmd_type)

                        if full_cmd:
                            os.write(fd, bytes.fromhex(full_cmd))
                            if self.show_tx:
                                logger.debug(f"TX → {full_cmd} ({cmd_type.upper()})")
                            else:
                                logger.info(f"▶ Command: {cmd_type.upper()}")
                            time.sleep(0.5)
                        else:
                            logger.warning(f"Unknown command: {cmd_type}")

                    # 1b. POSITION CONTROL - Automatically move to target position
                    if self.position_control_active and self.target_position is not None:
                        current_pos = self.status["wing1"]
                        target = self.target_position
                        tolerance = self.position_tolerance

                        # Check if we've reached the target
                        if abs(current_pos - target) <= tolerance:
                            # Target reached - send stop
                            logger.info(f"Target position {target}% reached (current: {current_pos}%)")
                            os.write(fd, bytes.fromhex(FaacProtocol.COMMANDS["stop"]))
                            self.position_control_active = False
                            self.target_position = None
                            time.sleep(0.5)
                        else:
                            # Not at target yet - check if we need to start/continue movement
                            state = self.status["state"]

                            if current_pos < target:
                                # Need to open more
                                if state != "MOVING" or state == "STOPPED":
                                    logger.debug(f"Position control: opening (current={current_pos}%, target={target}%)")
                                    os.write(fd, bytes.fromhex(FaacProtocol.COMMANDS["open"]))
                                    time.sleep(0.5)
                            elif current_pos > target:
                                # Need to close more
                                if state != "MOVING" or state == "STOPPED":
                                    logger.debug(f"Position control: closing (current={current_pos}%, target={target}%)")
                                    os.write(fd, bytes.fromhex(FaacProtocol.COMMANDS["close"]))
                                    time.sleep(0.5)

                    # 2. POLL - Query status
                    os.write(fd, bytes.fromhex(FaacProtocol.POLL_CMD))
                    time.sleep(0.4)

                    # 3. RECEIVE (RX) - Read and parse response
                    try:
                        res = os.read(fd, 1024)
                        if res:
                            hex_res = res.hex().upper()
                            if self.show_rx:
                                logger.debug(f"RX ← {hex_res}")

                            # Parse position data
                            idx = hex_res.find(FaacProtocol.POSITION_HEADER)
                            if idx != -1:
                                # Extract wing positions
                                w1 = FaacProtocol.parse_position(hex_res, idx + FaacProtocol.WING1_OFFSET)
                                w2 = FaacProtocol.parse_position(hex_res, idx + FaacProtocol.WING2_OFFSET)

                                if w1 is not None and w2 is not None:
                                    # Determine state
                                    state, still_count = FaacProtocol.determine_state(
                                        w1, w2, last_w1, last_w2, still_count
                                    )

                                    last_w1, last_w2 = w1, w2

                                    if self.show_parser:
                                        logger.debug(f"PARSE │ W1: {w1:3d}% │ W2: {w2:3d}% │ {state}")

                                    # Update status
                                    self._update_status(wing1=w1, wing2=w2, state=state)

                    except OSError:
                        pass

                    time.sleep(0.1)

            except Exception as e:
                logger.error(f"Error in gate controller: {e}")
                if fd:
                    try:
                        os.close(fd)
                    except Exception:
                        pass
                self._update_status(online=False)
                time.sleep(5)
