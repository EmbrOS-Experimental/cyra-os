"""
Plugin: file_manager
Read, write, search, and organize local files.
"""
import os
import shutil
from pathlib import Path
from typing import Optional

def list_directory(path: str = "."):
    """List files and folders in a directory."""
    try:
        p = Path(path)
        if not p.exists():
            return {"error": f"Path not found: {path}"}
        items = []
        for item in sorted(p.iterdir()):
            items.append({
                "name": item.name,
                "type": "dir" if item.is_dir() else "file",
                "size": item.stat().st_size if item.is_file() else 0,
                "modified": item.stat().st_mtime
            })
        return {"path": str(p.resolve()), "items": items}
    except Exception as e:
        return {"error": str(e)}

def read_file(path: str, limit: int = 200):
    """Read a text file."""
    try:
        p = Path(path)
        if not p.exists():
            return {"error": f"File not found: {path}"}
        text = p.read_text(encoding="utf-8")
        lines = text.split("\n")
        if len(lines) > limit:
            text = "\n".join(lines[:limit]) + f"\n... ({len(lines)} total lines)"
        return {"path": str(p.resolve()), "content": text, "lines": len(lines)}
    except Exception as e:
        return {"error": str(e)}

def write_file(path: str, content: str):
    """Write content to a file."""
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return {"status": "ok", "path": str(p.resolve()), "bytes": len(content)}
    except Exception as e:
        return {"error": str(e)}

def search_files(pattern: str, path: str = "."):
    """Find files by name pattern (glob)."""
    try:
        p = Path(path)
        matches = list(p.glob(pattern))
        return {"matches": [str(m) for m in matches[:50]]}
    except Exception as e:
        return {"error": str(e)}

def delete_file(path: str):
    """Delete a file."""
    try:
        p = Path(path)
        if not p.exists():
            return {"error": f"File not found: {path}"}
        p.unlink()
        return {"status": "ok", "deleted": str(p.resolve())}
    except Exception as e:
        return {"error": str(e)}

tools = [
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "List files and folders in a directory on the local machine.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Directory path to list. Default: current directory."}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a text file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to read."},
                    "limit": {"type": "integer", "description": "Max lines to return. Default 200."}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file. Creates parent directories if needed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to write."},
                    "content": {"type": "string", "description": "Content to write."}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_files",
            "description": "Find files by name pattern (glob, e.g. '*.py', '**/*.md').",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Glob pattern like '*.py' or '**/*.md'."},
                    "path": {"type": "string", "description": "Base directory to search. Default: current directory."}
                },
                "required": ["pattern"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_file",
            "description": "Delete a file from the local machine.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to delete."}
                },
                "required": ["path"]
            }
        }
    }
]
