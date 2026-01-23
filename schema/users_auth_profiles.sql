-- =============================================================================
-- CloudPeople: Minimal PostgreSQL Schema
-- Scope: Users, Authentication, User Profiles (Identity Only)
-- Based on: CP Build 1 Specification
-- =============================================================================

-- -----------------------------------------------------------------------------
-- ENUM: user_role
-- From CP Build 1: UserRole enum defines access control boundaries
-- -----------------------------------------------------------------------------

CREATE TYPE user_role AS ENUM (
    'CANDIDATE',
    'EMPLOYER',
    'ADMIN'
);

-- -----------------------------------------------------------------------------
-- TABLE: users
-- Core user account for authentication
-- Rationale: Matches the User model from CP Build 1 spec, containing only
-- fields necessary for identity and authentication - no marketplace logic.
-- -----------------------------------------------------------------------------

CREATE TABLE users (
    id              TEXT PRIMARY KEY,           -- cuid() generated in application layer
    email           TEXT NOT NULL UNIQUE,       -- Primary login identifier
    email_verified  TIMESTAMPTZ,                -- NULL = unverified, timestamp = when verified
    password        TEXT NOT NULL,              -- Hashed password (algorithm chosen at app layer)
    role            user_role NOT NULL,         -- Determines profile type + route access
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login      TIMESTAMPTZ                 -- Tracks most recent authentication
);

-- Index for login lookups
CREATE INDEX idx_users_email ON users(email);

-- Index for role-based queries (e.g., admin listing all employers)
CREATE INDEX idx_users_role ON users(role);

-- -----------------------------------------------------------------------------
-- TABLE: user_profiles
-- Minimal identity information for any user type
-- Rationale: Extracted common identity fields from Candidate/Employer models.
-- Contains only display/identity data, no marketplace-specific attributes.
-- -----------------------------------------------------------------------------

CREATE TABLE user_profiles (
    id              TEXT PRIMARY KEY,           -- cuid() generated in application layer
    user_id         TEXT NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    
    -- Identity fields (common to all user types)
    first_name      TEXT NOT NULL,
    last_name       TEXT NOT NULL,
    display_name    TEXT,                       -- Optional public display name
    avatar_url      TEXT,                       -- Profile image (stored in S3 per spec)
    
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);

-- =============================================================================
-- AUTHENTICATION STRATEGY OPTIONS
-- =============================================================================
-- 
-- CP Build 1 mentions multiple authentication approaches. This schema does NOT
-- prescribe a specific strategy. Options to consider:
--
-- OPTION A: Server-side Sessions (Database-backed)
-- ------------------------------------------------
-- CREATE TABLE sessions (
--     id          TEXT PRIMARY KEY,
--     user_id     TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
--     token       TEXT NOT NULL UNIQUE,
--     expires_at  TIMESTAMPTZ NOT NULL,
--     created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
-- );
--
-- Pros: Easy revocation, server control, works with NextAuth.js database adapter
-- Cons: Database lookup on each request, horizontal scaling requires shared store
--
-- OPTION B: JWT Tokens (Stateless)
-- --------------------------------
-- No database table required. Tokens are self-contained and verified via signature.
-- Refresh tokens may optionally be stored for revocation.
--
-- Pros: Stateless, scalable, no DB hit per request
-- Cons: Cannot revoke until expiry (unless using blocklist), token size in requests
--
-- OPTION C: Hybrid (JWT + Redis Session Cache)
-- --------------------------------------------
-- Short-lived JWTs for API auth, with session state cached in Redis (per spec:
-- "AWS ElastiCache - Redis for sessions/caching").
--
-- Pros: Best of both - stateless verification, centralized revocation
-- Cons: Additional infrastructure dependency
--
-- RECOMMENDATION: Defer decision until authentication implementation phase.
-- The users table above supports all three options.
--
-- =============================================================================

-- =============================================================================
-- END OF SCHEMA
-- =============================================================================
