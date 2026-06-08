# Cyra-OS Skill Engine v2
# Dynamically loads Python tools from the plugins/ folder.
# Each plugin file should expose a `tools` list and matching function names.

import os
import importlib.util
import json
from pathlib import Path
from typing import Dict, Any, List

SKILLS_DIR = Path(__file__).parent.parent / "skills"
PLUGINS_DIR = Path(__file__).parent.parent / "plugins"


class SkillEngine:
    def __init__(self):
        SKILLS_DIR.mkdir(exist_ok=True)
        PLUGINS_DIR.mkdir(exist_ok=True)
        self.tools: Dict[str, Dict] = {}
        self.load_plugins()

    def load_plugins(self):
        """Dynamically load Python tools from the plugins folder."""
        if not PLUGINS_DIR.exists():
            return

        for f in sorted(PLUGINS_DIR.glob("*.py")):
            if f.name == "__init__.py":
                continue
            try:
                spec = importlib.util.spec_from_file_location(f.stem, f)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                if hasattr(module, "tools"):
                    for tool in module.tools:
                        name = tool["function"]["name"]
                        handler = getattr(module, name, None)
                        if handler:
                            self.tools[name] = {
                                "spec": tool,
                                "handler": handler
                            }
                    print(f"[Skills] Loaded {len(module.tools)} tools from {f.name}")
            except Exception as e:
                print(f"[Skills] Error loading {f.name}: {e}")

        print(f"[Skills] Total tools: {list(self.tools.keys())}")

    def get_tool_specs(self) -> List[Dict[str, Any]]:
        return [t["spec"] for t in self.tools.values()]

    def execute_tool(self, name: str, args: Dict[str, Any]) -> Any:
        if name in self.tools:
            try:
                return self.tools[name]["handler"](**args)
            except Exception as e:
                return {"error": f"Tool '{name}' execution failed: {e}"}
        return f"Tool '{name}' not found."

    def create_skill(self, name: str, procedure: str):
        """Save a new procedural skill as a Markdown file."""
        skill_file = SKILLS_DIR / f"{name.lower().replace(' ', '_')}.md"
        content = f"# Skill: {name}\n\n## Procedure\n{procedure}\n"
        skill_file.write_text(content)
        return f"Skill '{name}' saved to {skill_file}"


skill_engine = SkillEngine()
