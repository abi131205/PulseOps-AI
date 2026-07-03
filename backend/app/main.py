import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from backend.app.core.config import settings

app = FastAPI(
    title="PulseOps AI API",
    description="Hospital Operations Decision Intelligence Platform API",
    version="1.0.0"
)

# Enable CORS for local React development server (Vite defaults to port 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import pipeline and decision engine services
from analytics.pipeline import load_data_source, run_performance_benchmark
from backend.app.services.decision_engine import compute_all_ops
from backend.app.services.recommendation_engine import generate_operational_recommendations
from backend.app.services.gemini import generate_recommendation_briefing

# Placeholder route to verify API health
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "dataset_profile": settings.DATASET_PROFILE,
        "gcp_project": settings.GCP_PROJECT_ID
    }

@app.get("/api/command-center")
async def get_command_center():
    """
    Consolidates data inputs to provide a live snapshot of hospital operations.
    """
    try:
        occupancy = load_data_source("bed_occupancy_logs", use_gpu=False).to_dict(orient="records")
        incidents = load_data_source("emergency_incident_log", use_gpu=False).to_dict(orient="records")
        telemetry = load_data_source("equipment_telemetry", use_gpu=False).to_dict(orient="records")
        
        latest_occ = occupancy[-1] if occupancy else {}
        active_inc = [inc for inc in incidents if inc.get("status") == "In-Progress"]
        critical_alerts = [t for t in telemetry if t.get("alarm_status") == 2]
        
        return {
            "status": "active",
            "icu_occupied": latest_occ.get("icu_beds_occupied", 30),
            "icu_total": latest_occ.get("icu_beds_total", 50),
            "er_occupied": latest_occ.get("er_beds_occupied", 40),
            "er_total": latest_occ.get("er_beds_total", 80),
            "er_queue_length": latest_occ.get("emergency_queue_length", 5),
            "active_incidents_count": len(active_inc),
            "active_incidents": active_inc[:5],
            "critical_alarms_count": len(critical_alerts)
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to retrieve command center logs: {e}"}

@app.get("/api/recommendations")
async def get_recommendations():
    """
    Triggers AI Decision / Recommendation engines and attaches Gemini briefings.
    """
    try:
        telemetry = load_data_source("equipment_telemetry", use_gpu=False).to_dict(orient="records")
        maintenance = load_data_source("maintenance_records", use_gpu=False).to_dict(orient="records")
        occupancy = load_data_source("bed_occupancy_logs", use_gpu=False).to_dict(orient="records")
        
        raw_recs = generate_operational_recommendations(telemetry, maintenance, occupancy)
        
        # Attach Gemini natural-language explanations
        final_recs = []
        for rec in raw_recs:
            briefing = generate_recommendation_briefing(rec)
            rec["gemini_explanation"] = briefing
            final_recs.append(rec)
            
        return final_recs
    except Exception as e:
        return {"status": "error", "message": f"Failed to compile recommendations: {e}"}

@app.get("/api/benchmark")
async def run_benchmark():
    """
    Executes raw Pandas vs cuDF aggregations and returns performance metrics.
    """
    try:
        results = run_performance_benchmark()
        return results
    except Exception as e:
        return {"status": "error", "message": f"Failed to execute timing benchmark: {e}"}

@app.get("/api/equipment")
async def get_equipment():
    """
    Retrieves the complete list of equipment marked with calculated OPS indices.
    """
    try:
        telemetry = load_data_source("equipment_telemetry", use_gpu=False).to_dict(orient="records")
        maintenance = load_data_source("maintenance_records", use_gpu=False).to_dict(orient="records")
        
        scored_equipment = compute_all_ops(telemetry, maintenance)
        return scored_equipment
    except Exception as e:
        return []

# Serve React static assets in production
frontend_dist_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/dist"))

if os.path.exists(frontend_dist_path):
    app.mount("/", StaticFiles(directory=frontend_dist_path, html=True), name="static")
else:
    @app.get("/")
    async def index():
        return HTMLResponse(
            content="""
            <html>
                <head>
                    <title>PulseOps AI Backend</title>
                    <style>
                        body { font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #121212; color: #ffffff; }
                        div { text-align: center; border: 1px solid #333; padding: 40px; border-radius: 8px; background-color: #1e1e1e; }
                    </style>
                </head>
                <body>
                    <div>
                        <h1>PulseOps AI Server Initialized</h1>
                        <p>FastAPI API is running. React frontend has not been compiled yet.</p>
                        <p><a href="/docs" style="color: #646cff;">View API Documentation (Swagger Docs)</a></p>
                    </div>
                </body>
            </html>
            """
        )
