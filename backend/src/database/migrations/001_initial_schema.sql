-- Initial database schema for RAG Chatbot Backend
-- Creates tables for chat sessions, messages, and indexing jobs

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Chat Sessions Table
CREATE TABLE IF NOT EXISTS chat_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    user_id UUID NULL,
    CONSTRAINT chk_activity_after_creation CHECK (last_activity >= created_at)
);

-- Index for session cleanup queries
CREATE INDEX IF NOT EXISTS idx_chat_sessions_last_activity
    ON chat_sessions(last_activity DESC);

-- Index for user queries (future auth)
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id
    ON chat_sessions(user_id) WHERE user_id IS NOT NULL;

-- Chat Messages Table
CREATE TABLE IF NOT EXISTS chat_messages (
    message_id SERIAL PRIMARY KEY,
    session_id UUID NOT NULL,
    question TEXT NOT NULL CHECK (char_length(question) <= 5000),
    answer TEXT NOT NULL,
    cited_sources JSONB NOT NULL DEFAULT '[]'::jsonb,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    response_time_ms INTEGER NOT NULL CHECK (response_time_ms > 0),
    CONSTRAINT fk_session FOREIGN KEY(session_id)
        REFERENCES chat_sessions(session_id) ON DELETE CASCADE
);

-- Index for retrieving messages by session
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_timestamp
    ON chat_messages(session_id, timestamp DESC);

-- Index for recent messages queries
CREATE INDEX IF NOT EXISTS idx_chat_messages_timestamp
    ON chat_messages(timestamp DESC);

-- Indexing Jobs Table (for tracking chapter indexing)
CREATE TABLE IF NOT EXISTS indexing_jobs (
    job_id SERIAL PRIMARY KEY,
    chapter_id VARCHAR(100) NOT NULL UNIQUE,
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'in_progress', 'completed', 'failed')),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE NULL,
    chunks_indexed INTEGER DEFAULT 0,
    error_message TEXT NULL,
    CONSTRAINT chk_completed_after_started CHECK (completed_at IS NULL OR completed_at >= started_at)
);

-- Index for job status queries
CREATE INDEX IF NOT EXISTS idx_indexing_jobs_status
    ON indexing_jobs(status);

-- Index for chapter lookup
CREATE INDEX IF NOT EXISTS idx_indexing_jobs_chapter
    ON indexing_jobs(chapter_id);

-- Comments for documentation
COMMENT ON TABLE chat_sessions IS 'Stores user conversation sessions for multi-turn dialogue';
COMMENT ON TABLE chat_messages IS 'Stores individual question-answer exchanges with citations';
COMMENT ON TABLE indexing_jobs IS 'Tracks textbook chapter indexing progress and status';
