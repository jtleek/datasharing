# Authentication Flows Design Proposal

Based on the merged `users` + `user_profiles` schema for CloudPeople.

---

## Table of Contents

1. [Overview](#overview)
2. [Email/Password Authentication Flow](#emailpassword-authentication-flow)
3. [OAuth Authentication Flow (Optional)](#oauth-authentication-flow-optional)
4. [Session Management Options](#session-management-options)
5. [Trade-offs Summary](#trade-offs-summary)
6. [MVP Recommendation](#mvp-recommendation)

---

## Overview

This document proposes authentication flows that align with the existing schema:

| Schema Element | Auth Relevance |
|----------------|----------------|
| `users.email` | Primary login identifier |
| `users.password` | Hashed credential storage |
| `users.email_verified` | Verification state tracking |
| `users.role` | Post-auth access control |
| `users.last_login` | Session activity tracking |

**Guiding Principles:**
- No vendor lock-in (portable across providers)
- Standards-based protocols (OAuth 2.0, OpenID Connect)
- Schema-compatible (works with existing `users` table)
- Minimal infrastructure for MVP

---

## Email/Password Authentication Flow

### Registration Flow

```
User                    Application                  Database
  |                          |                           |
  |-- Submit email/password ->|                           |
  |                          |-- Validate format          |
  |                          |-- Check email uniqueness ->|
  |                          |<- Email available ---------|
  |                          |-- Hash password            |
  |                          |-- Insert user record ----->|
  |                          |<- User created ------------|
  |                          |-- Generate verify token    |
  |                          |-- Send verification email  |
  |<- "Check your email" ----|                           |
```

**Key Decisions:**

| Decision | Options | Trade-off |
|----------|---------|-----------|
| Password hashing | Argon2id, bcrypt, scrypt | Argon2id is newest/recommended; bcrypt has widest library support |
| Email verification | Required before login vs. Required for full access | Blocking login reduces friction but delays access |
| Rate limiting | IP-based, email-based, or both | IP-only can be bypassed; email-based may block legitimate retries |

### Login Flow

```
User                    Application                  Database
  |                          |                           |
  |-- Submit email/password ->|                           |
  |                          |-- Lookup user by email --->|
  |                          |<- User record (or null) ---|
  |                          |-- Verify password hash     |
  |                          |-- Check email_verified     |
  |                          |-- Update last_login ------>|
  |                          |-- Create session/token     |
  |<- Session token + role --|                           |
```

**Key Decisions:**

| Decision | Options | Trade-off |
|----------|---------|-----------|
| Failed login response | Generic "invalid credentials" vs. Specific errors | Generic prevents enumeration but frustrates users |
| Account lockout | Temporary lockout vs. CAPTCHA vs. Exponential delay | Lockout can enable DoS; CAPTCHA adds friction |
| Remember me | Extended session vs. Separate persistent token | Extended sessions increase window of compromise |

### Password Reset Flow

```
User                    Application                  Database
  |                          |                           |
  |-- Request reset (email) ->|                           |
  |                          |-- Lookup user by email --->|
  |                          |<- User exists (silent) ----|
  |                          |-- Generate reset token     |
  |                          |-- Store token (hashed) --->|
  |                          |-- Send reset email         |
  |<- "Check your email" ----|                           |
  |                          |                           |
  |-- Click reset link ------>|                           |
  |                          |-- Validate token --------->|
  |                          |<- Token valid --------------|
  |-- Submit new password --->|                           |
  |                          |-- Hash new password        |
  |                          |-- Update password -------->|
  |                          |-- Invalidate all sessions  |
  |<- Login with new password |                           |
```

**Key Decisions:**

| Decision | Options | Trade-off |
|----------|---------|-----------|
| Token expiry | 15 min, 1 hour, 24 hours | Shorter = more secure but less convenient |
| Token storage | Database table vs. Signed JWT | DB requires lookup; JWT can't be revoked early |
| Session invalidation | Invalidate all vs. Current only | All sessions is safer but may frustrate multi-device users |

---

## OAuth Authentication Flow (Optional)

OAuth provides "Login with Google/GitHub/etc." without storing external passwords.

### OAuth Registration/Login Flow

```
User                    Application                  OAuth Provider
  |                          |                           |
  |-- Click "Login with X" -->|                           |
  |                          |-- Generate state token     |
  |<- Redirect to provider --|                           |
  |-- Authorize at provider ----------------------->      |
  |<- Redirect with auth code -----------------------     |
  |                          |-- Exchange code for token ->|
  |                          |<- Access token + ID token --|
  |                          |-- Fetch user profile ------>|
  |                          |<- Email, name, avatar ------|
  |                          |                           |
  |                          |-- Lookup user by email --->| (Database)
  |                          |   (Link or Create)         |
  |<- Session established ---|                           |
```

### Account Linking Strategy

When an OAuth user's email matches an existing account:

| Strategy | Behavior | Trade-off |
|----------|----------|-----------|
| **Auto-link** | Automatically merge accounts | Convenient but risky if provider email isn't verified |
| **Prompt-link** | Ask user to confirm with password | Secure but adds friction |
| **Separate accounts** | Create distinct account | No risk but confusing for users |

**Recommendation:** Prompt-link for security—require password confirmation before linking OAuth to existing email/password account.

### Schema Consideration: OAuth Accounts Table

OAuth requires storing provider-specific identifiers. The current schema doesn't include this. A future addition would be:

| Table | Purpose |
|-------|---------|
| `oauth_accounts` | Links `user_id` to provider + provider_account_id |

**Structure (conceptual, not schema):**
- `user_id` → references `users.id`
- `provider` → "google", "github", etc.
- `provider_account_id` → unique ID from provider
- `access_token` (optional) → for API access
- `refresh_token` (optional) → for token refresh

### Provider Selection Trade-offs

| Provider | Pros | Cons |
|----------|------|------|
| **Google** | Ubiquitous, reliable | Requires Google Cloud Console setup |
| **GitHub** | Developer-friendly, good for tech users | Limited to developers |
| **Microsoft** | Enterprise/Azure integration | Complex configuration |
| **Generic OIDC** | Portable, no vendor lock-in | Requires configuration per provider |

**No Vendor Lock-in Approach:** Use OpenID Connect (OIDC) standard. Any compliant provider can be swapped without code changes—only configuration changes.

---

## Session Management Options

The schema comments mention three strategies. Here's the trade-off analysis:

### Option A: Database-Backed Sessions

| Aspect | Details |
|--------|---------|
| **Storage** | `sessions` table with token, user_id, expiry |
| **Verification** | Database lookup on each request |
| **Revocation** | Delete session row |
| **Scaling** | Requires shared database or sticky sessions |

**Trade-offs:**

| Pro | Con |
|-----|-----|
| Immediate revocation | Database hit per request |
| Full session control | Horizontal scaling complexity |
| Works with NextAuth.js | Additional table to maintain |
| Audit trail built-in | Session table can grow large |

### Option B: Stateless JWT

| Aspect | Details |
|--------|---------|
| **Storage** | Token contains claims, signed by secret |
| **Verification** | Signature check only (no DB) |
| **Revocation** | Not possible until expiry (without blocklist) |
| **Scaling** | Trivial—any server can verify |

**Trade-offs:**

| Pro | Con |
|-----|-----|
| No database lookup | Cannot revoke before expiry |
| Horizontally scalable | Token size in requests |
| Stateless/simple | Secret rotation requires re-auth |
| Works offline | Claims can become stale |

### Option C: Hybrid (JWT + Redis)

| Aspect | Details |
|--------|---------|
| **Storage** | JWT for auth, Redis for session state |
| **Verification** | Signature check + Redis lookup |
| **Revocation** | Delete from Redis |
| **Scaling** | Requires Redis cluster (ElastiCache per spec) |

**Trade-offs:**

| Pro | Con |
|-----|-----|
| Fast verification | Additional infrastructure (Redis) |
| Revocation possible | Two systems to maintain |
| Session data without DB | Redis adds latency vs. pure JWT |
| Spec mentions ElastiCache | Operational complexity |

---

## Trade-offs Summary

### Authentication Method Trade-offs

| Method | Security | UX | Implementation | Vendor Lock-in |
|--------|----------|----|--------------------|----------------|
| **Email/Password** | Depends on implementation | Familiar but friction | Medium | None |
| **OAuth only** | Delegated to provider | Low friction | Medium | Provider-dependent |
| **Email/Password + OAuth** | Best coverage | Best UX | Higher | Minimal with OIDC |

### Session Strategy Trade-offs

| Strategy | Performance | Revocation | Complexity | Spec Alignment |
|----------|-------------|------------|------------|----------------|
| **Database Sessions** | Slower (DB hit) | Immediate | Low | Works with NextAuth |
| **Stateless JWT** | Fastest | Delayed | Lowest | Minimal infra |
| **Hybrid (JWT+Redis)** | Fast | Immediate | Highest | Uses ElastiCache |

### Password Hashing Trade-offs

| Algorithm | Security | Performance | Library Support |
|-----------|----------|-------------|-----------------|
| **Argon2id** | Best (memory-hard) | Configurable | Growing |
| **bcrypt** | Good (battle-tested) | Fixed cost | Universal |
| **scrypt** | Good (memory-hard) | Configurable | Moderate |

---

## MVP Recommendation

For the initial MVP, the following configuration balances security, simplicity, and future flexibility:

### Recommended MVP Configuration

| Aspect | Recommendation | Rationale |
|--------|----------------|-----------|
| **Primary Auth** | Email/Password | Universal, no external dependencies |
| **OAuth** | Defer to post-MVP | Adds complexity; email/password sufficient for launch |
| **Password Hashing** | bcrypt | Widest library support, battle-tested |
| **Session Strategy** | Database-backed sessions | Simple, immediate revocation, works with NextAuth.js |
| **Email Verification** | Required for full access, not login | Balances security with onboarding friction |
| **Password Reset** | 1-hour token expiry | Standard balance of security/convenience |

### Why This Configuration?

1. **Minimal Dependencies:** No Redis, no OAuth provider setup—just the existing PostgreSQL database.

2. **No Vendor Lock-in:** Email/password is universal. bcrypt is standard across all languages. Database sessions work with any framework.

3. **Clear Upgrade Path:**
   - Add OAuth later by creating `oauth_accounts` table
   - Switch to hybrid sessions by adding Redis when scaling requires it
   - Migrate to Argon2id when library support matures

4. **Matches Schema:** The existing `users` table supports this configuration without modification.

### Post-MVP Enhancements (in priority order)

| Priority | Enhancement | Trigger |
|----------|-------------|---------|
| 1 | Add OAuth (Google) | User feedback requesting social login |
| 2 | Add Redis session cache | Database session queries become bottleneck |
| 3 | Add MFA/2FA | Enterprise customers require it |
| 4 | Add passwordless (magic links) | UX research indicates password friction |

---

## Summary

| Question | Answer |
|----------|--------|
| Email/Password for MVP? | Yes—universal, no dependencies |
| OAuth for MVP? | No—defer to reduce complexity |
| Session strategy? | Database-backed—simple, revocable |
| Password hashing? | bcrypt—battle-tested, universal support |
| Vendor lock-in risk? | None—all choices are standards-based |

This configuration provides a secure, maintainable authentication system that can evolve with product needs while avoiding premature optimization and external dependencies.
