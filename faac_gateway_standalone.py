#!/usr/bin/env python3
"""
FAAC Tor-Steuerung & Live-Monitor v3.0 - FINAL
Vollständig rekonstruiertes EasyBoard-Protokoll
Alle Befehle: OPEN ✓ | CLOSE ✓ | STOP ✓
"""

import os, time, threading, queue, json, logging, argparse
from flask import Flask, Response
from datetime import datetime

# Flask-Logs minimieren
logging.getLogger('werkzeug').setLevel(logging.ERROR)

# Argument Parser Setup
parser = argparse.ArgumentParser(
    description='FAAC Tor-Steuerung & Live-Monitor',
    formatter_class=argparse.RawTextHelpFormatter
)
parser.add_argument('-tx', action='store_true', help='GESENDETE BEFEHLE ANZEIGEN')
parser.add_argument('-rx', action='store_true', help='ROHDATEN-EMPFANG ANZEIGEN')
parser.add_argument('-p', '--parser', action='store_true', help='VERARBEITETE DATEN ANZEIGEN')

args = parser.parse_args()

app = Flask(__name__)
PORT = '/dev/ttyUSB1'

gate_status = {"wing1": 0, "wing2": 0, "state": "UNKNOWN", "online": False}
command_queue = queue.Queue()
status_changed = threading.Event()

def get_ts():
    """Zeitstempel für Logging"""
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]

def parse_position(hex_str, start_offset):
    """Extrahiert Position aus der Antwort (0-100%)"""
    try:
        hex_pair = hex_str[start_offset : start_offset + 4]
        val_str = bytes.fromhex(hex_pair).decode('ascii')
        return int(val_str, 16)
    except:
        return None

def gate_manager():
    """Hauptschleife für Tor-Steuerung und Monitoring"""
    global gate_status
    last_w1, last_w2 = -1, -1
    still_count = 0

    # ========================================================================
    # FAAC BEFEHLE - Aus EasyBoard Traffic-Analyse extrahiert
    # ========================================================================
    
    # Status-Abfrage (wird kontinuierlich gesendet)
    POLL_CMD = "023035303030363330333033303330333803"
    
    # Steuerbefehle (alle verifiziert und funktionsfähig!)
    RAW_CMDS = {
        "open":  "0230393030384133303330333033303032303030303030423203",  # ✓ OPEN
        "close": "0230393030384133303330333033303038303030303030414303",  # ✓ CLOSE
        "stop":  "0230393030384133303330333033303030303230303030423203",  # ✓ STOP
    }
    
    while True:
        fd = None
        try:
            if not os.path.exists(PORT):
                gate_status["online"] = False
                time.sleep(5)
                continue

            fd = os.open(PORT, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
            gate_status["online"] = True
            print(f"[{get_ts()}] ✓ FAAC VERBUNDEN - ALLE FUNKTIONEN AKTIV")
            
            while True:
                # ============================================================
                # 1. SENDEN (TX) - Befehle aus der Queue
                # ============================================================
                if not command_queue.empty():
                    cmd_type = command_queue.get()
                    full_cmd = RAW_CMDS.get(cmd_type)
                    
                    if full_cmd:
                        os.write(fd, bytes.fromhex(full_cmd))
                        if args.tx:
                            print(f"[{get_ts()}] TX → {full_cmd} ({cmd_type.upper()})") 
                        else:
                            print(f"[{get_ts()}] ▶ Befehl: {cmd_type.upper()}")
                        time.sleep(0.5)
                    else:
                        print(f"[{get_ts()}] ⚠ Unbekannter Befehl: {cmd_type}")

                # ============================================================
                # 2. POLL - Status abfragen
                # ============================================================
                os.write(fd, bytes.fromhex(POLL_CMD))
                time.sleep(0.4)
                
                # ============================================================
                # 3. EMPFANGEN (RX) - Antwort lesen und parsen
                # ============================================================
                try:
                    res = os.read(fd, 1024)
                    if res:
                        hex_res = res.hex().upper()
                        if args.rx: 
                            print(f"[{get_ts()}] RX ← {hex_res}") 
                        
                        # Parser für Positionsdaten
                        # Suche nach Header: "30 00 86" = "3030303836"
                        idx = hex_res.find("3030303836")
                        if idx != -1:
                            # Positionen extrahieren (Offset +66 und +70)
                            w1 = parse_position(hex_res, idx + 66)
                            w2 = parse_position(hex_res, idx + 70)

                            if w1 is not None and w2 is not None:
                                # Status bestimmen
                                if w1 == 0 and w2 == 0: 
                                    s = "CLOSED"
                                elif w1 >= 95 or w2 >= 95: 
                                    s = "OPEN"
                                else:
                                    # Bewegungs-Detektion
                                    if w1 == last_w1 and w2 == last_w2:
                                        still_count += 1
                                    else:
                                        still_count = 0
                                    s = "STOPPED" if still_count >= 3 else "MOVING"
                                
                                last_w1, last_w2 = w1, w2

                                if args.parser:
                                    print(f"[{get_ts()}] PARSE │ W1: {w1:3d}% │ W2: {w2:3d}% │ {s}")
                                
                                # Status-Update für Web-UI
                                if (w1 != gate_status["wing1"] or 
                                    w2 != gate_status["wing2"] or 
                                    s != gate_status["state"]):
                                    gate_status.update({"wing1": w1, "wing2": w2, "state": s})
                                    status_changed.set()
                                    status_changed.clear()
                except OSError: 
                    pass
                    
                time.sleep(0.1)
                
        except Exception as e:
            print(f"[{get_ts()}] ❌ Fehler: {e}")
            if fd: 
                os.close(fd)
            gate_status["online"] = False
            time.sleep(5)

# ============================================================================
# WEB-INTERFACE
# ============================================================================

@app.route('/action/<cmd>')
def action(cmd):
    """REST-Endpoint für Tor-Steuerung"""
    command_queue.put(cmd)
    return {"ok": True, "command": cmd}

@app.route('/stream')
def stream():
    """Server-Sent Events für Live-Updates"""
    def event_stream():
        yield f"data: {json.dumps(gate_status)}\n\n"
        while True:
            status_changed.wait(timeout=5)
            yield f"data: {json.dumps(gate_status)}\n\n"
    return Response(event_stream(), mimetype="text/event-stream")

@app.route('/')
def index():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>FAAC Monitor v3.0</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: linear-gradient(135deg, #0f0f0f 0%, #1a1a1a 100%);
            color: #e0e0e0;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .card {
            background: rgba(30, 30, 30, 0.95);
            backdrop-filter: blur(10px);
            padding: 30px;
            border-radius: 20px;
            max-width: 450px;
            width: 100%;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        }
        .header {
            text-align: center;
            margin-bottom: 25px;
        }
        .version {
            font-size: 0.7em;
            opacity: 0.5;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        #state {
            font-size: 2.5em;
            font-weight: 700;
            margin-top: 10px;
            text-align: center;
            text-transform: uppercase;
            letter-spacing: 2px;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
        }
        .wing {
            margin: 15px 0;
        }
        .wing-label {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 0.9em;
            opacity: 0.8;
        }
        .wing-value {
            font-weight: 600;
            font-size: 1.1em;
        }
        .bar-bg {
            background: rgba(0, 0, 0, 0.5);
            height: 28px;
            border-radius: 14px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: inset 0 2px 5px rgba(0, 0, 0, 0.5);
        }
        .bar-fill {
            height: 100%;
            width: 0%;
            transition: width 0.6s cubic-bezier(0.4, 0.0, 0.2, 1),
                        background-color 0.3s ease;
            box-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
        }
        .buttons {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-top: 25px;
        }
        .btn {
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
        }
        .btn:active {
            transform: scale(0.95);
        }
        .btn-open {
            background: linear-gradient(135deg, #2e7d32 0%, #388e3c 100%);
            grid-column: span 2;
        }
        .btn-open:hover {
            background: linear-gradient(135deg, #388e3c 0%, #43a047 100%);
        }
        .btn-close {
            background: linear-gradient(135deg, #c62828 0%, #d32f2f 100%);
        }
        .btn-close:hover {
            background: linear-gradient(135deg, #d32f2f 0%, #e53935 100%);
        }
        .btn-stop {
            background: linear-gradient(135deg, #424242 0%, #616161 100%);
        }
        .btn-stop:hover {
            background: linear-gradient(135deg, #616161 0%, #757575 100%);
        }
        .status-dot {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .footer {
            text-align: center;
            margin-top: 20px;
            font-size: 0.75em;
            opacity: 0.4;
        }
    </style>
</head>
<body>
    <div class="card">
        <div class="header">
            <div class="version">FAAC Monitor v3.0 Final</div>
            <div id="state">
                <span class="status-dot"></span>LÄDT...
            </div>
        </div>
        
        <div class="wing">
            <div class="wing-label">
                <span>Flügel 1 (Master)</span>
                <span class="wing-value"><span id="w1v">0</span>%</span>
            </div>
            <div class="bar-bg">
                <div id="w1b" class="bar-fill"></div>
            </div>
        </div>
        
        <div class="wing">
            <div class="wing-label">
                <span>Flügel 2 (Slave)</span>
                <span class="wing-value"><span id="w2v">0</span>%</span>
            </div>
            <div class="bar-bg">
                <div id="w2b" class="bar-fill"></div>
            </div>
        </div>
        
        <div class="buttons">
            <button class="btn btn-open" onclick="sendCmd('open')">
                Öffnen
            </button>
            <button class="btn btn-close" onclick="sendCmd('close')">
                Schließen
            </button>
            <button class="btn btn-stop" onclick="sendCmd('stop')">
                Stop
            </button>
        </div>
        
        <div class="footer">
            EasyBoard Protocol · Reverse Engineered
        </div>
    </div>
    
    <script>
        const source = new EventSource("/stream");
        const stateColors = {
            "OPEN": "#4caf50",
            "CLOSED": "#f44336",
            "MOVING": "#ffb300",
            "STOPPED": "#00bcd4",
            "UNKNOWN": "#757575"
        };
        
        source.onmessage = function(e) {
            const d = JSON.parse(e.data);
            
            // Status-Text
            const stateEl = document.getElementById("state");
            stateEl.innerHTML = '<span class="status-dot"></span>' + d.state;
            
            // Farben
            const color = stateColors[d.state] || "#757575";
            stateEl.style.color = color;
            document.querySelector(".status-dot").style.backgroundColor = color;
            
            // Flügel-Werte
            document.getElementById("w1v").innerText = d.wing1;
            document.getElementById("w1b").style.width = d.wing1 + "%";
            document.getElementById("w1b").style.backgroundColor = color;
            
            document.getElementById("w2v").innerText = d.wing2;
            document.getElementById("w2b").style.width = d.wing2 + "%";
            document.getElementById("w2b").style.backgroundColor = color;
        };
        
        function sendCmd(cmd) {
            fetch('/action/' + cmd)
                .then(r => r.json())
                .then(d => console.log('✓ Befehl gesendet:', cmd))
                .catch(e => console.error('Fehler:', e));
        }
        
        // Tastatur-Shortcuts
        document.addEventListener('keydown', function(e) {
            if (e.key === 'o' || e.key === 'O') sendCmd('open');
            if (e.key === 'c' || e.key === 'C') sendCmd('close');
            if (e.key === 's' || e.key === 'S' || e.key === ' ') sendCmd('stop');
        });
    </script>
</body>
</html>
    """

if __name__ == '__main__':
    print("=" * 80)
    print("FAAC TOR-STEUERUNG v3.0 FINAL")
    print("=" * 80)
    print()
    print("📡 EasyBoard-Protokoll vollständig rekonstruiert")
    print()
    print("VERFÜGBARE BEFEHLE:")
    print("  ✓ OPEN  - Tor öffnen")
    print("  ✓ CLOSE - Tor schließen")
    print("  ✓ STOP  - Bewegung stoppen")
    print()
    print(f"🔌 Port: {PORT}")
    print(f"🌐 Web-UI: http://localhost:5000")
    print()
    print("TASTATUR-SHORTCUTS:")
    print("  [O] - Öffnen")
    print("  [C] - Schließen")
    print("  [S] oder [SPACE] - Stop")
    print()
    print("DEBUG-MODI:")
    print("  -tx     Gesendete Befehle anzeigen")
    print("  -rx     Empfangene Rohdaten anzeigen")
    print("  -p      Geparste Positionsdaten anzeigen")
    print("=" * 80)
    print()
    
    threading.Thread(target=gate_manager, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
