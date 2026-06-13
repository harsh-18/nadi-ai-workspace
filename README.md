# Nadi AI 📡
**Autonomous Multi-Agent DevOps Diagnostic Engine**
*Built for the Band of Agents Hackathon (Track 2: Multi-Agent Software Development)*

---

## 📖 Project Overview
Nadi AI acts as an automated, self-healing DevOps nervous system designed to eliminate costly enterprise system downtime. By leveraging the **Band SDK** as our universal coordination layer, Nadi AI orchestrates an interoperable, cross-framework trio of specialized AI agents that continuously detect, patch, and review software errors in real time.

When a server crashes, a human usually has to read the error logs, figure out what went wrong, write a code patch, and wait for a senior engineer to review it. Nadi AI automates this entire loop.

## 🧠 The Multi-Agent Architecture
Our system moves beyond simple chatbots by implementing a fully autonomous, closed-loop technical handoff across three distinct agents:

1. **Agent 1: The Sentry (Log Analyzer)**
   - **Framework:** LangChain
   - **Role:** Intercepts system failure logs, extracts raw stack traces, and formats the exact error context into a structured JSON layout.
2. **Agent 2: The Patch Engineer**
   - **Framework:** Codeband + Featherless AI
   - **Role:** Ingests the Sentry's report, reviews documentation via open-source inference models, and autonomously drafts a targeted code fix.
3. **Agent 3: The Senior Code Reviewer**
   - **Framework:** CrewAI + AI/ML API
   - **Role:** The ultimate technical gatekeeper. Critiques the proposed patch, evaluates edge cases, and executes strict veto power—either approving the secure code or bouncing it back to Agent 2 for an automated refactor loop.

## 👨‍💻 Team Syncra: Roles & Responsibilities

| Team Member | Role | Primary Domain | Responsibilities |
| :--- | :--- | :--- | :--- |
| **Harsh** *(Captain)* | Project Lead & Reviewer Agent | UI, Architecture, CrewAI | Build the Streamlit dashboard, manage GitHub, handle the project submission, and build **Agent 3 (The Reviewer)** to evaluate reasoning accuracy and code logic. |
| **Wycliff Ochieng** | Data Pipeline Engineer | LangChain, Band SDK | Build **Agent 1 (The Sentry)**. Handle JSON data extraction, parse messy error logs, and set up the core Band SDK communication room. |
| **Syed Wajihul Hassan** | Backend AI Engineer | Codeband, Featherless API | Build **Agent 2 (The Engineer)**. Connect to the Featherless AI inference API to generate Python/Node.js code patches based on error reports. |

## 🚀 Quick Start (Local Setup)
To run this project locally, follow the steps in `PLAN_AND_IMPLEMENTATION.md`.

1. Clone the repository.
2. Create your `.env` file (never push this).
3. Install dependencies: `pip install -r requirements.txt`.
4. Run the Streamlit dashboard: `streamlit run app.py`.

---
*Developed by Team Syncra for Lablab.ai.*
