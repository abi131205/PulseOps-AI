import os
import pandas as pd
from backend.app.core.config import settings

def calculate_equipment_ops(telemetry_row: dict, maintenance_record: dict = None) -> float:
    """
    Calculates the Operational Priority Score (OPS) for a single piece of equipment.
    OPS ranges from 0 (lowest urgency) to 100 (highest urgency/critical action needed).
    
    Formula components:
    - Utilization Rate: up to 30 points
    - Temperature Deviation: up to 20 points
    - Alarm Status: up to 30 points
    - Days Since Last Service: up to 20 points
    """
    # Heuristic Weights (can be optimized dynamically by ML in future scopes)
    w_utilization = 30
    w_temperature = 20
    w_alarm = 30
    w_service_delay = 20
    
    # 1. Utilization Rate (0.0 to 1.0)
    util = telemetry_row.get("utilization_rate", 0.0)
    score_util = util * w_utilization
    
    # 2. Temperature deviation (normal is ~36C; temp above 38C gets scaled)
    temp = telemetry_row.get("temperature", 36.0)
    temp_dev = max(0.0, temp - 36.9)
    # Scale deviation: temp of 43C or higher gets max 20 points
    score_temp = min(1.0, temp_dev / 6.1) * w_temperature
    
    # 3. Alarm Status (0 = Normal, 1 = Warning, 2 = Critical)
    alarm = telemetry_row.get("alarm_status", 0)
    if alarm == 2:
        score_alarm = w_alarm
    elif alarm == 1:
        score_alarm = w_alarm * 0.5
    else:
        score_alarm = 0.0
        
    # 4. Days since last service
    days_since = 30 # default fallback
    if maintenance_record:
        days_since = maintenance_record.get("days_since_last_service", 30)
    
    # Scale service delay: 180+ days gets max 20 points
    score_service = min(1.0, days_since / 180.0) * w_service_delay
    
    total_ops = score_util + score_temp + score_alarm + score_service
    return round(min(100.0, total_ops), 1)

def compute_all_ops(telemetry_data: list, maintenance_data: list) -> list:
    """
    Computes OPS for all active equipment and returns them ordered by highest score.
    """
    # Convert maintenance lists to lookup dictionary
    m_lookup = {r["equipment_id"]: r for r in maintenance_data}
    
    scored_list = []
    # Keep track of last recorded state per device
    seen_devices = {}
    
    # Process from newest to oldest logs
    for row in reversed(telemetry_data):
        eq_id = row["equipment_id"]
        if eq_id not in seen_devices:
            seen_devices[eq_id] = row
            
    for eq_id, row in seen_devices.items():
        m_rec = m_lookup.get(eq_id)
        ops = calculate_equipment_ops(row, m_rec)
        
        scored_list.append({
            "equipment_id": eq_id,
            "name": row["name"],
            "department": row["department"],
            "utilization_rate": row["utilization_rate"],
            "temperature": row["temperature"],
            "alarm_status": row["alarm_status"],
            "days_since_last_service": m_rec.get("days_since_last_service", 30) if m_rec else 30,
            "operational_priority_score": ops
        })
        
    # Sort by score descending
    scored_list.sort(key=lambda x: x["operational_priority_score"], reverse=True)
    return scored_list
