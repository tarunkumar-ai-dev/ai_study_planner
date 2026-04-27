import os
import re
import math
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}

ALL_SUBJECTS = [
    "Hindi", "Sanskrit", "Social Science", "Science",
    "Physical Education", "General Studies", "Civics",
    "Information Technology", "Informatics Practices",
    "Environmental Studies", "Home Science", "Fine Arts",
    "Mathematics Basic", "Mathematics Standard",
    "English Language and Literature", "English Core",
    "Mathematics", "Advanced Mathematics", "Calculus", "Statistics", "Linear Algebra",
    "Discrete Mathematics", "Number Theory", "Probability", "Trigonometry", "Geometry",
    "Physics", "Advanced Physics", "Quantum Mechanics", "Thermodynamics", "Electromagnetism",
    "Mechanics", "Optics", "Nuclear Physics", "Astrophysics", "Fluid Dynamics",
    "Chemistry", "Organic Chemistry", "Inorganic Chemistry", "Physical Chemistry",
    "Biochemistry", "Analytical Chemistry", "Environmental Chemistry", "Polymer Chemistry",
    "Biology", "Molecular Biology", "Cell Biology", "Genetics", "Ecology",
    "Microbiology", "Anatomy", "Physiology", "Botany", "Zoology", "Evolutionary Biology",
    "Computer Science", "Data Structures", "Algorithms", "Operating Systems",
    "Computer Networks", "Database Systems", "Software Engineering", "Artificial Intelligence",
    "Machine Learning", "Cybersecurity", "Web Development", "Mobile Development",
    "Cloud Computing", "Computer Architecture", "Compiler Design", "Distributed Systems",
    "English Literature", "English Grammar", "Creative Writing", "Linguistics",
    "World Literature", "Poetry Analysis", "Rhetoric", "Academic Writing",
    "History", "World History", "Ancient History", "Modern History", "Political History",
    "Economic History", "Cultural History", "Military History", "Art History",
    "Geography", "Physical Geography", "Human Geography", "Cartography", "Climatology",
    "Economics", "Microeconomics", "Macroeconomics", "International Economics",
    "Development Economics", "Econometrics", "Finance", "Accounting", "Business Studies",
    "Marketing", "Management", "Entrepreneurship", "Supply Chain Management",
    "Political Science", "International Relations", "Public Policy", "Comparative Politics",
    "Constitutional Law", "Philosophy", "Ethics", "Logic", "Epistemology", "Metaphysics",
    "Psychology", "Cognitive Psychology", "Social Psychology", "Developmental Psychology",
    "Clinical Psychology", "Neuroscience", "Behavioral Science",
    "Sociology", "Anthropology", "Cultural Studies", "Media Studies", "Communication",
    "Art", "Music Theory", "Design", "Architecture", "Photography", "Film Studies",
    "Physical Education", "Health Sciences", "Nutrition", "Environmental Science",
    "Geology", "Astronomy", "Meteorology", "Oceanography",
    "French", "Spanish", "German", "Mandarin", "Japanese", "Arabic", "Latin",
    "Engineering Mathematics", "Civil Engineering", "Mechanical Engineering",
    "Electrical Engineering", "Chemical Engineering", "Materials Science",
    "Law", "Constitutional Studies", "Criminal Justice", "Forensic Science",
    "Data Science", "Bioinformatics", "Biotechnology", "Pharmacology", "Medical Sciences"
]
ALL_SUBJECTS = sorted(set(ALL_SUBJECTS))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_subjects_from_image(image_path):
    detected = []
    try:
        import pytesseract
        from PIL import Image

        # Render/Linux pe Tesseract path
        pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

        img = Image.open(image_path)
        img = img.convert('L')
        img = img.point(lambda x: 0 if x < 140 else 255)

        raw_text = pytesseract.image_to_string(img)
        print("RAW OCR TEXT:", raw_text)

        text_lower = raw_text.lower()

        for subject in ALL_SUBJECTS:
            if subject.lower() in text_lower:
                detected.append(subject)

        keywords_map = {
          'math': 'Mathematics',
          'physics': 'Physics',
          'chem': 'Chemistry',
          'bio': 'Biology',
          'english': 'English Core',
          'language': 'English Language and Literature',
          'history': 'History',
          'geo': 'Geography',
          'economics': 'Economics',
          'computer': 'Computer Science',
          'account': 'Accounting',
          'stats': 'Statistics',
          'science': 'Science',
          'hindi': 'Hindi',
          'sanskrit': 'Sanskrit',
          'social': 'Social Science',
          'physical': 'Physical Education',
          'p.e': 'Physical Education',
          'civics': 'Civics',
          'it': 'Information Technology',
          'ip': 'Informatics Practices',
          'env': 'Environmental Studies',
          'home': 'Home Science',
          'fine': 'Fine Arts',
          'network': 'Computer Networks',
          'database': 'Database Systems',
          'ai': 'Artificial Intelligence',
          'ml': 'Machine Learning',
          'calc': 'Calculus',
          'algo': 'Algorithms',
    }

        for kw, subj in keywords_map.items():
            if kw in text_lower and subj not in detected:
                detected.append(subj)

        print("DETECTED SUBJECTS:", detected)

    except Exception as e:
        print("OCR ERROR:", e)

    return detected
def generate_study_plan(subjects_data, total_hours, exam_days):
    """
    Generate a weighted study plan.
    subjects_data: list of dicts {name, difficulty, priority}
    total_hours: float
    exam_days: int (days until exam)
    Returns list of sessions: {subject, hours, session, order}
    """
    if not subjects_data:
        return []

    DIFFICULTY_WEIGHT = {'Easy': 1.0, 'Medium': 1.5, 'Hard': 2.2}
    PROXIMITY_BONUS = 1.0
    if exam_days is not None:
        if exam_days <= 3:
            PROXIMITY_BONUS = 2.0
        elif exam_days <= 7:
            PROXIMITY_BONUS = 1.6
        elif exam_days <= 14:
            PROXIMITY_BONUS = 1.3
        else:
            PROXIMITY_BONUS = 1.0

    raw_scores = []
    for s in subjects_data:
        diff_w = DIFFICULTY_WEIGHT.get(s.get('difficulty', 'Medium'), 1.5)
        prio_w = float(s.get('priority', 3)) / 3.0
        score = diff_w * prio_w * PROXIMITY_BONUS
        raw_scores.append(score)

    total_score = sum(raw_scores) or 1
    planned_hours = []
    total_hours_f = float(total_hours)

    for score in raw_scores:
        h = (score / total_score) * total_hours_f
        h = max(0.25, round(h * 4) / 4)
        planned_hours.append(h)

    # Scale to match total_hours exactly
    current_total = sum(planned_hours)
    if current_total > 0:
        scale = total_hours_f / current_total
        planned_hours = [round(h * scale * 4) / 4 for h in planned_hours]

    # Sort by priority desc, difficulty desc
    combined = list(zip(subjects_data, planned_hours))
    combined.sort(key=lambda x: (
        -int(x[0].get('priority', 3)),
        -['Easy', 'Medium', 'Hard'].index(x[0].get('difficulty', 'Medium'))
    ))

    # Distribute into Morning / Afternoon / Night
    morning_cap = total_hours_f * 0.40
    afternoon_cap = total_hours_f * 0.35
    # night gets rest

    plan = []
    morning_used = 0
    afternoon_used = 0
    night_used = 0

    sessions_order = ['Morning', 'Afternoon', 'Night']
    session_caps = {
        'Morning': morning_cap,
        'Afternoon': afternoon_cap,
        'Night': float('inf')
    }
    session_used = {'Morning': 0, 'Afternoon': 0, 'Night': 0}
    current_session_idx = 0

    for idx, (subj, hours) in enumerate(combined):
        remaining = hours
        while remaining > 0:
            sess = sessions_order[current_session_idx]
            cap = session_caps[sess]
            available = cap - session_used[sess]
            if available <= 0:
                current_session_idx = min(current_session_idx + 1, 2)
                continue
            allocate = min(remaining, available)
            allocate = round(allocate * 4) / 4
            if allocate <= 0:
                current_session_idx = min(current_session_idx + 1, 2)
                if current_session_idx > 2:
                    break
                continue
            plan.append({
                'subject': subj['name'],
                'difficulty': subj.get('difficulty', 'Medium'),
                'priority': subj.get('priority', 3),
                'hours': allocate,
                'minutes': int(allocate * 60),
                'session': sess,
                'order': len(plan)
            })
            session_used[sess] += allocate
            remaining -= allocate
            remaining = round(remaining * 4) / 4
            if remaining > 0 and session_used[sess] >= cap:
                current_session_idx = min(current_session_idx + 1, 2)

    return plan

@app.route('/ocr-preview', methods=['POST'])
def ocr_preview():
    ocr_subjects = []
    exam_days = request.form.get('exam_days', '')
    total_hours = request.form.get('total_hours', 8)

    if 'datesheet' in request.files:
        file = request.files['datesheet']
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            ocr_subjects = extract_subjects_from_image(filepath)
            print("OCR SUBJECTS:", ocr_subjects)

    return render_template(
        'index.html',
        subjects=ALL_SUBJECTS,
        ocr_subjects=ocr_subjects,
        exam_days=exam_days,
        total_hours=total_hours
    )

@app.route('/')
def index():
    return render_template('index.html', subjects=ALL_SUBJECTS)

@app.route('/generate', methods=['POST'])
def generate():
    total_hours = request.form.get('total_hours', 8)
    exam_days_str = request.form.get('exam_days', '').strip()
    exam_days = None
    if exam_days_str and exam_days_str.isdigit():
        exam_days = int(exam_days_str)

    # Handle datesheet image upload
    ocr_subjects = []
    if 'datesheet' in request.files:
        file = request.files['datesheet']
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            ocr_subjects = extract_subjects_from_image(filepath)

    # Collect manually selected subjects
    selected_subjects = request.form.getlist('subjects')

    # Merge OCR + manual, deduplicate
    all_selected = list(dict.fromkeys(selected_subjects + ocr_subjects))

    subjects_data = []
    for subj in all_selected:
        difficulty = request.form.get(f'difficulty_{subj}', 'Medium')
        priority = request.form.get(f'priority_{subj}', '3')
        subjects_data.append({
            'name': subj,
            'difficulty': difficulty,
            'priority': priority
        })

    if not subjects_data:
        return redirect(url_for('index'))

    plan = generate_study_plan(subjects_data, total_hours, exam_days)

    morning = [p for p in plan if p['session'] == 'Morning']
    afternoon = [p for p in plan if p['session'] == 'Afternoon']
    night = [p for p in plan if p['session'] == 'Night']

    total_minutes = sum(p['minutes'] for p in plan)

    return render_template(
        'result.html',
        plan=plan,
        morning=morning,
        afternoon=afternoon,
        night=night,
        total_hours=total_hours,
        exam_days=exam_days,
        ocr_subjects=ocr_subjects,
        total_minutes=total_minutes
    )

if __name__ == '__main__':
    app.run(debug=True)
