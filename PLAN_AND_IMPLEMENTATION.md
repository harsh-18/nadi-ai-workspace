# 🛠️ Nadi AI: Plan & Implementation Guide

Welcome to the engineering hub for Nadi AI. This document outlines our git workflow, sprint schedule, and exact implementation steps. **Please read the Git Workflow carefully before writing any code.**

---

## 🛡️ The Git Workflow (CRITICAL)
To avoid overwriting each other's code, breaking the Streamlit UI, or leaking API keys, we are using a strict branching strategy.

### 🚫 Rule 1: Never push directly to `main`
The `main` branch is our production environment. If you push broken code here, the whole app crashes. 

### 🌿 Rule 2: Create your own branch
Before you start working, branch off from main.
* **Teammate 1:** `git checkout -b agent-1-sentry`
* **Teammate 2:** `git checkout -b agent-2-engineer`

Work, commit, and push entirely on your own branch. 
* `git push origin agent-1-sentry`

### 🤝 Rule 3: Use Pull Requests (PRs)
When your agent is working and ready to connect to the rest of the system:
1. Go to our GitHub repo in your browser.
2. Click **Compare & pull request**.
3. Harsh will review the code and merge it into `main`.

### 🔑 Rule 4: The `.env` File Vault
Never commit your API keys. Make sure your local repository has a `.env` file for your keys, and ensure `.env` is listed inside the `.gitignore` file.

---

## 🗓️ Sprint Schedule (June 13 – June 19)

### Phase 1: Foundation (June 13 - 14)
* **All:** Clone repo, setup isolated local environments (`venv`), verify `.env` security.
* **Teammate 1:** Initialize the Band SDK room endpoint and draft the LangChain parser script.
* **Teammate 2:** Connect to Featherless API and successfully generate a basic code block from a hardcoded prompt.
* **Harsh:** Scaffold Streamlit UI layout and initialize GitHub structure.

### Phase 2: Independent Agent Builds (June 15 - 16)
* **Teammate 1:** Finalize Agent 1. It must take a messy `.txt` log, extract data, and post clean JSON to the Band room.
* **Teammate 2:** Finalize Agent 2. It must pull data from the Band room, send it to Featherless, and return a code patch.
* **Harsh:** Build Agent 3 (CrewAI) logic evaluator using AI/ML API.

### Phase 3: The Integration Loop (June 17)
* **All Hands:** We wire the system together. Agent 1 -> Agent 2 -> Agent 3. We run end-to-end tests to ensure the JSON handoffs don't break between frameworks.

### Phase 4: Polish & Pitch (June 18 - 19)
* **Backend:** Code freeze. No new features. Fix bugs only.
* **Harsh:** Connect Streamlit frontend to the live Band room data. Record the 5-minute video pitch showing a successful autonomous code fix. Submit on Lablab.

---

## 💻 Environment Setup Cheat Sheet

```bash
# 1. Clone the repo
git clone [our-repo-link]
cd [repo-folder-name]

# 2. Create and activate virtual environment
python -m venv venv
# Windows: .\venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# 3. Create your local secrets file (DO NOT COMMIT THIS)
touch .env

# 4. Install dependencies
pip install -r requirements.txt
```
