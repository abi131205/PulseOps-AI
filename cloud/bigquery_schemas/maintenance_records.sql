CREATE TABLE IF NOT EXISTS `pulseops_ai.maintenance_records` (
  record_id INT64,
  equipment_id STRING,
  technician_assigned STRING,
  downtime_hours INT64,
  days_since_last_service INT64,
  maintenance_type STRING
);
