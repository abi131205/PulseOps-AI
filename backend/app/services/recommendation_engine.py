import datetime
from backend.app.services.decision_engine import compute_all_ops
from backend.app.services.validation import validate_resource_reallocation

def generate_operational_recommendations(telemetry_data: list, maintenance_data: list, occupancy_data: list) -> list:
    """
    Analyzes OPS scores, bed occupancies, and incident queues to produce
    validated, high-impact hospital resource recommendations.
    """
    scored_equipment = compute_all_ops(telemetry_data, maintenance_data)
    
    # Analyze occupancy logs for bed pressure
    latest_occupancy = occupancy_data[-1] if occupancy_data else {
        "icu_beds_occupied": 30, "icu_beds_total": 50,
        "er_beds_occupied": 40, "er_beds_total": 80,
        "emergency_queue_length": 5
    }
    
    icu_total = latest_occupancy.get("icu_beds_total", 50)
    icu_occ = latest_occupancy.get("icu_beds_occupied", 30)
    icu_ratio = icu_occ / max(icu_total, 1)
    
    er_total = latest_occupancy.get("er_beds_total", 80)
    er_occ = latest_occupancy.get("er_beds_occupied", 40)
    er_ratio = er_occ / max(er_total, 1)
    er_queue = latest_occupancy.get("emergency_queue_length", 5)

    recommendations = []
    rec_counter = 1
    
    # Case 1: Critical Equipment Maintenance Trigger
    # If a device has high OPS (>80) and has warning alarms or long service delay, trigger service
    for eq in scored_equipment:
        if eq["operational_priority_score"] >= 75.0:
            ops_score = eq["operational_priority_score"]
            eq_id = eq["equipment_id"]
            eq_name = eq["name"]
            dept = eq["department"]
            
            # Simple heuristic confidence
            confidence = int(85 + (ops_score - 75) * 0.5)
            confidence = min(98, confidence)
            
            action = f"Schedule Immediate Preventative Maintenance for {eq_name} ({eq_id}) in {dept}"
            reasoning = f"{eq_name} {eq_id} has reached a critical Operational Priority Score of {ops_score}. Utilization stands at {int(eq['utilization_rate']*100)}% with temp at {eq['temperature']}°C."
            impact = f"Prevents sudden operational failure and extends asset lifespan."
            alternative = f"Keep operational but throttle utilization to under 50%."
            
            recommendations.append({
                "recommendation_id": f"REC-{rec_counter:03d}",
                "action": action,
                "operational_priority_score": int(ops_score),
                "confidence": confidence,
                "reasoning": reasoning,
                "expected_impact": impact,
                "alternative": alternative,
                "generated_at": datetime.datetime.utcnow().isoformat() + "Z"
            })
            rec_counter += 1
            
    # Case 2: ER/ICU Pressure Resource Reallocation
    # If ER queue is large (>15) and occupancy ratio is high (>0.7), look for idle equipment in other depts
    if er_queue > 12 or er_ratio > 0.75:
        # Find low utilization ventilators in General Ward or Operating Room
        for eq in scored_equipment:
            if eq["name"] == "Ventilator" and eq["department"] in ["General Ward", "Operating Room"] and eq["utilization_rate"] < 0.45:
                # Validate the move through our validation constraint layer
                is_valid = validate_resource_reallocation(
                    eq["equipment_id"], eq["department"], "Emergency", 
                    telemetry_data, maintenance_data
                )
                
                if is_valid:
                    recommendations.append({
                        "recommendation_id": f"REC-{rec_counter:03d}",
                        "action": f"Reallocate Ventilator {eq['equipment_id']} from {eq['department']} to Emergency Department",
                        "operational_priority_score": 88,
                        "confidence": 92,
                        "reasoning": f"Emergency department queue is critical ({er_queue} patient waitlist) with ER occupancy at {int(er_ratio*100)}%. Ventilator {eq['equipment_id']} is currently underutilized at {int(eq['utilization_rate']*100)}% in {eq['department']}.",
                        "expected_impact": "Reduces emergency incident response times by an estimated 15%.",
                        "alternative": "Deploy standby ventilator from inventory; note that this requires a 45-minute calibration delay.",
                        "generated_at": datetime.datetime.utcnow().isoformat() + "Z"
                    })
                    rec_counter += 1
                    break # Only reallocate one device per cycle to prevent over-adjustment
                    
    # Case 3: ICU Surge ICU Ventilator Shift
    if icu_ratio > 0.85:
        for eq in scored_equipment:
            if eq["name"] == "Ventilator" and eq["department"] == "General Ward" and eq["utilization_rate"] < 0.40:
                is_valid = validate_resource_reallocation(
                    eq["equipment_id"], eq["department"], "ICU",
                    telemetry_data, maintenance_data
                )
                if is_valid:
                    recommendations.append({
                        "recommendation_id": f"REC-{rec_counter:03d}",
                        "action": f"Shift Ventilator {eq['equipment_id']} from General Ward to ICU",
                        "operational_priority_score": 84,
                        "confidence": 90,
                        "reasoning": f"ICU bed utilization is at {int(icu_ratio*100)}% capacity. General Ward device {eq['equipment_id']} has low utilization of {int(eq['utilization_rate']*100)}% and can be transferred safely.",
                        "expected_impact": "Secures equipment capacity for upcoming ICU bed admissions.",
                        "alternative": "Calibrate and dispatch standby ventilators from clinical inventory.",
                        "generated_at": datetime.datetime.utcnow().isoformat() + "Z"
                    })
                    rec_counter += 1
                    break
                    
    return recommendations
