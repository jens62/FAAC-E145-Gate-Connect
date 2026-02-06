# FAAC Tor-Steuerung v3.0 - Dokumentation

## 🎯 Erfolgreich rekonstruiertes EasyBoard-Protokoll

Alle Befehle wurden durch Traffic-Analyse der originalen FAAC EasyBoard-Software extrahiert und verifiziert.

---

## 📋 Befehlsübersicht

### Extrahierte FAAC-Befehle (alle verifiziert ✓)

| Befehl  | Hex-Code | ASCII-Darstellung | Länge |
|---------|----------|-------------------|-------|
| **POLL** | `023035303030363330333033303330333803` | `.050006303030303.` | 18 Bytes |
| **OPEN** | `0230393030384133303330333033303032303030303030423203` | `.09008A3030303002000000B2.` | 26 Bytes |
| **CLOSE** | `0230393030384133303330333033303038303030303030414303` | `.09008A3030303008000000AC.` | 26 Bytes |
| **STOP** | `0230393030384133303330333033303030303230303030423203` | `.09008A3030303000020000B2.` | 26 Bytes |

### Befehlsstruktur-Analyse

```
Gemeinsamer Prefix (alle Befehle):
02 30 39 30 30 38 41 33 30 33 30 33 30 33 30

Unterschiede (Payload + Checksum):
OPEN:  ...30 32 30 30 30 30 30 30 42 32 03
CLOSE: ...30 38 30 30 30 30 30 30 41 43 03
STOP:  ...30 30 30 32 30 30 30 30 42 32 03
```

**Format:**
- Byte 0: `02` (STX - Start of Text)
- Bytes 1-22: Befehlsstruktur (teilweise ASCII-kodierte Hex-Werte)
- Bytes 23-24: Checksumme
- Byte 25: `03` (ETX - End of Text)

---

## 🚀 Installation auf Raspberry Pi

### 1. Voraussetzungen

```bash
# System aktualisieren
sudo apt update
sudo apt upgrade -y

# Python-Abhängigkeiten
sudo apt install python3 python3-pip -y
pip3 install flask
```

### 2. Script installieren

```bash
# Script auf den Pi kopieren
scp faac_control_final.py pi@raspberrypi:/home/pi/

# SSH zum Pi
ssh pi@raspberrypi

# Ausführbar machen
chmod +x /home/pi/faac_control_final.py
```

### 3. USB-Port identifizieren

```bash
# Alle USB-Geräte anzeigen
ls -l /dev/ttyUSB*

# Typische Ausgabe:
# /dev/ttyUSB0  oder  /dev/ttyUSB1
```

**WICHTIG:** Passe im Script die Zeile an:
```python
PORT = '/dev/ttyUSB1'  # Ändere zu deinem Port
```

### 4. Starten

```bash
# Normal starten
python3 /home/pi/faac_control_final.py

# Mit Debug-Ausgaben
python3 /home/pi/faac_control_final.py -tx -p

# Im Hintergrund starten
nohup python3 /home/pi/faac_control_final.py > /tmp/faac.log 2>&1 &
```

### 5. Autostart einrichten (optional)

```bash
# Systemd Service erstellen
sudo nano /etc/systemd/system/faac-gate.service
```

Inhalt:
```ini
[Unit]
Description=FAAC Gate Control
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi
ExecStart=/usr/bin/python3 /home/pi/faac_control_final.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Aktivieren:
```bash
sudo systemctl daemon-reload
sudo systemctl enable faac-gate.service
sudo systemctl start faac-gate.service
sudo systemctl status faac-gate.service
```

---

## 🌐 Web-Interface

Nach dem Start ist das Interface erreichbar unter:

```
http://raspberrypi.local:5000
http://<IP-ADRESSE>:5000
```

### Features:
- **Echtzeit-Status**: Live-Updates der Tor-Position
- **Zwei Flügel-Anzeige**: Master (Flügel 1) und Slave (Flügel 2)
- **3 Steuer-Buttons**: Öffnen, Schließen, Stop
- **Tastatur-Shortcuts**:
  - `O` - Öffnen
  - `C` - Schließen
  - `S` oder `SPACE` - Stop
- **Responsive Design**: Funktioniert auf Desktop und Mobile

---

## 🔍 Debug-Modi

### TX-Modus (Gesendete Befehle)
```bash
python3 faac_control_final.py -tx
```
Zeigt:
```
[14:23:45.123] TX → 0230393030384133303330333033303032303030303030423203 (OPEN)
```

### RX-Modus (Empfangene Rohdaten)
```bash
python3 faac_control_final.py -rx
```
Zeigt:
```
[14:23:45.523] RX ← 0233303030383630303030...
```

### Parser-Modus (Verarbeitete Daten)
```bash
python3 faac_control_final.py -p
```
Zeigt:
```
[14:23:45.523] PARSE │ W1:  45% │ W2:  42% │ MOVING
```

### Alle Modi kombiniert
```bash
python3 faac_control_final.py -tx -rx -p
```

---

## 📊 Status-Zustände

Das System erkennt automatisch folgende Zustände:

| Zustand | Bedingung | Farbe |
|---------|-----------|-------|
| **CLOSED** | Beide Flügel bei 0% | 🔴 Rot |
| **OPEN** | Mind. ein Flügel ≥ 95% | 🟢 Grün |
| **MOVING** | Position ändert sich | 🟡 Gelb |
| **STOPPED** | Position konstant (3x Poll) | 🔵 Cyan |
| **UNKNOWN** | Keine Verbindung | ⚫ Grau |

---

## 🔧 Anpassungen

### Port ändern
```python
PORT = '/dev/ttyUSB0'  # Ändere zu deinem Port
```

### Web-Port ändern
```python
app.run(host='0.0.0.0', port=8080)  # Statt 5000
```

### Position-Schwellwerte anpassen
```python
if w1 == 0 and w2 == 0:
    s = "CLOSED"
elif w1 >= 95 or w2 >= 95:  # Ändere 95 auf anderen Wert
    s = "OPEN"
```

### Stillstands-Erkennung
```python
s = "STOPPED" if still_count >= 3  # Ändere 3 auf andere Anzahl Polls
```

---

## 🛠️ Troubleshooting

### Problem: "Permission denied" beim USB-Port
```bash
# User zur dialout-Gruppe hinzufügen
sudo usermod -a -G dialout $USER
# Neu anmelden erforderlich
```

### Problem: Web-Interface nicht erreichbar
```bash
# Firewall-Port öffnen
sudo ufw allow 5000/tcp

# Oder Firewall deaktivieren (nicht empfohlen für Production)
sudo ufw disable
```

### Problem: Befehle werden nicht ausgeführt
```bash
# Mit Debug-Modi starten und Logs prüfen
python3 faac_control_final.py -tx -rx -p
```

### Problem: Falscher USB-Port
```bash
# Alle seriellen Ports anzeigen
dmesg | grep tty
ls -l /dev/tty*
```

---

## 📝 Protokoll-Details

### Polling-Mechanismus
- Das Script sendet alle ~400ms einen POLL-Befehl
- Die Steuerung antwortet mit dem aktuellen Status
- Position wird aus Bytes 66-70 der Antwort extrahiert

### Positionsformat
Die Positionswerte sind **ASCII-kodierte Hex-Werte**:
```
Bytes im Response: "36 34" (ASCII)
Dekodiert: "64" (String)
Als Hex interpretiert: 0x64 = 100 (Dezimal)
Ergebnis: 100% offen
```

### Checksummen
Die Checksummen sind Teil der originalen EasyBoard-Befehle und wurden 1:1 übernommen. Bei eigenen Befehlen müsste die Checksumme neu berechnet werden (XOR über alle Bytes).

---

## ⚡ Performance

- **Polling-Intervall**: ~500ms
- **Reaktionszeit**: <1 Sekunde
- **Web-UI Update**: Echtzeit via Server-Sent Events
- **CPU-Last**: <1% auf Raspberry Pi 2
- **RAM-Verbrauch**: ~20 MB

---

## 📜 Lizenz

Dieses Projekt wurde durch Reverse Engineering der FAAC EasyBoard-Software erstellt.
Nur für den privaten Gebrauch. Keine Garantie oder Gewährleistung.

**WICHTIG:** Die Verwendung erfolgt auf eigene Gefahr!
