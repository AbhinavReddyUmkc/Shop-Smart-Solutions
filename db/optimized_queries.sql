-- Create optimized indexes for threat detection system
CREATE INDEX idx_threat_type_risk ON threat_data(threat_type, risk_score);
CREATE INDEX idx_timestamp_risk ON threat_data(event_timestamp, risk_score);
CREATE INDEX idx_source_ip ON threat_data(source_ip) WHERE source_ip IS NOT NULL;

-- For text search operations
CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- PostgreSQL specific
CREATE INDEX idx_threat_description_trgm ON threat_data USING gin (description gin_trgm_ops);

-- Regularly analyze tables for query optimization
ANALYZE threat_data;

-- Set up automated vacuum for PostgreSQL (adjust for your DBMS)
ALTER TABLE threat_data SET (autovacuum_enabled = true, autovacuum_vacuum_scale_factor = 0.1);
