# Flask backend voor SentiCare
from flask import Flask, render_template, request, jsonify
import openai
import json
import datetime
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY", "sk-...")

MOOD_FILE = "moods.json"

if not os.path.exists(MOOD_FILE):
    with open(MOOD_FILE, "w") as f:
        json.dump({}, f)

def load_moods():
    with open(MOOD_FILE, "r") as f:
        return json.load(f)

def save_mood(date, mood):
    data = load_moods()
    data[date] = mood
    with open(MOOD_FILE, "w") as f:
        json.dump(data, f)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat")
def chat():
    return render_template("chat.html")

@app.route("/overview")
def overview():
    moods = load_moods()
    return render_template("overview.html", moods=moods)

@app.route("/submit_mood", methods=["POST"])
def submit_mood():
    mood = request.json.get("mood")
    today = datetime.date.today().isoformat()
    save_mood(today, mood)
    return jsonify({"status": "success", "mood_saved": mood})

@app.route("/ask_ai", methods=["POST"])
def ask_ai():
    user_input = request.json.get("message")

    prompt = f"""
    Jij bent een empathische AI-psycholoog. Beantwoord alleen vragen over gevoelens.
    Toon begrip, benoem emoties en stel rustige reflectieve vragen.

    Gebruiker zegt: "{user_input}"

    Reageer als een warme therapeut:
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Je bent een AI-psycholoog."},
                {"role": "user", "content": prompt}
            ]
        )
        ai_message = response["choices"][0]["message"]["content"]
        return jsonify({"reply": ai_message})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
