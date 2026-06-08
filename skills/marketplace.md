# Skill Marketplace

Browse and install community skills for Cyra-OS.

## Available Skills

### Built-in
- **file_manager** — List, read, write, search, delete files
- **web_tools** — Web search and URL fetching
- **system_tools** — Screenshot, reminders, system info
- **browser_control** — Screen interaction, click, type, find images
- **proactive_monitor** — File watching, disk space, uptime
- **romanian** — Romanian language support
- **security_sandbox** — Tool permission levels

### Installing Custom Skills
1. Create a Python file in `plugins/` with `tools` list and handler functions
2. Restart Cyra-OS or call `skill_engine.load_plugins()`
3. Skills are auto-discovered on startup

### Skill File Template
```python
# plugins/my_skill.py
def my_tool(param: str):
    """Description of what this tool does."""
    return {"result": "Hello " + param}

tools = [
    {
        "type": "function",
        "function": {
            "name": "my_tool",
            "description": "What this tool does.",
            "parameters": {
                "type": "object",
                "properties": {
                    "param": {"type": "string", "description": "A parameter."}
                },
                "required": ["param"]
            }
        }
    }
]
```
