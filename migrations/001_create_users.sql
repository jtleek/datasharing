-- Migration: 001_create_users
-- Description: Create users table for authentication
-- Based on: schema/AUTHENTICATION_FLOWS.md and schema/users_auth_profiles.sql

-- Create user_role enum
CREATE TYPE user_role AS ENUM ('CANDIDATE', 'EMPLOYER', 'ADMIN');

-- Create users table
CREATE TABLE users (
    id              TEXT PRIMARY KEY,
    email           TEXT NOT NULL UNIQUE,
    email_verified  TIMESTAMPTZ,
    password        TEXT NOT NULL,
    role            user_role NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login      TIMESTAMPTZ
);

-- Indexes for common queries
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
