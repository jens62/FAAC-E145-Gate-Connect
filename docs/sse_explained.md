# Server-Sent Events (SSE) im FAAC-Script - Detaillierte Erklärung

## 🎯 Was ist das Problem?

Der Browser soll **in Echtzeit** sehen, wenn sich die Tor-Position ändert.

### ❌ Schlechte Lösungen:

**Polling (Browser fragt ständig nach):**
```javascript
// Alle 500ms den Server fragen - INEFFIZIENT!
setInterval(() => {
    fetch('/status').then(r => r.json()).then(update);
}, 500);
```
❌ Viel Netzwerk-Traffic  
❌ Hohe Server-Last  
❌ Verzögerung (max. 500ms)

### ✅ Gute Lösung: Server-Sent Events (SSE)

Der Server "pushed" Updates **nur wenn sich etwas ändert**.

---

## 📊 Wie SSE im FAAC-Script funktioniert

### Architektur-Übersicht:

```
┌─────────────────────────────────────────────────────────────────────┐
│                         RASPBERRY PI                                │
│                                                                     │
│  ┌────────────────────┐                  ┌────────────────────┐   │
│  │ Background Thread  │                  │  Flask Web Server  │   │
│  │  (gate_manager)    │                  │                    │   │
│  │                    │                  │                    │   │
│  │  while True:       │                  │  @app.route(...)   │   │
│  │    read USB        │                  │                    │   │
│  │    parse position  │                  │                    │   │
│  │    ▼               │                  │                    │   │
│  │    gate_status = { │◄─────shared─────►│  def stream():     │   │
│  │      wing1: 45%    │     memory       │    yield data      │   │
│  │      wing2: 43%    │                  │                    │   │
│  │    }               │                  │                    │   │
│  │    ▼               │                  │         ▲          │   │
│  │    status_changed  │─────signal──────►│         │          │   │
│  │    .set()          │                  │    wait for event  │   │
│  └────────────────────┘                  └────────────────────┘   │
│                                                      │              │
└──────────────────────────────────────────────────────┼──────────────┘
                                                       │ SSE Stream
                                                       ▼
                                            ┌──────────────────┐
                                            │    BROWSER       │
                                            │                  │
                                            │  EventSource     │
                                            │  onmessage: ...  │
                                            └──────────────────┘
```

---

## 🔧 Die drei Schlüssel-Komponenten

### 1️⃣ Shared State (gate_status Dict)

```python
# Globale Variable - wird von BEIDEN Threads verwendet
gate_status = {
    "wing1": 0,      # Position Flügel 1 (0-100%)
    "wing2": 0,      # Position Flügel 2 (0-100%)
    "state": "UNKNOWN",  # OPEN/CLOSED/MOVING/STOPPED
    "online": False
}
```

**Warum global?**
- Background Thread (gate_manager) schreibt rein
- Web-Thread (stream) liest daraus
- Python Dict-Operationen sind thread-safe für einfache Zugriffe

---

### 2️⃣ Threading Event (status_changed)

```python
status_changed = threading.Event()
```

**Was ist ein Event?**
Ein Event ist wie eine **Flagge** mit zwei Zuständen:
- 🚫 Nicht gesetzt (clear)
- ✅ Gesetzt (set)

**Operationen:**

```python
# SETZEN (Background Thread macht das)
status_changed.set()    # Flagge hochziehen

# WARTEN (Web Thread macht das)
status_changed.wait()   # Blockiert bis Flagge gesetzt wird

# ZURÜCKSETZEN (Background Thread macht das)
status_changed.clear()  # Flagge runter für nächstes Mal
```

**Im gate_manager Thread:**
```python
# Wenn sich Position ändert:
gate_status["wing1"] = new_position
gate_status["wing2"] = new_position
status_changed.set()    # ← Signal: "Hey, es gibt Updates!"
status_changed.clear()  # ← Sofort zurücksetzen
```

**Im SSE Stream:**
```python
while True:
    status_changed.wait(timeout=5)  # ← Warte auf Signal (max 5 Sek)
    yield f"data: {json.dumps(gate_status)}\n\n"
```

---

### 3️⃣ SSE Stream (Flask Generator)

```python
@app.route('/stream')
def stream():
    def event_stream():
        # Initial-Update sofort senden
        yield f"data: {json.dumps(gate_status)}\n\n"
        
        # Endlosschleife
        while True:
            status_changed.wait(timeout=5)
            yield f"data: {json.dumps(gate_status)}\n\n"
    
    return Response(event_stream(), mimetype="text/event-stream")
```

**Was passiert hier?**

1. **Generator-Funktion** (`yield` statt `return`)
   - Funktion pausiert bei jedem `yield`
   - Läuft weiter wenn Browser bereit ist
   - Kann "unendlich" lang laufen

2. **SSE-Format:**
   ```
   data: {"wing1": 45, "wing2": 43}\n\n
   ```
   - Muss mit `data: ` beginnen
   - Muss mit `\n\n` enden (zwei Newlines!)
   
3. **MIME-Type:** `text/event-stream`
   - Signalisiert Browser: "Das ist ein SSE-Stream"

---

## 🌐 Browser-Seite (JavaScript)

```javascript
// EventSource erstellen - öffnet HTTP-Verbindung zu /stream
const source = new EventSource("/stream");

// Event-Handler: Wird aufgerufen wenn Daten ankommen
source.onmessage = function(e) {
    const data = JSON.parse(e.data);  // Parse JSON
    
    // UI updaten
    document.getElementById("w1v").innerText = data.wing1;
    document.getElementById("w2v").innerText = data.wing2;
    // ... etc
};
```

**EventSource macht automatisch:**
- ✅ Verbindung öffnen
- ✅ Daten empfangen
- ✅ Bei Fehler: Automatisch reconnecten!
- ✅ Parse SSE-Format

---

## 📝 Vollständiger Ablauf - Schritt für Schritt

### Szenario: Tor öffnet sich

```
Zeit | Background Thread        | SSE Stream              | Browser
─────┼──────────────────────────┼─────────────────────────┼─────────────────
  0s │ Read USB: Position = 0%  │                         │
     │ gate_status["wing1"] = 0 │                         │
     │ status_changed.set()     │ ← WACHT AUF             │
     │ status_changed.clear()   │                         │
     │                          │ yield data: {"wing1":0} │ → Empfängt Update
     │                          │ wait(timeout=5)...      │    UI zeigt 0%
─────┼──────────────────────────┼─────────────────────────┼─────────────────
  1s │ Read USB: Position = 15% │                         │
     │ gate_status["wing1"] = 15│                         │
     │ status_changed.set()     │ ← WACHT AUF             │
     │ status_changed.clear()   │                         │
     │                          │ yield data: {"wing1":15}│ → Empfängt Update
     │                          │ wait(timeout=5)...      │    UI zeigt 15%
─────┼──────────────────────────┼─────────────────────────┼─────────────────
  2s │ Read USB: Position = 30% │                         │
     │ gate_status["wing1"] = 30│                         │
     │ status_changed.set()     │ ← WACHT AUF             │
     │                          │ yield data: {"wing1":30}│ → Empfängt Update
     │                          │                         │    UI zeigt 30%
─────┼──────────────────────────┼─────────────────────────┼─────────────────
     │          ...             │          ...            │      ...
```

---

## 🔍 Wichtige Details

### Timeout bei wait()

```python
status_changed.wait(timeout=5)
```

**Warum timeout?**
- Event kann auch OHNE Änderung zurückkehren (nach 5 Sek)
- Verhindert dass Stream "einfriert"
- Sendet alle 5 Sek ein Update (auch wenn nichts passiert)
- Hält Verbindung am Leben (wichtig für NAT/Firewall)

### Multiple Clients

Jeder Browser bekommt seinen **eigenen Stream**:

```python
# Jeder Browser-Tab ruft /stream auf
# → Jeder bekommt eigene event_stream() Generator-Instanz
# → Alle teilen sich das gleiche gate_status Dict
# → Alle warten auf das gleiche status_changed Event
```

**Wenn 3 Browser-Tabs offen:**
```
Browser 1 ───┐
Browser 2 ───┼──► Alle warten auf status_changed
Browser 3 ───┘
             ▼
          Event wird gesetzt
             ▼
         ALLE werden geweckt ←── Threading.Event weckt ALLE Warter
             ▼
     Jeder sendet ein Update
```

---

## ⚡ Performance

**Effizienz:**
- ✅ Keine unnötigen Requests
- ✅ Update nur bei Änderung
- ✅ Minimale Server-Last
- ✅ Minimaler Netzwerk-Traffic

**Zahlen (typisch):**
- Polling (500ms): ~120 Requests/Minute
- SSE: ~6 Updates/Minute (nur bei Bewegung)
- **95% weniger Traffic!**

---

## 🆚 SSE vs. WebSockets vs. Polling

| Feature              | Polling | SSE   | WebSocket |
|---------------------|---------|-------|-----------|
| Server → Client     | ❌ Nein | ✅ Ja | ✅ Ja     |
| Client → Server     | ✅ Ja   | ✅ Ja (separate Requests) | ✅ Ja |
| Bidirektional       | ❌ Nein | ⚠️ Hybrid | ✅ Ja  |
| Auto-Reconnect      | N/A     | ✅ Ja | ❌ Nein   |
| Browser-Support     | ✅ 100% | ✅ 95%| ✅ 95%    |
| Komplexität         | Einfach | Einfach | Komplex  |
| Für Status-Updates  | ❌      | ✅ ✅ ✅ | ⚠️ Overkill |

**Für FAAC perfekt weil:**
- Server muss nur pushen (Tor-Status)
- Client sendet Befehle via normale HTTP-Requests
- Auto-Reconnect wichtig (Tor läuft 24/7)
- Einfach zu implementieren

---

## 🐛 Debugging

### Im Python-Code

```python
# Event-Status prüfen
print(f"Event gesetzt? {status_changed.is_set()}")

# Anzahl wartender Threads (intern)
# Nicht direkt zugänglich, aber für Verständnis:
# Threading.Event intern: _cond.wait() = Liste von wartenden Threads
```

### Im Browser

```javascript
// Console-Logging
const source = new EventSource("/stream");

source.onopen = () => console.log("SSE: Verbunden");
source.onmessage = (e) => console.log("SSE: Daten", e.data);
source.onerror = (e) => console.error("SSE: Fehler", e);

// DevTools: Network Tab
// → Typ: "eventsource"
// → Status: "pending" (bleibt offen!)
// → Messages: Siehe EventStream
```

---

## 🎓 Zusammenfassung

**SSE im FAAC-Script:**

1. **Background Thread** liest USB, updated `gate_status`
2. Bei Änderung: `status_changed.set()` signalisiert
3. **SSE Generator** wartet auf Event, sendet Update
4. **Browser** empfängt und zeigt sofort an

**Vorteile:**
- ✅ Echtzeit ohne Polling
- ✅ Minimal Traffic
- ✅ Automatisches Reconnect
- ✅ Einfach zu verstehen

**Das Schöne:**
- Gate-Manager kümmert sich nur um USB
- SSE kümmert sich nur um Updates
- Browser kümmert sich nur um UI
- Alles entkoppelt und sauber! 🎯
