# Optimized Query Results

## 01_recent_logs_optimized

## Purpose
Fetch recent logs while selecting only the columns needed for browsing and analysis.

## Baseline Time
242.98 ms

## Optimized Time
194.51 ms

## Improvement
About 1.25x faster

## Observation
This query improved only modestly because it still scans the raw `logs` table. The main gain came from reducing row width by avoiding `SELECT *`.

## 02_errors_by_service_optimized

## Purpose
Count service-wise errors using precomputed daily service summaries instead of rescanning the raw fact table.

## Baseline Time
248.89 ms

## Optimized Time
0.87 ms

## Improvement
About 287x faster

## Observation
The largest gain came from using `mv_daily_service_activity`, where error counts are already summarized per day and service.

## 03_slowest_endpoints_optimized

## Purpose
Find slow endpoints using pre-aggregated daily endpoint latency summaries.

## Baseline Time
254.35 ms

## Optimized Time
6.63 ms

## Improvement
About 38x faster

## Observation
The query no longer groups over the full `logs` table and instead uses `mv_daily_endpoint_latency`.

## 04_status_code_distribution_optimized

## Purpose
Compute the distribution of status codes using daily summarized counts.

## Baseline Time
245.88 ms

## Optimized Time
14.96 ms

## Improvement
About 16x faster

## Observation
This optimization reduced the scan size from the raw million-row fact table to the materialized-view summary table.

## 05_service_activity_optimized

## Purpose
Measure recent service activity using daily service summaries.

## Baseline Time
242.17 ms

## Optimized Time
1.02 ms

## Improvement
About 237x faster

## Observation
Filtering and aggregating over daily service summaries made the query dramatically faster than scanning recent raw logs.
