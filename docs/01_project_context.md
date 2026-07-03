# PulseOps AI - Project Context (Single Source of Truth)

This document is the absolute single source of truth for **PulseOps AI**. All other project documentation, codebase files, API models, and presentation materials must align with the concepts, terminology, and structural parameters defined here.

---

## 🎯 1. Platform Vision & Objectives

PulseOps AI is an **AI-powered Hospital Operations Decision Intelligence Platform** designed to help hospital administrators, logistics coordinators, and biomedical engineers make faster and better resource allocation decisions.

### Crucial Boundaries:
* **Hospital Operations, NOT Medical AI:** PulseOps AI does **NOT** diagnose diseases, recommend patient treatments, or suggest clinical interventions. It operates strictly on **hospital logistics, asset management, and resource allocation**.
* **Decision Intelligence, NOT a CRUD System:** It is not a Hospital Management System (HMS) or an Electronic Medical Record (EMR). It runs analytical and predictive algorithms to determine the **Operational Priority Score (OPS)**, validation rules, and explainable recommendations.

---

## 🏗️ 2. Core Technological Blueprint

The platform integrates Google Cloud, NVIDIA RAPIDS, and modern web frameworks into a high-performance, single-container deployment:

```text
[Dataset Generator] ---> [Google BigQuery] 
                               │
                               ▼ (BigQuery Storage API Arrow stream)
                    [NVIDIA RAPIDS cuDF Analytics]
                               │
                               ▼ (Feature Aggregates)
                    [AI Decision Engine]
                               │
                               ▼ (Operational Priority Scores)
                    [Recommendation Engine]
                               │
                               ▼ (Draft Allocations)
                    [Recommendation Validation Layer]
                               │
                               ▼ (Validated JSON Output)
                    [Google Gemini API]
                               │
                               ▼ (Natural Language Explanations)
                    [FastAPI Web API Services]
                               │
                               ▼ (JSON Payloads)
                    [React Command Center UI]
```

---

## 📋 3. Standardized Terminology

To maintain consistency during judges' evaluations, the following terms must be used:
* **Operational Priority Score (OPS):** The dynamic urgency index (0–100) computed by the AI Decision Engine. It measures resource stress and logistics urgency, replacing any references to "risk scores".
* **Central Analytical Data Warehouse:** Refers to **Google BigQuery** where historical logs and telemetry are stored.
* **NVIDIA RAPIDS Pipeline:** The GPU-accelerated cuDF processing engine running time-series joins and rollups.
* **Google Gemini API:** The generative AI model used **exclusively** to explain recommendation logs.
* **Development Mode vs. Production Mode:** 
  - *Development Mode:* Falls back to CPU Pandas for local code validation.
  - *Production Mode:* Activates GPU-accelerated cuDF for high-volume logs.

---

## 💻 4. Dashboard Viewports
The interface is structured into exactly four primary pages:
1. **Hospital Command Center:** Real-time bed occupancy metrics, active incident tracking, and alarm counts.
2. **Operational Priorities:** Rank-ordered equipment and resource allocations requiring immediate coordinator actions.
3. **Equipment Intelligence:** Detailed biomedical maintenance tracking and the GPU-to-CPU benchmarking panel.
4. **System Performance:** CPU vs. GPU benchmark speedup graphs, API response latency, and throughput counters.
