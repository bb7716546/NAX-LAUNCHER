from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import sqlite3, json, random

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

db = sqlite3.connect("data.db", check_same_thread=False)

db.execute("CREATE TABLE IF NOT EXISTS users (name TEXT PRIMARY KEY, role TEXT)")
db.execute("CREATE TABLE IF NOT EXISTS threads (id INTEGER PRIMARY KEY, title TEXT, author TEXT)")
db.commit()

ROLE_COLORS = {"admin":"#ff5555","mod":"#55ffff","user":"#55ff55"}

@app.websocket("/chat")
async def chat(ws: WebSocket):
    await ws.accept()
    name = f"NAX{random.randint(1000,9999)}"
    role = "user"
    color = ROLE_COLORS[role]

    while True:
        text = await ws.receive_text()

        if text.startswith("/"):
            cmd = text.split()
            if cmd[0] == "/role" and len(cmd) == 3:
                db.execute("INSERT OR REPLACE INTO users VALUES (?,?)",(cmd[1],cmd[2]))
                db.commit()
                continue

        msg = json.dumps({"user":name,"role":role,"color":color,"text":text})
        await ws.send_text(msg)

@app.get("/forums")
def forums():
    rows = db.execute("SELECT title, author FROM threads").fetchall()
    return [{"title":t,"author":a} for t,a in rows]

@app.post("/forums/thread")
def new_thread(data:dict):
    db.execute("INSERT INTO threads (title,author) VALUES (?,?)",(data["title"],"Guest"))
    db.commit()
    return {"ok":True}

@app.post("/admin/role")
def role(data:dict):
    db.execute("INSERT OR REPLACE INTO users VALUES (?,?)",(data["user"],data["role"]))
    db.commit()
    return {"ok":True}
