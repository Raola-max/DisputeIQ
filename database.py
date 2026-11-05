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

def seed_sample_disputes():
    """Seed sample test disputes into the database with structured AI triage JSON."""
    sample_id = "PP-D-101"
    sample_data = {
        "dispute_id": sample_id,
        "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
        "dispute_amount": {"value": "150.00", "currency_code": "USD"}
    }
    
    
    sample_rec = json.dumps({
        "recommendation": "ACCEPT",
        "confidence": "92%",
        "reasoning": "Tracking info shows delivery failure at the destination sorting facility.",
        "draft_response": "Hello, we sincerely apologize for the delivery delay. Tracking records confirm a carrier exception. We have processed a full refund for your order of $150.00."
    })
    
    save_dispute(sample_id, sample_data, sample_rec)

init_db()