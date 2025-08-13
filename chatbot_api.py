from flask import Flask, request, jsonify
from chatbot import generate_answer

app = Flask(__name__)

@app.get("/")
def home():
    return "✅ Movie Chatbot API is running!"

@app.post("/api/chat")
def chat():
    data = request.get_json(silent=True) or {}
    msg = (data.get("message") or "").strip()
    return jsonify({"reply": generate_answer(msg) if msg else "Thiếu message"})
