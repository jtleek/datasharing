# Minimal PostgreSQL Schema Proposal
## Users, Authentication, User Profiles

Based on **CP Build 1** specification for CloudPeople.

---

## Schema Overview

| Table | Purpose | Key Fields | Relationships |
|-------|---------|------------|---------------|
| `users` | Core authentication account | `id`, `email`, `password`, `role` | 1:1 → `candidates` or `employers` |
| `sessions` | Token-based session management | `user_id`, `token`, `expires_at` | N:1 → `users` |
| `candidates` | Profile for CANDIDATE users | `user_id`, `status`, profile fields, `min_salary` | 1:1 → `users` |
| `employers` | Profile for EMPLOYER users | `user_id`, `verification_status`, company fields | 1:1 → `users` |

---

## Enums

| Enum | Values | Purpose |
|------|--------|---------|
| `user_role` | `CANDIDATE`, `EMPLOYER`, `ADMIN` | Role-based access control |
| `candidate_status` | `DRAFT`, `ACTIVE`, `PAUSED`, `CLOSED` | Profile/auction availability state |
| `employer_verification_status` | `PENDING`, `VERIFIED`, `REJECTED`, `SUSPENDED` | Trust verification workflow |

---

## Table Details & Rationale

### 1. `users`

**Purpose:** Core identity and authentication record.

| Column | Type | Rationale |
|--------|------|-----------|
| `id` | TEXT (cuid) | Spec uses Prisma's `@default(cuid())` |
| `email` | TEXT UNIQUE | Primary login identifier |
| `email_verified` | TIMESTAMPTZ | Tracks email verification (required per spec) |
| `password` | TEXT | Bcrypt hash (spec: "Bcrypt password hashing") |
| `role` | user_role | Determines profile type + route access |
| `last_login` | TIMESTAMPTZ | Session tracking, spec explicitly includes |

**Why separate from profiles?**
- Spec shows `User` as distinct from `Candidate`/`Employer`
- Enables role-based middleware on all routes
- Supports ADMIN users who have neither profile type

---

### 2. `sessions`

**Purpose:** Server-side session storage for NextAuth.js.

| Column | Type | Rationale |
|--------|------|-----------|
| `token` | TEXT UNIQUE | JWT or session token |
| `expires_at` | TIMESTAMPTZ | Token expiration (spec: "JWT tokens with refresh") |

**Why included?**
- Spec mentions "Session[]" relation in User model
- Redis is for caching; Postgres is source of truth
- Required for "Sessions storage" per infrastructure section

---

### 3. `candidates`

**Purpose:** Complete profile for job-seeking users.

| Column Group | Rationale |
|--------------|-----------|
| Profile basics | `first_name`, `last_name`, `headline`, `bio` - Core identity display |
| Professional | `skills[]`, `domains[]`, `seniority` - Search/matching criteria |
| Location/work | `remote_preference`, `timezone`, `work_authorization[]` - Employer filtering |
| Salary/availability | `min_salary` is **auction floor** - critical for auction system |
| Visibility | `is_searchable`, `is_public` - Privacy controls per spec |
| External links | Portfolio, GitHub, LinkedIn, Resume URLs - S3 storage references |

**Why `min_salary` is NOT NULL?**
- Serves as auction floor price (spec: "minSalary Decimal // Auction floor")
- Auctions cannot function without a floor

---

### 4. `employers`

**Purpose:** Company profile for hiring organizations.

| Column Group | Rationale |
|--------------|-----------|
| Company details | `company_name`, `company_size`, `industry` - Display + matching |
| Verification | `verification_status`, `verification_docs[]`, `verified_by` - Trust workflow |
| Billing | `stripe_customer_id`, `deposit_amount` - Payment integration |

**Why verification fields included?**
- Spec: "Employer verification required for bidding"
- Spec: "Deposit system for auction participation"
- Admin workflow: `GET /api/admin/verification-queue`

---

## Indexes Rationale

| Index | Purpose |
|-------|---------|
| `idx_users_email` | Login lookups |
| `idx_sessions_token` | Token validation on each request |
| `idx_sessions_expires_at` | Session cleanup queries |
| `idx_candidates_is_searchable` | Partial index for employer search |
| `idx_candidates_skills` (GIN) | Array contains queries for skill matching |
| `idx_employers_verification_status` | Admin verification queue filtering |

---

## What's Excluded (and why)

Per constraints "No assumptions beyond CP Build 1", the following spec tables are **not** included as they belong to other domains:

| Excluded | Domain | Build Phase |
|----------|--------|-------------|
| `EmployerSeat` | Multi-user employer accounts | Phase 2+ |
| `JobOpportunity` | Job listings | Phase 2 (Search & Requests) |
| `Request`, `Conversation`, `Message` | Communication | Phase 2 |
| `Auction`, `Bid`, `AuctionSlot` | Auction system | Phase 3-4 |
| `Outcome`, `Payment` | Post-auction | Phase 5 |
| `AuditLog`, `ModerationFlag` | Admin/compliance | Phase 5 |
| `Match`, `SavedSearch` | Discovery features | Phase 2+ |

---

## Data Type Decisions

| Decision | Rationale |
|----------|-----------|
| `TEXT` for IDs | Prisma cuid() generates strings |
| `TEXT[]` for arrays | Native Postgres arrays, matches Prisma `String[]` |
| `DECIMAL` for money | Spec uses `Decimal` for salary/amounts |
| `TIMESTAMPTZ` | Timezone-aware timestamps for global platform |
| Snake_case columns | Postgres convention; Prisma maps to camelCase |

---

## Next Steps (when ready)

1. **Migration file** - Add Prisma migration after schema approval
2. **Application constraints** - cuid generation, bcrypt hashing in app layer
3. **Audit logging** - Add `AuditLog` table when implementing Phase 5
