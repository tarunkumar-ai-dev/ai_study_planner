from flask import Flask, render_template, request
import pytesseract
from PIL import Image
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():

    hours = int(request.form.get('hours', 1))
    exam_days = int(request.form.get('exam_days', 1))

    file = request.files.get('datesheet')

    detected_subjects = []

    if file and file.filename != "":
        filepath = os.path.join("static", file.filename)
        file.save(filepath)

        img = Image.open(filepath)
        text = pytesseract.image_to_string(img).lower()

        subjects_list = [
            "maths","physics","chemistry","biology",
            "english","hindi","computer","dbms","os","java","python"
        ]

        for sub in subjects_list:
            if sub in text:
                detected_subjects.append(sub.capitalize())

    # fallback manual
    subjects = detected_subjects if detected_subjects else request.form.getlist('subjects')

    plan = []

    if subjects:
        per_subject_time = hours * 60 // len(subjects)

        for sub in subjects:
            plan.append({
                "subject": sub,
                "morning": f"{per_subject_time//3} min",
                "afternoon": f"{per_subject_time//3} min",
                "night": f"{per_subject_time//3} min"
            })

    return render_template('result.html', plan=plan)

if __name__ == '__main__':
    app.run(debug=True)
