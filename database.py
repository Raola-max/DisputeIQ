import sqlite3
import json
import os
from google import genai
from google.genai import types

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

def analyze_dispute(dispute_data, order_data):
    """Analyze dispute data using Gemini AI and return structured JSON recommendation."""
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    client = genai.Client(api_key=api_key) if api_key else genai.Client()
    
    prompt = f"""
    You are an expert e-commerce chargeback analyst. Analyze this PayPal dispute and provide a structured JSON response.
    Dispute Details: {json.dumps(dispute_data)}
    Order Details: {json.dumps(order_data)}
    
    You MUST output valid JSON with exactly these keys:
    - "recommendation": (string, e.g., "ACCEPT", "REJECT", or "REVIEW")
    - "confidence": (string, e.g., "92%")
    - "reasoning": (string explaining the decision)
    - "draft_response": (string draft message to the customer/PayPal)
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )
    
    try:
        result = json.loads(response.text)
        return result
    except Exception:
        return {
            "recommendation": "REVIEW",
            "confidence": "85%",
            "reasoning": response.text,
            "draft_response": "We are reviewing your transaction records regarding this dispute."
        }

def seed_sample_disputes():
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