from flask import Flask, request, redirect, session, url_for, render_template_string, send_file
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = "uper_secret_key_1234ssssssssssssssssssssssssssssssssssssssss2345"

# Configure Gemini API
genai.configure(api_key="AIzaSyBkU7C6lEDhQ_gqE-730xCWTXjKTuN-qPI")
model = genai.GenerativeModel("gemini-2.0-flash")

# Load index.html from root and render with chat history
@app.route('/')
def index():
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()
    return render_template_string(html, session=session)

# Serve background image from root
@app.route('/bgfinal.jpeg')
def serve_bg():
    return send_file("bgfinal.jpeg", mimetype='image/jpeg')

# Process user question
@app.route('/ask', methods=['POST'])
def ask_question():
    question = request.form.get("question", "").strip()
    if not question:
        return "Please enter a question."

    try:
        response = model.generate_content(question)
        chat = session.get("chat_history", [])
        chat.append({"question": question, "answer": response.text})
        session["chat_history"] = chat
        return redirect(url_for("index"))
    except Exception as e:
        return f"Error calling Gemini API: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)
