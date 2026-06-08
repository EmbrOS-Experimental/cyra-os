"""
Cyra-OS v2 — Main Server
FastAPI backend with streaming chat, heartbeat, expanded plugins, multi-model fallback.
"""
import asyncio
import json
import os
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
import uvicorn
from dotenv import load_dotenv

load_dotenv()

from core.agent import CyraAgent
from core.skills import skill_engine
from brain.memory import memory
from core.vision import vision
from core.voice import voice
from core.heartbeat import HeartbeatSystem

# ── Activity Stream ────────────────────────────────────────────────────────
class ActivityStream:
    def __init__(self):
        self.queues: list = []

    def log(self, text: str, type: str = "info", metadata: Dict = None):
        msg = json.dumps({
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "text": text,
            "type": type,
            "metadata": metadata or {}
        })
        for q in self.queues:
            try:
                q.put_nowait(msg)
            except:
                pass

    async def subscribe(self):
        q = asyncio.Queue()
        self.queues.append(q)
        try:
            while True:
                msg = await q.get()
                yield f"data: {msg}\n\n"
        finally:
            if q in self.queues:
                self.queues.remove(q)


stream = ActivityStream()
agent = CyraAgent()


def stream_log(text: str, type: str = "info", metadata: Dict = None):
    """Helper for heartbeat to use stream.log"""
    stream.log(text, type, metadata)


heartbeat = HeartbeatSystem(agent=agent, stream_log_fn=stream_log)

BRAIN_DIR = Path(__file__).parent
UI_DIR = BRAIN_DIR / "ui"

# ── Voice input handler ────────────────────────────────────────────────────
_loop: asyncio.AbstractEventLoop = None


def handle_voice_input(text: str):
    stream.log(f"Voice recognized: {text}", "hearing")

    if voice.wake_word_mode:
        if "cyra" not in text.lower():
            return
        text = text.lower().replace("cyra", "").strip()
        if not text:
            voice.speak_sync("Yes, I am listening.")
            return

    if _loop:
        asyncio.run_coroutine_threadsafe(process_chat(text), _loop)


# ── Lifespan ───────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    global _loop
    _loop = asyncio.get_running_loop()
    stream.log("Cyra-OS v2 starting...", "system")

    # Start vision
    if vision.start():
        stream.log("Vision system initialized.", "system")
    else:
        stream.log(f"Vision unavailable: {vision.error}", "error")

    # Start heartbeat
    heartbeat.start()
    stream.log("Heartbeat system active.", "system")

    yield

    heartbeat.stop()
    vision.running = False
    voice.stop_listening()
    stream.log("Cyra-OS v2 stopped.", "system")


app = FastAPI(title="Cyra-OS v2", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ── Routes ─────────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return HTMLResponse((UI_DIR / "index.html").read_text(encoding="utf-8"))


@app.get("/stream")
async def stream_activity():
    return StreamingResponse(stream.subscribe(), media_type="text/event-stream")


@app.get("/webcam")
async def webcam():
    frame = vision.get_frame_jpeg()
    return JSONResponse({"frame": frame, "status": vision.get_status()})


@app.post("/chat")
async def chat(data: dict):
    """Non-streaming chat (backward compat)."""
    msg = data.get("message", "")
    if not msg:
        return {"status": "error", "message": "Empty message"}
    result = await process_chat(msg)
    return result


@app.post("/chat/stream")
async def chat_stream(data: dict):
    """Streaming chat via SSE."""
    msg = data.get("message", "")
    if not msg:
        return {"status": "error", "message": "Empty message"}

    async def generate():
        full_response = ""
        try:
            relevant_memories = memory.search_semantic(msg, limit=3)
            memory_context = "\n".join([m[0] for m in relevant_memories])

            system_prompt = f"""{memory.get_cyra_soul()}

User Profile: {memory.get_user_profile()}

Relevant Memories:
{memory_context}"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": msg}
            ]

            tools = skill_engine.get_tool_specs()
            stream.log(f"Thinking with model: {agent.model}", "thinking")

            # Try streaming first
            try:
                async for item in agent.chat_stream(messages, tools=tools):
                    if "error" in item:
                        stream.log(f"Agent Error: {item['error']}", "error")
                        yield f"data: {json.dumps({'error': item['error']})}\n\n"
                        return
                    if "chunk" in item:
                        chunk = item["chunk"]
                        if hasattr(chunk, "choices") and chunk.choices:
                            delta = chunk.choices[0].delta
                            if hasattr(delta, "content") and delta.content:
                                full_response += delta.content
                                yield f"data: {json.dumps({'token': delta.content})}\n\n"
            except Exception as e:
                # Fallback to non-streaming
                stream.log(f"Streaming failed, falling back: {e}", "system")
                response = await agent.chat(messages, tools=tools)
                if isinstance(response, dict) and "error" in response:
                    yield f"data: {json.dumps({'error': response['error']})}\n\n"
                    return
                choice = response.choices[0].message
                full_response = choice.content or ""
                yield f"data: {json.dumps({'token': full_response})}\n\n"

            # Handle tool calls from non-streaming fallback
            if not full_response:
                response = await agent.chat(messages, tools=tools)
                if isinstance(response, dict) and "error" in response:
                    yield f"data: {json.dumps({'error': response['error']})}\n\n"
                    return
                choice = response.choices[0].message
                if hasattr(choice, "tool_calls") and choice.tool_calls:
                    for tc in choice.tool_calls:
                        func_name = tc.function.name
                        func_args = json.loads(tc.function.arguments)
                        stream.log(f"Calling tool: {func_name}", "tool", metadata=func_args)
                        result = skill_engine.execute_tool(func_name, func_args)
                        stream.log(f"Tool Result: {str(result)[:100]}", "tool_output")
                        messages.append(choice)
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "name": func_name,
                            "content": json.dumps(result)
                        })
                    response = await agent.chat(messages)
                    choice = response.choices[0].message
                full_response = choice.content or ""

            # Speak
            if full_response:
                stream.log(f"Cyra: {full_response[:100]}...", "speaking")
                voice.speak_sync(full_response)

            # Save to memory
            memory.add_episode(f"User: {msg}\nCyra: {full_response}", session_id="session_0")
            memory.add_chat_message("user", msg)
            memory.add_chat_message("assistant", full_response)

            yield f"data: {json.dumps({'done': True, 'full': full_response})}\n\n"

        except Exception as e:
            stream.log(f"Chat error: {e}", "error")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


async def process_chat(msg: str):
    """Non-streaming chat processing."""
    stream.log(f"Processing: {msg}", "hearing")

    relevant_memories = memory.search_semantic(msg, limit=3)
    memory_context = "\n".join([m[0] for m in relevant_memories])

    system_prompt = f"""{memory.get_cyra_soul()}

User Profile: {memory.get_user_profile()}

Relevant Memories:
{memory_context}"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": msg}
    ]

    stream.log(f"Thinking with model: {agent.model}", "thinking")
    tools = skill_engine.get_tool_specs()
    response = await agent.chat(messages, tools=tools)

    if isinstance(response, dict) and "error" in response:
        err = response.get("error", "Unknown error")
        stream.log(f"Agent Error: {err}", "error")
        return {"status": "error", "message": err}

    choice = response.choices[0].message

    if hasattr(choice, "tool_calls") and choice.tool_calls:
        for tc in choice.tool_calls:
            func_name = tc.function.name
            func_args = json.loads(tc.function.arguments)
            stream.log(f"Calling tool: {func_name}", "tool", metadata=func_args)
            result = skill_engine.execute_tool(func_name, func_args)
            stream.log(f"Tool Result: {str(result)[:100]}", "tool_output")
            messages.append(choice)
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "name": func_name,
                "content": json.dumps(result)
            })
        response = await agent.chat(messages)
        choice = response.choices[0].message

    final_text = choice.content or ""
    stream.log(f"Cyra: {final_text[:100]}...", "speaking")

    voice.speak_sync(final_text)
    memory.add_episode(f"User: {msg}\nCyra: {final_text}", session_id="session_0")
    memory.add_chat_message("user", msg)
    memory.add_chat_message("assistant", final_text)

    return {"status": "ok", "response": final_text}


@app.get("/state")
async def get_state():
    masked_key = ""
    if agent.api_key:
        masked_key = agent.api_key[:8] + "..." + agent.api_key[-4:] if len(agent.api_key) > 12 else "****"

    return {
        "model": agent.model,
        "api_key": masked_key,
        "skills": list(skill_engine.tools.keys()),
        "uptime": "Active",
        "audio": voice.get_status(),
        "vision": vision.get_status(),
        "heartbeat": {
            "running": heartbeat.running,
            "interval": heartbeat.interval
        },
        "available_models": [
            {"name": "Claude 3.5 Sonnet", "id": "openrouter/anthropic/claude-3.5-sonnet"},
            {"name": "Llama 3.3 70B (Free)", "id": "openrouter/meta-llama/llama-3.3-70b-instruct:free"},
            {"name": "DeepSeek V3 (Free)", "id": "openrouter/deepseek/deepseek-chat:free"},
            {"name": "Gemini 2.0 Flash (Free)", "id": "openrouter/google/gemini-2.0-flash-exp:free"},
            {"name": "Qwen 2.5 72B (Free)", "id": "openrouter/qwen/qwen-2.5-72b-instruct:free"},
        ]
    }


@app.post("/settings/config")
async def update_config(data: dict):
    new_model = data.get("model")
    new_key = data.get("api_key")

    if new_model:
        agent.switch_model(new_model)
        stream.log(f"Switched model to: {new_model}", "system")

    if new_key:
        agent.api_key = new_key
        os.environ["OPENROUTER_API_KEY"] = new_key
        env_path = Path(".env")
        env_path.write_text(f"OPENROUTER_API_KEY={new_key}\n")
        stream.log("API Key updated.", "system")

    return {"status": "ok", "model": agent.model}


@app.post("/settings/audio")
async def toggle_audio(data: dict):
    action = data.get("action")
    if action == "start_listening":
        voice.start_listening(handle_voice_input)
    elif action == "stop_listening":
        voice.stop_listening()
    elif action == "toggle_wake_word":
        voice.wake_word_mode = not voice.wake_word_mode

    return {"status": "ok", **voice.get_status()}


@app.post("/settings/heartbeat")
async def update_heartbeat(data: dict):
    interval = data.get("interval")
    if interval:
        heartbeat.set_interval(int(interval))
    action = data.get("action")
    if action == "trigger_now":
        await heartbeat.trigger_now()
    elif action == "stop":
        heartbeat.stop()
    elif action == "start":
        heartbeat.start()

    return {"status": "ok", "running": heartbeat.running, "interval": heartbeat.interval}


@app.post("/memory/reflect")
async def trigger_reflection():
    """Manually trigger memory reflection."""
    result = memory.reflect_memories()
    stream.log(f"Memory reflection: {result}", "system")
    return result


@app.get("/history")
async def get_history(session_id: str = "default", limit: int = 50):
    """Get chat history."""
    history = memory.get_chat_history(session_id, limit)
    return {"status": "ok", "history": history}


if __name__ == "__main__":
    stream.log("Cyra-OS v2 core starting...", "system")
    uvicorn.run(app, host="0.0.0.0", port=8200)
