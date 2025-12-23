-- Create workflows table
CREATE TABLE workflows (
    id BIGSERIAL PRIMARY KEY,
    workflow_name VARCHAR(500) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    platform_id VARCHAR(255),
    country VARCHAR(10),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_workflow UNIQUE(platform, platform_id, country)
);

ALTER TABLE workflows ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read access" ON workflows
    FOR SELECT USING (true);

CREATE POLICY "Allow service role full access" ON workflows
    FOR ALL USING (auth.role() = 'service_role');

CREATE INDEX idx_workflows_platform ON workflows(platform);
CREATE INDEX idx_workflows_country ON workflows(country);
CREATE INDEX idx_workflows_created_at ON workflows(created_at DESC);

-- Create popularity_metrics table
CREATE TABLE popularity_metrics (
    id BIGSERIAL PRIMARY KEY,
    workflow_id BIGINT REFERENCES workflows(id) ON DELETE CASCADE,
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    like_to_view_ratio DECIMAL(10, 6),
    comment_to_view_ratio DECIMAL(10, 6),
    engagement_score DECIMAL(10, 4),
    replies INTEGER,
    participants INTEGER,
    search_volume INTEGER,
    trend_direction VARCHAR(20),
    growth_percentage DECIMAL(10, 2),
    collected_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE popularity_metrics ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read access" ON popularity_metrics
    FOR SELECT USING (true);

CREATE POLICY "Allow service role full access" ON popularity_metrics
    FOR ALL USING (auth.role() = 'service_role');

CREATE INDEX idx_metrics_workflow_id ON popularity_metrics(workflow_id);
CREATE INDEX idx_metrics_collected_at ON popularity_metrics(collected_at DESC);
CREATE INDEX idx_metrics_engagement ON popularity_metrics(engagement_score DESC);

-- Create collection_logs table
CREATE TABLE collection_logs (
    id BIGSERIAL PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    workflows_collected INTEGER DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE collection_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read access" ON collection_logs
    FOR SELECT USING (true);

CREATE POLICY "Allow service role full access" ON collection_logs
    FOR ALL USING (auth.role() = 'service_role');

CREATE INDEX idx_logs_created_at ON collection_logs(created_at DESC);
CREATE INDEX idx_logs_platform ON collection_logs(platform);

-- Create auto-update trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_workflows_updated_at BEFORE UPDATE ON workflows
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
