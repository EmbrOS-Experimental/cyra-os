"""
Cyra-OS Memory System v2
SQLite + FTS5 + sqlite-vec semantic search, with memory reflection.
"""
import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime
import sqlite_vec
from sentence_transformers import SentenceTransformer

BRAIN_DIR = Path(__file__).parent.parent / "brain"
DB_PATH = BRAIN_DIR / "cyra_memory.db"


class CyraMemory:
    def __init__(self):
        BRAIN_DIR.mkdir(exist_ok=True)
        self.conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        self.conn.enable_load_extension(True)
        sqlite_vec.load(self.conn)
        self._init_db()
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')

    def _init_db(self):
        cur = self.conn.cursor()
        cur.execute("CREATE VIRTUAL TABLE IF NOT EXISTS episodic_history USING fts5(content, session_id, timestamp)")
        cur.execute("CREATE VIRTUAL TABLE IF NOT EXISTS semantic_memory USING vec0(embedding float[384])")
        cur.execute("CREATE TABLE IF NOT EXISTS semantic_metadata (id INTEGER PRIMARY KEY, content TEXT, timestamp TEXT)")
        # Chat history for conversation persistence
        cur.execute("CREATE TABLE IF NOT EXISTS chat_history (id INTEGER PRIMARY KEY, role TEXT, content TEXT, timestamp TEXT, session_id TEXT)")
        self.conn.commit()

    def add_episode(self, content: str, session_id: str = "default"):
        ts = datetime.now().isoformat()
        cur = self.conn.cursor()
        cur.execute("INSERT INTO episodic_history(content, session_id, timestamp) VALUES (?, ?, ?)",
                    (content, session_id, ts))
        self.conn.commit()

    def add_semantic(self, content: str):
        ts = datetime.now().isoformat()
        embedding = self.encoder.encode(content).tolist()
        cur = self.conn.cursor()
        cur.execute("INSERT INTO semantic_metadata(content, timestamp) VALUES (?, ?)", (content, ts))
        row_id = cur.lastrowid
        cur.execute("INSERT INTO semantic_memory(rowid, embedding) VALUES (?, ?)",
                    (row_id, json.dumps(embedding)))
        self.conn.commit()

    def add_chat_message(self, role: str, content: str, session_id: str = "default"):
        """Persist chat messages for conversation history."""
        ts = datetime.now().isoformat()
        cur = self.conn.cursor()
        cur.execute("INSERT INTO chat_history(role, content, timestamp, session_id) VALUES (?, ?, ?, ?)",
                    (role, content, ts, session_id))
        self.conn.commit()

    def get_chat_history(self, session_id: str = "default", limit: int = 50):
        """Get recent chat history for a session."""
        cur = self.conn.cursor()
        cur.execute("SELECT role, content, timestamp FROM chat_history WHERE session_id = ? ORDER BY id DESC LIMIT ?",
                    (session_id, limit))
        rows = cur.fetchall()
        return [{"role": r[0], "content": r[1], "timestamp": r[2]} for r in reversed(rows)]

    def search_chat_history(self, query: str, limit: int = 10):
        """Search chat history by keyword."""
        cur = self.conn.cursor()
        cur.execute("SELECT role, content, timestamp FROM chat_history WHERE content LIKE ? ORDER BY id DESC LIMIT ?",
                    (f"%{query}%", limit))
        return cur.fetchall()

    def search_episodic(self, query: str, limit=5):
        cur = self.conn.cursor()
        cur.execute("SELECT content, timestamp FROM episodic_history WHERE episodic_history MATCH ? ORDER BY rank LIMIT ?",
                    (query, limit))
        return cur.fetchall()

    def search_semantic(self, query: str, limit=5):
        try:
            embedding = self.encoder.encode(query).tolist()
            cur = self.conn.cursor()
            cur.execute("""
                SELECT m.content, m.timestamp, v.distance
                FROM semantic_memory v
                JOIN semantic_metadata m ON v.rowid = m.id
                WHERE embedding MATCH ? AND k = ?
                ORDER BY distance
            """, (json.dumps(embedding), limit))
            return cur.fetchall()
        except Exception as e:
            print(f"[Memory] Semantic search error: {e}")
            return []

    def get_recent_episodes(self, limit=20):
        cur = self.conn.cursor()
        cur.execute("SELECT content, timestamp FROM episodic_history ORDER BY rowid DESC LIMIT ?", (limit,))
        return cur.fetchall()

    def reflect_memories(self):
        """
        Memory reflection: review recent episodes, extract patterns,
        consolidate into semantic memory.
        """
        recent = self.get_recent_episodes(50)
        if len(recent) < 5:
            return {"status": "skipped", "reason": "Not enough episodes to reflect"}

        # Extract unique insights
        consolidated = []
        seen_content = set()
        for content, ts in recent:
            # Deduplicate similar content
            is_dup = False
            for seen in seen_content:
                # Simple overlap check
                words = set(content.lower().split())
                seen_words = set(seen.lower().split())
                if len(words & seen_words) > len(words) * 0.7:
                    is_dup = True
                    break
            if not is_dup and len(content) > 20:
                consolidated.append(content)
                seen_content.add(content)

        # Store consolidated memories
        for item in consolidated[:10]:
            self.add_semantic(item)

        return {"status": "ok", "consolidated": len(consolidated), "total_reviewed": len(recent)}

    def get_user_profile(self):
        user_file = BRAIN_DIR / "USER.md"
        if user_file.exists():
            return user_file.read_text(encoding="utf-8")
        return "No user profile found."

    def get_cyra_soul(self):
        soul_file = BRAIN_DIR / "CYRA.md"
        if soul_file.exists():
            return soul_file.read_text(encoding="utf-8")
        return "I am Cyra, your autonomous AI entity."


memory = CyraMemory()
