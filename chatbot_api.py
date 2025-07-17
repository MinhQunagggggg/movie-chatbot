from flask import Flask, request, jsonify
from chatbot import generate_answer

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Movie Chatbot API is running!"

@app.route("/api/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")
    reply = generate_answer(user_input)
    return jsonify({"reply": reply})



# app.py (Flask)
from datetime import datetime, timezone
try:
    from zoneinfo import ZoneInfo  # Py3.9+
except ImportError:
    from pytz import timezone as pytz_timezone
    ZoneInfo = lambda x: pytz_timezone(x)

@app.get("/debug/time")
def debug_time():
    utc_now = datetime.now(timezone.utc)
    vn_now = utc_now.astimezone(ZoneInfo("Asia/Ho_Chi_Minh"))
    server_local = datetime.now()  # theo system tz (thường = UTC trong container)
    return {
        "server_local_str": server_local.isoformat(),
        "server_utc_str": utc_now.isoformat(),
        "vn_time_str": vn_now.isoformat(),
    }


if __name__ == "__main__":
    app.run(debug=True, port=5000)
