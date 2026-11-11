"""Database layer for Campus Shikayat Setu (SQLite, zero-configuration)."""
import os
import sqlite3
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

import routing

DB_PATH = os.environ.get("SHIKAYAT_DB", os.path.join(os.path.dirname(__file__), "shikayat_setu.db"))
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema = f.read()
    conn = get_conn()
    conn.executescript(schema)
    conn.close()


DEPARTMENTS = [  # (name, head, email, location)
    ("Hostel Office",              "Mrs. S. Kulkarni",  "hostel@bvhrcet.ac.in",  "Hostel Block A, Ground Floor"),
    ("IT & Computer Labs",         "Mr. R. Pawar",      "itlabs@bvhrcet.ac.in",  "Computer Block, 2nd Floor"),
    ("Sanitation & Maintenance",   "Mr. V. Gade",       "maintenance@bvhrcet.ac.in", "Maintenance Office, Main Gate"),
    ("Examination Cell",           "Mrs. A. Borse",     "examcell@bvhrcet.ac.in", "Administrative Block, 1st Floor"),
    ("Security & Student Welfare", "Mr. D. Shinde",     "welfare@bvhrcet.ac.in",  "Main Building, Reception"),
    ("General & Administration",   "Mrs. P. Jagtap",    "admin@bvhrcet.ac.in",    "Administrative Block, Ground Floor"),
]

# (category, dept_index, default_priority, keywords)
CATEGORIES = [
    ("Ragging & Harassment", 4, "High", "ragging, harass, bullying, misbehave, threat, eve teasing, intimid"),
    ("Electrical & Safety",  2, "Medium", "fan, light, tube, wiring, switch, socket, electrical, shock, short circuit, power failure, voltage"),
    ("Water & Plumbing",     2, "Medium", "leak, pipe, tap, water, drain, toilet, washroom, bathroom, flush, sewage, tap leaking"),
    ("IT & Network",         1, "Medium", "computer, pc, wifi, network, internet, projector, printer, lab, software, login, portal, server, printer not"),
    ("Hostel Room & Mess",   0, "Medium", "hostel, room, bed, mess, food, canteen food, curfew, outpass, roommate, blanket, hostel mess, geyser"),
    ("Classroom Facility",   2, "Low",    "bench, desk, chair, classroom, board, chalk, door, window, sweeper, cleaning, dustbin"),
    ("Examination & Marks",  3, "High",   "exam, marks, admit card, hall ticket, result, grade, revaluation, rechecking, certificate, transcript, degree"),
    ("Fees & Finance",       3, "Medium", "fees, receipt, scholarship, payment, concession, fine receipt, challan"),
    ("Library & Reading Room", 5, "Low",  "library, book issue, book return, reading room, library card, overdue"),
    ("Academics & Faculty",  5, "Low",    "syllabus, lecture, faculty, professor, notes, assignment, class cancellation, timetable"),
    ("Sports & Activities",  4, "Low",    "sports, ground, equipment, tournament, gym, playground"),
    ("Security & Gate Pass", 4, "Medium", "gate, security, entry, visitor, gate pass, theft, lost, stolen"),
    ("Health & Canteen",     0, "High",   "food poisoning, canteen, hygiene, medicine, sick, injury, first aid, sick room, canteen food spoiled"),
    ("Canteen & Food",       5, "Medium", "canteen, food quality, snacks, canteen price, tea, menu"),
    ("General Query / Other",5, "Low",    "general, other, query, suggestion, feedback, information, help"),
]

STUDENTS = [  # roll, name, email, phone
    ("MCA2026001", "Yashwant Santosh Ahire", "yashwant.ahire@bvhrcet.ac.in",      "9876543201"),
    ("MCA2026002", "Priya Patil",            "priya.patil@bvhrcet.ac.in",         "9823456701"),
    ("MCA2026003", "Rohit Deshmukh",         "rohit.d@bvhrcet.ac.in",             "9912345602"),
    ("MCA2026004", "Snehal Jadhav",          "snehal.j@bvhrcet.ac.in",            "9765432103"),
    ("MCA2026005", "Aishwarya Gaikwad",      "aish.g@bvhrcet.ac.in",              "9654321076"),
    ("MCA2026006", "Suraj Pawar",            "suraj.p@bvhrcet.ac.in",             "9543210987"),
    ("MCA2026007", "Vaishnavi Kulkarni",     "vai.k@bvhrcet.ac.in",               "9432109876"),
    ("MCA2026008", "Tejas Waghmare",         "tejas.w@bvhrcet.ac.in",             "9321098760"),
]

# (student_idx, category_idx, title, description, location, submitted_offset_days, hour, status, resolution)
# resolution: None | (resolved_offset_days_or_None, remark).  Negative offset = in the past.
COMPLAINTS = [
    # --- resolved & closed, with feedback-worthy resolutions
    (1, 2, "Leaking washroom tap, 2nd floor", "The cold-water tap in the washroom near MCA-I classroom leaks continuously; floor is wet and slippery.", "Washroom, 2nd Floor", -38, 10, "Closed", (-37, "Tap replaced by plumber on the same day."), 5, "Fixed quickly, thank you."),
    (0, 3, "Projector not working in Lab 3", "The projector in Computer Lab 3 does not power on; we have lectures every morning.", "Lab 3, Computer Block", -33, 11, "Closed", (-32, "Lamp replaced; tested with HDMI."), 5, "Perfect."),
    (2, 1, "Tube light fused in classroom 2-B", "Two tube lights above the back bench are fused.", "Classroom 2-B", -29, 9, "Closed", (-28, "Both tubes replaced."), 4, "Good but took one extra day."),
    (3, 6, "Marks not shown in ERP for Paper-III", "Internal marks for Application Development are missing on the ERP portal.", "Examination Cell", -26, 15, "Closed", (-24, "Marks uploaded after moderation sheet was matched."), 5, "Resolved."),
    (4, 5, "Bench broken in classroom 1-C", "The bench near the door wobbles; screws are loose.", "Classroom 1-C", -22, 13, "Closed", (-20, "Screws tightened; one plank replaced."), 4, None),
    # --- resolved, awaiting student confirmation
    (5, 4, "Mess food quality poor this week", "Rice is undercooked and dal is too salty since Monday. The whole hostel is unhappy.", "Hostel Block A Mess", -12, 8, "Resolved", (-10, "Mess contractor warned; menu revised with supervisor."), None, None),
    (6, 11, "Gate pass lost near main gate", "Lost my gate pass yesterday evening; kindly deactivate it.", "Main Gate", -8, 19, "Resolved", (-7, "Old pass deactivated; new pass issued at welfare office."), None, None),
    (7, 2, "Toilet flush not working, hostel 2nd floor", "Flush in the common toilet on 2nd floor has not worked for two days.", "Hostel Block B, 2nd Floor", -6, 7, "Resolved", (-5, "Flush valve replaced."), None, None),
    (0, 10, "Sports ground floodlit fused", "Two floodlights on the volleyball side are fused; evening practice is not possible.", "Sports Ground", -5, 17, "Resolved", (-4, "Floodlight fixtures repaired."), None, None),
    # --- in progress (some overdue)
    (1, 1, "Corridor lights fused on ground floor", "Three corridor lights near the admin wing are fused; corridor is dark after 6 pm.", "Admin Wing, Ground Floor", -9, 18, "In Progress", None, None, None),
    (2, 3, "Wi-Fi in library wing not reachable", "The library Wi-Fi SSID disappears after every class hour; the router needs attention.", "Library, 1st Floor", -7, 12, "In Progress", None, None, None),
    (3, 4, "Water geyser not heating, room 214", "The geyser in hostel room 214 stopped heating yesterday.", "Room 214, Hostel Block B", -4, 22, "In Progress", None, None, None),
    (4, 6, "Revaluation result pending since June", "Applied for revaluation; the updated marks still show the old ones.", "Examination Cell", -3, 14, "In Progress", None, None, None),
    (5, 12, "Canteen food hygiene complaint", "Yesterday evening at canteen, the samosas smelled stale. Food poisoning risk for all students.", "Main Canteen", -2, 20, "In Progress", None, None, None),
    (6, 0, "Ragging in hostel staircase", "Seniors passed comments and pushed a junior near staircase S-2 last night. This must stop.", "Staircase S-2, Hostel Block A", -1, 23, "In Progress", None, None, None),
    # --- acknowledged
    (7, 3, "Lab 1 software crash on opening ERP", "Firefox crashes whenever the ERP portal is opened on the Lab 1 Windows image.", "Lab 1, Computer Block", -2, 10, "Acknowledged", None, None, None),
    (0, 9, "Syllabus uploaded for Sem-II not opening", "The Sem-II syllabus PDF on the ERP shows a download error.", "ERP Portal", -1, 9, "Acknowledged", None, None, None),
    (1, 11, "Visitor without pass at girls' hostel", "An unidentified visitor was seen near the girls' hostel entry at 8:30 pm.", "Girls' Hostel Entry", -1, 21, "Acknowledged", None, None, None),
    (2, 7, "Scholarship concession receipt not generated", "Paid fees with scholarship concession; receipt not generated even after 5 days.", "Fees Office", -1, 11, "Acknowledged", None, None, None),
    # --- submitted recently
    (3, 1, "Fan regulator not working, MCA-I", "Fan regulator in classroom 3-A turned off level 0; fan speed stuck at full.", "Classroom 3-A", 0, 8, "Submitted", None, None, None),
    (4, 2, "Leaking pipe, parking shed", "Water drips from the pipe above the bicycle parking shed.", "Bicycle Parking", 0, 9, "Submitted", None, None, None),
    (5, 8, "Unable to renew library card", "The ERP shows 'card expired'; the library renewal counter could not complete it.", "Library", 0, 10, "Submitted", None, None, None),
    (6, 9, "Extra class timings not notified", "Monday's extra Application Development class was not notified anywhere.", "Notice Board, MCA-I", 0, 12, "Submitted", None, None, None),
    (7, 5, "Dustbin overflowing, main corridor", "Dustbin near the main corridor entrance has not been emptied for two days.", "Main Corridor", 0, 13, "Submitted", None, None, None),
    # --- older generic ones (pendency spread)
    (0, 14, "Request for extra library hours", "Please extend library hours till 9 pm during exam season; everyone benefits.", "Library", -45, 19, "Resolved", (-41, "Library extended to 9 pm for December exam window."), None, None),
    (1, 11, "ID card correction on ERP", "My date of birth on the ERP ID card is wrong (shows 2004 instead of 2005).", "Student Section", -31, 16, "Resolved", (-29, "DOB corrected after document verification."), None, None),
    (2, 2, "Water cooler not cooling, near gym", "The water cooler near the gym dispenses warm water.", "Gym Corridor", -17, 15, "In Progress", None, None, None),
    (3, 10, "Volleyball posts loosely fitted", "Both volleyball posts near the court base wobble; safety risk.", "Sports Ground", -11, 17, "Acknowledged", None, None, None),
    (4, 7, "Fine receipt mismatch for hostel fees", "Paid ₹18,500 at the fee counter; receipt shows ₹15,000.", "Fees Office", -27, 12, "Closed", (-25, "Receipt re-issued after accounts verification."), 5, "Rectified, thank you."),
    (5, 3, "ERP login failing for few students", "Roll numbers MCA2026xx fail to log in to the ERP since yesterday.", "ERP Portal", -2, 15, "Acknowledged", None, None, None),
    (6, 12, "Sick room medicines expired", "First-aid box in the sick room contains expired medicines. This is a health risk for all students.", "Sick Room", -19, 9, "Resolved", (-17, "Expired medicines replaced; first-aid audit monthly."), None, None),
    (7, 4, "Block outpass not issued for Sunday", "Sunday outpass list shows my name missing even after applying on time.", "Hostel Office", -16, 10, "Resolved", (-14, "Name added; outpass desk process revised."), None, None),
]


def seed_if_empty():
    conn = get_conn()
    if conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"] > 0:
        conn.close()
        return

    now = datetime.now()

    def ts(offset_days, hour):
        d = now + timedelta(days=offset_days)
        return d.replace(hour=hour, minute=(13 * hour + 7) % 60, second=0, microsecond=0).strftime("%Y-%m-%d %H:%M:%S")

    # departments
    dept_ids = {}
    for name, head, email, loc in DEPARTMENTS:
        cur = conn.execute("INSERT INTO departments (name, head_name, email, location) VALUES (?,?,?,?)",
                           (name, head, email, loc))
        dept_ids[name] = cur.lastrowid

    # categories
    cat_ids = {}
    for name, di, prio, kw in CATEGORIES:
        cur = conn.execute(
            "INSERT INTO categories (name, department_id, default_priority, keywords) VALUES (?,?,?,?)",
            (name, list(dept_ids.values())[di], prio, kw))
        cat_ids[name] = cur.lastrowid

    # users: admin, one officer per department, students
    pw = generate_password_hash("admin123")
    conn.execute("INSERT INTO users (role, username, password_hash, full_name, status) VALUES ('admin','admin',?,?, 'Active')",
                 (pw, "System Administrator"))
    officer_ids = []
    officer_names = ["hostel.officer", "it.officer", "maint.officer", "exam.officer", "welfare.officer", "admin.officer"]
    dept_values = list(dept_ids.values())
    for (name, head, _e, _l), uname in zip(DEPARTMENTS, officer_names):
        cur = conn.execute(
            "INSERT INTO users (role, username, password_hash, full_name, department_id, status) VALUES ('officer',?,?,?,?, 'Active')",
            (uname, generate_password_hash("officer123"), head, dept_values[DEPARTMENTS.index(next(d for d in DEPARTMENTS if d[0] == name))]))
        officer_ids.append(cur.lastrowid)

    student_ids = []
    for roll, name, email, phone in STUDENTS:
        cur = conn.execute(
            "INSERT INTO users (role, username, password_hash, full_name, roll_no, phone, status) VALUES ('student',?,?,?,?,?, 'Active')",
            (roll, generate_password_hash("student123"), name, roll, phone))
        student_ids.append(cur.lastrowid)

    dept_of_category = {}
    for name, di, _p, _k in CATEGORIES:
        dept_of_category[name] = list(dept_ids.values())[di]

    cat_by_name = {}
    for name, di, prio, kw in CATEGORIES:
        cat_by_name[name] = conn.execute("SELECT * FROM categories WHERE name=?", (name,)).fetchone()

    # complaints
    for (si, ci, title, desc, loc, off, hour, status, resolution, rating, fb_comment) in COMPLAINTS:
        cat_name = CATEGORIES[ci][0]
        cat = cat_by_name[cat_name]
        dept_id = dept_of_category[cat_name]
        submitted = datetime.strptime(ts(off, hour), "%Y-%m-%d %H:%M:%S")
        # route competition scoring for audit realism
        text = routing.route_text(title, desc)
        score = routing.score_category(text, cat["keywords"])
        priority = routing.assign_priority(cat["default_priority"], title, desc)
        due = submitted + timedelta(hours=routing.SLA_HOURS[priority])
        cur = conn.execute(
            """INSERT INTO complaints
               (code, student_id, category_id, department_id, title, description, location, priority,
                routing, routing_score, status, is_anonymous, submitted_at, sla_due_at, resolved_at)
               VALUES ('TMP-' || lower(hex(randomblob(4))),?,?,?,?,?,?,?,'auto',?,?,?,?,?,?)""",
            (student_ids[si], cat["id"], dept_id, title, desc, loc, priority, score, status,
             1 if (si == 5 and ci == 0) else 0,   # the ragging complaint is anonymous
             submitted.strftime("%Y-%m-%d %H:%M:%S"), due.strftime("%Y-%m-%d %H:%M:%S"),
             datetime.strptime(ts(resolution[0], hour), "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S") if resolution else None))
        cid = cur.lastrowid
        code = f"CMP-{submitted.year}-{cid:04d}"
        conn.execute("UPDATE complaints SET code=? WHERE id=?", (code, cid))
        # events: routing always; status transitions per current state
        conn.execute("INSERT INTO complaint_events (complaint_id, event_type, note, actor_id, created_at) VALUES (?,?,?,?,?)",
                     (cid, "routed", f"Auto-routed to {cat['name']} → score {score}", None, submitted.strftime("%Y-%m-%d %H:%M:%S")))
        if status in ("Acknowledged", "In Progress", "Resolved", "Closed"):
            ack_time = submitted + timedelta(hours=2)
            officer = conn.execute("SELECT id FROM users WHERE role='officer' AND department_id=?", (dept_id,)).fetchone()
            conn.execute("INSERT INTO complaint_events (complaint_id, event_type, note, actor_id, created_at) VALUES (?,?,?,?,?)",
                         (cid, "acknowledged", "Complaint acknowledged by department.", officer["id"], ack_time.strftime("%Y-%m-%d %H:%M:%S")))
        if status in ("In Progress", "Resolved", "Closed"):
            ip_time = submitted + timedelta(hours=6)
            officer = conn.execute("SELECT id FROM users WHERE role='officer' AND department_id=?", (dept_id,)).fetchone()
            conn.execute("INSERT INTO complaint_events (complaint_id, event_type, note, actor_id, created_at) VALUES (?,?,?,?,?)",
                         (cid, "status", "Work started on the complaint.", officer["id"], ip_time.strftime("%Y-%m-%d %H:%M:%S")))
        if resolution:
            res_time = datetime.strptime(ts(resolution[0], hour), "%Y-%m-%d %H:%M:%S")
            officer = conn.execute("SELECT id FROM users WHERE role='officer' AND department_id=?", (dept_id,)).fetchone()
            conn.execute("INSERT INTO complaint_events (complaint_id, event_type, note, actor_id, created_at) VALUES (?,?,?,?,?)",
                         (cid, "status", f"Resolved — {resolution[1]}", officer["id"], res_time.strftime("%Y-%m-%d %H:%M:%S")))
        if status == "Closed":
            close_time = datetime.strptime(ts(resolution[0], hour), "%Y-%m-%d %H:%M:%S") + timedelta(days=1)
            conn.execute("INSERT INTO complaint_events (complaint_id, event_type, note, actor_id, created_at) VALUES (?,?,?,?,?)",
                         (cid, "closed", "Student confirmed resolution. Complaint closed.", student_ids[si], close_time.strftime("%Y-%m-%d %H:%M:%S")))
        if rating:
            conn.execute("INSERT INTO feedback (complaint_id, rating, comment, created_at) VALUES (?,?,?,?)",
                         (cid, rating, fb_comment or "", (datetime.strptime(ts(resolution[0], hour), "%Y-%m-%d %H:%M:%S") + timedelta(days=1)).strftime("%Y-%m-%d")))

    conn.commit()
    conn.close()


def reset_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()
    seed_if_empty()
