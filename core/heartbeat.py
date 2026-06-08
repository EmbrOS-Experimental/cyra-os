"""
Cyra-OS Heartbeat System
Wakes up periodically, checks HEARTBEAT.md for instructions,
executes tasks, and streams results.
"""
import asyncio
import json
import os
import time
from pathlib import Path
from datetime import datetime
from typing import Callable, Optional

HEARTBEAT_INTERVAL_DEFAULT = 300  # 5 minutes


class HeartbeatSystem:
    def __init__(self, agent=None, stream_log_fn=None):
        self.agent = agent
        self.stream_log = stream_log_fn  # callback(text, type, metadata)
        self.interval = HEARTBEAT_INTERVAL_DEFAULT
        self.running = False
        self._task: Optional[asyncio.Task] = None
        self.heartbeat_file = Path(__file__).parent.parent / "brain" / "HEARTBEAT.md"
        self._last_run = 0

    def start(self):
        if self.running:
            return
        self.running = True
        self._task = asyncio.create_task(self._loop())
        if self.stream_log:
            self.stream_log("Heartbeat system started.", "system")

    def stop(self):
        self.running = False
        if self._task:
            self._task.cancel()
            self._task = None

    def set_interval(self, seconds: int):
        self.interval = max(30, seconds)  # minimum 30s

    async def _loop(self):
        while self.running:
            try:
                await asyncio.sleep(self.interval)
                await self._run_heartbeat()
            except asyncio.CancelledError:
                break
            except Exception as e:
                if self.stream_log:
                    self.stream_log(f"Heartbeat error: {e}", "error")

    async def _run_heartbeat(self):
        if not self.agent or not self.stream_log:
            return

        now = datetime.now().strftime("%H:%M:%S")
        self.stream_log(f"Heartbeat triggered at {now}", "system")

        # Read HEARTBEAT.md instructions
        instructions = ""
        if self.heartbeat_file.exists():
            instructions = self.heartbeat_file.read_text(encoding="utf-8")

        if not instructions.strip():
            self.stream_log("No HEARTBEAT.md instructions found.", "system")
            return

        # Build heartbeat prompt
        system_prompt = f"""You are Cyra, an autonomous AI agent. You are running a heartbeat check.
Follow the instructions below. Be concise. Report what you found or did.

Heartbeat Instructions:
{instructions}
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Run the heartbeat check now. Report briefly."}
        ]

        try:
            response = await self.agent.chat(messages)
            if isinstance(response, dict) and "error" in response:
                self.stream_log(f"Heartbeat agent error: {response['error']}", "error")
                return

            if hasattr(response, "choices") and response.choices:
                content = response.choices[0].message.content
                self.stream_log(f"Heartbeat: {content}", "system")
        except Exception as e:
            self.stream_log(f"Heartbeat execution error: {e}", "error")

    async def trigger_now(self):
        """Manual trigger from API."""
        await self._run_heartbeat()


heartbeat = HeartbeatSystem()
