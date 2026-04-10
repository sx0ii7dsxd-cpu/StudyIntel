import calendar
import os
import random
import sqlite3
import string
from datetime import date, datetime, timedelta

# Register custom adapters to avoid DeprecationWarnings in Python 3.12+
sqlite3.register_adapter(date, lambda val: val.isoformat())
sqlite3.register_adapter(datetime, lambda val: val.isoformat(" "))

from flask import Flask, Response, jsonify, redirect, render_template, request, session
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = "secret"

TEACHER_SECRET = "World*2026"

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ---------------- DATABASE ----------------








#---------- ENV LOADER ---------
def load_env_file():
    env_path = ".env"
    if not os.path.exists(env_path):
        return

    with open(env_path, "r", encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def mask_secret(value):
    if not value:
        return "missing"
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}...{value[-4:]}"


def log_startup_configuration():
    gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()
    gemini_model = os.environ.get("GEMINI_MODEL", "").strip() or "gemini-2.5-flash"

    app.logger.info(
        "Startup config loaded | GEMINI_MODEL=%s | GEMINI_API_KEY=%s",
        gemini_model,
        mask_secret(gemini_key),
    )


load_env_file()
log_startup_configuration()

def get_db():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn


def generate_class_code():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


def get_study_level(minutes):
    if minutes <= 0:
        return 0
    if minutes < 60:
        return 1
    return 2


def build_month_heatmap(user_id, reference_date=None):
    conn = get_db()
    today = reference_date or datetime.now().date()
    month_start = today.replace(day=1)
    _, days_in_month = calendar.monthrange(today.year, today.month)
    month_end = today.replace(day=days_in_month)

    rows = conn.execute(
        """
        SELECT date, COALESCE(SUM(minutes), 0) AS total
        FROM study_sessions
        WHERE user_id=? AND date BETWEEN ? AND ?
        GROUP BY date
        """,
        (user_id, month_start.isoformat(), month_end.isoformat()),
    ).fetchall()

    daily_minutes = {row["date"]: int(row["total"] or 0) for row in rows}
    calendar_days = []
    leading_blanks = month_start.weekday()

    for _ in range(leading_blanks):
        calendar_days.append(None)

    for day in range(1, days_in_month + 1):
        current_date = today.replace(day=day)
        iso_date = current_date.isoformat()
        minutes = daily_minutes.get(iso_date, 0)
        calendar_days.append(
            {
                "date": iso_date,
                "day_number": day,
                "minutes": minutes,
                "level": get_study_level(minutes),
                "is_today": current_date == today,
            }
        )

    trailing_blanks = (-len(calendar_days)) % 7
    for _ in range(trailing_blanks):
        calendar_days.append(None)

    studied_days = sum(1 for minutes in daily_minutes.values() if minutes > 0)

    return {
        "month_label": today.strftime("%B %Y"),
        "studied_days": studied_days,
        "total_minutes": sum(daily_minutes.values()),
        "calendar_days": calendar_days,
    }













#---------- GEMINI STUDY CONTEXT ---------
def get_user_study_context(user_id, class_code):
    conn = get_db()
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())

    weekly_minutes = conn.execute(
        """
        SELECT COALESCE(SUM(minutes), 0)
        FROM study_sessions
        WHERE user_id=? AND date>=?
        """,
        (user_id, week_start),
    ).fetchone()[0]

    today_minutes = conn.execute(
        """
        SELECT COALESCE(SUM(minutes), 0)
        FROM study_sessions
        WHERE user_id=? AND date=?
        """,
        (user_id, today),
    ).fetchone()[0]

    class_average = conn.execute(
        """
        SELECT COALESCE(AVG(total), 0) FROM (
            SELECT COALESCE(SUM(study_sessions.minutes), 0) AS total
            FROM users
            LEFT JOIN study_sessions
                ON users.id = study_sessions.user_id
                AND study_sessions.date >= ?
            WHERE users.class_code=? AND users.role='student'
            GROUP BY users.id
        )
        """,
        (week_start, class_code),
    ).fetchone()[0]

    return {
        "today_minutes": int(today_minutes or 0),
        "weekly_minutes": int(weekly_minutes or 0),
        "class_average": round(float(class_average or 0), 1),
        "week_start": str(week_start),
        "today": str(today),
    }










#---------- GEMINI STUDY REPLY ---------
def generate_study_assistant_reply(user_message):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    genai.configure(api_key=api_key)
    context = get_user_study_context(session["user_id"], session["class_code"])

    system_prompt = (
        "You are StudyIntel's built-in Study Assistant. "
        "Help students study better, explain concepts simply, motivate them, "
        "and give practical productivity suggestions. Keep responses concise, "
        "supportive, and personalized to the user's study data."
    )

    user_prompt = (
        f"User role: {session.get('role', 'student')}\n"
        f"Weekly study minutes: {context['weekly_minutes']}\n"
        f"Class weekly average: {context['class_average']}\n"
        f"Today's study minutes: {context['today_minutes']}\n"
        f"Week start: {context['week_start']}\n"
        f"Today: {context['today']}\n\n"
        f"User question: {user_message}"
    )

    return generate_gemini_text(system_prompt, user_prompt, temperature=0.7)












#---------- STUDYAI GEMINI HELPERS ---------
def generate_gemini_text(system_prompt, user_prompt, temperature=0.7):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    genai.configure(api_key=api_key)

    model_candidates = get_gemini_model_candidates()

    last_error = None

    for model_name in model_candidates:
        try:
            gemini_model = genai.GenerativeModel(model_name)
            response = gemini_model.generate_content(
                [system_prompt, user_prompt],
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                ),
            )

            reply_text = getattr(response, "text", "").strip()
            if reply_text:
                return reply_text

            last_error = RuntimeError(f"{model_name} returned an empty response")
        except Exception as exc:
            if is_gemini_quota_error(exc):
                raise RuntimeError(build_gemini_quota_message(exc))
            last_error = exc

    raise RuntimeError(f"Gemini request failed: {last_error}")


def get_gemini_model_candidates():
    configured_model = os.environ.get("GEMINI_MODEL", "").strip()
    raw_candidates = [
        configured_model,
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-2.0-flash-001",
    ]

    unique_candidates = []
    for model_name in raw_candidates:
        if model_name and model_name not in unique_candidates:
            unique_candidates.append(model_name)
    return unique_candidates


def is_gemini_quota_error(exc):
    error_text = str(exc).lower()
    return (
        "quota exceeded" in error_text
        or "rate limit" in error_text
        or "429" in error_text
        or "resource_exhausted" in error_text
    )


def build_gemini_quota_message(exc):
    error_text = str(exc)
    retry_seconds = None

    if "retry in " in error_text.lower():
        retry_section = error_text.lower().split("retry in ", 1)[1]
        retry_seconds = retry_section.split("s", 1)[0].strip()
    elif "retry_delay" in error_text.lower() and "seconds:" in error_text.lower():
        retry_section = error_text.lower().split("seconds:", 1)[1]
        retry_seconds = retry_section.split("}", 1)[0].split("]", 1)[0].strip()

    message = (
        "Gemini quota reached for the current API key/project. "
        "Please try again in a short while"
    )

    if retry_seconds:
        message += f" (about {retry_seconds} seconds)"

    message += " or use a Gemini API key with available quota/billing enabled."
    return message


def generate_studyai_chat_reply(user_message):
    return generate_gemini_text(
        (
            "You are a study assistant.\n\n"
            "Always format responses properly:\n"
            "- Use CAPITAL headings when needed\n"
            "- Use bullet points for clarity\n"
            "- Keep answers structured and readable\n"
            "- Avoid random paragraphs"
        ),
        f"Student message: {user_message}",
        temperature=0.5,
    )


def generate_studyai_summary(notes_text):
    return generate_gemini_text(
        (
            "Summarize the following notes for a student.\n\n"
            "IMPORTANT: Follow this EXACT format strictly.\n\n"
            "KEY POINTS:\n"
            "- Point 1\n"
            "- Point 2\n\n"
            "SUMMARY:\n"
            "Write a short paragraph.\n\n"
            "SIMPLE EXPLANATION:\n"
            "Explain in very easy words.\n\n"
            "Do NOT change headings. Keep them in CAPITAL LETTERS."
        ),
        f"Study notes:\n{notes_text}",
        temperature=0.3,
    )


def generate_studyai_questions(notes_text):
    return generate_gemini_text(
        (
            "Generate questions from the following text.\n\n"
            "IMPORTANT: Follow EXACT format.\n\n"
            "MCQs:\n"
            "1. Question\n"
            "   a) Option\n"
            "   b) Option\n"
            "   c) Option\n"
            "   d) Option\n\n"
            "SHORT QUESTIONS:\n"
            "1. Question\n\n"
            "LONG QUESTIONS:\n"
            "1. Question\n\n"
            "Keep headings in CAPITAL LETTERS."
        ),
        f"Study content:\n{notes_text}",
        temperature=0.4,
    )


# ---------------- STUDENT LOGIN ----------------

@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=? AND role='student'",
            (username, password),
        ).fetchone()

        if user:
            session["user_id"] = user["id"]
            session["class_code"] = user["class_code"]
            session["role"] = "student"

            return redirect("/dashboard")

    return render_template("login.html")









# ---------------- STUDENT REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        class_code = request.form["class_code"]

        conn = get_db()

        teacher = conn.execute(
            "SELECT * FROM users WHERE class_code=? AND role='teacher'",
            (class_code,),
        ).fetchone()

        if not teacher:
            return "Invalid Class Code"

        conn.execute(
            "INSERT INTO users(username,password,role,class_code) VALUES(?,?,?,?)",
            (username, password, "student", class_code),
        )

        conn.commit()

        return redirect("/login")

    return render_template("register.html")







# ---------------- TEACHER REGISTER ----------------

@app.route("/teacher_register", methods=["GET", "POST"])
def teacher_register():
    if request.method == "POST":
        if request.form["secret_code"] != TEACHER_SECRET:
            return "Invalid Secret Code"

        username = request.form["username"]
        password = request.form["password"]

        full_name = request.form["full_name"]
        email = request.form["email"]
        phone = request.form["phone"]
        address = request.form["address"]
        aadhaar = request.form["aadhaar"]

        class_code = generate_class_code()

        conn = get_db()

        cursor = conn.execute(
            "INSERT INTO users(username,password,role,class_code) VALUES(?,?,?,?)",
            (username, password, "teacher", class_code),
        )

        user_id = cursor.lastrowid

        conn.execute(
            "INSERT INTO teacher_profiles VALUES(?,?,?,?,?,?)",
            (user_id, full_name, email, phone, address, aadhaar),
        )

        conn.commit()

        session["user_id"] = user_id
        session["class_code"] = class_code
        session["role"] = "teacher"

        return redirect("/teacher_dashboard")

    return render_template("teacher_register.html")











# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")
    if session.get("role") != "student":
        return redirect("/teacher_dashboard")

    conn = get_db()

    today = datetime.now().date()

    # TODAY'S STUDY TIME
    today_minutes = conn.execute(
        """
        SELECT COALESCE(SUM(minutes),0)
        FROM study_sessions
        WHERE user_id=? AND date=?
        """,
        (session["user_id"], today)
    ).fetchone()[0]

    # WEEK START (MONDAY)
    week_start = today - timedelta(days=today.weekday())

    # LEADERBOARD
    leaderboard = conn.execute(
        """
        SELECT users.username,
        COALESCE(SUM(study_sessions.minutes),0) as total

        FROM users

        LEFT JOIN study_sessions
        ON users.id = study_sessions.user_id
        AND study_sessions.date >= ?

        WHERE users.class_code=? AND users.role='student'

        GROUP BY users.username

        ORDER BY total DESC
        """,
        (week_start, session["class_code"])
    ).fetchall()

    # WEEKLY TOTAL OF USER
    user_week = conn.execute(
        """
        SELECT COALESCE(SUM(minutes),0)
        FROM study_sessions
        WHERE user_id=? AND date>=?
        """,
        (session["user_id"], week_start)
    ).fetchone()[0]

    # CLASS AVERAGE
    class_avg = conn.execute(
        """
        SELECT COALESCE(AVG(total),0) FROM (
            SELECT SUM(minutes) as total
            FROM study_sessions
            JOIN users ON users.id = study_sessions.user_id
            WHERE users.class_code=? AND date>=?
            GROUP BY users.id
        )
        """,
        (session["class_code"], week_start)
    ).fetchone()[0]

    month_heatmap = build_month_heatmap(session["user_id"], today)

    # AI MESSAGE
    if user_week > class_avg:
        insight = "🔥 You're above class average! Great job!"
    elif user_week == 0:
        insight = "😴 You haven't studied this week. Start now!"
    else:
        insight = "📈 You're below average. Try studying more daily."


    #<!!!---------- FETCH MATERIALS ---------!!!>
    materials = conn.execute(
        "SELECT * FROM materials WHERE class_code=? ORDER BY id DESC",
        (session["class_code"],)
        ).fetchall()
    
    return render_template(
        "home.html",
        today_minutes=today_minutes,
        leaderboard=leaderboard,
        insight=insight,
        materials=materials,
        month_heatmap=month_heatmap,
        )









# ---------------- TEACHER DASHBOARD ----------------

@app.route("/teacher_dashboard")
def teacher_dashboard():
    if "role" not in session or session["role"] != "teacher":
        return redirect("/login")

    conn = get_db()

    # GET ALL STUDENTS OF THIS CLASS
    students = conn.execute(
        """
        SELECT id, username
        FROM users
        WHERE class_code=? AND role='student'
        """,
        (session["class_code"],),
    ).fetchall()

    # LEADERBOARD (TOTAL STUDY TIME)
    leaderboard = conn.execute(
        """
        SELECT users.username,
        COALESCE(SUM(study_sessions.minutes),0) as total

        FROM users
        LEFT JOIN study_sessions
        ON users.id = study_sessions.user_id

        WHERE users.class_code=? AND users.role='student'

        GROUP BY users.id
        ORDER BY total DESC
        """,
        (session["class_code"],),
    ).fetchall()
    
    
    
    
    
    
    #<!!!---------- FETCH MATERIALS ---------!!!>
    materials = conn.execute(
        "SELECT * FROM materials WHERE class_code=? ORDER BY id DESC",
        (session["class_code"],)
        ).fetchall()
    
    return render_template(
        "teacher_dashboard.html",
        students=students,
        leaderboard=leaderboard,
        materials=materials,
    )


#---------- MATERIAL UPLOAD ---------

@app.route("/upload_material", methods=["POST"])
def upload_material():

    if "role" not in session or session["role"] != "teacher":
        return "Unauthorized"

    file = request.files["file"]
    title = request.form["title"]

    if file.filename == "":
        return redirect("/teacher_dashboard")

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    conn = get_db()
    conn.execute(
        "INSERT INTO materials(title, filename, class_code, uploaded_at) VALUES(?,?,?,?)",
        (title, file.filename, session["class_code"], datetime.now())
    )
    conn.commit()

    return redirect("/teacher_dashboard")










#---------- VIEW MATERIAL ---------

@app.route("/view_material/<int:material_id>")
def view_material(material_id):

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()

    material = conn.execute(
        "SELECT * FROM materials WHERE id=?",
        (material_id,)
    ).fetchone()

    if not material:
        return "Not found"

    # 🔒 SECURITY CHECK (VERY IMPORTANT)
    if material["class_code"] != session["class_code"]:
        return "Unauthorized"

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], material["filename"])

    from flask import send_file
    return send_file(filepath)
  






#---------- DELETE MATERIAL ---------

@app.route("/delete_material/<int:material_id>")
def delete_material(material_id):

    if "role" not in session or session["role"] != "teacher":
        return "Unauthorized"

    conn = get_db()
 
    material = conn.execute(
        "SELECT * FROM materials WHERE id=?",
        (material_id,)
    ).fetchone()

    if not material:
        return redirect("/teacher_dashboard")

    # delete file from folder
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], material["filename"])
    if os.path.exists(filepath):
        os.remove(filepath)

    # delete from DB
    conn.execute("DELETE FROM materials WHERE id=?", (material_id,))
    conn.commit()

    return redirect("/teacher_dashboard")







#---------- STUDENT MATERIALS ---------

@app.route("/materials")
def student_materials():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()

    materials = conn.execute(
        "SELECT * FROM materials WHERE class_code=? ORDER BY id DESC",
        (session["class_code"],)
    ).fetchall()

    return render_template("student_materials.html", materials=materials)








#---------- DOWNLOAD MATERIAL ---------

@app.route("/download_material/<int:material_id>")
def download_material(material_id):

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()

    material = conn.execute(
        "SELECT * FROM materials WHERE id=?",
        (material_id,)
    ).fetchone()

    if not material:
        return "Not found"

    if material["class_code"] != session["class_code"]:
        return "Unauthorized"

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], material["filename"])

    from flask import send_file
    return send_file(filepath, as_attachment=True)










#---------- EDIT MATERIAL ---------

@app.route("/edit_material/<int:material_id>", methods=["POST"])
def edit_material(material_id):

    if "role" not in session or session["role"] != "teacher":
        return "Unauthorized"

    new_title = request.form["title"]

    conn = get_db()

    conn.execute(
        "UPDATE materials SET title=? WHERE id=?",
        (new_title, material_id)
    )

    conn.commit()

    return redirect("/teacher_dashboard")








# ---------------- STUDY TIMER ----------------

@app.route("/study")
def study():
    if "user_id" not in session:
        return redirect("/login")
    if session.get("role") != "student":
        return redirect("/teacher_dashboard")

    return render_template("study.html")


@app.route("/music_player")
def music_player():
    if "user_id" not in session:
        return redirect("/login")
    if session.get("role") != "student":
        return redirect("/teacher_dashboard")

    return render_template("music_player.html")









# ---------------- STUDYAI ----------------

@app.route("/studyai")
def studyai():
    if "user_id" not in session:
        return redirect("/login")
    if session.get("role") != "student":
        return redirect("/teacher_dashboard")

    return render_template("studyai.html")









#---------- START STUDY ---------

@app.route("/start_study")
def start_study():

    if "user_id" not in session:
        return "no"

    conn = get_db()

    existing = conn.execute(
        "SELECT * FROM active_sessions WHERE user_id=?",
        (session["user_id"],)
    ).fetchone()

    if existing:
        conn.execute(
            "UPDATE active_sessions SET last_update=? WHERE user_id=?",
            (datetime.now(), session["user_id"])
        )
    else:
        conn.execute(
            "INSERT INTO active_sessions(user_id,seconds,last_update) VALUES(?,?,?)",
            (session["user_id"], 0, datetime.now())
        )

    conn.commit()

    return "started"









#---------- PAUSE STUDY ---------

@app.route("/pause_study", methods=["POST"])
def pause_study():

    if "user_id" not in session:
        return "no"

    conn = get_db()

    data = conn.execute(
        "SELECT seconds, last_update FROM active_sessions WHERE user_id=?",
        (session["user_id"],)
    ).fetchone()

    if not data:
        return "no"

    stored_seconds = data["seconds"]
    last_update = data["last_update"]

    if last_update:
        try:
            last_time = datetime.strptime(last_update, "%Y-%m-%d %H:%M:%S.%f")
        except:
            last_time = datetime.strptime(last_update, "%Y-%m-%d %H:%M:%S")

        diff = (datetime.now() - last_time).total_seconds()
        stored_seconds += int(diff)

    conn.execute(
        "UPDATE active_sessions SET seconds=?, last_update=NULL WHERE user_id=?",
        (stored_seconds, session["user_id"])
    )

    conn.commit()

    return "paused"









#---------- STOP STUDY ---------

@app.route("/stop_study", methods=["POST"])
def stop_study():

    if "user_id" not in session:
        return "no"

    conn = get_db()

    data = conn.execute(
        "SELECT seconds, last_update FROM active_sessions WHERE user_id=?",
        (session["user_id"],)
    ).fetchone()

    if not data:
        return "no"

    stored_seconds = data["seconds"]
    last_update = data["last_update"]

    if last_update:
        try:
            last_time = datetime.strptime(last_update, "%Y-%m-%d %H:%M:%S.%f")
        except:
            last_time = datetime.strptime(last_update, "%Y-%m-%d %H:%M:%S")

        diff = (datetime.now() - last_time).total_seconds()
        stored_seconds += int(diff)

    minutes = stored_seconds // 60

    # save session
    conn.execute(
        "INSERT INTO study_sessions(user_id,minutes,date) VALUES(?,?,?)",
        (session["user_id"], minutes, datetime.now().date())
    )

    # delete active session
    conn.execute(
        "DELETE FROM active_sessions WHERE user_id=?",
        (session["user_id"],)
    )

    conn.commit()

    return "saved"







#---------- GET ACTIVE SECONDS ---------

@app.route("/get_active_seconds")
def get_active_seconds():

    if "user_id" not in session:
        return "0"

    conn = get_db()

    data = conn.execute(
        "SELECT seconds, last_update FROM active_sessions WHERE user_id=?",
        (session["user_id"],)
    ).fetchone()

    if data:
        stored_seconds = data["seconds"]
        last_update = data["last_update"]

        if last_update:
            try:
                last_time = datetime.strptime(last_update, "%Y-%m-%d %H:%M:%S.%f")
            except:
                last_time = datetime.strptime(last_update, "%Y-%m-%d %H:%M:%S")
            diff = (datetime.now() - last_time).total_seconds()
            stored_seconds += int(diff)

        return str(stored_seconds)

    return "0"








#---------- ASK GEMINI AI ---------
@app.route("/ask_ai", methods=["POST"])
def ask_ai():
    if "user_id" not in session:
        return Response("Unauthorized", status=401, mimetype="text/plain")

    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()

    if not message:
        return Response("Message is required", status=400, mimetype="text/plain")

    try:
        reply = generate_study_assistant_reply(message)
        return Response(reply, mimetype="text/plain")
    except Exception as exc:
        app.logger.exception("AI request failed")
        status_code = 429 if is_gemini_quota_error(exc) else 500
        return Response(
            f"Study Assistant is unavailable right now: {exc}",
            status=status_code,
            mimetype="text/plain",
        )








#---------- STUDYAI APIs ---------
@app.route("/api/chat", methods=["POST"])
def studyai_chat_api():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()

    if not message:
        return jsonify({"error": "Message is required"}), 400

    try:
        reply = generate_studyai_chat_reply(message)
        return jsonify({"reply": reply})
    except Exception as exc:
        app.logger.exception("StudyAI chat request failed")
        status_code = 429 if is_gemini_quota_error(exc) else 500
        return jsonify({"error": f"StudyAI is unavailable right now: {exc}"}), status_code


@app.route("/api/summarize", methods=["POST"])
def studyai_summarize_api():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    notes = (data.get("notes") or "").strip()

    if not notes:
        return jsonify({"error": "Notes are required"}), 400

    try:
        summary = generate_studyai_summary(notes)
        return jsonify({"result": summary})
    except Exception as exc:
        app.logger.exception("StudyAI summarize request failed")
        status_code = 429 if is_gemini_quota_error(exc) else 500
        return jsonify({"error": f"StudyAI is unavailable right now: {exc}"}), status_code


@app.route("/api/questions", methods=["POST"])
def studyai_questions_api():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    notes = (data.get("notes") or "").strip()

    if not notes:
        return jsonify({"error": "Notes are required"}), 400

    try:
        questions = generate_studyai_questions(notes)
        return jsonify({"result": questions})
    except Exception as exc:
        app.logger.exception("StudyAI question request failed")
        status_code = 429 if is_gemini_quota_error(exc) else 500
        return jsonify({"error": f"StudyAI is unavailable right now: {exc}"}), status_code










# ---------------- CLASS CHAT ROUTE ----------------

@app.route("/class_chat", methods=["GET", "POST"])
def class_chat():
    blocked_words = [
        "fuck","shit","bitch","asshole","sex","nude","porn","xxx",
        "bhenchod","madarchod","gandu","randi","chutiya","loda","chodu","maderchod",
        "behen ke lode","lund","bhosdiwale","gand","randi ka bacha",
        "chutiye","bhosdi ke","lund ke","chutiya ke","madarchod ke", "lode","rape" , "gand"
    ]

    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()
    warning = None

    if request.method == "POST":
        message = request.form.get("message", "")
        clean_msg = message.lower()

        print("CHECKING MESSAGE:", clean_msg)

        #---------- BOT MESSAGE GUARD ---------
        if clean_msg.strip().startswith("@bot"):
            return "BOT_REDIRECT"

        # 🚫 CHECK BAD WORDS
        for word in blocked_words:
            if word in clean_msg:
                return "⚠️ Message blocked due to inappropriate content"

        # ✅ SAVE ONLY CLEAN MESSAGE
        conn.execute(
            "INSERT INTO class_messages(user_id,message,timestamp) VALUES(?,?,?)",
            (session["user_id"], message, datetime.now()),
        )
        conn.commit()

        return "ok"

    # ✅ FETCH ONLY SAME CLASS MESSAGES
    messages = conn.execute(
        """
        SELECT class_messages.*, users.username
        FROM class_messages
        LEFT JOIN users ON users.id = class_messages.user_id
        WHERE users.class_code = ?
        ORDER BY class_messages.id ASC
        """,
        (session["class_code"],),
    ).fetchall()

    # ✅ AJAX REQUEST → return ONLY messages
    if request.args.get("ajax"):
        return render_template("chat_messages.html", messages=messages)

    # ✅ NORMAL PAGE LOAD
    return render_template("class_chat.html", messages=messages, warning=warning)











# ---------------- PRIVATE CHAT ROUTE ----------------

@app.route("/private_chat", methods=["GET", "POST"])
def private_chat():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_db()

    blocked_words = [
        "fuck","shit","bitch","asshole","sex","nude","porn","xxx",
        "bhenchod","madarchod","gandu","randi","chutiya","loda","chodu","maderchod",
        "behen ke lode","lund","bhosdiwale","gand","randi ka bacha",
        "chutiye","bhosdi ke","lund ke","chutiya ke","madarchod ke", "lode","rape", "ma"
    ]

    warning = None

    # GET USERS (same class only)
    users = conn.execute(
        "SELECT id, username FROM users WHERE class_code=? AND id!=? AND role='student'",
        (session["class_code"], session["user_id"]),
    ).fetchall()

    selected_user = request.args.get("user_id")
    messages = []

    if request.method == "POST":
        message = request.form.get("message")

        if not message:
            return redirect(f"/private_chat?user_id={selected_user}")

        clean_msg = message.lower()

        #---------- BOT MESSAGE GUARD ---------
        if clean_msg.strip().startswith("@bot"):
            return "BOT_REDIRECT"

        # 🚫 CHECK BAD WORDS
        for word in blocked_words:
            if word in clean_msg:
                return "⚠️ Message blocked due to inappropriate content"

        # ✅ SAVE MESSAGE (ONLY IF CLEAN)
        conn.execute(
            "INSERT INTO private_messages(sender_id,receiver_id,message,timestamp) VALUES(?,?,?,?)",
            (session["user_id"], selected_user, message, datetime.now()),
        )

        conn.commit()

        return "ok"

    if selected_user:
        # FETCH MESSAGES (2-way)
        messages = conn.execute(
            """
            SELECT private_messages.*, users.username
            FROM private_messages
            JOIN users ON users.id = private_messages.sender_id
            WHERE (sender_id=? AND receiver_id=?)
            OR (sender_id=? AND receiver_id=?)
            ORDER BY id ASC
            """,
            (
                session["user_id"],
                selected_user,
                selected_user,
                session["user_id"],
            ),
        ).fetchall()

    return render_template(
        "private_chat.html",
        users=users,
        messages=messages,
        selected_user=selected_user,
        warning=warning,
    )
    
    
    
    
    
    
    
    
    
    
# --------------- REFRESH PRIVATE CHAT ----------------

@app.route("/get_private_messages")
def get_private_messages():
    if "user_id" not in session:
        return ""

    other_id = request.args.get("user_id")

    conn = get_db()

    messages = conn.execute(
        """
        SELECT private_messages.*, users.username
        FROM private_messages
        JOIN users ON users.id = private_messages.sender_id
        WHERE (sender_id=? AND receiver_id=?)
        OR (sender_id=? AND receiver_id=?)
        ORDER BY id ASC
        """,
        (
            session["user_id"],
            other_id,
            other_id,
            session["user_id"],
        ),
    ).fetchall()

    html = ""
    last_sender = None

    for msg in messages:
        align = "me" if msg["sender_id"] == session["user_id"] else "other"

        if last_sender != msg["sender_id"]:
            html += f"<div class='sender'>{msg['username']}</div>"

        html += f"""
        <div class='message {align}'>
            <div class='bubble'>{msg['message']}</div>
        </div>
        """

        last_sender = msg["sender_id"]

    return html









# ---------------- TEACHER LOGIN ----------------

@app.route("/teacher_login", methods=["GET", "POST"])
def teacher_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()

        teacher = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=? AND role='teacher'",
            (username, password),
        ).fetchone()

        if teacher:
            session["user_id"] = teacher["id"]
            session["class_code"] = teacher["class_code"]
            session["role"] = "teacher"

            return redirect("/teacher_dashboard")

    return render_template("teacher_login.html")










# -------------- HEATMAP ROUTE ----------------

@app.route("/heatmap_data")
def heatmap_data():
    if "user_id" not in session:
        return jsonify({})

    month_heatmap = build_month_heatmap(session["user_id"])
    return jsonify(month_heatmap)










# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")








# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True, port=5001)
