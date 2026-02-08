#!/usr/bin/env python3
"""
Test script for FAAC Gateway REST API
Demonstrates basic API usage with Python requests library

Usage:
    python3 test_rest_api.py [gateway-ip] [api-key]

Examples:
    python3 test_rest_api.py
    python3 test_rest_api.py 192.168.1.100
    python3 test_rest_api.py 192.168.1.100 your-secret-api-key
"""

import sys
import time
import requests
from typing import Optional

# Colors for terminal output
class Colors:
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    RED = '\033[0;31m'
    NC = '\033[0m'  # No Color


class FaacGatewayAPI:
    """Simple client for FAAC Gateway REST API"""

    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        Initialize API client

        Args:
            base_url: Base URL (e.g., http://localhost:5000/api)
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.headers = {}
        if api_key:
            self.headers['X-API-Key'] = api_key

    def get_status(self) -> dict:
        """Get current gate status"""
        response = requests.get(
            f"{self.base_url}/status",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def send_command(self, command: str) -> dict:
        """
        Send command to gate

        Args:
            command: Command to send (open/close/stop or 0-100)

        Returns:
            API response
        """
        response = requests.post(
            f"{self.base_url}/command",
            json={"command": command},
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def health_check(self) -> dict:
        """Get health status"""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()


def print_test(test_name: str):
    """Print test header"""
    print(f"\n{Colors.GREEN}{test_name}{Colors.NC}")
    print("-" * 50)


def print_response(response: dict):
    """Print API response"""
    import json
    print(json.dumps(response, indent=2))


def main():
    """Run API tests"""
    # Parse arguments
    gateway_ip = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    api_key = sys.argv[2] if len(sys.argv) > 2 else None

    base_url = f"http://{gateway_ip}:5000/api"

    print("=" * 50)
    print("  FAAC Gateway REST API Test (Python)")
    print("=" * 50)
    print(f"Gateway: {gateway_ip}")
    if api_key:
        print(f"API Key: {api_key[:10]}...")
    else:
        print("API Key: Not provided (assuming no authentication)")
    print("=" * 50)

    # Create API client
    api = FaacGatewayAPI(base_url, api_key)

    try:
        # Test 1: Health Check
        print_test("Test 1: Health Check")
        health = api.health_check()
        print_response(health)
        time.sleep(1)

        # Test 2: Get Status
        print_test("Test 2: Get Current Status")
        status = api.get_status()
        print_response(status)
        print(f"\nCurrent state: {status.get('state')}")
        print(f"Wing 1: {status.get('wing1')}%")
        print(f"Wing 2: {status.get('wing2')}%")
        print(f"Online: {status.get('online')}")
        time.sleep(1)

        # Test 3: Send OPEN Command
        print_test("Test 3: Send OPEN Command")
        result = api.send_command("open")
        print_response(result)
        time.sleep(3)

        # Test 4: Get Status (should show OPENING or OPEN)
        print_test("Test 4: Get Status (after OPEN)")
        status = api.get_status()
        print_response(status)
        print(f"\nState: {status.get('state')}")
        time.sleep(1)

        # Test 5: Send STOP Command
        print_test("Test 5: Send STOP Command")
        result = api.send_command("stop")
        print_response(result)
        time.sleep(2)

        # Test 6: Get Status (should show STOPPED)
        print_test("Test 6: Get Status (after STOP)")
        status = api.get_status()
        print_response(status)
        print(f"\nState: {status.get('state')}")
        time.sleep(1)

        # Test 7: Set Position to 50%
        print_test("Test 7: Set Position to 50%")
        result = api.send_command("50")
        print_response(result)
        time.sleep(3)

        # Test 8: Get Final Status
        print_test("Test 8: Get Final Status")
        status = api.get_status()
        print_response(status)
        print(f"\nFinal state: {status.get('state')}")
        print(f"Final position: Wing1={status.get('wing1')}%, Wing2={status.get('wing2')}%")

        print("\n" + "=" * 50)
        print(f"{Colors.GREEN}✓ Test Complete{Colors.NC}")
        print("=" * 50)

    except requests.exceptions.ConnectionError:
        print(f"\n{Colors.RED}Error: Could not connect to gateway at {gateway_ip}:5000{Colors.NC}")
        print("Make sure the gateway is running and accessible.")
        sys.exit(1)

    except requests.exceptions.HTTPError as e:
        print(f"\n{Colors.RED}HTTP Error: {e}{Colors.NC}")
        if e.response.status_code == 401:
            print("Authentication failed. Check your API key.")
        sys.exit(1)

    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.NC}")
        sys.exit(1)


if __name__ == "__main__":
    # Check if requests is installed
    try:
        import requests
    except ImportError:
        print(f"{Colors.RED}Error: 'requests' library not installed{Colors.NC}")
        print("Install it with: pip install requests")
        sys.exit(1)

    main()
