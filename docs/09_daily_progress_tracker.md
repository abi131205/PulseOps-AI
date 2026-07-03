# PulseOps AI - Daily Progress Tracker & Log

This document records the hourly progress, technical decisions, and active risks managed by the technical team during the hackathon development cycles.

---

## 🕒 1. Sprints Log (3 July – 6 July)

### Day 1 (3 July 2026) - Scaffolding & Data Setup
* **09:00 - 11:00 AM:** Setup project root, configured `.gitignore`, `.env.example`, and initialized main repository settings.
* **11:00 - 02:00 PM:** Initialized backend FastAPI structure and requirements. Created Vite React client with Tailwind CSS configs.
* **02:00 - 05:00 PM:** Implemented `datasets/generate_data.py` producing tabular logs (10k/250k/1M rows). Tested and generated initial datasets.
* **05:00 - 08:00 PM:** Created BigQuery SQL schemas under `cloud/bigquery_schemas/` and build the `cloud/upload_to_bigquery.py` script.
* **08:00 - 10:00 PM:** Nightly integration sync. Verified code compiles and pushes to develop branch cleanly.

### Day 2 (4 July 2026) - Analytics & Decision Logics
* **09:00 - 01:00 PM:** Built `analytics/pipeline.py` implementing parallel aggregates in cuDF and Pandas benchmarking timing code.
* **01:00 - 04:00 PM:** Created `backend/app/services/decision_engine.py` calculating dynamic Operational Priority Scores (OPS).
* **04:00 - 07:00 PM:** Implemented `backend/app/services/recommendation_engine.py` and the safety constraint rules in `validation.py`.
* **07:00 - 10:00 PM:** Connected `backend/app/services/gemini.py` client to Gemini API generating briefings for hospital admins. Checked fallback states.

### Day 3 (5 July 2026) - Web Binding & Frontpage Layouts
* **09:00 - 01:00 PM:** Replaced FastAPI mocks with active routes (/health, /command-center, /recommendations, /benchmark, /equipment).
* **01:00 - 05:00 PM:** Styled React dashboard views (Sidebar navigation, dark-theme layout cards, priority tables) in `App.jsx`.
* **05:00 - 09:00 PM:** Integrated Recharts visualizations for bed occupancy trends and CPU vs. GPU computation times. Connected views to backend endpoints via Axios.
* **09:00 - 10:00 PM:** Nightly integration. Ran full server test locally and verified chart animations.

### Day 4 (6 July 2026) - Dockerization, Deploy & Demo
* **09:00 - 11:00 AM:** Wrote multi-stage `Dockerfile` and configured `deploy.sh` Cloud Run setup script.
* **11:00 - 01:00 PM:** Setup GitHub Action CI script in `deploy.yml`. Deployed application container successfully to Google Cloud Run.
* **01:00 - 04:00 PM:** Recorded 3-minute video presentation showing all screens and benchmarking results. Prepared slide decks.
* **04:00 - 05:00 PM:** Final submission checks and package upload.

---

## 📑 2. Design Decisions Log

* **Decision 1: serving React from FastAPI.**
  - *Context:* Deploying frontend and backend separately introduces CORS and domain routing complexity.
  - *Choice:* Compile React into static assets via Vite, mount `/dist` folder directly in FastAPI, and serve everything from a single Cloud Run container.
  - *Impact:* Simpler deployment pipeline, zero CORS issues, faster loading speeds.
* **Decision 2: Decoupled AI architecture.**
  - *Context:* Relying on LLMs to perform arithmetic or sort priorities leads to hallucinations and violates safety constraints.
  - *Choice:* Heuristic priority calculation is kept inside deterministic Python code (Decision/Recommendation Engines), while Gemini API is used solely for natural-language briefings.
  - *Impact:* Clean, regulatory-compliant, hallucination-free decision support.

---

## ⚡ 3. Risk Register & Mitigation Log

| Risk Description | Severity | Likelihood | Mitigation Action Taken |
| :--- | :--- | :--- | :--- |
| **No GPU locally for cuDF**| High | High | Coded `pipeline.py` with automatic `try-except` imports. It runs in Pandas CPU mode locally and executes GPU cuDF in production. |
| **Gemini API Key missing** | Medium | Medium | Implemented a local fallback briefing string builder inside `gemini.py` that formats details locally if no key is configured. |
| **Large Data scale OOM** | High | Low | Configured `DATASET_PROFILE` variables enabling users to run `SMALL` telemetry logs locally and `LARGE` logs in high-perf environments. |
