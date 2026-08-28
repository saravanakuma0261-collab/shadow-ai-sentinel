-- =============================================================================
-- Shadow AI Sentinel - Complete Supabase Database Schema
-- Paste this entire script into your Supabase SQL Editor and click "Run".
-- =============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Users Table
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    auth_provider VARCHAR(50) DEFAULT 'local',
    google_id VARCHAR(255),
    role VARCHAR(50) DEFAULT 'viewer',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Password Resets Table
CREATE TABLE IF NOT EXISTS public.password_resets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Scans Table
CREATE TABLE IF NOT EXISTS public.scans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP WITH TIME ZONE,
    source_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'running',
    triggered_by VARCHAR(255)
);

-- 4. Findings Table
CREATE TABLE IF NOT EXISTS public.findings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    scan_id VARCHAR(255) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_value VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    vendor VARCHAR(255) NOT NULL,
    sanction_status VARCHAR(50) DEFAULT 'unknown',
    data_exposure_bytes BIGINT DEFAULT 0,
    users_affected INTEGER DEFAULT 1,
    event_count INTEGER DEFAULT 1,
    risk_score NUMERIC(5,2) DEFAULT 0.0,
    risk_tier VARCHAR(50) DEFAULT 'low',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Fingerprint Domains Table
CREATE TABLE IF NOT EXISTS public.fingerprint_domains (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    domain VARCHAR(255) UNIQUE NOT NULL,
    category VARCHAR(100) NOT NULL,
    vendor VARCHAR(255) NOT NULL,
    sanctioned BOOLEAN DEFAULT FALSE
);

-- 6. Fingerprint Extensions Table
CREATE TABLE IF NOT EXISTS public.fingerprint_extensions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) UNIQUE NOT NULL,
    category VARCHAR(100) NOT NULL,
    vendor VARCHAR(255) NOT NULL,
    sanctioned BOOLEAN DEFAULT FALSE
);

-- 7. Agent Investigations Table
CREATE TABLE IF NOT EXISTS public.agent_investigations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    finding_id VARCHAR(255) NOT NULL,
    summary TEXT NOT NULL,
    recommendation VARCHAR(50) NOT NULL,
    rationale TEXT NOT NULL,
    confidence NUMERIC(4,2) DEFAULT 0.9,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 8. Alerts Log Table
CREATE TABLE IF NOT EXISTS public.alerts_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    finding_id VARCHAR(255) NOT NULL,
    channel VARCHAR(50) NOT NULL,
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'sent'
);

-- 9. Performance Indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
CREATE INDEX IF NOT EXISTS idx_findings_scan_id ON public.findings(scan_id);
CREATE INDEX IF NOT EXISTS idx_findings_risk_tier ON public.findings(risk_tier);
CREATE INDEX IF NOT EXISTS idx_scans_status ON public.scans(status);
