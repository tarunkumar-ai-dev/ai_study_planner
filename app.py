from flask import Flask, render_template, request

app = Flask(__name__)

# HOME PAGE
@app.route('/')
def home():
    return render_template('index.html')


# GENERATE STUDY PLAN
@app.route('/generate', methods=['POST'])
def generate():

    selected = request.form.getlist('selected_subjects')

    # safety check
    if not selected:
        return "Please select at least one subject!"

    total_hours = int(request.form['hours'])
    exam_days = int(request.form['exam_days'])

    plan = []
    weights = []

    # 🔥 exam urgency (jitna exam paas utna weight jyada)
    urgency = 10 / exam_days if exam_days != 0 else 1

    # calculate weight
    for subject in selected:

        difficulty = request.form.get(f'difficulty_{subject}')
        priority = int(request.form.get(f'priority_{subject}'))

        # difficulty weight
        if difficulty == "hard":
            diff = 3
        elif difficulty == "medium":
            diff = 2
        else:
            diff = 1

        weight = (diff * priority) + urgency
        weights.append(weight)

    total_weight = sum(weights)

    # distribute time
    for i, subject in enumerate(selected):

        subject_hours = (weights[i] / total_weight) * total_hours
        total_minutes = int(subject_hours * 60)

        # split day
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


# RUN SERVER
if __name__ == '__main__':
    app.run(debug=True)
