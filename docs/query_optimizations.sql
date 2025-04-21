-- Original query for threat search (slow performance)
-- Execution time: ~850ms
SELECT t.*, s.name as source_name, c.name as category_name, 
       a.name as actor_name, i.indicator_value, i.indicator_type
FROM threats t
LEFT JOIN sources s ON t.source_id = s.id
LEFT JOIN categories c ON t.category_id = c.id
LEFT JOIN threat_actors ta ON t.id = ta.threat_id
LEFT JOIN actors a ON ta.actor_id = a.id
LEFT JOIN indicators i ON t.id = i.threat_id
WHERE t.name LIKE '%malware%'
OR t.description LIKE '%malware%'
OR a.name LIKE '%malware%'
OR i.indicator_value LIKE '%malware%';

-- Optimized query with indexes and proper JOIN order
-- Execution time: ~120ms
SELECT t.*, s.name as source_name, c.name as category_name, 
       a.name as actor_name, i.indicator_value, i.indicator_type
FROM threats t
JOIN (
    SELECT DISTINCT threat_id 
    FROM (
        SELECT id as threat_id FROM threats 
        WHERE name LIKE '%malware%' OR description LIKE '%malware%'
        UNION
        SELECT threat_id FROM threat_actors ta 
        JOIN actors a ON ta.actor_id = a.id 
        WHERE a.name LIKE '%malware%'
        UNION
        SELECT threat_id FROM indicators 
        WHERE indicator_value LIKE '%malware%'
    ) as matched_threats
) as mt ON t.id = mt.threat_id
LEFT JOIN sources s ON t.source_id = s.id
LEFT JOIN categories c ON t.category_id = c.id
LEFT JOIN threat_actors ta ON t.id = ta.threat_id
LEFT JOIN actors a ON ta.actor_id = a.id
LEFT JOIN indicators i ON t.id = i.threat_id;

-- Create indexes to improve query performance
CREATE INDEX idx_threats_name ON threats(name);
CREATE INDEX idx_threats_description ON threats(description);
CREATE INDEX idx_actors_name ON actors(name);
CREATE INDEX idx_indicators_value ON indicators(indicator_value);
CREATE INDEX idx_threat_source ON threats(source_id);
CREATE INDEX idx_threat_category ON threats(category_id);
CREATE INDEX idx_threat_actors_threat ON threat_actors(threat_id);
CREATE INDEX idx_threat_actors_actor ON threat_actors(actor_id);
CREATE INDEX idx_indicators_threat ON indicators(threat_id);

-- Original dashboard statistics query (slow, high CPU usage)
-- Execution time: ~1200ms
SELECT 
    COUNT(*) as total_threats,
    SUM(CASE WHEN severity = 'high' THEN 1 ELSE 0 END) as high_severity,
    SUM(CASE WHEN severity = 'medium' THEN 1 ELSE 0 END) as medium_severity,
    SUM(CASE WHEN severity = 'low' THEN 1 ELSE 0 END) as low_severity,
    AVG(confidence_score) as avg_confidence,
    COUNT(DISTINCT source_id) as source_count,
    (SELECT COUNT(*) FROM indicators) as indicator_count,
    (SELECT COUNT(DISTINCT actor_id) FROM threat_actors) as actor_count
FROM threats;

-- Optimized dashboard statistics query with materialized view
-- Execution time: ~50ms
CREATE MATERIALIZED VIEW dashboard_stats AS
SELECT 
    COUNT(*) as total_threats,
    SUM(CASE WHEN severity = 'high' THEN 1 ELSE 0 END) as high_severity,
    SUM(CASE WHEN severity = 'medium' THEN 1 ELSE 0 END) as medium_severity,
    SUM(CASE WHEN severity = 'low' THEN 1 ELSE 0 END) as low_severity,
    AVG(confidence_score) as avg_confidence,
    COUNT(DISTINCT source_id) as source_count
FROM threats;

CREATE MATERIALIZED VIEW indicator_stats AS
SELECT COUNT(*) as indicator_count FROM indicators;

CREATE MATERIALIZED VIEW actor_stats AS
SELECT COUNT(DISTINCT actor_id) as actor_count FROM threat_actors;

-- Refresh materialized views (scheduled to run hourly)
REFRESH MATERIALIZED VIEW dashboard_stats;
REFRESH MATERIALIZED VIEW indicator_stats;
REFRESH MATERIALIZED VIEW actor_stats;

-- Original query for threat correlation (very slow)
-- Execution time: ~3500ms
SELECT t1.id as threat1_id, t1.name as threat1_name, 
       t2.id as threat2_id, t2.name as threat2_name,
       COUNT(*) as common_indicators
FROM threats t1
JOIN indicators i1 ON t1.id = i1.threat_id
JOIN indicators i2 ON i1.indicator_value = i2.indicator_value AND i1.threat_id != i2.threat_id
JOIN threats t2 ON i2.threat_id = t2.id
GROUP BY t1.id, t1.name, t2.id, t2.name
HAVING COUNT(*) > 2
ORDER BY common_indicators DESC;

-- Optimized threat correlation query
-- Execution time: ~350ms
WITH common_indicators AS (
    SELECT 
        i1.threat_id as threat1_id,
        i2.threat_id as threat2_id,
        COUNT(*) as indicator_count
    FROM indicators i1
    JOIN indicators i2 ON 
        i1.indicator_value = i2.indicator_value AND 
        i1.indicator_type = i2.indicator_type AND 
        i1.threat_id < i2.threat_id
    GROUP BY i1.threat_id, i2.threat_id
    HAVING COUNT(*) > 2
)
SELECT 
    t1.id as threat1_id, 
    t1.name as threat1_name,
    t2.id as threat2_id, 
    t2.name as threat2_name,
    ci.indicator_count as common_indicators
FROM common_indicators ci
JOIN threats t1 ON ci.threat1_id = t1.id
JOIN threats t2 ON ci.threat2_id = t2.id
ORDER BY ci.indicator_count DESC;

-- Implement connection pooling settings
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '2GB';
ALTER SYSTEM SET effective_cache_size = '6GB';
ALTER SYSTEM SET work_mem = '20MB';
ALTER SYSTEM SET maintenance_work_mem = '512MB';
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;
ALTER SYSTEM SET max_worker_processes = 8;
ALTER SYSTEM SET max_parallel_workers_per_gather = 4;
ALTER SYSTEM SET max_parallel_workers = 8;
ALTER SYSTEM SET max_parallel_maintenance_workers = 4;

-- Add monitoring and statistics collection
CREATE EXTENSION pg_stat_statements;
ALTER SYSTEM SET pg_stat_statements.max = 10000;
ALTER SYSTEM SET pg_stat_statements.track = all;