from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():

    selected = request.form.getlist('selected_subjects')
    total_hours = int(request.form['hours'])

    plan = []
    weights = []

    # 🎯 STEP 1: weight calculation
    for subject in selected:

        difficulty = request.form.get(f'difficulty_{subject}')
        priority = int(request.form.get(f'priority_{subject}'))

        if difficulty == "hard":
            diff = 3
        elif difficulty == "medium":
            diff = 2
        else:
            diff = 1

        weight = diff * priority
        weights.append(weight)

    total_weight = sum(weights)

    # 🎯 STEP 2: distribute time
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


if __name__ == '__main__':
    app.run(debug=True)
