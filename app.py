from flask import Flask, render_template, request, redirect, session, url_for
from datetime import datetime
import google.generativeai as genai
import os

app = Flask(__name__)
app.secret_key = "uper_secret_key_1234ssssssssssssssssssssssssssssssssssssssss2345"

# === Configure Gemini API ===
genai.configure(api_key="AIzaSyBkU7C6lEDhQ_gqE-730xCWTXjKTuN-qPI")
model = genai.GenerativeModel("gemini-2.0-flash")

# === MAIN AI CHAT PAGE on `/` ===
@app.route('/')
def index():
    return render_template("index.html")

# === Handle question submission ===
@app.route('/ask', methods=['POST'])
def ask_question():
    question = request.form.get("question", "").strip()
    if not question:
        return "Please enter a question."

    try:
        # Call Gemini API
        response = model.generate_content(question)

        # Store chat history in session
        chat = session.get("chat_history", [])
        chat.append({"question": question, "answer": response.text})
        session["chat_history"] = chat

        return redirect(url_for("index"))
    except Exception as e:
        return f"Error calling Gemini API: {str(e)}"

# === Run the app ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
