import os
import time
import pandas as pd
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# CPU Fallback / GPU Switch logic
GPU_AVAILABLE = False
try:
    import cudf
    import cupy as cp
    GPU_AVAILABLE = True
    print("[NVIDIA RAPIDS] CUDA-enabled GPU detected. Running in Production (cuDF) mode.")
except ImportError:
    print("[NVIDIA RAPIDS] CUDA not available. Running in Development (Pandas) mode.")

# Paths setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASETS_DIR = os.path.join(BASE_DIR, "datasets")

# Simple In-Memory Cache to prevent repeated BigQuery calls
_DATA_CACHE = {}

def clear_data_cache():
    global _DATA_CACHE
    _DATA_CACHE.clear()
    print("[Data Cache] In-memory data cache cleared.")

def get_csv_path(table_name: str) -> str:
    return os.path.join(DATASETS_DIR, f"{table_name}.csv")

def load_data_source(table_name: str, use_gpu: bool = False):
    """
    Loads data from the analytical data warehouse.
    If GCP credentials and BigQuery dataset details are defined, we query BigQuery.
    Otherwise, we fall back to local synthetic CSV files.
    """
    cache_key = f"{table_name}_gpu_{use_gpu}"
    if cache_key in _DATA_CACHE:
        return _DATA_CACHE[cache_key].copy()
        
    csv_path = get_csv_path(table_name)
    
    # Check BigQuery credentials
    project_id = os.getenv("GCP_PROJECT_ID")
    dataset_id = os.getenv("BIGQUERY_DATASET", "pulseops_ai")
    
    # Prevent metadata lookup timeouts locally if credentials are not configured
    has_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS") is not None
    is_cloud_run = os.getenv("K_SERVICE") is not None
    
    res = None
    if project_id and (has_credentials or is_cloud_run):
        try:
            from google.cloud import bigquery
            client = bigquery.Client(project=project_id)
            query = f"SELECT * FROM `{project_id}.{dataset_id}.{table_name}`"
            
            # Use high-performance gRPC Storage API only in Cloud Run where gRPC is allowed
            if is_cloud_run:
                try:
                    from google.cloud import bigquery_storage
                    bqstorage_client = bigquery_storage.BigQueryReadClient()
                    df_arrow = client.query(query).to_arrow(bqstorage_client=bqstorage_client)
                    if use_gpu and GPU_AVAILABLE:
                        res = cudf.DataFrame.from_arrow(df_arrow)
                    else:
                        res = df_arrow.to_pandas()
                except Exception as bqse:
                    print(f"[BigQuery] gRPC Storage API failed: {bqse}. Falling back to REST...")
            
            if res is None:
                # Stable HTTP REST query for local development networks
                df = client.query(query).to_dataframe()
                if use_gpu and GPU_AVAILABLE:
                    res = cudf.DataFrame.from_pandas(df)
                else:
                    res = df
        except Exception as e:
            print(f"[BigQuery] Failed to fetch {table_name}: {e}. Falling back to CSV.")
            
    # Fallback to local CSV load if BigQuery failed or wasn't configured
    if res is None:
        if use_gpu and GPU_AVAILABLE:
            res = cudf.read_csv(csv_path)
        else:
            res = pd.read_csv(csv_path)
            
    _DATA_CACHE[cache_key] = res
    return res.copy()

def process_cpu_metrics(telemetry, maintenance, occupancy, incidents):
    """Runs data processing using Pandas (CPU)"""
    # 1. Pre-aggregate maintenance to one row per equipment_id BEFORE merging.
    # Merging raw log-to-log on a repeating key explodes combinatorially at
    # scale (confirmed: 1M telemetry x 20K maintenance rows -> 200M+ rows,
    # crashes on memory). Aggregating first keeps the merge a clean 1-to-many.
    maintenance_agg = maintenance.groupby("equipment_id").agg(
        downtime_hours=("downtime_hours", "sum"),
        days_since_last_service=("days_since_last_service", "mean")
    ).reset_index()
    merged = telemetry.merge(maintenance_agg, on="equipment_id", how="left")
    
    # 2. Aggregations (e.g. mean utilization, max temp per department and type)
    equipment_summary = merged.groupby(["department", "name"]).agg(
        avg_utilization=("utilization_rate", "mean"),
        max_temp=("temperature", "max"),
        total_downtime=("downtime_hours", "sum"),
        avg_service_delay=("days_since_last_service", "mean")
    ).reset_index()
    
    # 3. Rolling average calculations on bed occupancy logs
    occupancy["timestamp"] = pd.to_datetime(occupancy["timestamp"])
    occupancy = occupancy.sort_values("timestamp")
    occupancy["icu_occupancy_ratio"] = occupancy["icu_beds_occupied"] / occupancy["icu_beds_total"]
    occupancy["er_occupancy_ratio"] = occupancy["er_beds_occupied"] / occupancy["er_beds_total"]
    
    # 12-hour rolling average (assuming logs are spaced 10 mins apart, 12 hrs = 72 records)
    occupancy["icu_pressure_rolling"] = occupancy["icu_occupancy_ratio"].rolling(window=72, min_periods=1).mean()
    occupancy["er_pressure_rolling"] = occupancy["er_occupancy_ratio"].rolling(window=72, min_periods=1).mean()
    
    # 4. Group incidents by equipment type to flag failure rates
    incident_hotspots = incidents.groupby(["department", "equipment_required"]).agg(
        total_incidents=("incident_id", "count"),
        avg_response_time=("response_time_min", "mean")
    ).reset_index()

    # 5. NEW: standard deviation of response time across departments.
    # A department can have the same average response time as another but be
    # far less predictable - std captures that risk, mean alone doesn't.
    department_response_stats = incidents.groupby("department").agg(
        avg_response_time=("response_time_min", "mean"),
        response_time_std=("response_time_min", "std"),
        incident_count=("incident_id", "count")
    ).reset_index()
    # std is NaN when a department has only 1 incident - fill with 0 so it
    # never breaks downstream math in decision_engine.py
    department_response_stats["response_time_std"] = department_response_stats["response_time_std"].fillna(0)
    
    return {
        "equipment_summary": equipment_summary,
        "occupancy": occupancy,
        "incident_hotspots": incident_hotspots,
        "department_response_stats": department_response_stats
    }

def process_gpu_metrics(telemetry, maintenance, occupancy, incidents):
    """Runs data processing using RAPIDS cuDF (GPU)"""
    if not GPU_AVAILABLE:
        # Fall back to CPU if GPU not available
        return process_cpu_metrics(telemetry, maintenance, occupancy, incidents)
        
    # 1. Pre-aggregate maintenance to one row per equipment_id BEFORE merging
    # (see note in process_cpu_metrics - avoids combinatorial row explosion).
    maintenance_agg = maintenance.groupby("equipment_id").agg({
        "downtime_hours": "sum",
        "days_since_last_service": "mean"
    }).reset_index()
    maintenance_agg.columns = ["equipment_id", "downtime_hours", "days_since_last_service"]
    merged = telemetry.merge(maintenance_agg, on="equipment_id", how="left")
    
    # 2. Aggregations using cuDF groupby
    equipment_summary = merged.groupby(["department", "name"]).agg({
        "utilization_rate": "mean",
        "temperature": "max",
        "downtime_hours": "sum",
        "days_since_last_service": "mean"
    }).reset_index()
    
    # Rename columns to match CPU output format
    equipment_summary.columns = [
        "department", "name", "avg_utilization", 
        "max_temp", "total_downtime", "avg_service_delay"
    ]
    
    # 3. Rolling average calculations on bed occupancy logs
    occupancy["timestamp"] = cudf.to_datetime(occupancy["timestamp"])
    occupancy = occupancy.sort_values("timestamp")
    occupancy["icu_occupancy_ratio"] = occupancy["icu_beds_occupied"] / occupancy["icu_beds_total"]
    occupancy["er_occupancy_ratio"] = occupancy["er_beds_occupied"] / occupancy["er_beds_total"]
    
    # 12-hour rolling average window in cuDF
    occupancy["icu_pressure_rolling"] = occupancy["icu_occupancy_ratio"].rolling(window=72, min_periods=1).mean()
    occupancy["er_pressure_rolling"] = occupancy["er_occupancy_ratio"].rolling(window=72, min_periods=1).mean()
    
    # 4. Incident hotspots grouping
    incident_hotspots = incidents.groupby(["department", "equipment_required"]).agg({
        "incident_id": "count",
        "response_time_min": "mean"
    }).reset_index()
    
    incident_hotspots.columns = [
        "department", "equipment_required", "total_incidents", "avg_response_time"
    ]

    # 5. NEW: standard deviation of response time across departments.
    # Done as two separate aggs + merge rather than a multi-func agg dict,
    # because cuDF's support for {"col": ["mean","std"]} multi-index output
    # is inconsistent across versions - this mirrors the safer dict-agg +
    # manual-rename style already used elsewhere in this file.
    dept_mean_count = incidents.groupby("department").agg({
        "response_time_min": "mean",
        "incident_id": "count"
    }).reset_index()
    dept_mean_count.columns = ["department", "avg_response_time", "incident_count"]

    dept_std = incidents.groupby("department").agg({
        "response_time_min": "std"
    }).reset_index()
    dept_std.columns = ["department", "response_time_std"]

    department_response_stats = dept_mean_count.merge(dept_std, on="department", how="left")
    department_response_stats["response_time_std"] = department_response_stats["response_time_std"].fillna(0)
    
    return {
        "equipment_summary": equipment_summary,
        "occupancy": occupancy,
        "incident_hotspots": incident_hotspots,
        "department_response_stats": department_response_stats
    }

def run_performance_benchmark():
    """Runs and times the analytical pipelines on CPU vs. GPU"""
    print("Loading datasets for performance benchmarking...")
    
    # Load CPU datasets
    cpu_t = load_data_source("equipment_telemetry", use_gpu=False)
    cpu_m = load_data_source("maintenance_records", use_gpu=False)
    cpu_o = load_data_source("bed_occupancy_logs", use_gpu=False)
    cpu_i = load_data_source("emergency_incident_log", use_gpu=False)
    
    # Time CPU execution
    start_cpu = time.perf_counter()
    cpu_results = process_cpu_metrics(cpu_t, cpu_m, cpu_o, cpu_i)
    cpu_time_ms = round((time.perf_counter() - start_cpu) * 1000, 2)
    
    # Time GPU execution
    if GPU_AVAILABLE:
        gpu_t = load_data_source("equipment_telemetry", use_gpu=True)
        gpu_m = load_data_source("maintenance_records", use_gpu=True)
        gpu_o = load_data_source("bed_occupancy_logs", use_gpu=True)
        gpu_i = load_data_source("emergency_incident_log", use_gpu=True)
        
        start_gpu = time.perf_counter()
        gpu_results = process_gpu_metrics(gpu_t, gpu_m, gpu_o, gpu_i)
        gpu_time_ms = round((time.perf_counter() - start_gpu) * 1000, 2)
        speedup = round(cpu_time_ms / max(gpu_time_ms, 0.01), 1)
    else:
        # No real GPU available in this environment. We do NOT fabricate a speedup number - report None and say so clearly
        gpu_time_ms = None
        gpu_results = cpu_results
        speedup = None
        print("[NVIDIA RAPIDS] No GPU available in this environment - GPU time "
              "was NOT measured. Run this script on a real cuDF/GPU runtime "
              "(e.g. Google Colab with a T4 GPU) to get a genuine number.")
    
    if speedup is not None:
        print(f"Benchmark finished. CPU={cpu_time_ms}ms, GPU={gpu_time_ms}ms (Speedup: {speedup}x)")
    else:
        print(f"Benchmark finished. CPU={cpu_time_ms}ms, GPU=not measured (no GPU in this environment)")
    
    # Extract pandas DataFrames for downstream decision calculations
    if GPU_AVAILABLE and hasattr(gpu_results["equipment_summary"], "to_pandas"):
        eq_summary = gpu_results["equipment_summary"].to_pandas()
        occ_summary = gpu_results["occupancy"].to_pandas()
        inc_summary = gpu_results["incident_hotspots"].to_pandas()
        dept_response_summary = gpu_results["department_response_stats"].to_pandas()
    else:
        eq_summary = cpu_results["equipment_summary"]
        occ_summary = cpu_results["occupancy"]
        inc_summary = cpu_results["incident_hotspots"]
        dept_response_summary = cpu_results["department_response_stats"]
        
    return {
        "benchmark": {
            "cpu_time_ms": cpu_time_ms,
            "gpu_time_ms": gpu_time_ms,
            "speedup": speedup,
            "gpu_native": GPU_AVAILABLE
        },
        "data": {
            "equipment_summary": eq_summary.to_dict(orient="records"),
            "bed_occupancy": occ_summary.tail(50).to_dict(orient="records"),
            "incident_hotspots": inc_summary.to_dict(orient="records"),
            "department_response_stats": dept_response_summary.to_dict(orient="records")
        }
    }

if __name__ == "__main__":
    # Test script run
    run_performance_benchmark()