"""
Plugin: system_tools
Screenshot, reminders, and system info.
"""
import subprocess
import os
import json
import time
from pathlib import Path
from datetime import datetime

def take_screenshot():
    """Take a screenshot and return the file path."""
    try:
        desktop = Path.home() / "Desktop"
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = desktop / f"cyra_screenshot_{ts}.png"
        
        # Use Python to capture screen
        try:
            from PIL import ImageGrab
            img = ImageGrab.grab()
            img.save(str(out_path))
            return {"status": "ok", "path": str(out_path), "message": f"Screenshot saved to {out_path.name}"}
        except ImportError:
            # Fallback: use PowerShell
            ps_cmd = f"Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Screen]::PrimaryScreen.Bounds"
            return {"error": "PIL not installed. Install with: pip install Pillow"}
    except Exception as e:
        return {"error": str(e)}

def set_reminder(text: str, minutes: int = 5):
    """Set a reminder. Saves to reminders file for heartbeat to check."""
    try:
        reminders_file = Path(__file__).parent.parent / "brain" / "reminders.json"
        reminders = []
        if reminders_file.exists():
            reminders = json.loads(reminders_file.read_text())
        
        trigger_time = time.time() + (minutes * 60)
        reminders.append({
            "text": text,
            "trigger_at": trigger_time,
            "created_at": datetime.now().isoformat(),
            "triggered": False
        })
        reminders_file.write_text(json.dumps(reminders, indent=2))
        return {"status": "ok", "message": f"Reminder set: '{text}' in {minutes} minutes"}
    except Exception as e:
        return {"error": str(e)}

def check_reminders():
    """Check for due reminders. Called by heartbeat."""
    try:
        reminders_file = Path(__file__).parent.parent / "brain" / "reminders.json"
        if not reminders_file.exists():
            return {"due": []}
        
        reminders = json.loads(reminders_file.read_text())
        now = time.time()
        due = []
        remaining = []
        
        for r in reminders:
            if not r.get("triggered") and r["trigger_at"] <= now:
                due.append(r["text"])
                r["triggered"] = True
            remaining.append(r)
        
        reminders_file.write_text(json.dumps(remaining, indent=2))
        return {"due": due, "total_active": len([r for r in remaining if not r.get("triggered")])}
    except Exception as e:
        return {"error": str(e)}

def get_system_info():
    """Get basic system information."""
    try:
        import platform
        info = {
            "os": platform.system(),
            "os_version": platform.version(),
            "machine": platform.machine(),
            "python": platform.python_version(),
            "hostname": platform.node(),
        }
        
        # Disk usage
        try:
            import shutil
            total, used, free = shutil.disk_usage("C:\\")
            info["disk_total_gb"] = round(total / (1024**3), 1)
            info["disk_free_gb"] = round(free / (1024**3), 1)
        except:
            pass
        
        return info
    except Exception as e:
        return {"error": str(e)}

tools = [
    {
        "type": "function",
        "function": {
            "name": "take_screenshot",
            "description": "Take a screenshot of the current screen. Returns the file path.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_reminder",
            "description": "Set a reminder. Cyra will notify you when it's due.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Reminder text."},
                    "minutes": {"type": "integer", "description": "Minutes from now. Default 5."}
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_reminders",
            "description": "Check for due reminders. Used by heartbeat system.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_system_info",
            "description": "Get system information: OS, disk space, Python version.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    }
]
