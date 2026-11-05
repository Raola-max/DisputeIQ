import os
import time
import json
import traceback
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import database

# Load environment variables from .env file for local development
load_dotenv()

app = FastAPI(title="DisputeIQ Backend", version="1.0.0")

# Enable CORS for Streamlit frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database tables on startup
@app.on_event("startup")
def startup_event():
    database.init_db()


def analyze_dispute_with_retry(dispute_data, order_data, max_retries=3):
    delay = 2
    for attempt in range(max_retries):
        try:
            return database.analyze_dispute(dispute_data, order_data)
        except Exception as e:
            error_str = str(e)
            if "503" in error_str or "UNAVAILABLE" in error_str:
                if attempt == max_retries - 1:
                    raise e
                print(f"Gemini overloaded (503). Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                raise e


@app.get("/health")
def health_check():
    return {"status": "ok", "models_loaded": True}


@app.get("/disputes")
async def get_all_disputes():
    """Fetch all disputes for the frontend dashboard as dictionaries."""
    try:
        rows = database.get_disputes()
        disputes = []
        for row in rows:
            raw_data = row[1]
            if isinstance(raw_data, str):
                try:
                    parsed_data = json.loads(raw_data)
                except:
                    parsed_data = raw_data
            else:
                parsed_data = raw_data

            disputes.append({
                "id": row[0],
                "data": parsed_data,
                "ai_recommendation": row[2],
                "status": row[3]
            })
        return disputes
    except Exception as e:
        print(f"Error fetching disputes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/resolve")
async def resolve_dispute(request: Request):
    """Endpoint for Streamlit frontend to update dispute resolution status."""
    try:
        body = await request.json()
        dispute_id = body.get("dispute_id") or body.get("id")
        action = body.get("action", "RESOLVED")
        
        if not dispute_id:
            raise HTTPException(status_code=400, detail="Dispute ID missing in request body")
        
        database.update_status(dispute_id, action)
        print(f"Dispute {dispute_id} updated to status: {action}")
        return {"status": "success", "message": f"Dispute {dispute_id} successfully updated."}
    except Exception as e:
        print(f"Error resolving dispute: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/seed")
def seed_disputes():
    """Seed test disputes into the database with Gemini AI triage."""
    try:
        database.seed_sample_disputes()
        return {"status": "success", "message": "Sample disputes seeded successfully."}
    except Exception as e:
        print(f"Error seeding disputes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhook/paypal")
async def paypal_webhook(request: Request):
    try:
        body = await request.json()
    except Exception as e:
        print(f"Failed to parse incoming webhook JSON: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    event_type = body.get("event_type", "unknown")
    resource = body.get("resource", {})
    
    current_time = datetime.utcnow().isoformat()
    print(f"\n=== WEBHOOK RECEIVED [{current_time}]: {event_type} ===")

    if event_type == "CUSTOMER.DISPUTE.CREATED":
        dispute_id = resource.get("dispute_id") or resource.get("id")
        if not dispute_id:
            print("Error: Dispute ID missing in webhook resource payload.")
            return {"received": True, "warning": "Dispute ID missing"}

        print(f"Fetching dispute details for: {dispute_id}")
        
        try:
            if "PP-000" in dispute_id or "PP-D-" in dispute_id or "PP-WEBHOOK-" in dispute_id:
                dispute_data = resource
                print("Test ID detected. Using raw webhook data.")
            else:
                dispute_data = resource
            
            order_data = {} 
            
            print("Sending data to Gemini AI with retry protection...")
            ai_recommendation = analyze_dispute_with_retry(dispute_data, order_data)
            
            print("\n=== AI TRIAGE RESULT ===")
            print(ai_recommendation)
            print("========================\n")

            database.save_dispute(dispute_id, dispute_data, ai_recommendation)
            print(f"Saved dispute {dispute_id} to database at {current_time}.")

        except Exception as e:
            print(f"Error processing dispute {dispute_id}: {str(e)}")
            traceback.print_exc()

    return {"received": True}