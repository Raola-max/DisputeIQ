import streamlit as st
import httpx
import json


st.set_page_config(page_title="DisputeIQ | PayPal AI", page_icon="🛡️", layout="wide")


BACKEND_URL = st.secrets.get("BACKEND_URL", "http://localhost:8000")


with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/b/b5/PayPal.svg", width=150)
    st.markdown("### DisputeIQ Merchant Portal")
    st.markdown("Automated chargeback resolution powered by Gemini AI.")
    st.divider()
    st.markdown("**Merchant:** Raola Store")
    st.markdown("**Sandbox Mode:** Active 🟢")


st.title("🛡️ DisputeIQ Dashboard")
st.markdown("Review AI-recommended actions for incoming PayPal disputes. Save time, recover revenue.")


try:
    response = httpx.get(f"{BACKEND_URL}/disputes", timeout=30.0)
    disputes = response.json()
except Exception as e:
    st.error(f"Could not connect to backend at {BACKEND_URL}. Error: {e}")
    disputes = []


if disputes is None:
    disputes = []


col1, col2, col3 = st.columns(3)
active_disputes = [d for d in disputes if d["status"] != "RESOLVED"]
col1.metric(label="Active Disputes", value=len(active_disputes))
col2.metric(label="AI Automation Rate", value="85%", delta="+12% this week")
col3.metric(label="Revenue Protected", value="$1,450.00", delta="+$500 today")
st.divider()

if not disputes:
    st.info(f"No active disputes found. Go to `{BACKEND_URL}/seed` to simulate an incoming PayPal webhook.")
else:
    for dispute in disputes:
        d_id = dispute["id"]
        data = dispute["data"]
        ai_rec = dispute["ai_recommendation"]
        status = dispute["status"]
        
        reason = data.get("reason", "UNKNOWN").replace("_", " ").title()
        amount_data = data.get("dispute_amount", {})
        amount = amount_data.get("value", "0.00")
        
        with st.container(border=True):
            col_info, col_action = st.columns([2, 1])
            
            with col_info:
                st.subheader(f"Dispute ID: {d_id}")
                st.write(f"**Reason:** {reason} | **Amount:** ${amount}")
                
                
                if "REFUND" in ai_rec.upper():
                    st.error("🤖 **Gemini AI Recommendation: FULL REFUND**")
                elif "FIGHT" in ai_rec.upper():
                    st.success("🤖 **Gemini AI Recommendation: FIGHT DISPUTE**")
                else:
                    st.warning("🤖 **Gemini AI Recommendation: PARTIAL REFUND / REVIEW**")
                
                with st.expander("View AI Reasoning & Draft Response"):
                    st.write(ai_rec)
                with st.expander("View Raw PayPal Data"):
                    st.json(data)
            
            with col_action:
                st.markdown("### Take Action")
                if status != "RESOLVED":
                    if st.button("✅ Execute AI Recommendation", type="primary", use_container_width=True, key=f"res_{d_id}"):
                        with st.spinner("Calling PayPal Disputes API..."):
                            try:
                                
                                httpx.post(f"{BACKEND_URL}/resolve/{d_id}", timeout=30.0)
                                st.success("Successfully resolved via PayPal!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed to resolve: {e}")
                else:
                    st.success("✅ Resolved via API")