# Cyra-OS v2

**The AI that actually does things.** A local-first autonomous AI companion for Windows.

Cyra-OS is a personal AI agent that runs on your machine, sees through your webcam, hears through your microphone, speaks back, manages files, searches the web, controls your desktop, and proactively monitors your workspace — all through a sleek dark dashboard or your phone.

## What's New in v2

| Feature | v1 | v2 |
|---------|----|----|
| Chat | Blocking POST | **SSE streaming** |
| Memory | Basic SQLite | **Semantic search + reflection** |
| Plugins | 1 (shell) | **7 plugins, 20+ tools** |
| Heartbeat | ❌ | **Proactive monitoring** |
| Multi-model | ❌ | **Auto-fallback chain** |
| Voice | Basic | **Interruption support** |
| Vision | Basic | **Status reporting** |
| Browser control | ❌ | **Screenshot + pyautogui** |
| File management | ❌ | **Full CRUD + search** |
| Web search | ❌ | **DuckDuckGo + URL fetch** |
| Reminders | ❌ | **Set + heartbeat check** |
| Security | ❌ | **Permission levels** |
| Avatar | ❌ | **Animated SVG face** |
| Mobile | ❌ | **Mobile companion page** |
| Romanian | ❌ | **RO language support** |

## Quick Start

```bash
# 1. Clone
git clone https://github.com/EmbrOS-Experimental/cyra-os.git
cd cyra-os

# 2. Setup
python setup.py

# 3. Configure API key
python manage.py setup

# 4. Start
python manage.py start
# Or directly:
python server.py
```

Open **http://localhost:8200** in your browser.

Mobile: **http://YOUR_IP:8200/mobile.html**

## Architecture

```
cyra-os/
├── server.py          # FastAPI main server
├── core/
│   ├── agent.py       # LiteLLM wrapper + multi-model fallback
│   ├── skills.py      # Plugin loader
│   ├── vision.py      # OpenCV webcam
│   ├── voice.py       # Edge TTS + Google STT
│   └── heartbeat.py   # Proactive monitoring
├── plugins/
│   ├── system.py      # Shell commands
│   ├── file_manager.py
│   ├── web_tools.py
│   ├── browser_control.py
│   ├── proactive_monitor.py
│   ├── romanian.py
│   ├── avatar.py
│   └── security_sandbox.py
├── brain/
│   ├── memory.py       # SQLite + FTS5 + sqlite-vec
│   ├── CYRA.md         # Identity/persona
│   ├── USER.md         # User profile
│   └── HEARTBEAT.md    # Heartbeat instructions
├── ui/
│   ├── index.html      # Main dashboard
│   └── mobile.html     # Mobile companion
└── config/
    └── settings.json   # App configuration
```

## Plugins

Cyra-OS uses a plugin system. Each Python file in `plugins/` with a `tools` list is auto-discovered on startup.

See `skills/marketplace.md` for the full list and how to create custom skills.

## Heartbeat

Cyra wakes up every 5 minutes (configurable) to:
- Check reminders
- Monitor watched directories
- Report notable changes

Edit `brain/HEARTBEAT.md` to customize.

## Security

Tools have 3 permission levels:
- **allow** — Execute automatically
- **confirm** — Ask first (default for dangerous ops)
- **deny** — Blocked

## License

MIT
