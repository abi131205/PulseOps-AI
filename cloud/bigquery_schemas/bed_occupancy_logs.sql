CREATE TABLE IF NOT EXISTS `pulseops_ai.bed_occupancy_logs` (
  timestamp TIMESTAMP,
  icu_beds_occupied INT64,
  icu_beds_total INT64,
  er_beds_occupied INT64,
  er_beds_total INT64,
  emergency_queue_length INT64
);
