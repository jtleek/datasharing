-- Migration: 006_create_oauth_accounts
-- Description: Create oauth_accounts table for OAuth provider linking
-- Note: OAuth is scaffolding only, not enabled by default

CREATE TABLE oauth_accounts (
    id                  TEXT PRIMARY KEY,
    user_id             TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider            TEXT NOT NULL,
    provider_account_id TEXT NOT NULL,
    access_token        TEXT,
    refresh_token       TEXT,
    expires_at          TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    UNIQUE(provider, provider_account_id)
);

CREATE INDEX idx_oauth_accounts_user_id ON oauth_accounts(user_id);
CREATE INDEX idx_oauth_accounts_provider ON oauth_accounts(provider, provider_account_id);
