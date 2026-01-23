/**
 * POST /api/auth/register
 * 
 * Creates a new user account with email/password.
 * Per AUTHENTICATION_FLOWS.md: Registration creates user + profile,
 * generates email verification token, and establishes session.
 */

import { NextRequest } from 'next/server';
import { query, queryOne, generateId } from '@/lib/db';
import { hashPassword, registerSchema, generateToken, hashToken, EMAIL_VERIFICATION_DURATION_MS } from '@/lib/auth';
import { createSession, setSessionCookie } from '@/lib/session';
import { success, error, validationError, errors } from '@/lib/api';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // Validate input
    const parsed = registerSchema.safeParse(body);
    if (!parsed.success) {
      return validationError(parsed.error);
    }

    const { email, password, role, firstName, lastName } = parsed.data;

    // Check if email exists
    const existing = await queryOne<{ id: string }>(
      'SELECT id FROM users WHERE email = $1',
      [email]
    );
    if (existing) {
      return errors.emailExists();
    }

    // Hash password
    const passwordHash = await hashPassword(password);

    // Generate IDs
    const userId = generateId();
    const profileId = generateId();

    // Generate email verification token
    const verifyToken = generateToken();
    const verifyTokenHash = hashToken(verifyToken);
    const verifyExpiresAt = new Date(Date.now() + EMAIL_VERIFICATION_DURATION_MS);

    // Create user, profile, and verification token in transaction
    await query('BEGIN');
    try {
      await query(
        `INSERT INTO users (id, email, password, role)
         VALUES ($1, $2, $3, $4)`,
        [userId, email, passwordHash, role]
      );

      await query(
        `INSERT INTO user_profiles (id, user_id, first_name, last_name)
         VALUES ($1, $2, $3, $4)`,
        [profileId, userId, firstName, lastName]
      );

      await query(
        `INSERT INTO email_verification_tokens (id, user_id, token_hash, expires_at)
         VALUES ($1, $2, $3, $4)`,
        [generateId(), userId, verifyTokenHash, verifyExpiresAt]
      );

      await query('COMMIT');
    } catch (err) {
      await query('ROLLBACK');
      throw err;
    }

    // Create session
    const userAgent = request.headers.get('user-agent') ?? undefined;
    const ipAddress = request.headers.get('x-forwarded-for')?.split(',')[0] ?? undefined;
    const sessionToken = await createSession(userId, { userAgent, ipAddress });

    // TODO: Send verification email with verifyToken
    if (process.env.NODE_ENV === 'development') {
      console.log(`[DEV] Verification token for ${email}: ${verifyToken}`);
    }

    // Build response
    const response = success(
      {
        user: { id: userId, email, role, emailVerified: false },
        message: 'Registration successful. Please verify your email.',
      },
      201
    );

    return setSessionCookie(response, sessionToken);
  } catch (err) {
    console.error('Register error:', err);
    return errors.internal();
  }
}
