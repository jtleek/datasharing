# Minimal PostgreSQL Schema Proposal
## Users, Authentication, User Profiles (Identity Only)

Based on **CP Build 1** specification for CloudPeople.

---

## Schema Overview

| Table | Purpose | Key Fields | Relationships |
|-------|---------|------------|---------------|
| `users` | Core authentication account | `id`, `email`, `password`, `role` | 1:1 → `user_profiles` |
| `user_profiles` | Identity information | `user_id`, `first_name`, `last_name`, `avatar_url` | 1:1 → `users` |

---

## Enum

| Enum | Values | Purpose |
|------|--------|---------|
| `user_role` | `CANDIDATE`, `EMPLOYER`, `ADMIN` | Role-based access control |

---

## Table Details & Rationale

### 1. `users`

**Purpose:** Core identity and authentication record.

| Column | Type | Rationale |
|--------|------|-----------|
| `id` | TEXT | Spec uses Prisma's `@default(cuid())` |
| `email` | TEXT UNIQUE | Primary login identifier |
| `email_verified` | TIMESTAMPTZ | Tracks email verification (required per spec) |
| `password` | TEXT | Hashed password; algorithm decided at app layer |
| `role` | user_role | Determines profile type + route access |
| `last_login` | TIMESTAMPTZ | Session tracking, spec explicitly includes |

**Why a separate `users` table?**
- Spec shows `User` as the core authentication entity
- Enables role-based middleware on all routes
- Single source of truth for credentials

---

### 2. `user_profiles`

**Purpose:** Minimal identity information for display purposes.

| Column | Type | Rationale |
|--------|------|-----------|
| `user_id` | TEXT UNIQUE | 1:1 relationship with users |
| `first_name` | TEXT | Common identity field from spec's Candidate model |
| `last_name` | TEXT | Common identity field from spec's Candidate model |
| `display_name` | TEXT | Optional public-facing name |
| `avatar_url` | TEXT | Profile image reference (S3 per spec) |

**Why minimal?**
- Contains only identity/display data
- Marketplace-specific fields (skills, salary, verification) belong in domain-specific tables added later

---

## Authentication Strategy

This schema **does not prescribe** a specific authentication strategy. The `users` table supports multiple approaches:

| Option | Description | Storage |
|--------|-------------|---------|
| **A. Server-side Sessions** | Database-backed session tokens | Requires `sessions` table |
| **B. JWT Tokens** | Stateless, self-contained tokens | No table needed |
| **C. Hybrid** | JWT + Redis session cache | Uses ElastiCache per spec |

See `users_auth_profiles.sql` for detailed pros/cons of each option.

**Recommendation:** Defer strategy decision until authentication implementation phase.

---

## What's Excluded (and why)

| Excluded | Reason |
|----------|--------|
| `candidates` table | Marketplace-specific; add during Phase 2+ |
| `employers` table | Marketplace-specific; add during Phase 2+ |
| Skills, domains, seniority | Marketplace concepts |
| Salary, auction floor | Auction-specific |
| Visibility flags | Search/discovery feature |
| Verification status | Employer workflow feature |
| Concrete session table | Auth strategy not yet chosen |

---

## Next Steps

1. **Choose auth strategy** during implementation phase
2. **Add marketplace tables** (`candidates`, `employers`) when building Phase 2
3. **Add audit logging** when implementing compliance features
