# pyrefly: ignore [missing-import]
import streamlit as st
import os
from dotenv import load_dotenv

# 🔥 IMPORT YOUR AGENT HERE
from reviewer_agent import run_code_evaluation

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
# Added a specific tab for Agent 3 Manual Testing
tab_monitor, tab_agents, tab_reviewer, tab_logs = st.tabs([
    "📈 System Pulse Monitor", 
    "🤖 Agent Collaboration Rooms", 
    "⚖️ Agent 3: Reviewer Sandbox", # New Tab
    "📜 Central Incident Logs"
])

with tab_monitor:
    st.header("Live Infrastructure State")
    st.info("System operational. Awaiting incoming webhooks or log streams to analyze.")

with tab_agents:
    st.header("Active Band Room Status")
    st.markdown("Select an active agent workspace below to inspect historical deliberations.")

# 🔥 THE REVIEWER SANDBOX
with tab_reviewer:
    st.header("⚖️ Agent 3: Senior Code Reviewer")
    st.markdown("Paste proposed code patches below to manually trigger the strict CrewAI evaluation pipeline.")
    
    # Default broken code for easy testing
    default_bad_code = """def connect_to_database(db_url):
    # Missing timeout handling and raw string execution
    connection = open_socket(db_url)
    return connection"""
    
    code_input = st.text_area("Proposed Code Patch (from Agent 2):", height=200, value=default_bad_code)
    
    # Execution Button
    if st.button("Run Strict Evaluation Pipeline"):
        if not os.getenv("AI_ML_API_KEY"):
            st.error("Cannot run evaluation: AI_ML_API_KEY is missing from your .env file.")
        else:
            with st.spinner("Agent 3 is analyzing reasoning accuracy and edge cases..."):
                try:
                    # Trigger your backend CrewAI logic
                    evaluation_result = run_code_evaluation(code_input)
                    
                    st.success("Evaluation Sequence Complete!")
                    st.markdown("### 📝 Official Evaluation Report")
                    
                    # Display the model's output in the UI
                    st.markdown(evaluation_result)
                except Exception as e:
                    st.error(f"An error occurred during evaluation: {e}")

with tab_logs:
    st.header("Historical Stack Traces")
    st.text_area("Raw Incident Stream", value="No anomalies detected in the last 24 hours.", height=150)