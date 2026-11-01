import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options=types.HttpOptions(timeout=60000) 
)

def analyze_dispute(dispute_data: dict, order_data: dict) -> str:
    prompt = f"""
    You are a dispute resolution analyst for a merchant.
    
    DISPUTE DATA:
    {dispute_data}
    
    ORIGINAL ORDER DATA:
    {order_data}
    
    Based on this, recommend one of: REFUND, FIGHT, or PARTIAL.
    Give a confidence score from 0 to 100.
    Provide a short reasoning.
    Provide a draft response to the customer if we choose to FIGHT.
    """
    try:
        response = client.models.generate_content(
            model='gemini-3.5-flash-lite',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"Error analyzing dispute: {str(e)}"