EXPLAIN ANALYZE
SELECT *
FROM logs l
JOIN log_levels ll
ON l.log_level_id = ll.log_level_id
WHERE ll.level_name = 'ERROR'
AND created_at >= NOW() - INTERVAL '30 days';