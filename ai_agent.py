import os
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options=types.HttpOptions(timeout=60000) 
)


class DisputeTriage(BaseModel):
    recommendation: str = Field(description="Must be one of: REFUND, FIGHT, or PARTIAL")
    confidence_score: int = Field(description="Confidence score from 0 to 100")
    reasoning: str = Field(description="Short rationale for the triage decision")
    draft_response: str = Field(description="Draft response to send to the customer if we choose to FIGHT")

def analyze_dispute(dispute_data: dict, order_data: dict) -> str:
    prompt = f"""
    You are an expert dispute resolution analyst for an e-commerce merchant. Analyze the following dispute and order details.
    
    DISPUTE DATA:
    {dispute_data}
    
    ORIGINAL ORDER DATA:
    {order_data}
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-3.5-flash-lite',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=DisputeTriage,
                temperature=0.2, 
            ),
        )
        return response.text
    except Exception as e:
        return f'{{"error": "Error analyzing dispute: {str(e)}"}}'