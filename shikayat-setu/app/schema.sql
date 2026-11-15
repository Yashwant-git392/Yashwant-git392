-- Campus Shikayat Setu -- College Grievance Redressal System
-- SPPU MCA-I (Sem-I) Application Development mini project
-- Creator: Yashwant Santosh Ahire
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS departments (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE,
    head_name   TEXT NOT NULL,
    email       TEXT NOT NULL,
    location    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS categories (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    name             TEXT NOT NULL UNIQUE,
    department_id    INTEGER NOT NULL REFERENCES departments(id) ON DELETE CASCADE,
    default_priority TEXT NOT NULL CHECK (default_priority IN ('High','Medium','Low')),
    keywords         TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    role          TEXT NOT NULL CHECK (role IN ('student','officer','admin')),
    username      TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    full_name     TEXT NOT NULL,
    roll_no       TEXT UNIQUE,                      -- students only
    phone         TEXT,
    department_id INTEGER REFERENCES departments(id), -- officers only
    status        TEXT NOT NULL DEFAULT 'Active' CHECK (status IN ('Active','Inactive')),
    created_at    TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);

CREATE TABLE IF NOT EXISTS complaints (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    code          TEXT NOT NULL UNIQUE,             -- CMP-YYYY-NNNN
    student_id    INTEGER NOT NULL REFERENCES users(id),
    category_id   INTEGER NOT NULL REFERENCES categories(id),
    department_id INTEGER NOT NULL REFERENCES departments(id),
    title         TEXT NOT NULL,
    description   TEXT NOT NULL,
    location      TEXT NOT NULL DEFAULT '',
    priority      TEXT NOT NULL CHECK (priority IN ('High','Medium','Low')),
    routing       TEXT NOT NULL DEFAULT 'auto' CHECK (routing IN ('auto','manual')),
    routing_score INTEGER NOT NULL DEFAULT 0,
    status        TEXT NOT NULL DEFAULT 'Submitted'
                  CHECK (status IN ('Submitted','Acknowledged','In Progress','Resolved','Closed')),
    is_anonymous  INTEGER NOT NULL DEFAULT 0,
    submitted_at  TEXT NOT NULL DEFAULT (datetime('now','localtime')),
    sla_due_at    TEXT NOT NULL,
    resolved_at   TEXT
);
CREATE INDEX IF NOT EXISTS idx_complaints_dept_status ON complaints(department_id, status);
CREATE INDEX IF NOT EXISTS idx_complaints_student     ON complaints(student_id);

CREATE TABLE IF NOT EXISTS complaint_events (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id INTEGER NOT NULL REFERENCES complaints(id) ON DELETE CASCADE,
    event_type   TEXT NOT NULL,    -- routed | acknowledged | status | remark | reassign | escalated | feedback | reopened | closed | created
    note         TEXT NOT NULL DEFAULT '',
    actor_id     INTEGER REFERENCES users(id),
    created_at   TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);
CREATE INDEX IF NOT EXISTS idx_events_complaint ON complaint_events(complaint_id);

CREATE TABLE IF NOT EXISTS feedback (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    complaint_id INTEGER NOT NULL UNIQUE REFERENCES complaints(id) ON DELETE CASCADE,
    rating       INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment      TEXT NOT NULL DEFAULT '',
    created_at   TEXT NOT NULL DEFAULT (datetime('now','localtime'))
);
