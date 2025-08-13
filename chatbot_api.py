from flask import Flask, request, jsonify
from chatbot import generate_answer

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Movie Chatbot API is running!"

@app.route("/api/chat", methods=["GET", "POST"])
def chat():
    if request.method == "GET":
        return jsonify({"info": "✅ Gửi POST với JSON {'message': '...'} để nhận phản hồi."})
    user_input = request.json.get("message", "")
    reply = generate_answer(user_input)
    return jsonify({"reply": reply})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
