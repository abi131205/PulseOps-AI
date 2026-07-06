# PulseOps AI

**AI-Powered Hospital Operations Decision Intelligence Platform**

PulseOps AI is a decision intelligence platform designed to help hospital administrators optimize operational resource allocation, schedule preventative equipment maintenance, and manage patient queues efficiently.

Unlike diagnostic or clinical AI tools, PulseOps AI operates strictly within **hospital logistics and operations**, transforming complex telemetry streams into prioritized, explainable operational actions.

---

## 🚀 Key Features

* **Hospital Command Center:** Real-time visual monitoring of bed occupancy, active emergency incidents, and system alerts.
* **Operational Priority Score (OPS):** Dynamic, multi-factor calculations ranking resource allocation urgency.
* **Equipment Intelligence:** Accelerated maintenance prioritization and scheduling logs.
* **NVIDIA RAPIDS Benchmarking:** Real-time speed comparison of GPU-accelerated cuDF processing against CPU Pandas across multiple data scales.
* **Google Gemini API Explanations:** Explains and justifies computed operational decisions in natural language.

---

## 🛠️ Technology Stack

* **Frontend:** React (Vite), Tailwind CSS, Recharts
* **Backend:** FastAPI (Python), Uvicorn
* **Data Warehouse:** Google BigQuery
* **GPU Processing:** NVIDIA RAPIDS cuDF
* **LLM Layer:** Google Gemini API
* **Deployment:** Google Cloud Run (Docker Container)

---

## 📂 Project Structure

```text
PulseOps-AI/
├── analytics/
│   └── pipeline.py            # RAPIDS cuDF metrics, aggregates, and benchmarks
├── backend/
│   ├── app/
│   │   ├── api/               # API Router endpoints
│   │   ├── services/          # Decision Engine, Recommendation, Validation, Gemini
│   │   └── main.py            # FastAPI main router and static file serving
│   ├── Dockerfile             # Multi-stage Docker config
│   └── requirements.txt
├── datasets/
│   └── generate_data.py       # Configurable synthetic data generator (10k, 250k, 1M+ rows)
├── frontend/                  # React Vite Tailwind app
└── README.md
```

---

## ⚙️ Quick Start

### 1. Environment Configuration
Copy `.env.example` to `.env` and configure your API keys:
```bash
cp .env.example .env
```

### 2. Generate Synthetic Data
Run the custom telemetry generator:
```bash
python datasets/generate_data.py
```

### 3. Start Local Development
Run the FastAPI development server:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```
Then run the React frontend (if in dev mode):
```bash
cd frontend
npm install
npm run dev
```

---

## 🔒 Secure Developer Tunnelling (Ngrok)

During local prototyping, evaluations, and hackathon judging, the platform can be exposed securely to the internet using **Ngrok**. 

### 🛡️ The Importance of Tunnel Security
Exposing local developer ports (e.g., port `8080`) to a public URL introduces significant security risks:
1. **Unauthorized Access:** Anyone discovering the URL can query the system, view telemetry, and access endpoints.
2. **API Key Exhaustion:** Bots or unauthorized users scraping the site can trigger repeated calls to the Google Gemini API, quickly depleting your key quotas.
3. **Data Exposure:** Direct queries to your BigQuery schemas could be initiated by malicious actors.

To prevent this, we enforce **Edge Basic Authentication** at the Ngrok tunnel layer. This blocks all traffic at Ngrok's cloud edge before it ever reaches your local network.

### ⚙️ How to Start the Secure Tunnel
Run the following command in your terminal to create a password-protected endpoint:

```bash
ngrok http 8080 --basic-auth "admin:pulseops2026"
```

### 🔑 Credentials for Access
When accessing the public Ngrok link, the browser will display a standard HTTP basic login popup. Enter the following credentials:
* **Username:** `admin`
* **Password:** `pulseops2026`

*(You can customize these values in the `--basic-auth` flag to rotate credentials or set strong passwords as needed).*
