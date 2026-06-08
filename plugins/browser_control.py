"""
Plugin: browser_control
Screenshot, screen interaction, and browser automation via pyautogui.
"""
import subprocess
import os
import time
from pathlib import Path
from datetime import datetime

def take_screenshot():
    """Take a screenshot and return the file path."""
    try:
        from PIL import ImageGrab
        desktop = Path.home() / "Desktop"
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = desktop / f"cyra_screenshot_{ts}.png"
        img = ImageGrab.grab()
        img.save(str(out_path))
        return {"status": "ok", "path": str(out_path), "message": f"Screenshot saved to {out_path.name}"}
    except ImportError:
        return {"error": "Pillow not installed. Run: pip install Pillow"}
    except Exception as e:
        return {"error": str(e)}

def click_screen(x: int, y: int):
    """Click at screen coordinates (x, y)."""
    try:
        import pyautogui
        pyautogui.click(x, y)
        return {"status": "ok", "action": "click", "x": x, "y": y}
    except ImportError:
        return {"error": "pyautogui not installed. Run: pip install pyautogui"}
    except Exception as e:
        return {"error": str(e)}

def type_text(text: int):
    """Type text at current cursor position."""
    try:
        import pyautogui
        pyautogui.typewrite(str(text), interval=0.02)
        return {"status": "ok", "action": "type", "text": str(text)[:50]}
    except ImportError:
        return {"error": "pyautogui not installed"}
    except Exception as e:
        return {"error": str(e)}

def press_key(key: str):
    """Press a keyboard key (e.g. 'enter', 'tab', 'escape', 'ctrl+s')."""
    try:
        import pyautogui
        keys = [k.strip() for k in key.split('+')]
        pyautogui.hotkey(*keys)
        return {"status": "ok", "action": "hotkey", "keys": keys}
    except ImportError:
        return {"error": "pyautogui not installed"}
    except Exception as e:
        return {"error": str(e)}

def get_screen_size():
    """Get screen resolution."""
    try:
        import pyautogui
        w, h = pyautogui.size()
        return {"width": w, "height": h}
    except:
        return {"error": "Cannot determine screen size"}

def find_on_screen(image_path: str):
    """Find an image on screen. Returns coordinates or None."""
    try:
        import pyautogui
        p = Path(image_path)
        if not p.exists():
            return {"error": f"Image not found: {image_path}"}
        location = pyautogui.locateOnScreen(str(p), confidence=0.8)
        if location:
            center = pyautogui.center(location)
            return {"found": True, "x": center.x, "y": center.y, "box": [location.left, location.top, location.width, location.height]}
        return {"found": False}
    except ImportError:
        return {"error": "pyautogui not installed"}
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
            "name": "click_screen",
            "description": "Click at specific screen coordinates.",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {"type": "integer", "description": "X coordinate."},
                    "y": {"type": "integer", "description": "Y coordinate."}
                },
                "required": ["x", "y"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "type_text",
            "description": "Type text at the current cursor position.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to type."}
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "press_key",
            "description": "Press a keyboard key or hotkey combo (e.g. 'enter', 'ctrl+s', 'alt+tab').",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "Key or combo like 'enter', 'ctrl+s'."}
                },
                "required": ["key"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_screen_size",
            "description": "Get screen resolution (width x height).",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_on_screen",
            "description": "Find an image on screen. Provide path to reference image.",
            "parameters": {
                "type": "object",
                "properties": {
                    "image_path": {"type": "string", "description": "Path to reference image file."}
                },
                "required": ["image_path"]
            }
        }
    }
]
