#!/bin/bash
#
# Test script for FAAC Gateway REST API
# Usage: ./test_rest_api.sh [gateway-ip] [api-key]
#

# Configuration
GATEWAY_IP="${1:-localhost}"
API_KEY="${2:-}"
API_URL="http://${GATEWAY_IP}:5000/api"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Helper function to make API calls
api_call() {
    local method=$1
    local endpoint=$2
    local data=$3

    echo -e "${YELLOW}▶ ${method} ${endpoint}${NC}"

    if [ -n "$API_KEY" ]; then
        if [ "$method" = "GET" ]; then
            curl -s -H "X-API-Key: $API_KEY" "$API_URL/$endpoint"
        else
            curl -s -X POST \
                 -H "Content-Type: application/json" \
                 -H "X-API-Key: $API_KEY" \
                 -d "$data" \
                 "$API_URL/$endpoint"
        fi
    else
        if [ "$method" = "GET" ]; then
            curl -s "$API_URL/$endpoint"
        else
            curl -s -X POST \
                 -H "Content-Type: application/json" \
                 -d "$data" \
                 "$API_URL/$endpoint"
        fi
    fi

    echo
    echo
}

# Check if jq is available for pretty printing
if command -v jq &> /dev/null; then
    JQ="jq"
else
    JQ="cat"
    echo -e "${YELLOW}Note: Install 'jq' for prettier JSON output${NC}"
    echo
fi

echo "=============================================="
echo "  FAAC Gateway REST API Test"
echo "=============================================="
echo "Gateway: $GATEWAY_IP"
if [ -n "$API_KEY" ]; then
    echo "API Key: ${API_KEY:0:10}..."
else
    echo "API Key: Not provided (assuming no authentication)"
fi
echo "=============================================="
echo

# Test 1: Health Check
echo -e "${GREEN}Test 1: Health Check${NC}"
echo "----------------------------------------------"
api_call GET health | $JQ
sleep 1

# Test 2: Get Status
echo -e "${GREEN}Test 2: Get Current Status${NC}"
echo "----------------------------------------------"
api_call GET status | $JQ
sleep 1

# Test 3: Send OPEN Command
echo -e "${GREEN}Test 3: Send OPEN Command${NC}"
echo "----------------------------------------------"
api_call POST command '{"command":"open"}' | $JQ
sleep 3

# Test 4: Get Status (should show MOVING or OPEN)
echo -e "${GREEN}Test 4: Get Status (after OPEN)${NC}"
echo "----------------------------------------------"
api_call GET status | $JQ
sleep 1

# Test 5: Send STOP Command
echo -e "${GREEN}Test 5: Send STOP Command${NC}"
echo "----------------------------------------------"
api_call POST command '{"command":"stop"}' | $JQ
sleep 2

# Test 6: Get Status (should show STOPPED)
echo -e "${GREEN}Test 6: Get Status (after STOP)${NC}"
echo "----------------------------------------------"
api_call GET status | $JQ
sleep 1

# Test 7: Set Position to 50%
echo -e "${GREEN}Test 7: Set Position to 50%${NC}"
echo "----------------------------------------------"
api_call POST command '{"command":"50"}' | $JQ
sleep 3

# Test 8: Get Final Status
echo -e "${GREEN}Test 8: Get Final Status${NC}"
echo "----------------------------------------------"
api_call GET status | $JQ

echo "=============================================="
echo -e "${GREEN}✓ Test Complete${NC}"
echo "=============================================="
echo
echo "To test with API key:"
echo "  $0 $GATEWAY_IP your-api-key-here"
echo
