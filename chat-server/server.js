import express from "express";
import { WebSocketServer } from "ws";

const app = express();
const server = app.listen(process.env.PORT || 3000);
const wss = new WebSocketServer({ server });

app.get("/", (_, res) => res.send("NAX CHAT SERVER RUNNING"));

function broadcast(data) {
  const msg = JSON.stringify(data);
  wss.clients.forEach(c => c.readyState === 1 && c.send(msg));
}

wss.on("connection", ws => {
  ws.name = "Guest";

  ws.on("message", raw => {
    const data = JSON.parse(raw);
    if (data.type === "join") ws.name = data.name;
    if (data.type === "chat")
      broadcast({ name: ws.name, text: data.text });
  });
});
