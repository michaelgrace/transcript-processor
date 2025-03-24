-- Create tables if they don't exist
CREATE TABLE IF NOT EXISTS transcripts (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    original_content TEXT NOT NULL,
    processed_content TEXT NOT NULL,
    format_style VARCHAR(50),
    source_type VARCHAR(50) DEFAULT 'transcript',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE transcripts ADD COLUMN IF NOT EXISTS source_type VARCHAR(50) DEFAULT 'transcript';

CREATE TABLE IF NOT EXISTS post_ideas (
    id SERIAL PRIMARY KEY,
    transcript_id INTEGER REFERENCES transcripts(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE post_ideas ADD CONSTRAINT unique_transcript_post_ideas UNIQUE (transcript_id);

CREATE TABLE IF NOT EXISTS rewrites (
    id SERIAL PRIMARY KEY,
    transcript_id INTEGER REFERENCES transcripts(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    options TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add transcript metadata table
CREATE TABLE IF NOT EXISTS transcript_metadata (
    transcript_id INTEGER PRIMARY KEY REFERENCES transcripts(id) ON DELETE CASCADE,
    topics JSONB,
    keywords JSONB,
    sentiment JSONB,
    tags JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add analytics table
CREATE TABLE IF NOT EXISTS analytics (
    id SERIAL PRIMARY KEY,
    transcript_id INTEGER REFERENCES transcripts(id) ON DELETE CASCADE,
    action_type VARCHAR(50) NOT NULL,
    action_details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_transcripts_created_at ON transcripts(created_at);
CREATE INDEX IF NOT EXISTS idx_post_ideas_transcript_id ON post_ideas(transcript_id);
CREATE INDEX IF NOT EXISTS idx_rewrites_transcript_id ON rewrites(transcript_id);
CREATE INDEX IF NOT EXISTS idx_topics ON transcript_metadata USING gin (topics);
CREATE INDEX IF NOT EXISTS idx_keywords ON transcript_metadata USING gin (keywords);
CREATE INDEX IF NOT EXISTS idx_tags ON transcript_metadata USING gin (tags);
CREATE INDEX IF NOT EXISTS idx_analytics_transcript_id ON analytics(transcript_id);
CREATE INDEX IF NOT EXISTS idx_analytics_action_type ON analytics(action_type);