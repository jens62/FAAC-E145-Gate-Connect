"""
FAAC E145 Protocol Implementation
Commands extracted from EasyBoard traffic analysis
"""

from datetime import datetime


class FaacProtocol:
    """FAAC E145 protocol constants and utilities"""

    # Status query command (sent continuously)
    POLL_CMD = "023035303030363330333033303330333803"

    # Control commands (all verified and functional)
    COMMANDS = {
        "open":  "0230393030384133303330333033303032303030303030423203",
        "close": "0230393030384133303330333033303038303030303030414303",
        "stop":  "0230393030384133303330333033303030303230303030423203",
    }

    # Protocol header for position data
    POSITION_HEADER = "3030303836"

    # Offsets for extracting wing positions from response
    WING1_OFFSET = 66
    WING2_OFFSET = 70

    # State thresholds
    CLOSED_THRESHOLD = 0
    OPEN_THRESHOLD = 95
    STILLNESS_COUNT = 3  # Number of identical readings to consider stopped

    @staticmethod
    def get_timestamp():
        """Get formatted timestamp for logging"""
        return datetime.now().strftime("%H:%M:%S.%f")[:-3]

    @staticmethod
    def parse_position(hex_string: str, start_offset: int) -> int:
        """
        Extract position from FAAC response (0-100%)

        Args:
            hex_string: Hexadecimal response string
            start_offset: Offset where position data starts

        Returns:
            Position as integer (0-100) or None if parsing fails
        """
        try:
            hex_pair = hex_string[start_offset : start_offset + 4]
            val_str = bytes.fromhex(hex_pair).decode('ascii')
            return int(val_str, 16)
        except Exception:
            return None

    @staticmethod
    def determine_state(wing1: int, wing2: int, last_wing1: int, last_wing2: int,
                       still_count: int) -> tuple[str, int]:
        """
        Determine gate state based on wing positions

        Args:
            wing1: Current wing 1 position
            wing2: Current wing 2 position
            last_wing1: Previous wing 1 position
            last_wing2: Previous wing 2 position
            still_count: Number of consecutive identical readings

        Returns:
            Tuple of (state_string, updated_still_count)
        """
        # Check if fully closed
        if wing1 == FaacProtocol.CLOSED_THRESHOLD and wing2 == FaacProtocol.CLOSED_THRESHOLD:
            return "CLOSED", 0

        # Check if fully open
        if wing1 >= FaacProtocol.OPEN_THRESHOLD or wing2 >= FaacProtocol.OPEN_THRESHOLD:
            return "OPEN", 0

        # Motion detection
        if wing1 == last_wing1 and wing2 == last_wing2:
            still_count += 1
        else:
            still_count = 0

        state = "STOPPED" if still_count >= FaacProtocol.STILLNESS_COUNT else "MOVING"
        return state, still_count

    @staticmethod
    def validate_command(command: str) -> bool:
        """
        Validate command string

        Args:
            command: Command to validate

        Returns:
            True if valid, False otherwise
        """
        return command.lower() in FaacProtocol.COMMANDS
