/**
 * POST /api/auth/login
 * 
 * Authenticates user with email/password.
 * Per AUTHENTICATION_FLOWS.md: Generic error to prevent enumeration,
 * updates last_login, creates session with HttpOnly cookie.
 */

import { NextRequest } from 'next/server';
import { query, queryOne } from '@/lib/db';
import { verifyPassword, loginSchema } from '@/lib/auth';
import { createSession, setSessionCookie } from '@/lib/session';
import { success, validationError, errors } from '@/lib/api';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // Validate input
    const parsed = loginSchema.safeParse(body);
    if (!parsed.success) {
      return validationError(parsed.error);
    }

    const { email, password, rememberMe } = parsed.data;

    // Find user
    const user = await queryOne<{
      id: string;
      email: string;
      password: string;
      role: string;
      email_verified: Date | null;
    }>(
      'SELECT id, email, password, role, email_verified FROM users WHERE email = $1',
      [email]
    );

    // Generic error to prevent email enumeration
    if (!user) {
      return errors.invalidCredentials();
    }

    // Verify password
    const valid = await verifyPassword(password, user.password);
    if (!valid) {
      return errors.invalidCredentials();
    }

    // Update last_login
    await query('UPDATE users SET last_login = NOW() WHERE id = $1', [user.id]);

    // Create session
    const userAgent = request.headers.get('user-agent') ?? undefined;
    const ipAddress = request.headers.get('x-forwarded-for')?.split(',')[0] ?? undefined;
    const sessionToken = await createSession(user.id, {
      rememberMe,
      userAgent,
      ipAddress,
    });

    // Build response
    const response = success({
      user: {
        id: user.id,
        email: user.email,
        role: user.role,
        emailVerified: user.email_verified !== null,
      },
    });

    return setSessionCookie(response, sessionToken, rememberMe);
  } catch (err) {
    console.error('Login error:', err);
    return errors.internal();
  }
}
