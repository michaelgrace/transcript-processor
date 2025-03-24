-- fix-db.sql
CREATE TABLE IF NOT EXISTS transcript_metadata (
    transcript_id INTEGER PRIMARY KEY REFERENCES transcripts(id) ON DELETE CASCADE,
    topics JSONB,
    keywords JSONB,
    sentiment JSONB,
    tags JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS analytics (
    id SERIAL PRIMARY KEY,
    transcript_id INTEGER REFERENCES transcripts(id) ON DELETE CASCADE,
    action_type VARCHAR(50) NOT NULL,
    action_details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_topics ON transcript_metadata USING gin (topics);
CREATE INDEX IF NOT EXISTS idx_keywords ON transcript_metadata USING gin (keywords);
CREATE INDEX IF NOT EXISTS idx_tags ON transcript_metadata USING gin (tags);
CREATE INDEX IF NOT EXISTS idx_analytics_action_type ON analytics(action_type);