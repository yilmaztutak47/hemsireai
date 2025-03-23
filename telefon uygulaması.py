from flask import Flask, request, jsonify, render_template
import json

app = Flask(__name__)

# JSON dosyasını oku
DATA_FILE = "data.json"
def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/get_answer', methods=['POST'])
def get_answer():
    data = load_data()
    question = request.json.get("question").strip().lower()
    
    for item in data:
        if question in item["question"].lower():
            return jsonify({"answer": item["answer"]})
    
    return jsonify({"answer": "Bu sorunun cevabını bulamadım."})

@app.route('/add_question', methods=['POST'])
def add_question():
    data = load_data()
    new_question = request.json.get("question").strip()
    new_answer = request.json.get("answer").strip()
    
    data.append({"question": new_question, "answer": new_answer})
    save_data(data)
    
    return jsonify({"message": "Soru eklendi."})

if __name__ == '__main__':
    app.run(debug=True)
