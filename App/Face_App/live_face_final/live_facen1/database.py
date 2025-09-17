# database.py

import sqlite3
from datetime import datetime

DB_NAME = 'recognition_logs.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            person_id TEXT,
            name TEXT,
            status TEXT,
            location TEXT,
            company_id TEXT,
            email TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_log(person_id, name, status, location, company_id, email):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute('''
        INSERT INTO logs (timestamp, person_id, name, status, location, company_id, email)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (timestamp, person_id, name, status, location, company_id, email))
    conn.commit()
    conn.close()
    print(f"[DB LOG] {timestamp} - {person_id} - {name} - {status} - {location} - {company_id} - {email}")
