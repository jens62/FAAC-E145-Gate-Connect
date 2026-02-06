# FAAC E145 Gate Connect

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

**Open-source Python gateway for FAAC E145 gate controllers.** Monitor, control, and integrate your automated gate with modern home automation platforms - all locally, no cloud required!

🔐 **Privacy-First** • 🏠 **Home Automation Ready** • 🔧 **Fully Reverse-Engineered Protocol**

---

## ✨ Features

- ✅ **Real-Time Monitoring** - Track both gate wings (0-100% position)
- ✅ **Full Control** - Open, Close, Stop commands
- ✅ **Modern Web UI** - Responsive interface with live Server-Sent Events
- ✅ **MQTT Integration** - Home Assistant auto-discovery support
- ✅ **OpenHAB Ready** - Native binding integration (coming soon)
- ✅ **Local Only** - No cloud, complete privacy
- ✅ **Raspberry Pi Optimized** - Runs on RPi 2+
- ✅ **Keyboard Shortcuts** - O (open), C (close), S (stop)

---

## 📸 Screenshots

*Web interface and mobile screenshots coming soon*

---

## 🚀 Quick Start

### Prerequisites

- **Hardware**: Raspberry Pi (or Linux machine) with USB port
- **Software**: Python 3.8+
- **Connection**: USB cable to FAAC E145 controller

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/FAAC-E145-Gate-Connect.git
cd FAAC-E145-Gate-Connect

# 2. Install dependencies
pip3 install -r requirements.txt

# 3. Configure (find your USB port with: ls -l /dev/ttyUSB*)
# Edit PORT in faac_gateway_standalone.py

# 4. Run!
python3 faac_gateway_standalone.py
```

**Access:** Open `http://localhost:5000` in your browser

### Debug Modes

```bash
# Show transmitted commands
python3 faac_gateway_standalone.py -tx

# Show received data
python3 faac_gateway_standalone.py -rx

# Show parsed positions
python3 faac_gateway_standalone.py -p

# All at once
python3 faac_gateway_standalone.py -tx -rx -p
```

---

## 🔌 MQTT Integration

Enable MQTT for Home Assistant auto-discovery:

```python
# Coming in v1.1 - Configuration file support
mqtt:
  enabled: true
  broker: localhost
  topic_prefix: faac/gate
  homeassistant_discovery: true
```

### MQTT Topics

```
faac/gate/status         # {"wing1": 45, "wing2": 43, "state": "MOVING"}
faac/gate/wing1          # 45
faac/gate/wing2          # 43
faac/gate/state          # OPEN/CLOSED/MOVING/STOPPED
faac/gate/command        # Publish: open/close/stop
```

---

## 📚 Documentation

- [Protocol Documentation](docs/protocol.md) - Reverse-engineered FAAC E145 protocol
- [Installation Guide](docs/installation.md) - Detailed setup instructions
- [Configuration](docs/configuration.md) - All configuration options
- [API Reference](docs/api.md) - REST API and SSE endpoints
- [Troubleshooting](docs/troubleshooting.md) - Common issues

---

## 🏗️ Architecture

```
┌──────────────────────────────────────┐
│     FAAC E145 Gate Controller        │
└────────────────┬─────────────────────┘
                 │ USB Serial
                 ▼
┌──────────────────────────────────────┐
│         FAAC Gateway (Python)        │
│  ┌────────────┐   ┌──────────────┐  │
│  │   Serial   │──→│  Web Server  │  │
│  │  Protocol  │   │  Flask + SSE │  │
│  └────────────┘   └──────────────┘  │
│         │                 │          │
│         ▼                 ▼          │
│   ┌─────────────────────────────┐   │
│   │  MQTT (Coming Soon)         │   │
│   │  - Home Assistant           │   │
│   │  - OpenHAB                  │   │
│   └─────────────────────────────┘   │
└──────────────────────────────────────┘
         │           │
         ▼           ▼
    Browser    Home Automation
```

---

## 🔧 Protocol Details

### Commands (Reverse-Engineered)

| Command | Hex String | Description |
|---------|-----------|-------------|
| **POLL** | `023035303030363330333033303330333803` | Status query (continuous) |
| **OPEN** | `0230393030384133303330333033303032...` | Open gate |
| **CLOSE** | `0230393030384133303330333033303038...` | Close gate |
| **STOP** | `0230393030384133303330333033303030...` | Stop movement |

### Protocol Structure

- **Framing**: STX (0x02) ... ETX (0x03)
- **Encoding**: Double-encoding (Binary → ASCII-Hex → Binary)
- **Checksum**: Included in original EasyBoard commands
- **No timestamps**: Stateless protocol

[Full protocol documentation](docs/protocol.md)

---

## 📋 Roadmap

### v1.0 (Current)
- [x] Core protocol implementation
- [x] Web UI with real-time updates
- [x] Position monitoring (both wings)
- [x] Full command support

### v1.1 (Planned)
- [ ] MQTT integration
- [ ] Home Assistant auto-discovery
- [ ] Configuration file support
- [ ] Systemd service setup

### v1.2 (Future)
- [ ] OpenHAB integration
- [ ] Docker container
- [ ] Multiple gate support
- [ ] Scheduling & automation
- [ ] Mobile app (React Native)
- [ ] RESTful API with authentication

---

## 🤝 Contributing

Contributions welcome! Areas needed:

- 🐛 Bug reports and fixes
- 📝 Documentation improvements
- 🔌 New integrations (Node-RED, Domoticz, etc.)
- 🌐 Translations
- 🧪 Test coverage
- 🎨 UI improvements

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 🔐 Security

⚠️ **Important Security Notes:**

- This software controls physical gate hardware
- Run on isolated/VLAN network recommended
- Do not expose web interface to internet without VPN
- Use MQTT authentication when enabled
- Keep software updated

**Report security issues**: Create a private security advisory on GitHub

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- **FAAC EasyBoard** - Protocol reverse-engineered from official software
- **Home Assistant Community** - Integration guidance
- **USB Traffic Analysis** - Protocol discovery via VirtualHere + USB monitoring

---

## ⚠️ Disclaimer

**This software is not affiliated with, endorsed by, or connected to FAAC International S.p.A.**

- Use at your own risk
- Test thoroughly before production use
- Author not responsible for gate malfunctions
- Verify commands before sending to hardware

---

## 📞 Support

- 📖 **Documentation**: [/docs](docs/)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/yourusername/FAAC-E145-Gate-Connect/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/FAAC-E145-Gate-Connect/discussions)
- 📧 **Email**: your.email@example.com

---

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=yourusername/FAAC-E145-Gate-Connect&type=Date)](https://star-history.com/#yourusername/FAAC-E145-Gate-Connect&Date)

---

**Made with ❤️ for the home automation community**

*Compatible Models: E145, E245 (untested), E595 (untested)*
