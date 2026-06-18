# pyrefly: ignore [missing-import]
import streamlit as st
import os
import sys
from dotenv import load_dotenv

# 1. Setup Python Path to import from hyphenated directories
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(base_dir, "agent-1-sentry"))
sys.path.append(os.path.join(base_dir, "agent-2-engineer"))

# 2. Import Agent Logic
from sentry_parser import SentryParser
from engineer_agent import build_prompt, call_featherless
from reviewer_agent import run_code_evaluation

# 3. Load background configurations
load_dotenv()

# 4. Configure the browser page settings
st.set_page_config(
    page_title="Nadi AI | Diagnostics Command Center",
    page_icon="📡",
    layout="wide"
)

# 5. Inject Premium CSS Styles
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
}

/* Base style overrides */
.stApp {
    background-color: #0b0f19;
    color: #cbd5e1;
}

/* Header styling */
.header-container {
    background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%);
    padding: 30px;
    border-radius: 16px;
    margin-bottom: 25px;
    border: 1px solid #312e81;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    text-align: center;
}
.header-title {
    color: #f8fafc;
    font-size: 2.8rem;
    font-weight: 700;
    margin: 0;
    letter-spacing: -0.05em;
    background: linear-gradient(to right, #67e8f9, #a5b4fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.header-subtitle {
    color: #94a3b8;
    font-size: 1.1rem;
    font-weight: 400;
    margin-top: 10px;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #0f172a;
    border-right: 1px solid #1e293b;
}

/* Card layout elements */
.agent-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -2px rgba(0,0,0,0.1);
}

.agent-title {
    color: #38bdf8;
    font-weight: 600;
    font-size: 1.25rem;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
}

/* Custom premium button style override */
div.stButton > button {
    background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
    color: #ffffff;
    border: none;
    padding: 12px 28px;
    border-radius: 8px;
    font-weight: 600;
    font-size: 1rem;
    box-shadow: 0 4px 15px rgba(6, 182, 212, 0.3);
    transition: all 0.3s ease;
    width: 100%;
}
div.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(6, 182, 212, 0.5);
    background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%);
}
div.stButton > button:active {
    transform: translateY(1px);
}

/* Styled text area */
textarea {
    background-color: #0f172a !important;
    color: #e2e8f0 !important;
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
}

/* Custom Tabs Styling */
button[data-baseweb="tab"] {
    font-size: 1.1rem !important;
    font-weight: 500 !important;
    color: #94a3b8 !important;
    border-bottom-width: 2px !important;
    transition: all 0.3s ease !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #38bdf8 !important;
    border-bottom-color: #38bdf8 !important;
}

</style>
""", unsafe_allow_html=True)

# 6. Top Header Visual
st.markdown("""
<div class="header-container">
    <h1 class="header-title">📡 Nadi AI</h1>
    <div class="header-subtitle">Autonomous Multi-Agent DevOps Diagnostic Engine</div>
</div>
""", unsafe_allow_html=True)

# 7. Sidebar Credentials Verification
st.sidebar.markdown("### 🔑 Security Gate")
keys_missing = False
required_keys = ["BAND_API_KEY", "FEATHERLESS_API_KEY", "AI_ML_API_KEY"]

for key in required_keys:
    if not os.getenv(key):
        st.sidebar.warning(f"⚠️ Missing: {key}")
        keys_missing = True

if keys_missing:
    st.sidebar.info("💡 Please specify missing credentials in your `.env` file.")
else:
    st.sidebar.success("✅ All API bridges fully authorized.")

# 8. Initialize Session States for Data Handoffs
if "passed_error" not in st.session_state:
    st.session_state["passed_error"] = None
if "proposed_patch" not in st.session_state:
    st.session_state["proposed_patch"] = ""

# Default messy log trace for Agent 1 testing
default_crash_log = """2026-06-19 01:04:12 [ERROR] Database Connection Failed:
Traceback (most recent call last):
  File "/app/utils/db_connector.py", line 114, in query_database
    cursor.execute(sql_query)
psycopg2.OperationalError: Connection closed unexpectedly by server.
"""

# Default bad code for Agent 3 manual override testing
default_bad_code = """def connect_to_database(db_url):
    # Missing timeout handling and raw string execution
    connection = open_socket(db_url)
    return connection"""

# 9. UI Tab Setup
tab_monitor, tab_agents, tab_reviewer, tab_logs = st.tabs([
    "📈 System Pulse Monitor",
    "🤖 Agent Collaboration Rooms",
    "⚖️ Agent 3: Reviewer Sandbox",
    "📜 Central Incident Logs"
])

# TAB 1: System Pulse Monitor
with tab_monitor:
    st.markdown("""
    <div class="agent-card">
        <div class="agent-title">📈 Tab 1: System Pulse Monitor</div>
        <p style="color: #94a3b8; font-size: 0.95rem;">
            Simulate a crash event. Paste a raw trace log below to initiate <b>Agent 1 (The Sentry)</b> diagnostics.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    raw_log = st.text_area("Raw Incident Log Trace:", value=default_crash_log, height=220, key="raw_log_input")
    
    if st.button("Trigger Sentry Diagnostics", key="btn_trigger_sentry"):
        with st.spinner("Sentry Parser (Agent 1) is analyzing the log..."):
            try:
                parser = SentryParser()
                report = parser.parse_log(raw_log)
                # Store Pydantic report dict to session state
                st.session_state["passed_error"] = report.model_dump()
                st.success("Sentry analysis complete! Structured error report generated.")
            except Exception as e:
                st.error(f"Sentry Parser failed: {e}")
                
    if st.session_state["passed_error"]:
        st.subheader("📋 Ingested Error Context (JSON)")
        st.json(st.session_state["passed_error"])

# TAB 2: Agent Collaboration Rooms
with tab_agents:
    st.markdown("""
    <div class="agent-card">
        <div class="agent-title">🤖 Tab 2: Agent Collaboration Rooms</div>
        <p style="color: #94a3b8; font-size: 0.95rem;">
            Deliberation space for <b>Agent 2 (The Patch Engineer)</b>. Pulls the Sentry error details and generates a code patch using Mistral via Featherless AI.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state["passed_error"]:
        st.info("💡 No active incident. Paste a log in the 'System Pulse Monitor' tab to initialize diagnostics.")
    else:
        st.subheader("📋 Current Target Incident Report")
        st.json(st.session_state["passed_error"])
        
        st.markdown("---")
        st.markdown("### 🛠️ Patch Generation Room")
        
        if st.button("Generate Patch (Agent 2)", key="btn_generate_patch"):
            with st.spinner("Featherless AI is formulating code patch..."):
                try:
                    prompt = build_prompt(st.session_state["passed_error"])
                    patch_code = call_featherless(prompt)
                    st.session_state["proposed_patch"] = patch_code
                    st.success("Targeted patch generated successfully!")
                except Exception as e:
                    st.error(f"Featherless Patch Generation failed: {e}")
                    
        if st.session_state["proposed_patch"]:
            st.subheader("💻 Proposed Code Patch")
            st.code(st.session_state["proposed_patch"], language="python")

# TAB 3: Agent 3 Reviewer Sandbox
with tab_reviewer:
    st.markdown("""
    <div class="agent-card">
        <div class="agent-title">⚖️ Tab 3: Agent 3 Reviewer Sandbox</div>
        <p style="color: #94a3b8; font-size: 0.95rem;">
            Strict verification room run by <b>Agent 3 (Senior Code Reviewer)</b> using CrewAI. Evaluates proposed patches and prints the final report.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Pre-fill code input with patch from Tab 2, or default bad code if empty
    prefilled_code = st.session_state.get("proposed_patch") or default_bad_code
    
    code_to_review = st.text_area("Code Patch for Review:", value=prefilled_code, height=250, key="review_code_input")
    
    if st.button("Run Strict Evaluation", key="btn_run_evaluation"):
        if not os.getenv("AI_ML_API_KEY"):
            st.error("Missing AI_ML_API_KEY in environment variables.")
        else:
            with st.spinner("CrewAI Reviewer is analyzing patch architecture and edge cases..."):
                try:
                    evaluation_report = run_code_evaluation(code_to_review)
                    st.success("Review sequence finalized!")
                    st.subheader("📝 CrewAI Evaluation Report")
                    st.markdown(evaluation_report)
                except Exception as e:
                    st.error(f"Review Agent failed: {e}")

# TAB 4: Central Incident Logs
with tab_logs:
    st.markdown("""
    <div class="agent-card">
        <div class="agent-title">📜 Tab 4: Central Incident Logs</div>
        <p style="color: #94a3b8; font-size: 0.95rem;">
            Full audit session trails containing diagnostic reports and generated patches.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state["passed_error"] or st.session_state["proposed_patch"]:
        if st.session_state["passed_error"]:
            st.markdown("### 📋 Parser Report Session Audit")
            st.json(st.session_state["passed_error"])
        if st.session_state["proposed_patch"]:
            st.markdown("### 💻 Patch Code Session Audit")
            st.code(st.session_state["proposed_patch"], language="python")
    else:
        st.info("No logs present in the current session.")