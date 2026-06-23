"""
Student Performance Analytics System (SPAS)
Bowen University, Iwo - Department of Computer Science
Full-stack Flask application with authentication and analytics
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import json, os, re, statistics
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = "spas_bowen_secret_key_2026"


# Simple JSON file-based "database"

DB_PATH = os.path.join(os.path.dirname(__file__), "db.json")

def load_db():
    if not os.path.exists(DB_PATH):
        return {"users": [], "students": [], "scores": []}
    with open(DB_PATH) as f:
        return json.load(f)

def save_db(data):
    with open(DB_PATH, "w") as f:
        json.dump(data, f, indent=2)

def init_db():
    """Seed with demo data on first run."""
    db = load_db()
    if db["users"]:
        return
    # Default admin
    db["users"].append({
        "id": 1, "name": "Admin User", "email": "admin@bowen.edu.ng",
        "password": generate_password_hash("admin123"),
        "role": "admin", "created_at": str(datetime.now())
    })
    # Demo students
    demo_students = [
        {"id": 1, "name": "Akanbi Timothy Oluwagbemiga", "matric": "BU22CSC1001", "level": 300, "department": "Computer Science"},
        {"id": 2, "name": "Adeyemi Funmilayo Grace",    "matric": "BU22CSC1002", "level": 300, "department": "Computer Science"},
        {"id": 3, "name": "Olatunji Emmanuel Seun",      "matric": "BU21CSC1003", "level": 400, "department": "Computer Science"},
        {"id": 4, "name": "Balogun Oluwatobi Daniel",    "matric": "BU22CSC1004", "level": 300, "department": "Computer Science"},
        {"id": 5, "name": "Fasanya Rukayat Adeola",      "matric": "BU21CSC1005", "level": 400, "department": "Computer Science"},
        {"id": 6, "name": "Okonkwo Chukwuemeka Bright",  "matric": "BU23CSC1006", "level": 200, "department": "Computer Science"},
        {"id": 7, "name": "Salami Mariam Adunola",       "matric": "BU23CSC1007", "level": 200, "department": "Computer Science"},
        {"id": 8, "name": "Eze Chidinma Blessing",       "matric": "BU22CSC1008", "level": 300, "department": "Computer Science"},
        {"id": 9, "name": "Adewale Babatunde Moses",     "matric": "BU21CSC1009", "level": 400, "department": "Computer Science"},
        {"id": 10,"name": "Obinna Nkechi Chioma",        "matric": "BU23CSC1010", "level": 200, "department": "Computer Science"},
    ]
    db["students"] = demo_students

    # Demo scores (session=2024/2025, two semesters, several courses)
    courses_s1 = ["CSC301", "CSC303", "CSC305", "CSC307", "CSC309"]
    courses_s2 = ["CSC302", "CSC304", "CSC306", "CSC308", "CSC310"]
    import random; random.seed(42)

    score_id = 1
    for student in demo_students:
        for course in courses_s1:
            ca1 = random.randint(5, 15)
            ca2 = random.randint(5, 15)
            exam = random.randint(25, 70)
            total = ca1 + ca2 + exam
            db["scores"].append({
                "id": score_id, "student_id": student["id"],
                "course_code": course, "session": "2024/2025", "semester": 1,
                "ca1": ca1, "ca2": ca2, "exam": exam, "total": total,
                "grade": compute_grade(total), "created_at": str(datetime.now())
            })
            score_id += 1
        for course in courses_s2:
            ca1 = random.randint(5, 15)
            ca2 = random.randint(5, 15)
            exam = random.randint(25, 70)
            total = ca1 + ca2 + exam
            db["scores"].append({
                "id": score_id, "student_id": student["id"],
                "course_code": course, "session": "2024/2025", "semester": 2,
                "ca1": ca1, "ca2": ca2, "exam": exam, "total": total,
                "grade": compute_grade(total), "created_at": str(datetime.now())
            })
            score_id += 1
    save_db(db)

def compute_grade(total):
    if total >= 70: return "A"
    if total >= 60: return "B"
    if total >= 50: return "C"
    if total >= 45: return "D"
    if total >= 40: return "E"
    return "F"

def grade_point(grade):
    return {"A": 5, "B": 4, "C": 3, "D": 2, "E": 1, "F": 0}.get(grade, 0)

def validate_matric(matric):
    """Format: BU22CSC1049"""
    return bool(re.match(r'^BU\d{2}[A-Z]{3}\d{4}$', matric))


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("auth_page"))

@app.route("/auth")
def auth_page():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("auth.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth_page"))
    return render_template("dashboard.html")

# ──────────────────────────────────────────────
# Auth API
# ──────────────────────────────────────────────
@app.route("/api/auth/signup", methods=["POST"])
def signup():
    data = request.get_json()
    name = data.get("name","").strip()
    email = data.get("email","").strip().lower()
    password = data.get("password","")
    role = data.get("role","lecturer")

    if not all([name, email, password]):
        return jsonify({"error": "All fields are required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    db = load_db()
    if any(u["email"] == email for u in db["users"]):
        return jsonify({"error": "Email already registered"}), 409

    new_user = {
        "id": len(db["users"]) + 1,
        "name": name, "email": email,
        "password": generate_password_hash(password),
        "role": role, "created_at": str(datetime.now())
    }
    db["users"].append(new_user)
    save_db(db)
    session["user_id"] = new_user["id"]
    session["user_name"] = new_user["name"]
    session["user_role"] = new_user["role"]
    return jsonify({"message": "Account created", "name": new_user["name"], "role": new_user["role"]})

@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email","").strip().lower()
    password = data.get("password","")

    db = load_db()
    user = next((u for u in db["users"] if u["email"] == email), None)
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid email or password"}), 401

    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    session["user_role"] = user["role"]
    return jsonify({"message": "Login successful", "name": user["name"], "role": user["role"]})

@app.route("/api/auth/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})

@app.route("/api/auth/me")
@login_required
def me():
    return jsonify({"id": session["user_id"], "name": session["user_name"], "role": session["user_role"]})

# ──────────────────────────────────────────────
# Students API
# ──────────────────────────────────────────────
@app.route("/api/students", methods=["GET"])
@login_required
def get_students():
    db = load_db()
    return jsonify(db["students"])

@app.route("/api/students", methods=["POST"])
@login_required
def add_student():
    data = request.get_json()
    name   = data.get("name","").strip()
    matric = data.get("matric","").strip().upper()
    level  = data.get("level", 100)
    dept   = data.get("department","Computer Science").strip()

    if not all([name, matric]):
        return jsonify({"error": "Name and matric number are required"}), 400
    if not validate_matric(matric):
        return jsonify({"error": "Matric must follow format: BU22CSC1049"}), 400

    db = load_db()
    if any(s["matric"] == matric for s in db["students"]):
        return jsonify({"error": "Matric number already exists"}), 409

    student = {
        "id": max((s["id"] for s in db["students"]), default=0) + 1,
        "name": name, "matric": matric,
        "level": int(level), "department": dept
    }
    db["students"].append(student)
    save_db(db)
    return jsonify(student), 201

@app.route("/api/students/<int:sid>", methods=["DELETE"])
@login_required
def delete_student(sid):
    db = load_db()
    db["students"] = [s for s in db["students"] if s["id"] != sid]
    db["scores"]   = [sc for sc in db["scores"] if sc["student_id"] != sid]
    save_db(db)
    return jsonify({"message": "Student deleted"})

# ──────────────────────────────────────────────
# Scores API
# ──────────────────────────────────────────────
@app.route("/api/scores", methods=["GET"])
@login_required
def get_scores():
    session_filter   = request.args.get("session","2024/2025")
    semester_filter  = request.args.get("semester","1")
    student_filter   = request.args.get("student_id")

    db = load_db()
    scores = db["scores"]
    scores = [s for s in scores if s["session"] == session_filter]
    scores = [s for s in scores if str(s["semester"]) == str(semester_filter)]
    if student_filter:
        scores = [s for s in scores if str(s["student_id"]) == str(student_filter)]

    # Enrich with student name
    students_map = {s["id"]: s for s in db["students"]}
    for sc in scores:
        st = students_map.get(sc["student_id"], {})
        sc["student_name"]  = st.get("name","")
        sc["student_matric"]= st.get("matric","")
    return jsonify(scores)

@app.route("/api/scores", methods=["POST"])
@login_required
def add_score():
    data = request.get_json()
    required = ["student_id","course_code","session","semester","ca1","ca2","exam"]
    if not all(k in data for k in required):
        return jsonify({"error": "Missing required fields"}), 400

    ca1  = float(data["ca1"])
    ca2  = float(data["ca2"])
    exam = float(data["exam"])

    if ca1 > 15 or ca2 > 15: return jsonify({"error": "CA scores max 15 each"}), 400
    if exam > 70:             return jsonify({"error": "Exam score max 70"}), 400

    total = ca1 + ca2 + exam
    grade = compute_grade(total)

    db = load_db()
    # Prevent duplicates
    dup = any(
        s["student_id"] == data["student_id"] and
        s["course_code"] == data["course_code"] and
        s["session"]     == data["session"] and
        str(s["semester"]) == str(data["semester"])
        for s in db["scores"]
    )
    if dup:
        return jsonify({"error": "Score already exists for this student/course/semester"}), 409

    score = {
        "id": max((s["id"] for s in db["scores"]), default=0) + 1,
        "student_id":  data["student_id"],
        "course_code": data["course_code"].upper(),
        "session":     data["session"],
        "semester":    int(data["semester"]),
        "ca1": ca1, "ca2": ca2, "exam": exam,
        "total": total, "grade": grade,
        "created_at": str(datetime.now())
    }
    db["scores"].append(score)
    save_db(db)
    return jsonify(score), 201

@app.route("/api/scores/<int:score_id>", methods=["PUT"])
@login_required
def update_score(score_id):
    data = request.get_json()
    db = load_db()
    for sc in db["scores"]:
        if sc["id"] == score_id:
            ca1  = float(data.get("ca1", sc["ca1"]))
            ca2  = float(data.get("ca2", sc["ca2"]))
            exam = float(data.get("exam", sc["exam"]))
            if ca1 > 15 or ca2 > 15: return jsonify({"error": "CA max 15"}), 400
            if exam > 70:             return jsonify({"error": "Exam max 70"}), 400
            sc["ca1"] = ca1; sc["ca2"] = ca2; sc["exam"] = exam
            sc["total"] = ca1 + ca2 + exam
            sc["grade"] = compute_grade(sc["total"])
            save_db(db)
            return jsonify(sc)
    return jsonify({"error": "Score not found"}), 404

@app.route("/api/scores/<int:score_id>", methods=["DELETE"])
@login_required
def delete_score(score_id):
    db = load_db()
    db["scores"] = [s for s in db["scores"] if s["id"] != score_id]
    save_db(db)
    return jsonify({"message": "Score deleted"})

# ──────────────────────────────────────────────
# Analytics API
# ──────────────────────────────────────────────
@app.route("/api/analytics/overview")
@login_required
def analytics_overview():
    session_q  = request.args.get("session","2024/2025")
    semester_q = request.args.get("semester","1")
    db = load_db()

    scores = [s for s in db["scores"]
              if s["session"] == session_q and str(s["semester"]) == str(semester_q)]

    if not scores:
        return jsonify({"total_students": 0, "total_scores": 0,
                        "class_average": 0, "pass_rate": 0,
                        "grade_dist": {}, "at_risk": []})

    totals     = [s["total"] for s in scores]
    class_avg  = round(statistics.mean(totals), 2)
    passed     = sum(1 for t in totals if t >= 40)
    pass_rate  = round(passed / len(totals) * 100, 1)

    grade_dist = {"A":0,"B":0,"C":0,"D":0,"E":0,"F":0}
    for s in scores:
        grade_dist[s["grade"]] = grade_dist.get(s["grade"],0) + 1

    # At-risk: students with average below 40
    students_map = {st["id"]: st for st in db["students"]}
    sid_scores   = {}
    for sc in scores:
        sid_scores.setdefault(sc["student_id"], []).append(sc["total"])
    at_risk = []
    for sid, totals_list in sid_scores.items():
        avg = statistics.mean(totals_list)
        if avg < 45:
            st = students_map.get(sid, {})
            at_risk.append({"name": st.get("name",""), "matric": st.get("matric",""),
                             "average": round(avg, 1)})
    at_risk.sort(key=lambda x: x["average"])

    return jsonify({
        "total_students": len(db["students"]),
        "total_scores":   len(scores),
        "class_average":  class_avg,
        "pass_rate":      pass_rate,
        "grade_dist":     grade_dist,
        "at_risk":        at_risk[:5],
        "std_dev":        round(statistics.stdev(totals), 2) if len(totals) > 1 else 0,
        "highest":        max(totals),
        "lowest":         min(totals),
    })

@app.route("/api/analytics/course_performance")
@login_required
def course_performance():
    session_q  = request.args.get("session","2024/2025")
    semester_q = request.args.get("semester","1")
    db = load_db()

    scores = [s for s in db["scores"]
              if s["session"] == session_q and str(s["semester"]) == str(semester_q)]

    course_data = {}
    for sc in scores:
        cc = sc["course_code"]
        course_data.setdefault(cc, []).append(sc["total"])

    result = []
    for cc, totals in sorted(course_data.items()):
        result.append({
            "course": cc,
            "average": round(statistics.mean(totals), 1),
            "highest": max(totals),
            "lowest":  min(totals),
            "count":   len(totals),
            "pass_rate": round(sum(1 for t in totals if t >= 40) / len(totals) * 100, 1)
        })
    return jsonify(result)

@app.route("/api/analytics/student/<int:sid>")
@login_required
def student_analytics(sid):
    db = load_db()
    student = next((s for s in db["students"] if s["id"] == sid), None)
    if not student:
        return jsonify({"error": "Student not found"}), 404

    scores = [s for s in db["scores"] if s["student_id"] == sid]
    by_sem = {}
    for sc in scores:
        key = f"{sc['session']} S{sc['semester']}"
        by_sem.setdefault(key, []).append(sc)

    semesters = []
    for key, sem_scores in sorted(by_sem.items()):
        totals = [s["total"] for s in sem_scores]
        gpa_pts = sum(grade_point(s["grade"]) for s in sem_scores)
        cgpa    = round(gpa_pts / len(sem_scores), 2) if sem_scores else 0
        semesters.append({
            "label":    key,
            "average":  round(statistics.mean(totals), 1),
            "cgpa":     cgpa,
            "courses":  sem_scores,
            "pass_rate": round(sum(1 for t in totals if t >= 40) / len(totals) * 100, 1)
        })

    return jsonify({"student": student, "semesters": semesters})

@app.route("/api/analytics/sessions")
@login_required
def get_sessions():
    db = load_db()
    sessions  = sorted(set(s["session"]  for s in db["scores"]), reverse=True)
    semesters = sorted(set(s["semester"] for s in db["scores"]))
    return jsonify({"sessions": sessions or ["2024/2025"], "semesters": semesters or [1,2]})

# ──────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
