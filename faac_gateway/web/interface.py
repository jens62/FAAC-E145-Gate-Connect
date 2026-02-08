"""
Flask web interface for FAAC gate control
"""

import json
import threading
from flask import Flask, Response
from .api import api_bp


def create_app(gate_controller, mqtt_enabled=False, config=None):
    """
    Create Flask application

    Args:
        gate_controller: GateController instance
        mqtt_enabled: Whether MQTT is enabled (for display purposes)
        config: Configuration dict (optional, for API settings)

    Returns:
        Flask app instance
    """
    app = Flask(__name__)
    status_changed = threading.Event()

    # Store controller and config in app context for API access
    app.config['GATE_CONTROLLER'] = gate_controller
    app.config['GATE_CONFIG'] = config or {}

    # Register REST API blueprint
    api_enabled = True
    if config:
        api_enabled = config.get('api', {}).get('enabled', True)

    if api_enabled:
        app.register_blueprint(api_bp)

    # Set up status callback to notify web clients
    original_callback = gate_controller.status_callback

    def status_callback(status):
        status_changed.set()
        status_changed.clear()
        if original_callback:
            original_callback(status)

    gate_controller.status_callback = status_callback

    @app.route('/action/<cmd>')
    def action(cmd):
        """REST endpoint for gate control"""
        gate_controller.send_command(cmd)
        return {"ok": True, "command": cmd}

    @app.route('/stream')
    def stream():
        """Server-Sent Events for live updates"""
        def event_stream():
            yield f"data: {json.dumps(gate_controller.get_status())}\n\n"
            while True:
                status_changed.wait(timeout=5)
                yield f"data: {json.dumps(gate_controller.get_status())}\n\n"
        return Response(event_stream(), mimetype="text/event-stream")

    @app.route('/')
    def index():
        footer_text = "MQTT Integration Enabled" if mqtt_enabled else "EasyBoard Protocol · Reverse Engineered"
        title_suffix = " + MQTT" if mqtt_enabled else ""

        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>FAAC Monitor{title_suffix}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: linear-gradient(135deg, #0f0f0f 0%, #1a1a1a 100%);
            color: #e0e0e0;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        .card {{
            background: rgba(30, 30, 30, 0.95);
            backdrop-filter: blur(10px);
            padding: 30px;
            border-radius: 20px;
            max-width: 450px;
            width: 100%;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        }}
        .header {{
            text-align: center;
            margin-bottom: 25px;
        }}
        .version {{
            font-size: 0.7em;
            opacity: 0.5;
            text-transform: uppercase;
            letter-spacing: 2px;
        }}
        #state {{
            font-size: 2.5em;
            font-weight: 700;
            margin-top: 10px;
            text-align: center;
            text-transform: uppercase;
            letter-spacing: 2px;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
        }}
        .gate-viewport {{
            width: 100%;
            min-height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(to bottom, #d4e6f1 0%, #e8f4f8 50%, #d0d8dc 100%);
            border-radius: 15px;
            border: 2px solid rgba(255, 255, 255, 0.1);
            margin: 20px 0;
            padding: 20px 10px;
            overflow: hidden;
        }}
        .gate-wrapper {{
            width: 100%;
            max-width: 100%;
        }}
        .gate-wrapper svg {{
            display: block;
            width: 100%;
            height: auto;
        }}
        .wing {{
            margin: 15px 0;
        }}
        .wing-label {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 0.9em;
            opacity: 0.8;
        }}
        .wing-value {{
            font-weight: 600;
            font-size: 1.1em;
        }}
        .bar-bg {{
            background: rgba(0, 0, 0, 0.5);
            height: 28px;
            border-radius: 14px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.5);
        }}
        .bar-fill {{
            height: 100%;
            width: 0%;
            transition: width 0.6s cubic-bezier(0.4, 0.0, 0.2, 1),
                        background-color 0.3s ease;
            box-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
        }}
        .buttons {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-top: 25px;
        }}
        .btn {{
            padding: 16px;
            border: none;
            border-radius: 12px;
            color: white;
            font-weight: 600;
            font-size: 0.95em;
            cursor: pointer;
            transition: all 0.2s;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }}
        .btn:active {{
            transform: scale(0.95);
        }}
        .btn-open {{
            background: linear-gradient(135deg, #2e7d32 0%, #388e3c 100%);
        }}
        .btn-open:hover {{
            background: linear-gradient(135deg, #388e3c 0%, #43a047 100%);
        }}
        .btn-close {{
            background: linear-gradient(135deg, #c62828 0%, #d32f2f 100%);
        }}
        .btn-close:hover {{
            background: linear-gradient(135deg, #d32f2f 0%, #e53935 100%);
        }}
        .btn-stop {{
            background: linear-gradient(135deg, #424242 0%, #616161 100%);
            grid-column: span 2;
        }}
        .btn-stop:hover {{
            background: linear-gradient(135deg, #616161 0%, #757575 100%);
        }}
        .last-update {{
            font-size: 0.7em;
            opacity: 0.6;
            text-align: center;
            margin-top: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
        }}
        .status-heart {{
            display: inline-block;
            color: #ef5350;
            font-size: 0.7em;
            animation: heartbeat 1.5s ease-in-out infinite;
        }}
        @keyframes heartbeat {{
            0%, 100% {{ transform: scale(1); }}
            10% {{ transform: scale(1.2); }}
            20% {{ transform: scale(1); }}
            30% {{ transform: scale(1.2); }}
            40% {{ transform: scale(1); }}
        }}
        .stale {{
            opacity: 0.3;
        }}
        .footer {{
            text-align: center;
            margin-top: 20px;
            font-size: 0.75em;
            opacity: 0.4;
        }}
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <div class="version">FAAC Monitor{title_suffix}</div>
            <div id="state">LOADING...</div>
            <div class="last-update" id="lastUpdate">
                <span class="status-heart">❤</span>
                <span id="lastUpdateText">Connecting...</span>
            </div>
        </div>

        <div class="gate-viewport">
            <div class="gate-wrapper">
                <svg id="gate-svg" viewBox="-7.5 -7.5 3480 1330" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <symbol id="hinge" width="32" height="105">
                            <rect width="32" height="105" fill="#555" />
                            <line x1="0" y1="35" x2="32" y2="35" stroke="#888" stroke-width="1" />
                            <line x1="0" y1="70" x2="32" y2="70" stroke="#888" stroke-width="1" />
                        </symbol>

                        <symbol id="post">
                            <line x1="50" y1="0" x2="50" y2="1330" stroke="#555" stroke-width="100" />
                        </symbol>
                    </defs>

                    <!-- Left side -->
                    <use href="#post" x="0" y="-7.5" />
                    <use href="#hinge" x="105.25" y="10" />
                    <use href="#hinge" x="105.25" y="1100" />

                    <!-- Left wing -->
                    <g id="wing1-group">
                        <line id="wing1-frame-top" y1="7.5" y2="7.5" stroke="#555" stroke-width="15" />
                        <line id="wing1-frame-bottom" y1="1207.5" y2="1207.5" stroke="#555" stroke-width="15" />
                        <line id="wing1-frame-left" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                        <line id="wing1-frame-right" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                        <line id="wing1-reinf-1" y1="242.5" y2="242.5" stroke="#555" stroke-width="15" />
                        <line id="wing1-reinf-2" y1="1092.5" y2="1092.5" stroke="#555" stroke-width="15" />
                        <line id="wing1-bar-1" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                        <line id="wing1-bar-2" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                        <line id="wing1-bar-3" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                        <line id="wing1-bar-4" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                        <line id="wing1-bar-5" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                        <line id="wing1-bar-6" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                        <line id="wing1-bar-7" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                        <line id="wing1-bar-8" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                        <line id="wing1-bar-9" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                        <line id="wing1-bar-10" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                        <line id="wing1-bar-11" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                        <line id="wing1-bar-12" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                    </g>

                    <!-- Right side (mirrored) -->
                    <g transform="translate(3480, 0) scale(-1, 1)">
                        <use href="#post" x="0" y="-7.5" />
                        <use href="#hinge" x="105.25" y="10" />
                        <use href="#hinge" x="105.25" y="1100" />

                        <g id="wing2-group">
                            <line id="wing2-frame-top" y1="7.5" y2="7.5" stroke="#555" stroke-width="15" />
                            <line id="wing2-frame-bottom" y1="1207.5" y2="1207.5" stroke="#555" stroke-width="15" />
                            <line id="wing2-frame-left" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                            <line id="wing2-frame-right" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                            <line id="wing2-reinf-1" y1="242.5" y2="242.5" stroke="#555" stroke-width="15" />
                            <line id="wing2-reinf-2" y1="1092.5" y2="1092.5" stroke="#555" stroke-width="15" />
                            <line id="wing2-bar-1" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                            <line id="wing2-bar-2" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                            <line id="wing2-bar-3" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                            <line id="wing2-bar-4" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                            <line id="wing2-bar-5" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                            <line id="wing2-bar-6" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                            <line id="wing2-bar-7" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                            <line id="wing2-bar-8" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                            <line id="wing2-bar-9" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                            <line id="wing2-bar-10" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                            <line id="wing2-bar-11" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                            <line id="wing2-bar-12" y1="7.5" y2="1207.5" stroke="#555" stroke-width="15" />
                        </g>
                    </g>
                </svg>
            </div>
        </div>

        <div class="wing">
            <div class="wing-label">
                <span>Wing 1</span>
                <span class="wing-value"><span id="w1v">0</span>%</span>
            </div>
            <div class="bar-bg">
                <div id="w1b" class="bar-fill"></div>
            </div>
        </div>

        <div class="wing">
            <div class="wing-label">
                <span>Wing 2</span>
                <span class="wing-value"><span id="w2v">0</span>%</span>
            </div>
            <div class="bar-bg">
                <div id="w2b" class="bar-fill"></div>
            </div>
        </div>

        <div class="buttons">
            <button class="btn btn-open" onclick="sendCmd('open')">
                Open
            </button>
            <button class="btn btn-close" onclick="sendCmd('close')">
                Close
            </button>
            <button class="btn btn-stop" onclick="sendCmd('stop')">
                Stop
            </button>
        </div>

        <div class="footer">
            {footer_text}
        </div>
    </div>

    <script>
        const source = new EventSource("/stream");
        const stateColors = {{
            "OPEN": "#4caf50",
            "CLOSED": "#f44336",
            "OPENING": "#66bb6a",
            "CLOSING": "#ef5350",
            "STOPPED": "#00bcd4",
            "UNKNOWN": "#757575"
        }};

        let lastUpdateTime = Date.now();
        let sseConnected = false;

        // Gate animation geometry
        const ROTATION_X = 125;
        const FRAME_LEFT_CLOSED = 150;
        const FRAME_RIGHT_CLOSED = 1725;
        const FRAME_LEFT_DX = FRAME_LEFT_CLOSED - ROTATION_X;
        const FRAME_RIGHT_DX = FRAME_RIGHT_CLOSED - ROTATION_X;
        const FRAME_STROKE_CLOSED = 15;
        const FRAME_STROKE_OPEN = 40;
        const barAbsolute = [271.15, 392.31, 513.46, 634.62, 755.77, 876.92,
                             998.08, 1119.23, 1240.38, 1361.54, 1482.69, 1603.85];
        const barDX = barAbsolute.map(x => x - ROTATION_X);

        function updateGateVisual(wingId, position) {{
            const angle = (position / 100) * (Math.PI / 2);
            const cosA = Math.cos(angle);
            const sinA = Math.sin(angle);

            const frameLeftX = ROTATION_X + FRAME_LEFT_DX * cosA;
            const frameRightX = ROTATION_X + FRAME_RIGHT_DX * cosA;
            const vertStroke = FRAME_STROKE_CLOSED * cosA + FRAME_STROKE_OPEN * sinA;
            const halfVS = vertStroke / 2;

            const fl = document.getElementById(`${{wingId}}-frame-left`);
            fl.setAttribute('x1', frameLeftX);
            fl.setAttribute('x2', frameLeftX);
            fl.setAttribute('stroke-width', vertStroke);

            const fr = document.getElementById(`${{wingId}}-frame-right`);
            fr.setAttribute('x1', frameRightX);
            fr.setAttribute('x2', frameRightX);
            fr.setAttribute('stroke-width', vertStroke);

            const hLeft = frameLeftX - halfVS;
            const hRight = frameRightX + halfVS;

            document.getElementById(`${{wingId}}-frame-top`).setAttribute('x1', hLeft);
            document.getElementById(`${{wingId}}-frame-top`).setAttribute('x2', hRight);
            document.getElementById(`${{wingId}}-frame-bottom`).setAttribute('x1', hLeft);
            document.getElementById(`${{wingId}}-frame-bottom`).setAttribute('x2', hRight);

            document.getElementById(`${{wingId}}-reinf-1`).setAttribute('x1', frameLeftX);
            document.getElementById(`${{wingId}}-reinf-1`).setAttribute('x2', frameRightX);
            document.getElementById(`${{wingId}}-reinf-2`).setAttribute('x1', frameLeftX);
            document.getElementById(`${{wingId}}-reinf-2`).setAttribute('x2', frameRightX);

            for (let i = 0; i < 12; i++) {{
                const barX = ROTATION_X + barDX[i] * cosA;
                const bar = document.getElementById(`${{wingId}}-bar-${{i + 1}}`);
                bar.setAttribute('x1', barX);
                bar.setAttribute('x2', barX);
            }}
        }}

        // Initialize gate at closed position
        updateGateVisual('wing1', 0);
        updateGateVisual('wing2', 0);

        source.onopen = function() {{
            sseConnected = true;
            console.log("SSE connection established");
        }};

        source.onerror = function(e) {{
            sseConnected = false;
            console.error("SSE connection error", e);
            document.getElementById("lastUpdateText").textContent = "Connection lost - Reconnecting...";
            document.getElementById("lastUpdate").classList.add("stale");
        }};

        source.onmessage = function(e) {{
            const d = JSON.parse(e.data);
            lastUpdateTime = Date.now();
            sseConnected = true;

            const stateEl = document.getElementById("state");
            stateEl.textContent = d.state;

            const color = stateColors[d.state] || "#757575";
            stateEl.style.color = color;

            document.getElementById("w1v").innerText = d.wing1;
            document.getElementById("w1b").style.width = d.wing1 + "%";
            document.getElementById("w1b").style.backgroundColor = color;

            document.getElementById("w2v").innerText = d.wing2;
            document.getElementById("w2b").style.width = d.wing2 + "%";
            document.getElementById("w2b").style.backgroundColor = color;

            // Update gate animation
            updateGateVisual('wing1', d.wing1);
            updateGateVisual('wing2', d.wing2);
        }};

        // Update "last seen" timestamp every second
        setInterval(function() {{
            // Don't update if SSE connection is broken (error handler shows reconnect message)
            if (!sseConnected) return;

            const elapsed = Math.floor((Date.now() - lastUpdateTime) / 1000);
            const lastUpdateText = document.getElementById("lastUpdateText");
            const lastUpdateEl = document.getElementById("lastUpdate");

            if (elapsed < 15) {{
                lastUpdateText.textContent = "Live";
                lastUpdateEl.classList.remove("stale");
            }} else if (elapsed < 60) {{
                lastUpdateText.textContent = "Last update: " + elapsed + "s ago";
                lastUpdateEl.classList.add("stale");
            }} else {{
                const minutes = Math.floor(elapsed / 60);
                lastUpdateText.textContent = "Last update: " + minutes + "m ago";
                lastUpdateEl.classList.add("stale");
            }}
        }}, 1000);

        function sendCmd(cmd) {{
            fetch('/action/' + cmd)
                .then(r => r.json())
                .then(d => console.log('Command sent:', cmd))
                .catch(e => console.error('Error:', e));
        }}

        document.addEventListener('keydown', function(e) {{
            if (e.key === 'o' || e.key === 'O') sendCmd('open');
            if (e.key === 'c' || e.key === 'C') sendCmd('close');
            if (e.key === 's' || e.key === 'S' || e.key === ' ') sendCmd('stop');
        }});
    </script>
</body>
</html>
        """

    return app
