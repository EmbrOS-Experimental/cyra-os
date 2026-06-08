import subprocess
import os

def run_command(command: str):
    """Execute a system command in the local shell."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode
        }
    except Exception as e:
        return {"error": str(e)}

tools = [
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Execute a shell command on the local Windows machine.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The command to run (e.g. 'dir', 'ipconfig')"
                    }
                },
                "required": ["command"]
            }
        }
    }
]
