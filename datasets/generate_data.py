import os
import csv
import uuid
import random
import datetime
from dotenv import load_dotenv

# Load env file
load_dotenv()

# Read dataset profile scale
PROFILE = os.getenv("DATASET_PROFILE", "SMALL").upper()

# Set table scaling based on profile
SCALES = {
    "SMALL": {
        "telemetry": 10000,
        "maintenance": 500,
        "occupancy": 1000,
        "incidents": 200
    },
    "MEDIUM": {
        "telemetry": 250000,
        "maintenance": 5000,
        "occupancy": 10000,
        "incidents": 2000
    },
    "LARGE": {
        "telemetry": 1000000,
        "maintenance": 20000,
        "occupancy": 50000,
        "incidents": 10000
    }
}

scale = SCALES.get(PROFILE, SCALES["SMALL"])
print(f"Initializing synthetic data generation for profile: {PROFILE}")
print(f"Configured Row Counts: Telemetry={scale['telemetry']:,}, Maintenance={scale['maintenance']:,}, Bed Occupancy={scale['occupancy']:,}, Incidents={scale['incidents']:,}")

# Base static arrays
DEPARTMENTS = ["ICU", "Emergency", "General Ward", "Operating Room"]
EQUIPMENT_TYPES = ["Ventilator", "Defibrillator", "Infusion Pump", "Anesthesia Machine"]
INCIDENT_TYPES = ["Trauma", "Cardiac Arrest", "Respiratory Distress", "Stroke"]
SEVERITIES = ["Low", "Medium", "High", "Critical"]
TECHNICIANS = ["Tech_Alex", "Tech_Sarah", "Tech_James", "Tech_Maria", "Tech_David"]

# Generate consistent equipment IDs
EQUIPMENT_LIST = []
for i in range(1, 101):
    eq_type = random.choice(EQUIPMENT_TYPES)
    eq_id = f"{eq_type[0]}-{i:03d}"
    EQUIPMENT_LIST.append({
        "id": eq_id,
        "type": eq_type,
        "dept": random.choice(DEPARTMENTS)
    })

# Output folder path
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. Generate Equipment Telemetry
telemetry_path = os.path.join(OUTPUT_DIR, "equipment_telemetry.csv")
print(f"Generating {telemetry_path}...")
start_time = datetime.datetime.now() - datetime.timedelta(days=10)

with open(telemetry_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "log_id", "equipment_id", "name", "department", 
        "utilization_rate", "temperature", "power_draw", 
        "alarm_status", "timestamp"
    ])
    
    for i in range(scale["telemetry"]):
        eq = random.choice(EQUIPMENT_LIST)
        timestamp = start_time + datetime.timedelta(seconds=(i * (860000 / scale["telemetry"])))
        util_rate = round(random.uniform(0.1, 0.98), 2)
        
        # High utilization rate correlates with temperature increase and alerts
        if util_rate > 0.85:
            temp = round(random.uniform(37.5, 44.5), 1)
            power = round(random.uniform(1.2, 1.8), 2)
            alarm = random.choice([1, 2]) # Warning, Critical
        else:
            temp = round(random.uniform(31.0, 36.9), 1)
            power = round(random.uniform(0.4, 0.99), 2)
            alarm = 0 # Normal
            
        writer.writerow([
            i + 1, eq["id"], eq["type"], eq["dept"],
            util_rate, temp, power, alarm, timestamp.strftime("%Y-%m-%d %H:%M:%S")
        ])

# 2. Generate Maintenance Records
maintenance_path = os.path.join(OUTPUT_DIR, "maintenance_records.csv")
print(f"Generating {maintenance_path}...")
with open(maintenance_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "record_id", "equipment_id", "technician_assigned", 
        "downtime_hours", "days_since_last_service", "maintenance_type"
    ])
    
    for i in range(scale["maintenance"]):
        eq = random.choice(EQUIPMENT_LIST)
        downtime = random.choice([0, random.randint(1, 48)])
        days_since = random.randint(5, 360)
        m_type = random.choice(["Routine", "Emergency", "Calibration"])
        
        # Emergency maintenance correlates with high downtime
        if m_type == "Emergency":
            downtime = random.randint(12, 72)
            
        writer.writerow([
            i + 1, eq["id"], random.choice(TECHNICIANS),
            downtime, days_since, m_type
        ])

# 3. Generate Bed & ICU Occupancy Logs
occupancy_path = os.path.join(OUTPUT_DIR, "bed_occupancy_logs.csv")
print(f"Generating {occupancy_path}...")
with open(occupancy_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "timestamp", "icu_beds_occupied", "icu_beds_total", 
        "er_beds_occupied", "er_beds_total", "emergency_queue_length"
    ])
    
    for i in range(scale["occupancy"]):
        timestamp = start_time + datetime.timedelta(seconds=(i * (860000 / scale["occupancy"])))
        icu_total = 50
        er_total = 80
        icu_occ = random.randint(25, 49)
        er_occ = random.randint(30, 78)
        
        # High ER occupancy drives longer queues
        if er_occ > 70:
            queue = random.randint(15, 38)
        else:
            queue = random.randint(0, 14)
            
        writer.writerow([
            timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            icu_occ, icu_total, er_occ, er_total, queue
        ])

# 4. Generate Emergency Incident Log
incidents_path = os.path.join(OUTPUT_DIR, "emergency_incident_log.csv")
print(f"Generating {incidents_path}...")
with open(incidents_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "incident_id", "department", "incident_type", "severity", 
        "equipment_required", "response_time_min", "resolution_time_min", "status"
    ])
    
    for i in range(scale["incidents"]):
        inc_id = f"INC-{1000 + i}"
        dept = random.choice(DEPARTMENTS)
        inc_type = random.choice(INCIDENT_TYPES)
        severity = random.choice(SEVERITIES)
        eq_req = random.choice(EQUIPMENT_TYPES)
        resp_time = random.randint(2, 25)
        
        # Critical incidents require fast response but take longer to resolve
        if severity == "Critical":
            resp_time = random.randint(2, 8)
            resol_time = random.randint(45, 180)
        else:
            resol_time = random.randint(15, 90)
            
        status = random.choice(["Resolved", "In-Progress"])
        
        writer.writerow([
            inc_id, dept, inc_type, severity,
            eq_req, resp_time, resol_time, status
        ])

print("Synthetic data generation completed successfully!")
