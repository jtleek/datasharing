-- Migration: 003_create_sessions
-- Description: Create sessions table for database-backed session management
-- Based on: MVP recommendation in AUTHENTICATION_FLOWS.md

CREATE TABLE sessions (
    id          TEXT PRIMARY KEY,
    user_id     TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash  TEXT NOT NULL UNIQUE,
    expires_at  TIMESTAMPTZ NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    user_agent  TEXT,
    ip_address  TEXT
);

-- Index for token lookups (primary auth path)
CREATE INDEX idx_sessions_token_hash ON sessions(token_hash);

-- Index for user session management
CREATE INDEX idx_sessions_user_id ON sessions(user_id);

-- Index for cleanup of expired sessions
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);
