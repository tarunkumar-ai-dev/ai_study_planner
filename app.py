from flask import Flask, render_template, request

import pytesseract
from PIL import Image
import os

app = Flask(__name__)

# ⚠️ Windows user ke liye (path check kar lena)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# HOME PAGE
@app.route('/')
def home():
    return render_template('index.html')


# GENERATE PLAN
@app.route('/generate', methods=['POST'])
def generate():

    # 📄 FILE UPLOAD
    file = request.files['datesheet']

    file_path = "datesheet.png"
    file.save(file_path)

    # 🔍 OCR TEXT
    text = pytesseract.image_to_string(Image.open(file_path))
    print("Detected Text:", text)

    # 📚 SUBJECT LIST
    all_subjects = [
        "Maths","Physics","Chemistry","Biology","English","Hindi",
        "Computer","DBMS","OS","Java","Python","C++",
        "AI","ML","Data Science","Statistics"
    ]

    # 🎯 DETECT SUBJECTS
    selected = []

    for sub in all_subjects:
        if sub.lower() in text.lower():
            selected.append(sub)

    # ⚠️ SAFETY
    if not selected:
        return "❌ No subjects detected from date sheet!"

    # ⏱ HOURS
    total_hours = int(request.form['hours'])

    plan = []
    weights = []

    # 🧠 CALCULATE WEIGHT
    for subject in selected:

        difficulty = request.form.get(f'difficulty_{subject}')
        priority = int(request.form.get(f'priority_{subject}', 3))

        # difficulty weight
        if difficulty == "hard":
            diff = 3
        elif difficulty == "medium":
            diff = 2
        else:
            diff = 1

        weight = diff * priority
        weights.append(weight)

    total_weight = sum(weights)

    # 🧩 DISTRIBUTE TIME
    for i, subject in enumerate(selected):

        subject_hours = (weights[i] / total_weight) * total_hours
        total_minutes = int(subject_hours * 60)

        morning = int(total_minutes * 0.5)
        afternoon = int(total_minutes * 0.3)
        night = total_minutes - (morning + afternoon)

        plan.append({
            "subject": subject,
            "morning": f"{morning} min",
            "afternoon": f"{afternoon} min",
            "night": f"{night} min"
        })

    return render_template("result.html", plan=plan)


# RUN
if __name__ == '__main__':
    app.run(debug=True)
