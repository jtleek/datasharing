-- =============================================================================
-- CloudPeople: Minimal PostgreSQL Schema
-- Scope: Users, Authentication, User Profiles
-- Based on: CP Build 1 Specification
-- =============================================================================

-- -----------------------------------------------------------------------------
-- ENUMS (from CP Build 1 spec)
-- -----------------------------------------------------------------------------

CREATE TYPE user_role AS ENUM (
    'CANDIDATE',
    'EMPLOYER',
    'ADMIN'
);

CREATE TYPE candidate_status AS ENUM (
    'DRAFT',
    'ACTIVE',
    'PAUSED',
    'CLOSED'
);

CREATE TYPE employer_verification_status AS ENUM (
    'PENDING',
    'VERIFIED',
    'REJECTED',
    'SUSPENDED'
);

-- -----------------------------------------------------------------------------
-- TABLE: users
-- Core user account for authentication
-- -----------------------------------------------------------------------------

CREATE TABLE users (
    id              TEXT PRIMARY KEY,           -- cuid() in application layer
    email           TEXT NOT NULL UNIQUE,
    email_verified  TIMESTAMPTZ,
    password        TEXT NOT NULL,              -- bcrypt hash (per spec security section)
    role            user_role NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login      TIMESTAMPTZ
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- -----------------------------------------------------------------------------
-- TABLE: sessions
-- Token-based session management (NextAuth.js compatible)
-- -----------------------------------------------------------------------------

CREATE TABLE sessions (
    id          TEXT PRIMARY KEY,               -- cuid() in application layer
    user_id     TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token       TEXT NOT NULL UNIQUE,
    expires_at  TIMESTAMPTZ NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_token ON sessions(token);
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);

-- -----------------------------------------------------------------------------
-- TABLE: candidates
-- Profile for users with role = 'CANDIDATE'
-- -----------------------------------------------------------------------------

CREATE TABLE candidates (
    id                  TEXT PRIMARY KEY,       -- cuid() in application layer
    user_id             TEXT NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    status              candidate_status NOT NULL DEFAULT 'DRAFT',
    
    -- Profile basics
    first_name          TEXT NOT NULL,
    last_name           TEXT NOT NULL,
    headline            TEXT,
    bio                 TEXT,
    profile_image_url   TEXT,
    
    -- Professional details
    current_title       TEXT,
    years_experience    INTEGER,
    skills              TEXT[],                 -- Array of skill tags
    domains             TEXT[],                 -- Industry domains
    seniority           TEXT,                   -- Junior, Mid, Senior, Lead, Principal, etc.
    
    -- Location & work preferences
    location            TEXT,
    remote_preference   TEXT,                   -- Remote, Hybrid, Onsite, Flexible
    timezone            TEXT,
    work_authorization  TEXT[],                 -- US, UK, EU, etc.
    
    -- Salary & availability (auction floor)
    min_salary          DECIMAL NOT NULL,
    currency            TEXT NOT NULL DEFAULT 'USD',
    available_from      TIMESTAMPTZ,
    notice_period       INTEGER,                -- Days
    
    -- Visibility controls
    is_searchable       BOOLEAN NOT NULL DEFAULT TRUE,
    is_public           BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- External links & attachments
    portfolio_url       TEXT,
    github_url          TEXT,
    linkedin_url        TEXT,
    resume_url          TEXT,
    certifications      TEXT[],
    
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_candidates_user_id ON candidates(user_id);
CREATE INDEX idx_candidates_status ON candidates(status);
CREATE INDEX idx_candidates_is_searchable ON candidates(is_searchable) WHERE is_searchable = TRUE;
CREATE INDEX idx_candidates_skills ON candidates USING GIN(skills);
CREATE INDEX idx_candidates_domains ON candidates USING GIN(domains);

-- -----------------------------------------------------------------------------
-- TABLE: employers
-- Profile for users with role = 'EMPLOYER'
-- -----------------------------------------------------------------------------

CREATE TABLE employers (
    id                      TEXT PRIMARY KEY,   -- cuid() in application layer
    user_id                 TEXT NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    verification_status     employer_verification_status NOT NULL DEFAULT 'PENDING',
    
    -- Company details
    company_name            TEXT NOT NULL,
    company_logo            TEXT,
    company_website         TEXT,
    company_size            TEXT,               -- 1-10, 11-50, 51-200, etc.
    industry                TEXT,
    headquarters            TEXT,
    
    -- Verification
    verification_docs       TEXT[],             -- URLs to uploaded docs in S3
    verified_at             TIMESTAMPTZ,
    verified_by             TEXT,               -- Admin user ID who verified
    
    -- Billing (Stripe integration)
    stripe_customer_id      TEXT,
    deposit_amount          DECIMAL,
    
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_employers_user_id ON employers(user_id);
CREATE INDEX idx_employers_verification_status ON employers(verification_status);
CREATE INDEX idx_employers_company_name ON employers(company_name);

-- =============================================================================
-- END OF SCHEMA
-- =============================================================================
