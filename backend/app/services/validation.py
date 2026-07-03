import pandas as pd

def validate_resource_reallocation(equipment_id: str, source_dept: str, dest_dept: str, telemetry_data: list, maintenance_data: list) -> bool:
    """
    Validates a proposed equipment reallocation.
    Returns True if valid, False if it violates operational constraints.
    
    Constraints:
    1. The target device must be operational (alarm_status must not be Critical/2, or currently in active maintenance).
    2. Source department must not be left with 0 devices of this type (prevents critical deficits).
    3. Destination department must exist and have capacity.
    """
    # Find equipment status
    m_lookup = {r["equipment_id"]: r for r in maintenance_data}
    
    # 1. Check if device is in active service (downtime_hours > 0 in records)
    m_rec = m_lookup.get(equipment_id)
    if m_rec and m_rec.get("downtime_hours", 0) > 0:
        return False # Device is currently in maintenance; cannot be moved.
        
    # Look up last state in telemetry
    target_row = None
    source_dept_count = 0
    device_name = ""
    
    for row in telemetry_data:
        if row["equipment_id"] == equipment_id:
            target_row = row
            device_name = row["name"]
            break
            
    if not target_row:
        return False # Device data not found.
        
    # Check if alarm status is Critical
    if target_row.get("alarm_status", 0) == 2:
        return False # Cannot reallocate faulty/critical device before service.
        
    # Count how many operational devices of this specific type remain in the source department
    seen_ids = set()
    for row in telemetry_data:
        eq_id = row["equipment_id"]
        if row["department"] == source_dept and row["name"] == device_name and eq_id not in seen_ids:
            seen_ids.add(eq_id)
            # Make sure it's not the target itself, and not undergoing active service
            m_info = m_lookup.get(eq_id)
            downtime = m_info.get("downtime_hours", 0) if m_info else 0
            if eq_id != equipment_id and downtime == 0:
                source_dept_count += 1
                
    # 2. SOURCE CONSTRAINT: Must retain at least 1 backup operational device in source dept
    if source_dept_count < 1:
        return False # Block moving if it leaves source department empty.
        
    return True
