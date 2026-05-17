# OLAP Aggregation

## Overview

OLAP aggregation was added to support multi-dimensional analysis on top of the log dataset. While materialized views in this project focus on single-purpose summaries, OLAP aggregation supports multiple reporting dimensions from one summary structure.

This is useful for drill-down and roll-up style reporting, where the same dataset may be analyzed by:

- day
- service
- endpoint
- log level
- status code

## What Was Implemented

An OLAP-style materialized summary was created:

- [sql/schema/03_create_olap_aggregation.sql](/D:/Academia/Semester%206/Advanced%20DBMS/Project/log-management-analytics-system/sql/schema/03_create_olap_aggregation.sql)

The summary object is:

- `mv_log_olap_daily`

It uses PostgreSQL `GROUPING SETS` to create several useful rollups inside one summary object instead of using a full `CUBE`.

The selected grouping sets are:

- daily total
- daily service summary
- daily endpoint summary
- daily log level summary
- daily status code summary
- daily service plus log level summary

Benchmark/example queries were added in:

- [sql/benchmarks/olap/01_service_error_trend_from_olap.sql](/D:/Academia/Semester%206/Advanced%20DBMS/Project/log-management-analytics-system/sql/benchmarks/olap/01_service_error_trend_from_olap.sql)
- [sql/benchmarks/olap/02_log_level_trend_from_olap.sql](/D:/Academia/Semester%206/Advanced%20DBMS/Project/log-management-analytics-system/sql/benchmarks/olap/02_log_level_trend_from_olap.sql)
- [sql/benchmarks/olap/03_daily_totals_from_olap.sql](/D:/Academia/Semester%206/Advanced%20DBMS/Project/log-management-analytics-system/sql/benchmarks/olap/03_daily_totals_from_olap.sql)

## Why GROUPING SETS Were Used

PostgreSQL supports advanced OLAP-style aggregation using `GROUPING SETS`, `ROLLUP`, and `CUBE`.

For this project, `GROUPING SETS` was the best fit because:

- it gives control over exactly which summaries are generated
- it avoids unnecessary combinations
- it keeps the summary table smaller than a full cube
- it matches the project workload better than a generic all-dimensions aggregation

A full `CUBE` would generate many combinations that are not needed for this project and would increase storage and refresh cost.

## How It Works

The raw `logs` table contains detailed records for every event. OLAP aggregation transforms that fact table into a summary layer with multiple rollup levels.

The column `aggregation_level` labels what each row represents, such as:

- `day_total`
- `day_service`
- `day_endpoint`
- `day_log_level`
- `day_status_code`
- `day_service_log_level`

This allows one materialized object to answer multiple types of reporting questions.

## How It Improves Performance

Without OLAP aggregation, every trend or drill-down query would need to:

- scan the raw `logs` table
- group rows by different dimensions
- calculate counts and averages repeatedly
- sort the grouped result every time

With OLAP aggregation:

- the rollups are precomputed
- repeated trend analysis becomes much cheaper
- multiple dimensions can be queried from one summary layer
- reporting queries avoid repeated full-table grouping

This improves performance especially for:

- daily service trends
- daily error trends
- log-level trend reports
- daily totals and summaries

## Benefits

- supports multi-dimensional analytics
- enables drill-down and roll-up style reporting
- avoids repeated heavy aggregation on the fact table
- creates one reusable analytical summary object

## Trade-Offs

- OLAP summaries use extra storage
- refresh time increases because more group combinations are computed
- results are not real-time and depend on refresh timing
- too many grouping combinations can cause summary growth

## Why It Fits This Project

This project has:

- a large fact table
- repeated analytics queries
- a small number of dimensions like services, endpoints, and log levels

That makes OLAP aggregation a strong fit because the number of useful dimensions is manageable, while the raw row count is large enough that repeated aggregation becomes costly.

## Conclusion

OLAP aggregation was implemented using `GROUPING SETS` to create a reusable multi-dimensional summary over the log dataset. This adds a true analytics layer beyond simple dashboard summaries and supports more flexible reporting without repeatedly scanning the full `logs` table.
