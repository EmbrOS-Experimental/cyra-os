"""
Plugin: proactive_monitor
File watching, email checking hints, and system monitoring.
"""
import os
import json
import time
from pathlib import Path
from datetime import datetime

WATCH_FILE = Path(__file__).parent.parent / "brain" / "watches.json"

def watch_directory(path: str = ".", pattern: str = "*"):
    """Add a directory to watch for changes."""
    try:
        p = Path(path)
        if not p.exists():
            return {"error": f"Path not found: {path}"}

        watches = []
        if WATCH_FILE.exists():
            watches = json.loads(WATCH_FILE.read_text())

        # Snapshot current state
        files = {}
        for f in p.glob(pattern):
            if f.is_file():
                files[str(f)] = f.stat().st_mtime

        watches.append({
            "path": str(p.resolve()),
            "pattern": pattern,
            "files": files,
            "added_at": datetime.now().isoformat()
        })
        WATCH_FILE.write_text(json.dumps(watches, indent=2))
        return {"status": "ok", "watching": len(files), "path": str(p.resolve())}
    except Exception as e:
        return {"error": str(e)}

def check_watches():
    """Check all watched directories for changes. Returns list of changes."""
    try:
        if not WATCH_FILE.exists():
            return {"changes": [], "message": "No watches configured"}

        watches = json.loads(WATCH_FILE.read_text())
        all_changes = []

        for watch in watches:
            p = Path(watch["path"])
            if not p.exists():
                continue

            old_files = watch.get("files", {})
            current_files = {}
            for f in p.glob(watch.get("pattern", "*")):
                if f.is_file():
                    current_files[str(f)] = f.stat().st_mtime

            # Find new files
            new_files = set(current_files.keys()) - set(old_files.keys())
            # Find modified files
            modified = []
            for f_path in set(current_files.keys()) & set(old_files.keys()):
                if current_files[f_path] != old_files[f_path]:
                    modified.append(f_path)

            if new_files or modified:
                changes = {
                    "path": watch["path"],
                    "new": list(new_files),
                    "modified": modified
                }
                all_changes.append(changes)

            # Update snapshot
            watch["files"] = current_files

        WATCH_FILE.write_text(json.dumps(watches, indent=2))
        return {"changes": all_changes}
    except Exception as e:
        return {"error": str(e)}

def get_uptime():
    """Get system uptime."""
    try:
        import platform
        if platform.system() == "Windows":
            result = subprocess.run(
                ["powershell", "-Command", "(Get-Date) - (Get-CimInstance Win32_OperatingSystem).LastBootUpTime | Select-Object -ExpandProperty TotalMinutes"],
                capture_output=True, text=True, timeout=10
            )
            minutes = float(result.stdout.strip())
            hours = int(minutes // 60)
            mins = int(minutes % 60)
            return {"uptime_hours": hours, "uptime_minutes": mins, "total_minutes": int(minutes)}
    except:
        pass
    return {"error": "Cannot determine uptime"}

def check_disk_space():
    """Check disk space on C: drive."""
    try:
        import shutil
        total, used, free = shutil.disk_usage("C:\\")
        return {
            "total_gb": round(total / (1024**3), 1),
            "used_gb": round(used / (1024**3), 1),
            "free_gb": round(free / (1024**3), 1),
            "percent_used": round(used / total * 100, 1)
        }
    except Exception as e:
        return {"error": str(e)}

import subprocess

tools = [
    {
        "type": "function",
        "function": {
            "name": "watch_directory",
            "description": "Watch a directory for file changes (new/modified files).",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory path to watch."},
                    "pattern": {"type": "string", "description": "Glob pattern like '*.py'. Default: '*'."}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_watches",
            "description": "Check all watched directories for changes since last check.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_disk_space",
            "description": "Check disk space on C: drive.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_uptime",
            "description": "Get system uptime in hours and minutes.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    }
]
