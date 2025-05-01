from flask import Flask, render_template, request, redirect, session, url_for
from flask_dance.contrib.google import make_google_blueprint, google
from datetime import datetime
import google.generativeai as genai
import os

app = Flask(__name__)
app.secret_key = "uper_secret_key_1234ssssssssssssssssssssssssssssssssssssssss2345"  # 🔐 Use a strong random key!

# === Replace this with your Gemini 2.0 Flash API key ===
genai.configure(api_key="AIzaSyCh0FoS9WD8KYH2POXpFxJg9u0UEUqJO-c")
model = genai.GenerativeModel("gemini-2.0-flash")

# === Google OAuth Setup ===
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Enable HTTP for local testing

blueprint = make_google_blueprint(
    client_id="465923208288-85md66s2fbj3jbslosbmj9726kke6v26.apps.googleusercontent.com",
    client_secret="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",
    redirect_to="google_login_authorized",
    scope=["profile", "email"]
)
app.register_blueprint(blueprint, url_prefix="/login")


@app.route('/')
def index():
    user_info = None
    if google.authorized:
        resp = google.get("/oauth2/v2/userinfo")
        if resp.ok:
            user_info = resp.json()
            session['user_email'] = user_info["email"]
            session['user_name'] = user_info["name"]
            # Admin check
            session['is_admin'] = user_info["email"] == "at41rv@gmail.com"
    return render_template("index.html", user_info=user_info)


@app.route('/login/authorized')
def google_login_authorized():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        return "Failed to fetch user info.", 400
    user_info = resp.json()
    session["user_email"] = user_info["email"]
    session["user_name"] = user_info["name"]
    session["is_admin"] = user_info["email"] == "at41rv@gmail.com"
    return redirect(url_for("index"))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/ask', methods=['POST'])
def ask_question():
    question = request.form.get("question", "").strip()
    if not question:
        return "Please enter a question."

    today = datetime.today().strftime('%Y-%m-%d')
    if session.get("last_asked") != today:
        session["questions_asked"] = 0
        session["last_asked"] = today

    is_admin = session.get("is_admin", False)
    user_logged_in = "user_email" in session
    asked = session.get("questions_asked", 0)

    if not is_admin:
        if user_logged_in and asked >= 20:
            return render_template("limit_reached.html")
        elif not user_logged_in and asked >= 2:
            return render_template("login_required.html")

    try:
        response = model.generate_content(question)
        session["questions_asked"] = asked + 1

        chat = session.get("chat_history", [])
        chat.append({"question": question, "answer": response.text})
        session["chat_history"] = chat

        return redirect(url_for("index"))
    except Exception as e:
        return f"Error calling Gemini API: {str(e)}"


@app.route('/admin')
def admin_page():
    if not session.get("is_admin"):
        return "Unauthorized", 403
    return render_template("admin_page.html")


if __name__ == "__main__":
    app.run(debug=True)
