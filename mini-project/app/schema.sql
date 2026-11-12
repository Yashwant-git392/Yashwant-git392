-- SmartLibrary — College Library Management System
-- SPPU MCA-I (Sem-I) Mini Project — Dr. B. V. Hiray College of Management and Research Centre, Malegaon

CREATE TABLE IF NOT EXISTS admin (
    admin_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    full_name     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS book (
    book_id            INTEGER PRIMARY KEY AUTOINCREMENT,
    isbn               TEXT NOT NULL UNIQUE,
    title              TEXT NOT NULL,
    author             TEXT NOT NULL,
    publisher          TEXT,
    category           TEXT NOT NULL,
    edition            TEXT,
    quantity           INTEGER NOT NULL CHECK (quantity >= 0),
    available_quantity INTEGER NOT NULL CHECK (available_quantity >= 0),
    shelf_location     TEXT,
    added_on           TEXT NOT NULL DEFAULT (date('now'))
);

CREATE TABLE IF NOT EXISTS member (
    member_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_no         TEXT NOT NULL UNIQUE,
    name            TEXT NOT NULL,
    email           TEXT NOT NULL UNIQUE,
    phone           TEXT NOT NULL,
    department      TEXT NOT NULL,
    semester        TEXT NOT NULL,
    membership_type TEXT NOT NULL DEFAULT 'Student' CHECK (membership_type IN ('Student','Faculty')),
    status          TEXT NOT NULL DEFAULT 'Active'  CHECK (status IN ('Active','Inactive')),
    joined_on       TEXT NOT NULL DEFAULT (date('now'))
);

CREATE TABLE IF NOT EXISTS issue_transaction (
    issue_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id     INTEGER NOT NULL REFERENCES book(book_id)   ON DELETE CASCADE,
    member_id   INTEGER NOT NULL REFERENCES member(member_id) ON DELETE CASCADE,
    issue_date  TEXT NOT NULL,
    due_date    TEXT NOT NULL,
    return_date TEXT,
    status      TEXT NOT NULL DEFAULT 'Issued' CHECK (status IN ('Issued','Returned')),
    fine_amount REAL NOT NULL DEFAULT 0 CHECK (fine_amount >= 0)
);

CREATE INDEX IF NOT EXISTS idx_txn_status  ON issue_transaction(status);
CREATE INDEX IF NOT EXISTS idx_txn_due     ON issue_transaction(due_date);
CREATE INDEX IF NOT EXISTS idx_book_title  ON book(title);
CREATE INDEX IF NOT EXISTS idx_member_roll ON member(roll_no);
