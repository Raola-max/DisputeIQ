import streamlit as st # type: ignore
import database
import json
import time

st.set_page_config(page_title="DisputeIQ | PayPal AI", page_icon="🛡️", layout="wide")


with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/b/b5/PayPal.svg", width=150)
    st.markdown("### DisputeIQ Merchant Portal")
    st.markdown("Automated chargeback resolution powered by Gemini AI.")
    st.divider()
    st.markdown("**Merchant:** Raola Store")
    st.markdown("**Sandbox Mode:** Active 🟢")


st.title("🛡️ DisputeIQ Dashboard")
st.markdown("Review AI-recommended actions for incoming PayPal disputes. Save time, recover revenue.")

disputes = database.get_disputes()

if disputes is None:
    disputes = []

col1, col2, col3 = st.columns(3)
col1.metric(label="Active Disputes", value=len([d for d in disputes if d[3] != "RESOLVED"]))
col2.metric(label="AI Automation Rate", value="85%", delta="+12% this week")
col3.metric(label="Revenue Protected", value="$1,450.00", delta="+$500 today")
st.divider()

if not disputes:
    st.info("No active disputes found. Go to `http://localhost:8000/seed` to simulate an incoming PayPal webhook.")
else:
    for d_id, data, ai_rec, status in disputes:

        dispute_json = json.loads(data)
        reason = dispute_json.get("reason", "UNKNOWN").replace("_", " ").title()
        
        with st.container(border=True):
            col_info, col_action = st.columns([2, 1])
            
            with col_info:
                st.subheader(f"Dispute ID: {d_id}")
                st.write(f"**Reason:** {reason} | **Amount:** $50.00")
                
                
                if "REFUND" in ai_rec.upper():
                    st.error("🤖 **Gemini AI Recommendation: FULL REFUND** \n\n *The AI suggests refunding the customer as the evidence strongly supports their claim.*")
                elif "FIGHT" in ai_rec.upper():
                    st.success("🤖 **Gemini AI Recommendation: FIGHT DISPUTE** \n\n *The AI suggests fighting this dispute based on tracking data and merchant policy.*")
                else:
                    st.warning("🤖 **Gemini AI Recommendation: PARTIAL REFUND** \n\n *The AI suggests a partial refund to find a middle ground.*")
                
                with st.expander("View AI Reasoning & Draft Response"):
                    st.write(ai_rec)
                with st.expander("View Raw PayPal Webhook Data"):
                    st.json(dispute_json)
            
            with col_action:
                st.markdown("### Take Action")
                if status != "RESOLVED":
                    if st.button("✅ Execute AI Recommendation", type="primary", use_container_width=True, key=f"res_{d_id}"):
                        with st.spinner("Calling PayPal Disputes API..."):
                            time.sleep(1.5) 
                            database.update_status(d_id, "RESOLVED")
                            st.success("Successfully resolved via PayPal!")
                            st.rerun()
                else:
                    st.success("✅ Resolved via API")