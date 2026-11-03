from fastapi import FastAPI, Request, HTTPException
from paypal_client import get_access_token, paypal_get
from ai_agent import analyze_dispute
import database
import json
import time
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="DisputeIQ", description="AI-Powered PayPal Dispute Triage")

@app.get("/")
async def root():
    return {"status": "ok", "service": "DisputeIQ"}

@app.get("/health")
async def health():
    try:
        token = await get_access_token()
        return {"paypal_auth": "ok", "token_preview": token[:20] + "..."}
    except Exception as e:
        return {"paypal_auth": "failed", "error": str(e)}

@app.post("/webhook/paypal")
async def paypal_webhook(request: Request):
    body = await request.json()
    event_type = body.get("event_type", "unknown")
    resource = body.get("resource", {})
    
    print(f"\n=== WEBHOOK RECEIVED: {event_type} ===")

    if event_type == "CUSTOMER.DISPUTE.CREATED":
        dispute_id = resource.get("dispute_id")
        print(f"Fetching dispute details for: {dispute_id}")
        
        try:
            
            if "PP-000" in dispute_id:
                dispute_data = resource
                print("Mock ID detected. Using raw webhook data.")
            else:
                dispute_data = await paypal_get(f"/v1/customer/disputes/{dispute_id}")
            
            order_data = {}
            
            print("Sending data to Gemini AI...")
            ai_recommendation = analyze_dispute(dispute_data, order_data)
            
            print("\n=== AI TRIAGE RESULT ===")
            print(ai_recommendation)
            print("========================\n")

            database.save_dispute(dispute_id, dispute_data, ai_recommendation)
            print(f"Saved dispute {dispute_id} to database.")

        except Exception as e:
            print(f"Error processing dispute: {str(e)}")

    return {"received": True}

@app.get("/disputes")
async def get_all_disputes():
    """Fetch all disputes for the Streamlit frontend."""
    disputes = database.get_disputes()
    result = []
    if disputes:
        for d in disputes:
            result.append({
                "id": d[0],
                "data": json.loads(d[1]),
                "ai_recommendation": d[2],
                "status": d[3]
            })
    return result

@app.post("/resolve/{dispute_id}")
async def resolve_dispute(dispute_id: str):
    """Mark a dispute as resolved."""
    database.update_status(dispute_id, "RESOLVED")
    return {"status": "success", "message": f"Dispute {dispute_id} resolved."}

@app.get("/seed")
async def seed_data():
    fake_dispute_id = f"PP-D-{int(time.time())}"
    fake_dispute_data = {
        "dispute_id": fake_dispute_id,
        "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
        "status": "OPEN",
        "dispute_amount": {"currency_code": "USD", "value": "125.00"},
        "disputed_transactions": [{
            "seller_transaction_id": "8AB12345CD678901E",
            "buyer_transaction_id": "9XY98765ZW432109Q",
            "transaction_status": "COMPLETED",
            "item_details": {
                "item_name": "Nike Air Max 270 (Size 10)",
                "item_amount": {"currency_code": "USD", "value": "125.00"}
            }
        }]
    }
    
    try:
        print("Sending mock data to Gemini AI...")
        ai_recommendation = analyze_dispute(fake_dispute_data, {"status": "SHIPPED", "tracking": "1Z999AA10123456784"})
        
        database.save_dispute(fake_dispute_id, fake_dispute_data, ai_recommendation)
        return {"message": "Test dispute generated and saved!", "id": fake_dispute_id}
    except Exception as e:
        return {"error": str(e)}