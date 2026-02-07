"""
REST API for FAAC Gate Control
Provides RESTful endpoints for gate status and control
"""

import logging
from functools import wraps
from flask import Blueprint, jsonify, request, current_app

logger = logging.getLogger(__name__)

# Create API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')


def require_api_key(f):
    """
    Decorator to require API key authentication

    API key can be provided via:
    - X-API-Key header
    - api_key query parameter

    If no API key is configured, authentication is disabled.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        config = current_app.config.get('GATE_CONFIG', {})
        api_config = config.get('api', {})
        required_key = api_config.get('key')

        # If no API key is configured, skip authentication
        if not required_key:
            return f(*args, **kwargs)

        # Check API key from header or query parameter
        provided_key = request.headers.get('X-API-Key') or request.args.get('api_key')

        if not provided_key or provided_key != required_key:
            logger.warning(f"Unauthorized API access attempt from {request.remote_addr}")
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Invalid or missing API key'
            }), 401

        return f(*args, **kwargs)
    return decorated_function


@api_bp.route('/status', methods=['GET'])
@require_api_key
def get_status():
    """
    Get current gate status

    Returns:
        JSON with gate status including:
        - wing1: Position of wing 1 (0-100%)
        - wing2: Position of wing 2 (0-100%)
        - state: Gate state (OPEN/CLOSED/MOVING/STOPPED/UNKNOWN)
        - online: Connection status (true/false)

    Example:
        GET /api/status

        Response:
        {
            "wing1": 0,
            "wing2": 0,
            "state": "CLOSED",
            "online": true
        }
    """
    controller = current_app.config.get('GATE_CONTROLLER')

    if not controller:
        return jsonify({
            'error': 'Service unavailable',
            'message': 'Gate controller not initialized'
        }), 503

    try:
        status = controller.get_status()
        logger.debug(f"API status request from {request.remote_addr}")
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@api_bp.route('/command', methods=['POST'])
@require_api_key
def send_command():
    """
    Send command to gate

    Accepts JSON body with 'command' field:
    - Text commands: "open", "close", "stop"
    - Position: 0-100 (integer or string)

    Special behavior:
    - Position 0 is mapped to "close" command for limit switch accuracy
    - Position 100 is mapped to "open" command for limit switch accuracy

    Command validation and processing is handled by GateController.normalize_command()
    This ensures all interfaces (MQTT, REST, Web) use the same validation logic.

    Example:
        POST /api/command
        Content-Type: application/json

        {"command": "open"}

        Response:
        {
            "status": "ok",
            "command": "open"
        }
    """
    controller = current_app.config.get('GATE_CONTROLLER')

    if not controller:
        return jsonify({
            'error': 'Service unavailable',
            'message': 'Gate controller not initialized'
        }), 503

    # Parse request body
    if not request.is_json:
        return jsonify({
            'error': 'Bad request',
            'message': 'Content-Type must be application/json'
        }), 400

    data = request.get_json()
    command = data.get('command')

    if not command:
        return jsonify({
            'error': 'Bad request',
            'message': 'Missing "command" field'
        }), 400

    try:
        # Validate command using controller's normalize_command
        # This is the SINGLE place where all validation logic lives
        normalized = controller.normalize_command(str(command))

        if not normalized['valid']:
            return jsonify({
                'error': 'Bad request',
                'message': normalized['error']
            }), 400

        # Log the API command
        logger.info(f"API command from {request.remote_addr}: {command} -> {normalized['command']}")

        # Send command (controller handles everything)
        controller.send_command(str(command))

        # Build response
        response = {
            'status': 'ok',
            'command': command
        }

        # If command was mapped (e.g., 0->close, 100->open), include that info
        if normalized['command'] != str(command).lower().strip():
            response['mapped_to'] = normalized['command']

        return jsonify(response)

    except Exception as e:
        logger.error(f"Error sending command: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@api_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint (no authentication required)

    Returns service health status and basic info.
    Useful for monitoring and load balancers.

    Example:
        GET /api/health

        Response:
        {
            "status": "ok",
            "service": "faac-gateway",
            "online": true,
            "mqtt_enabled": true
        }
    """
    controller = current_app.config.get('GATE_CONTROLLER')
    config = current_app.config.get('GATE_CONFIG', {})
    mqtt_enabled = config.get('mqtt', {}).get('enabled', False)

    # Determine if controller is responsive
    online = False
    if controller:
        try:
            status = controller.get_status()
            online = status.get('online', False)
        except Exception:
            pass

    return jsonify({
        'status': 'ok',
        'service': 'faac-gateway',
        'online': online,
        'mqtt_enabled': mqtt_enabled
    })


@api_bp.errorhandler(404)
def api_not_found(e):
    """Handle 404 errors in API"""
    return jsonify({
        'error': 'Not found',
        'message': 'API endpoint not found'
    }), 404


@api_bp.errorhandler(405)
def method_not_allowed(e):
    """Handle 405 errors in API"""
    return jsonify({
        'error': 'Method not allowed',
        'message': f'Method {request.method} not allowed for this endpoint'
    }), 405


# CORS support (optional, can be enabled via config)
@api_bp.after_request
def add_cors_headers(response):
    """
    Add CORS headers if enabled in config

    This allows web apps from other domains to call the API.
    Only enable if needed and understand the security implications.
    """
    config = current_app.config.get('GATE_CONFIG', {})
    api_config = config.get('api', {})

    if api_config.get('cors_enabled', False):
        allowed_origins = api_config.get('cors_origins', '*')
        response.headers['Access-Control-Allow-Origin'] = allowed_origins
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-API-Key'

    return response
