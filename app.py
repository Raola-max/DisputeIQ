import streamlit as st
import httpx
import json
import time


st.set_page_config(page_title="DisputeIQ | PayPal AI", page_icon="🛡️", layout="wide")


BACKEND_URL = st.secrets.get("BACKEND_URL", "http://localhost:8000")


with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/b/b5/PayPal.svg", width=150)
    st.markdown("### DisputeIQ Merchant Portal")
    st.markdown("Automated chargeback resolution powered by Gemini AI.")
    st.divider()
    st.markdown("**Merchant:** Raola Store")
    st.markdown("**Sandbox Mode:** Active 🟢")
    st.divider()
    

    if st.button("🔄 Refresh Data & Wake Backend"):
        st.rerun()
        
    st.caption(f"Connected to: {BACKEND_URL}")


st.title("🛡️ DisputeIQ Dashboard")
st.markdown("Review AI-recommended actions for incoming PayPal disputes. Save time, recover revenue.")


disputes = []

with st.spinner("Connecting to backend (Render may take up to 60 seconds to wake up)..."):
    try:
        
        response = httpx.get(f"{BACKEND_URL}/disputes", timeout=60.0)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                disputes = data
            else:
                st.warning(f"Backend returned unexpected format. Data: {data}")
        else:
            st.error(f"Backend returned HTTP {response.status_code}. Check Render logs.")
            
    except httpx.ReadTimeout:
        st.error("⏱️ Connection timed out. Render is taking too long to wake up. Please click the 'Refresh Data' button in the sidebar.")
    except httpx.ConnectError:
        st.error(f"🔌 Could not connect to backend at {BACKEND_URL}. Is the URL in your Streamlit Secrets correct?")
    except Exception as e:
        st.error(f"❌ An unexpected error occurred: {e}")


col1, col2, col3 = st.columns(3)
active_disputes = [d for d in disputes if d.get("status") != "RESOLVED"]
col1.metric(label="Active Disputes", value=len(active_disputes))
col2.metric(label="AI Automation Rate", value="85%", delta="+12% this week")
col3.metric(label="Revenue Protected", value="$1,450.00", delta="+$500 today")
st.divider()


if not disputes:
    st.info(f"No active disputes found. Go to `{BACKEND_URL}/seed` to simulate an incoming PayPal webhook.")
else:
    for dispute in disputes:
        d_id = dispute.get("id", "Unknown ID")
        data = dispute.get("data", {})
        ai_rec = dispute.get("ai_recommendation", "No recommendation generated.")
        status = dispute.get("status", "UNKNOWN")
        
        reason = str(data.get("reason", "UNKNOWN")).replace("_", " ").title()
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
                                
                                time.sleep(1.5) 
                                
                                res = httpx.post(f"{BACKEND_URL}/resolve/{d_id}", timeout=30.0)
                                if res.status_code == 200:
                                    st.success("Successfully resolved via PayPal!")
                                    st.rerun()
                                else:
                                    st.error(f"Failed to resolve. Backend said: {res.text}")
                            except Exception as e:
                                st.error(f"Failed to resolve: {e}")
                else:
                    st.success("✅ Resolved via API")