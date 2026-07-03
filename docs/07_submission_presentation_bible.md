# PulseOps AI - Complete Submission & Presentation Bible

This document contains the presentation slide structures, speaking scripts, demo guides, and deployment checklists.

---

## 📽️ 1. Complete 3-Minute Demo Video Script

* **Speaker:** Project Lead (Biomedical student / Member 1)
* **Goal:** Hook the judges, show the technical RAPIDS and Gemini integrations, and prove the business value of PulseOps AI.

### Narration Timeline:

| Time | Screen Shown | Narration / Speaking Script |
| :--- | :--- | :--- |
| **00:00 - 00:30** | Landing/Command Center | "In a busy hospital, resource delays cost lives. Administrators face a constant challenge: matching telemetry alarms, bed constraints, and equipment failures with actual operational priority. This is PulseOps AI—a Decision Intelligence Platform for hospital logistics." |
| **00:30 - 01:10** | Operational Priorities | "Instead of clinical diagnosis, our platform calculates the **Operational Priority Score (OPS)**. Here, we see Ranked recommendations. Rather than raw data charts, administrators are prompted with validated reallocations, like moving a ventilator from the underutilized ICU to the surge-stressed Emergency ward." |
| **01:10 - 01:45** | System Performance | "To process millions of rows of historical hospital logs and telemetry in real time, we integrate **NVIDIA RAPIDS cuDF**. When we run our rolling averages and metrics, the GPU-accelerated pipeline runs in milliseconds. At a scale of 1 million rows, we achieve a **18x to 30x speedup** compared to standard Pandas CPU processing." |
| **01:45 - 02:30** | Recommendation Briefs | "Once the AI Decision Engine calculates the priority score and maps it to a validated reallocation, the **Google Gemini API** takes over. Rather than simple spreadsheets, Gemini generates natural-language briefings explaining why this move is critical, giving administrators clear, explainable decision support." |
| **02:30 - 03:00** | Deployment & Conclusion | "The entire platform is deployed in a single Docker container on **Google Cloud Run**, ensuring serverless scaling. PulseOps AI bridges the gap between high-volume data warehouses and immediate operational action. Thank you." |

---

## 📊 2. Pitch Deck Slide Outline

1. **Slide 1: Title Slide**
   * *Content:* PulseOps AI Logo, Tagline ("AI-Powered Hospital Operations Decision Intelligence Platform"), Team Member Names.
2. **Slide 2: The Problem**
   * *Content:* Bullet points of bottlenecks (siloed data, maintenance backlogs, reactive transfers). Highlight: *logistics errors cause resource delays*.
3. **Slide 3: Our Solution**
   * *Content:* Diagram showing data flowing from BigQuery -> RAPIDS -> AI Engines -> Gemini Briefing -> Command Center.
4. **Slide 4: Unique Selling Proposition (USP)**
   * *Content:* Comparison table contrasting EMR/HMS (CRUD storage) vs. PulseOps AI (automated score calculation, validation filters, explainability).
5. **Slide 5: Accelerated Data Pipeline (NVIDIA)**
   * *Content:* Details of RAPIDS cuDF performance gains. Benchmark chart showing CPU vs. GPU speeds across different dataset scales.
6. **Slide 6: Google Cloud Infrastructure**
   * *Content:* System diagram showing Google Cloud Run serverless hosting and Google Gemini API integration.
7. **Slide 7: Demo Highlight**
   * *Content:* Screen grabs of the Hospital Command Center and Priorities list.
8. **Slide 8: Future Roadmap & Venture Potential**
   * *Content:* Moving to machine learning weight optimizations, multi-hospital tenants, and enterprise scaling.
9. **Slide 9: Thank You**
   * *Content:* Q&A invite, GitHub link, team contact.

---

## 🚀 3. Deployment Verification Checklist

* [x] Local docker build compiles React build and installs `requirements.txt`.
* [x] Environment file `.env` configures `DATASET_PROFILE`, `GEMINI_API_KEY`, and `GCP_PROJECT_ID`.
* [x] Docker image submits successfully to Google Cloud Build.
* [x] Service deploys to Google Cloud Run, serving active endpoints under `/api`.
* [x] Main landing page successfully loads the Vite index script bundle.
