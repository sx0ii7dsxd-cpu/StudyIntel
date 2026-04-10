import sqlite3

conn = sqlite3.connect("users.db")

# USERS
conn.execute(
    """
    CREATE TABLE users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        role TEXT,
        class_code TEXT
    )
    """
)

# TEACHER PROFILE
conn.execute(
    """
    CREATE TABLE teacher_profiles(
        user_id INTEGER,
        full_name TEXT,
        email TEXT,
        phone TEXT,
        address TEXT,
        aadhaar TEXT
    )
    """
)

# STUDY SESSIONS
conn.execute(
    """
    CREATE TABLE study_sessions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        minutes INTEGER,
        date TEXT
    )
    """
)

# ACTIVE TIMER
conn.execute(
    """
    CREATE TABLE active_sessions(
        user_id INTEGER,
        seconds INTEGER
    )
    """
)

# CLASS CHAT
conn.execute(
    """
    CREATE TABLE class_messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        message TEXT,
        timestamp TEXT
    )
    """
)

# PRIVATE CHAT
conn.execute(
    """
    CREATE TABLE private_messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER,
        receiver_id INTEGER,
        message TEXT,
        timestamp TEXT
    )
    """
)

# MATERIALS
conn.execute(
    """
    CREATE TABLE IF NOT EXISTS materials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        filename TEXT,
        class_code TEXT,
        uploaded_at DATETIME
    )
    """
)
# ---------- LIVE TIMER ----------
try:
    conn.execute("ALTER TABLE active_sessions ADD COLUMN last_update TEXT")
    print("Column added successfully")
except:
    print("Column already exists, skipping...")

conn.commit()
conn.close()
