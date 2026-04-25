from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)

# HOME PAGE
@app.route('/')
def home():
    return render_template('index.html')


# GENERATE PLAN
@app.route('/generate', methods=['POST'])
def generate():

    selected = request.form.getlist('selected_subjects')
    hours = int(request.form['hours'])
    exam_date = request.form['exam_date']

    # DATE LOGIC
    today = datetime.today()
    exam = datetime.strptime(exam_date, "%Y-%m-%d")
    days_left = (exam - today).days

    subjects = []
    priorities = []

    # SUBJECT DATA
    for sub in selected:

        diff = request.form.get(f"difficulty_{sub}")
        pr = int(request.form.get(f"priority_{sub}"))

        # DIFFICULTY WEIGHT
        if diff == "hard":
            weight = 1.5
        elif diff == "medium":
            weight = 1.2
        else:
            weight = 1

        final_priority = pr * weight

        subjects.append(sub)
        priorities.append(final_priority)

    total_priority = sum(priorities)

    plan = []

    # TIME DISTRIBUTION
    for sub, pr in zip(subjects, priorities):

        total_time = (pr / total_priority) * hours

        morning = total_time * 0.4
        afternoon = total_time * 0.3
        night = total_time * 0.3

        # FORMAT FUNCTION
        def format_time(t):
            h = int(t)
            m = int((t - h) * 60)
            if h == 0:
                return f"{m} min"
            return f"{h} hr {m} min"

        plan.append({
            "subject": sub,
            "morning": format_time(morning),
            "afternoon": format_time(afternoon),
            "night": format_time(night)
        })

    # MESSAGE
    if days_left <= 3:
        message = "🔥 Exam very close! Study more!"
    elif days_left <= 7:
        message = "⚠️ Stay consistent!"
    else:
        message = "👍 You have enough time!"

    return render_template('result.html', plan=plan, message=message)


# RUN APP
if __name__ == '__main__':
    app.run(debug=True)