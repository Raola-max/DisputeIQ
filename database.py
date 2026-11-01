# database.py
import sqlite3
import json

def init_db():
    conn = sqlite3.connect('disputes.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS disputes
                 (id TEXT PRIMARY KEY, data TEXT, ai_recommendation TEXT, status TEXT)''')
    conn.commit()
    conn.close()

def save_dispute(dispute_id, data, ai_rec):
    conn = sqlite3.connect('disputes.db')
    c = conn.cursor()
    # We use INSERT OR REPLACE so if a webhook fires twice, it updates instead of crashing
    c.execute("INSERT OR REPLACE INTO disputes (id, data, ai_recommendation, status) VALUES (?, ?, ?, ?)",
              (dispute_id, json.dumps(data), ai_rec, "PENDING"))
    conn.commit()
    conn.close()

def get_disputes():
    conn = sqlite3.connect('disputes.db')
    c = conn.cursor()
    c.execute("SELECT id, data, ai_recommendation, status FROM disputes")
    rows = c.fetchall()
    conn.close()
    return rows

def update_status(dispute_id, new_status):
    conn = sqlite3.connect('disputes.db')
    c = conn.cursor()
    c.execute("UPDATE disputes SET status = ? WHERE id = ?", (new_status, dispute_id))
    conn.commit()
    conn.close()

# Initialize the DB when this file is imported
init_db()