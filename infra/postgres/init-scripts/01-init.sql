-- PostgreSQL Initialization Script for Project Sentinel
-- This runs automatically when starting the PostgreSQL container

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- pgvector extension is optional (may not be available in standard PostgreSQL image)
-- CREATE EXTENSION IF NOT EXISTS "pgvector";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- === STUDENT 1: INPUT LAYER TABLES ===

-- Assets table
CREATE TABLE IF NOT EXISTS assets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    ip_address INET,
    hostname VARCHAR(255),
    os_type VARCHAR(100),
    asset_type VARCHAR(50) DEFAULT 'generic',
    asset_criticality INTEGER DEFAULT 5 CHECK (asset_criticality >= 1 AND asset_criticality <= 10),
    owner_team VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_scanned TIMESTAMP
);

CREATE INDEX idx_assets_ip ON assets(ip_address);
CREATE INDEX idx_assets_hostname ON assets(hostname);

-- Events table
CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asset_id UUID REFERENCES assets(id) ON DELETE SET NULL,
    event_type VARCHAR(50) NOT NULL CHECK (event_type IN ('Auth', 'Access', 'Admin', 'System')),
    source_ip INET,
    user_id VARCHAR(255),
    action VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'success' CHECK (status IN ('success', 'failure')),
    severity INTEGER DEFAULT 5 CHECK (severity >= 1 AND severity <= 10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    raw_data JSONB
);

CREATE INDEX idx_events_asset ON events(asset_id);
CREATE INDEX idx_events_type ON events(event_type);
CREATE INDEX idx_events_created ON events(created_at DESC);
CREATE INDEX idx_events_user ON events(user_id);
CREATE INDEX idx_events_raw_data ON events USING GIN(raw_data);

-- SBOM records
CREATE TABLE IF NOT EXISTS sbom_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asset_id UUID REFERENCES assets(id) ON DELETE CASCADE,
    component_name VARCHAR(255),
    version VARCHAR(100),
    component_type VARCHAR(50),
    vulnerability_count INTEGER DEFAULT 0,
    high_criticality_vulns INTEGER DEFAULT 0,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sbom_asset ON sbom_records(asset_id);
CREATE INDEX idx_sbom_vulns ON sbom_records(vulnerability_count);

-- Golden baseline
CREATE TABLE IF NOT EXISTS golden_baseline (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asset_id UUID UNIQUE REFERENCES assets(id) ON DELETE CASCADE,
    file_hash VARCHAR(512),
    config_hash VARCHAR(512),
    baseline_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- === STUDENT 2: ENRICHMENT LAYER TABLES ===

-- Enriched events
CREATE TABLE IF NOT EXISTS enriched_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_id UUID UNIQUE REFERENCES events(id) ON DELETE CASCADE,
    
    -- GeoIP enrichment
    country_iso VARCHAR(2),
    city VARCHAR(100),
    is_vpn BOOLEAN DEFAULT FALSE,
    is_tor BOOLEAN DEFAULT FALSE,
    geo_risk_score FLOAT DEFAULT 0.0,
    
    -- CTI enrichment
    known_malicious BOOLEAN DEFAULT FALSE,
    cti_sources TEXT[],
    
    -- MITRE enrichment
    mitre_tactic VARCHAR(100),
    mitre_technique VARCHAR(100),
    mitre_technique_id VARCHAR(50),
    mitre_confidence FLOAT DEFAULT 0.0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_enriched_event ON enriched_events(event_id);
CREATE INDEX idx_enriched_geo_risk ON enriched_events(geo_risk_score);
CREATE INDEX idx_enriched_malicious ON enriched_events(known_malicious);
CREATE INDEX idx_enriched_mitre ON enriched_events(mitre_tactic, mitre_technique);

-- Attack trends (time-series)
CREATE TABLE IF NOT EXISTS attack_trends (
    time TIMESTAMPTZ NOT NULL,
    tactic VARCHAR(100),
    technique VARCHAR(100),
    event_count INTEGER,
    severity_avg FLOAT
);

SELECT create_hypertable('attack_trends', 'time', if_not_exists => TRUE);
CREATE INDEX idx_trends_tactic ON attack_trends(time DESC, tactic);

-- === STUDENT 3: INTELLIGENCE LAYER TABLES ===

-- Risk assessments
CREATE TABLE IF NOT EXISTS risk_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_id UUID REFERENCES events(id) ON DELETE CASCADE,
    asset_id UUID REFERENCES assets(id) ON DELETE CASCADE,
    
    event_severity INTEGER CHECK (event_severity >= 1 AND event_severity <= 10),
    asset_criticality INTEGER CHECK (asset_criticality >= 1 AND asset_criticality <= 10),
    risk_score FLOAT CHECK (risk_score >= 0 AND risk_score <= 100),
    risk_level VARCHAR(20) DEFAULT 'LOW',
    
    advisory_text TEXT,
    ai_confidence FLOAT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_risk_asset ON risk_assessments(asset_id);
CREATE INDEX idx_risk_score ON risk_assessments(risk_score DESC);
CREATE INDEX idx_risk_level ON risk_assessments(risk_level);

-- Playbooks
CREATE TABLE IF NOT EXISTS playbooks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_id UUID REFERENCES events(id),
    asset_id UUID REFERENCES assets(id),
    
    automation_type VARCHAR(100),
    commands TEXT[],
    
    execution_status VARCHAR(50) DEFAULT 'draft' CHECK (execution_status IN ('draft', 'pending', 'approved', 'executed', 'failed', 'rolled_back')),
    approver_id VARCHAR(255),
    approved_at TIMESTAMP,
    
    executed_by VARCHAR(255),
    executed_at TIMESTAMP,
    audit_log JSONB,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_playbook_status ON playbooks(execution_status);
CREATE INDEX idx_playbook_event ON playbooks(event_id);

-- ChatOps interactions
CREATE TABLE IF NOT EXISTS chatops_interactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255),
    channel VARCHAR(50) CHECK (channel IN ('telegram', 'discord')),
    query TEXT,
    response TEXT,
    action_taken VARCHAR(255),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_chatops_user ON chatops_interactions(user_id);
CREATE INDEX idx_chatops_timestamp ON chatops_interactions(timestamp DESC);

-- === UTILITY TABLES ===

-- Audit log
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255),
    action VARCHAR(255),
    resource_type VARCHAR(100),
    resource_id UUID,
    changes JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_created ON audit_logs(created_at DESC);

-- Configuration/settings
CREATE TABLE IF NOT EXISTS system_settings (
    key VARCHAR(255) PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default settings
INSERT INTO system_settings (key, value) VALUES
    ('risk_threshold_critical', '80'),
    ('risk_threshold_high', '60'),
    ('risk_threshold_medium', '40'),
    ('max_events_retention_days', '365'),
    ('enable_ai_advisor', 'true'),
    ('enable_chatops', 'false')
ON CONFLICT(key) DO UPDATE SET value = EXCLUDED.value;

-- === VIEWS ===

-- Dashboard risk summary
CREATE OR REPLACE VIEW risk_summary AS
SELECT 
    r.risk_level,
    COUNT(*) as count,
    AVG(r.risk_score) as avg_score,
    MAX(r.created_at) as latest
FROM risk_assessments r
WHERE r.created_at > NOW() - INTERVAL '24 hours'
GROUP BY r.risk_level;

-- Top at-risk assets
CREATE OR REPLACE VIEW at_risk_assets AS
SELECT 
    a.id,
    a.name,
    a.ip_address,
    MAX(r.risk_score) as max_risk_score,
    COUNT(DISTINCT e.id) as event_count_24h
FROM assets a
LEFT JOIN risk_assessments r ON a.id = r.asset_id
LEFT JOIN events e ON a.id = e.asset_id AND e.created_at > NOW() - INTERVAL '24 hours'
GROUP BY a.id, a.name, a.ip_address
ORDER BY max_risk_score DESC NULLS LAST;

-- === GRANTS ===

GRANT USAGE ON SCHEMA public TO sentinel_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO sentinel_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO sentinel_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO sentinel_user;
