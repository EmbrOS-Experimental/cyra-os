"""
Plugin: security_sandbox
Tool permission levels and confirmation for dangerous operations.
"""
import json
from pathlib import Path
from datetime import datetime

PERMISSIONS_FILE = Path(__file__).parent.parent / "brain" / "permissions.json"

# Permission levels: "allow", "confirm", "deny"
DEFAULT_PERMISSIONS = {
    "run_command": "confirm",
    "delete_file": "confirm",
    "write_file": "allow",
    "read_file": "allow",
    "list_directory": "allow",
    "search_files": "allow",
    "web_search": "allow",
    "fetch_url": "allow",
    "take_screenshot": "allow",
    "click_screen": "confirm",
    "type_text": "confirm",
    "press_key": "confirm",
    "watch_directory": "allow",
    "check_watches": "allow",
    "check_disk_space": "allow",
    "get_uptime": "allow",
    "set_reminder": "allow",
    "check_reminders": "allow",
    "get_system_info": "allow",
    "find_on_screen": "allow",
}

def _load_permissions():
    if PERMISSIONS_FILE.exists():
        return json.loads(PERMISSIONS_FILE.read_text())
    return DEFAULT_PERMISSIONS.copy()

def _save_permissions(perms):
    PERMISSIONS_FILE.write_text(json.dumps(perms, indent=2))

def set_permission(tool_name: str, level: str):
    """Set permission level for a tool: 'allow', 'confirm', or 'deny'."""
    if level not in ("allow", "confirm", "deny"):
        return {"error": "Level must be 'allow', 'confirm', or 'deny'"}
    perms = _load_permissions()
    perms[tool_name] = level
    _save_permissions(perms)
    return {"status": "ok", "tool": tool_name, "level": level}

def check_permission(tool_name: str):
    """Check permission level for a tool."""
    perms = _load_permissions()
    level = perms.get(tool_name, "confirm")
    return {"tool": tool_name, "level": level}

def list_permissions():
    """List all tool permissions."""
    perms = _load_permissions()
    return {"permissions": perms}

def reset_permissions():
    """Reset all permissions to defaults."""
    _save_permissions(DEFAULT_PERMISSIONS.copy())
    return {"status": "ok", "message": "Permissions reset to defaults"}

tools = [
    {
        "type": "function",
        "function": {
            "name": "set_permission",
            "description": "Set permission level for a tool: 'allow' (auto), 'confirm' (ask first), or 'deny' (blocked).",
            "parameters": {
                "type": "object",
                "properties": {
                    "tool_name": {"type": "string", "description": "Tool name."},
                    "level": {"type": "string", "description": "'allow', 'confirm', or 'deny'."}
                },
                "required": ["tool_name", "level"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_permission",
            "description": "Check the permission level for a tool.",
            "parameters": {
                "type": "object",
                "properties": {
                    "tool_name": {"type": "string", "description": "Tool name to check."}
                },
                "required": ["tool_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_permissions",
            "description": "List all tool permission levels.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "reset_permissions",
            "description": "Reset all permissions to defaults.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    }
]
