CREATE TABLE IF NOT EXISTS `pulseops_ai.emergency_incident_log` (
  incident_id STRING,
  department STRING,
  incident_type STRING,
  severity STRING,
  equipment_required STRING,
  response_time_min INT64,
  resolution_time_min INT64,
  status STRING
);
