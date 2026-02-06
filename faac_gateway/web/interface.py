"""
Flask web interface for FAAC gate control
"""

import json
import threading
from flask import Flask, Response


def create_app(gate_controller, mqtt_enabled=False):
    """
    Create Flask application

    Args:
        gate_controller: GateController instance
        mqtt_enabled: Whether MQTT is enabled (for display purposes)

    Returns:
        Flask app instance
    """
    app = Flask(__name__)
    status_changed = threading.Event()

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
            grid-column: span 2;
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
        }}
        .btn-stop:hover {{
            background: linear-gradient(135deg, #616161 0%, #757575 100%);
        }}
        .status-heart {{
            display: inline-block;
            margin-right: 8px;
            font-size: 0.8em;
            animation: heartbeat 1.5s ease-in-out infinite;
        }}
        @keyframes heartbeat {{
            0%, 100% {{ transform: scale(1); }}
            10% {{ transform: scale(1.2); }}
            20% {{ transform: scale(1); }}
            30% {{ transform: scale(1.2); }}
            40% {{ transform: scale(1); }}
        }}
        .last-update {{
            font-size: 0.7em;
            opacity: 0.6;
            text-align: center;
            margin-top: 8px;
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
            <div id="state">
                <span class="status-heart">❤</span>LOADING...
            </div>
            <div class="last-update" id="lastUpdate">Connecting...</div>
        </div>

        <div class="wing">
            <div class="wing-label">
                <span>Wing 1 (Master)</span>
                <span class="wing-value"><span id="w1v">0</span>%</span>
            </div>
            <div class="bar-bg">
                <div id="w1b" class="bar-fill"></div>
            </div>
        </div>

        <div class="wing">
            <div class="wing-label">
                <span>Wing 2 (Slave)</span>
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
            "MOVING": "#ffb300",
            "STOPPED": "#00bcd4",
            "UNKNOWN": "#757575"
        }};

        let lastUpdateTime = Date.now();

        source.onmessage = function(e) {{
            const d = JSON.parse(e.data);
            lastUpdateTime = Date.now();

            const stateEl = document.getElementById("state");
            stateEl.innerHTML = '<span class="status-heart">❤</span>' + d.state;

            const color = stateColors[d.state] || "#757575";
            stateEl.style.color = color;
            document.querySelector(".status-heart").style.color = color;

            document.getElementById("w1v").innerText = d.wing1;
            document.getElementById("w1b").style.width = d.wing1 + "%";
            document.getElementById("w1b").style.backgroundColor = color;

            document.getElementById("w2v").innerText = d.wing2;
            document.getElementById("w2b").style.width = d.wing2 + "%";
            document.getElementById("w2b").style.backgroundColor = color;
        }};

        // Update "last seen" timestamp every second
        setInterval(function() {{
            const elapsed = Math.floor((Date.now() - lastUpdateTime) / 1000);
            const lastUpdateEl = document.getElementById("lastUpdate");

            if (elapsed < 3) {{
                lastUpdateEl.textContent = "Live";
                lastUpdateEl.classList.remove("stale");
            }} else if (elapsed < 60) {{
                lastUpdateEl.textContent = "Last update: " + elapsed + "s ago";
                lastUpdateEl.classList.toggle("stale", elapsed > 10);
            }} else {{
                const minutes = Math.floor(elapsed / 60);
                lastUpdateEl.textContent = "Last update: " + minutes + "m ago";
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
