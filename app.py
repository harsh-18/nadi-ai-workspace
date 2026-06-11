import streamlit as st
import os
from dotenv import load_dotenv

# 1. Load background configurations from our hidden vault
load_dotenv()

# 2. Configure the browser page settings
st.set_page_config(
    page_title="Nadi AI | Diagnostic Command Center",
    page_icon="📡",
    layout="wide"
)

# 3. Create our Top Header Visuals
st.title("📡 Nadi AI")
st.subheader("Autonomous Multi-Agent DevOps Diagnostic Engine by Team Syncra")
st.markdown("---")

# 4. Verify API keys are present before letting the app run
keys_missing = False
required_keys = ["BAND_API_KEY", "FEATHERLESS_API_KEY", "AI_ML_API_KEY"]

for key in required_keys:
    if not os.getenv(key):
        st.sidebar.warning(f"⚠️ Missing credential: {key}")
        keys_missing = True

if keys_missing:
    st.sidebar.info("💡 Paste your keys into your local .env file to authorize connection rooms.")
else:
    st.sidebar.success("✅ All partner API bridges authorized and ready.")

# 5. Build our UI Operating Tabs
tab_monitor, tab_agents, tab_logs = st.tabs([
    "📈 System Pulse Monitor", 
    "🤖 Agent Collaboration Rooms", 
    "📜 Central Incident Logs"
])

with tab_monitor:
    st.header("Live Infrastructure State")
    st.info("System operational. Awaiting incoming webhooks or log streams to analyze.")

with tab_agents:
    st.header("Active Band Room Status")
    st.markdown("Select an active agent workspace below to inspect historical deliberations.")

with tab_logs:
    st.header("Historical Stack Traces")
    st.text_area("Raw Incident Stream", value="No anomalies detected in the last 24 hours.", height=150)