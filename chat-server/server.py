from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3, json, random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ---------- DATABASES ----------
users = sqlite3.connect("users.db", check_same_thread=False)
forums = sqlite3.connect("forums.db", check_same_thread=False)

users.execute("""
CREATE TABLE IF NOT EXISTS users (
    email TEXT PRIMARY KEY,
    role TEXT
)
""")

forums.execute("""
CREATE TABLE IF NOT EXISTS threads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    author TEXT
)
""")

forums.execute("""
CREATE TABLE IF NOT EXISTS replies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id INTEGER,
    author TEXT,
    text TEXT
)
""")

# ---------- ROLES ----------
ROLE_COLORS = {
    "admin": "#ff5555",
    "mod": "#55ffff",
    "user": "#55ff55"
}

def get_role(email):
    row = users.execute("SELECT role FROM users WHERE email=?", (email,)).fetchone()
    return row[0] if row else "user"

# ---------- CHAT ----------
clients = []

@app.websocket("/chat")
async def chat(ws: WebSocket):
    await ws.accept()

    email = f"user{random.randint(1000,9999)}@nax"
    role = get_role(email)
    color = ROLE_COLORS.get(role, "#ffffff")

    client = {"ws": ws, "email": email, "role": role, "color": color}
    clients.append(client)

    try:
        while True:
            text = await ws.receive_text()
            packet = json.dumps({
                "user": email.split("@")[0],
                "role": role.upper(),
                "color": color,
                "text": text
            })
            for c in clients:
                await c["ws"].send_text(packet)
    except:
        clients.remove(client)

# ---------- FORUMS ----------
@app.get("/forums")
def list_threads():
    rows = forums.execute("SELECT id, title, author FROM threads").fetchall()
    return [{"id": i, "title": t, "author": a} for i, t, a in rows]

@app.post("/forums/thread")
def new_thread(data: dict):
    forums.execute(
        "INSERT INTO threads (title, author) VALUES (?,?)",
        (data["title"], data["author"])
    )
    forums.commit()
    return {"ok": True}

@app.get("/forums/{thread_id}")
def get_replies(thread_id: int):
    rows = forums.execute(
        "SELECT author, text FROM replies WHERE thread_id=?",
        (thread_id,)
    ).fetchall()
    return [{"author": a, "text": t} for a, t in rows]

@app.post("/forums/reply")
def reply(data: dict):
    forums.execute(
        "INSERT INTO replies (thread_id, author, text) VALUES (?,?,?)",
        (data["thread_id"], data["author"], data["text"])
    )
    forums.commit()
    return {"ok": True}
