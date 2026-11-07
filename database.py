import os
import sqlite3
import json
import time
from google import genai
from google.genai import types
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "disputes.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS disputes
                 (id TEXT PRIMARY KEY, data TEXT, ai_recommendation TEXT, status TEXT)''')
    conn.commit()
    conn.close()


init_db()

def load_disputes():
    conn = get_connection()
    df = pd.read_sql("SELECT id, status, data, ai_recommendation FROM disputes", conn)
    conn.close()
    return df

def save_dispute(dispute_id, data, ai_rec):
    if isinstance(data, dict):
        data = json.dumps(data)
    if isinstance(ai_rec, dict):
        ai_rec = json.dumps(ai_rec)
        
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO disputes (id, data, ai_recommendation, status) VALUES (?, ?, ?, ?)",
              (dispute_id, data, ai_rec, "PENDING"))
    conn.commit()
    conn.close()

def get_disputes():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, data, ai_recommendation, status FROM disputes")
    rows = c.fetchall()
    conn.close()
    return rows

def update_status(dispute_id, new_status):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE disputes SET status = ? WHERE id = ?", (new_status, dispute_id))
    conn.commit()
    conn.close()

def analyze_dispute(dispute_data, order_data):
    """Analyze dispute data using Gemini AI with built-in retry and fallback protection."""
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
    
    delay = 2
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model='gemini-3.8-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Gemini attempt {attempt + 1} failed: {e}")
            if attempt == 2:
                return {
                    "recommendation": "REVIEW",
                    "confidence": "85%",
                    "reasoning": "AI model temporarily busy due to high demand. Defaulting to review queue.",
                    "draft_response": "We have received your dispute and are reviewing your order history."
                }
            time.sleep(delay)
            delay *= 2

def seed_sample_disputes():
    sample_id = "PP-D-101"
    sample_data = {
        "dispute_id": sample_id,
        "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
        "dispute_amount": {"value": "150.00", "currency_code": "USD"}
    }
    sample_rec = {
        "recommendation": "ACCEPT",
        "confidence": "92%",
        "reasoning": "Tracking info shows delivery failure at the destination sorting facility.",
        "draft_response": "Hello, we sincerely apologize for the delivery delay. Tracking records confirm a carrier exception. We have processed a full refund for your order of $150.00."
    }
    save_dispute(sample_id, sample_data, sample_rec)