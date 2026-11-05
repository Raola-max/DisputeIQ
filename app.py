import streamlit as st
import requests
import json

# Backend API URL (pointing to your live Render deployment)
BACKEND_URL = "https://disputeiq-5fxz.onrender.com"

st.set_page_config(
    page_title="DisputeIQ Merchant Portal",
    page_icon="🛡️",
    layout="wide"
)

# Custom CSS to make action buttons stand out in red
st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #ff4b4b;
        color: white;
        border-radius: 6px;
        font-weight: bold;
    }
    div.stButton > button:first-child:hover {
        background-color: #ff1a1a;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Header Section
st.title("🛡️ DisputeIQ Merchant Portal")
st.markdown("Automated chargeback resolution powered by Gemini AI.")
st.sidebar.markdown("### Merchant: Raola Store")
st.sidebar.markdown("### Sandbox Mode: Active 🟢")
st.sidebar.markdown(f"**Connected to:** `{BACKEND_URL}`")

st.markdown("---")
st.header("DisputeIQ Dashboard")
st.markdown("Review AI-recommended actions for incoming PayPal disputes. Save time, recover revenue.")

# Fetch disputes from backend
try:
    response = requests.get(f"{BACKEND_URL}/disputes", timeout=10)
    if response.status_code == 200:
        disputes = response.json()
    else:
        disputes = []
        st.error(f"Failed to fetch disputes from backend (Status: {response.status_code})")
except Exception as e:
    disputes = []
    st.error(f"Could not connect to backend server: {e}")

# Separate active and resolved disputes
active_disputes = [d for d in disputes if str(d.get("status", "")).upper() != "RESOLVED"]
resolved_disputes = [d for d in disputes if str(d.get("status", "")).upper() == "RESOLVED"]

# Metrics Overview
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Active Disputes", len(active_disputes))
with col2:
    st.metric("AI Automation Rate", "85%", "+12% this week")
with col3:
    st.metric("Revenue Protected", "$1,450.00", "+$500 today")

st.markdown("---")

# Create Tabs for Active vs Resolved
tab_active, tab_resolved = st.tabs([f"Active Disputes ({len(active_disputes)})", f"Resolved History ({len(resolved_disputes)})"])

with tab_active:
    if not active_disputes:
        st.info(f"No active disputes found. Open `{BACKEND_URL}/seed` in your browser to simulate an incoming PayPal webhook.")
    else:
        for dispute in active_disputes:
            dispute_id = dispute.get("id", "Unknown ID")
            raw_data = dispute.get("data", {})
            
            if isinstance(raw_data, str):
                try:
                    data = json.loads(raw_data)
                except:
                    data = {}
            else:
                data = raw_data if isinstance(raw_data, dict) else {}

            reason = data.get("reason", data.get("reason_code", "Merchandise Not Received"))
            amount_dict = data.get("dispute_amount", {})
            amount = amount_dict.get("value", "150.00")
            currency = amount_dict.get("currency_code", "USD")

            with st.container():
                st.subheader(f"Dispute ID: {dispute_id}")
                st.markdown(f"**Reason:** {reason} | **Amount:** ${amount} {currency}")

                ai_rec_raw = dispute.get("ai_recommendation", {})
                if isinstance(ai_rec_raw, str):
                    try:
                        ai_data = json.loads(ai_rec_raw)
                    except:
                        ai_data = {"reasoning": ai_rec_raw, "draft_response": ai_rec_raw}
                elif isinstance(ai_rec_raw, dict):
                    ai_data = ai_rec_raw
                else:
                    ai_data = {"reasoning": str(ai_rec_raw)}

                rec_raw = ai_data.get("recommendation", "REVIEW")
                rec_type = str(rec_raw).upper() if not isinstance(rec_raw, dict) else "REVIEW"
                confidence = ai_data.get("confidence", "85%")
                reasoning = ai_data.get("reasoning", "Awaiting AI review analysis.")
                draft = ai_data.get("draft_response", "We are reviewing your transaction records.")

                st.markdown(f"🤖 **Gemini AI Recommendation:** {rec_type} (Confidence: {confidence})")

                with st.expander("View AI Reasoning & Draft Response"):
                    st.markdown(f"**Reasoning:**\n{reasoning}")
                    st.markdown(f"**Draft Response:**\n{draft}")

                with st.expander("View Raw PayPal Data"):
                    st.json(data)

                if st.button(f"Take Action (Resolve {dispute_id})", key=f"btn_{dispute_id}"):
                    try:
                        res = requests.post(f"{BACKEND_URL}/resolve/{dispute_id}", json={"action": "RESOLVED"}, timeout=10)
                        if res.status_code == 200:
                            st.success(f"Dispute {dispute_id} resolved successfully!")
                            st.rerun()
                        else:
                            st.error(f"Failed to resolve. Backend said: {res.text}")
                    except Exception as e:
                        st.error(f"Error connecting to backend: {e}")

                st.markdown("---")

with tab_resolved:
    if not resolved_disputes:
        st.info("No resolved chargeback cases yet. Click 'Take Action' on an active dispute to move it here.")
    else:
        for dispute in resolved_disputes:
            dispute_id = dispute.get("id", "Unknown ID")
            raw_data = dispute.get("data", {})
            
            if isinstance(raw_data, str):
                try:
                    data = json.loads(raw_data)
                except:
                    data = {}
            else:
                data = raw_data if isinstance(raw_data, dict) else {}

            reason = data.get("reason", data.get("reason_code", "Merchandise Not Received"))
            amount_dict = data.get("dispute_amount", {})
            amount = amount_dict.get("value", "150.00")
            currency = amount_dict.get("currency_code", "USD")

            with st.container():
                st.subheader(f"Dispute ID: {dispute_id} ✅ (Resolved)")
                st.markdown(f"**Reason:** {reason} | **Amount:** ${amount} {currency}")
                st.markdown(f"**Status:** Successfully processed and closed.")
                
                with st.expander("View Case Details"):
                    st.json(data)
                
                st.markdown("---")