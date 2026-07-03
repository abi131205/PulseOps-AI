CREATE TABLE IF NOT EXISTS `pulseops_ai.equipment_telemetry` (
  log_id INT64,
  equipment_id STRING,
  name STRING,
  department STRING,
  utilization_rate FLOAT64,
  temperature FLOAT64,
  power_draw FLOAT64,
  alarm_status INT64,
  timestamp TIMESTAMP
);
