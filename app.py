from flask import Flask, render_template, request, jsonify, redirect, session, url_for
import json
import os
from dotenv import load_dotenv
from flask_cors import CORS
from rapidfuzz import fuzz, process

# Ortam değişkenlerini yükle
load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = "gizliAnahtar123"  # Session için gerekli

# Ana sayfa
@app.route("/")
def home():
    return render_template("index.html")

# Sohbet endpoint
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message").lower().strip()

    # Her istekte data.json'u oku
    try:
        with open("data.json", "r", encoding="utf-8") as file:
            questions = json.load(file)["sorular"]
    except:
        questions = []

    question_texts = [q["soru"] for q in questions]
    closest_match, score, _ = process.extractOne(user_message, question_texts, scorer=fuzz.token_set_ratio)

    if score > 65:
        matched_question = next(q for q in questions if q["soru"] == closest_match)
        return jsonify({"response": matched_question["cevap"]})

    # Eşleşme yoksa unknown.json’a ekle
    try:
        with open("unknown.json", "r+", encoding="utf-8") as f:
            try:
                unknowns = json.load(f)
            except:
                unknowns = []
            if user_message not in [q["soru"] for q in unknowns]:
                unknowns.append({"soru": user_message})
                f.seek(0)
                json.dump(unknowns, f, ensure_ascii=False, indent=2)
                f.truncate()
    except FileNotFoundError:
        with open("unknown.json", "w", encoding="utf-8") as f:
            json.dump([{"soru": user_message}], f, ensure_ascii=False, indent=2)

    return jsonify({"response": "Üzgünüm, bu konuda elimde bilgi yok. Lütfen farklı bir şekilde sorabilir misiniz?"})

# Admin giriş ekranı
@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password")
        if password == "meahortopedi":
            session["logged_in"] = True
            return redirect("/admin")
        else:
            return render_template("admin_login.html", error="Hatalı şifre!")
    return render_template("admin_login.html")

# Admin paneli
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not session.get("logged_in"):
        return redirect("/admin-login")

    if request.method == "GET":
        try:
            with open("unknown.json", "r", encoding="utf-8") as f:
                unknowns = json.load(f)
        except:
            unknowns = []
        return render_template("admin.html", unknowns=unknowns)

    elif request.method == "POST":
        soru = request.form.get("soru").strip()
        cevap = request.form.get("cevap").strip()

        # Yeni veri data.json'a ekle
        with open("data.json", "r+", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except:
                data = {"sorular": []}
            data["sorular"].append({"soru": soru, "cevap": cevap})
            f.seek(0)
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.truncate()

        # unknown.json'dan sil
        with open("unknown.json", "r+", encoding="utf-8") as f:
            unknowns = json.load(f)
            unknowns = [q for q in unknowns if q["soru"] != soru]
            f.seek(0)
            json.dump(unknowns, f, ensure_ascii=False, indent=2)
            f.truncate()

        return redirect("/admin")

# Çıkış
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
    
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)


