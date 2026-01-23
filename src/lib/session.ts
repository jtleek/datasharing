/**
 * Session Management
 * 
 * Database-backed sessions with HttpOnly cookies.
 * Per MVP recommendation in AUTHENTICATION_FLOWS.md.
 */

import { cookies } from 'next/headers';
import { query, queryOne, generateId } from './db';
import {
  generateToken,
  hashToken,
  isExpired,
  SESSION_DURATION_MS,
  EXTENDED_SESSION_DURATION_MS,
} from './auth';

const SESSION_COOKIE = 'session_token';

export interface SessionUser {
  id: string;
  email: string;
  role: string;
  emailVerified: boolean;
}

export interface Session {
  id: string;
  user: SessionUser;
  expiresAt: Date;
}

/**
 * Create a new session for a user
 */
export async function createSession(
  userId: string,
  options?: {
    rememberMe?: boolean;
    userAgent?: string;
    ipAddress?: string;
  }
): Promise<string> {
  const token = generateToken();
  const tokenHash = hashToken(token);
  const duration = options?.rememberMe
    ? EXTENDED_SESSION_DURATION_MS
    : SESSION_DURATION_MS;
  const expiresAt = new Date(Date.now() + duration);

  await query(
    `INSERT INTO sessions (id, user_id, token_hash, expires_at, user_agent, ip_address)
     VALUES ($1, $2, $3, $4, $5, $6)`,
    [generateId(), userId, tokenHash, expiresAt, options?.userAgent, options?.ipAddress]
  );

  return token;
}

/**
 * Validate session token and return session data
 */
export async function validateSession(token: string): Promise<Session | null> {
  const tokenHash = hashToken(token);

  const row = await queryOne<{
    session_id: string;
    expires_at: Date;
    user_id: string;
    email: string;
    role: string;
    email_verified: Date | null;
  }>(
    `SELECT 
       s.id as session_id,
       s.expires_at,
       u.id as user_id,
       u.email,
       u.role,
       u.email_verified
     FROM sessions s
     JOIN users u ON s.user_id = u.id
     WHERE s.token_hash = $1`,
    [tokenHash]
  );

  if (!row) return null;

  if (isExpired(row.expires_at)) {
    // Clean up expired session
    await query('DELETE FROM sessions WHERE id = $1', [row.session_id]);
    return null;
  }

  return {
    id: row.session_id,
    user: {
      id: row.user_id,
      email: row.email,
      role: row.role,
      emailVerified: row.email_verified !== null,
    },
    expiresAt: row.expires_at,
  };
}

/**
 * Delete a session by token
 */
export async function deleteSession(token: string): Promise<void> {
  const tokenHash = hashToken(token);
  await query('DELETE FROM sessions WHERE token_hash = $1', [tokenHash]);
}

/**
 * Delete all sessions for a user
 */
export async function deleteAllUserSessions(userId: string): Promise<void> {
  await query('DELETE FROM sessions WHERE user_id = $1', [userId]);
}

/**
 * Get session from request cookies
 */
export async function getSession(): Promise<Session | null> {
  const cookieStore = await cookies();
  const token = cookieStore.get(SESSION_COOKIE)?.value;
  if (!token) return null;
  return validateSession(token);
}

/**
 * Set session cookie in response
 */
export function setSessionCookie(
  response: Response,
  token: string,
  rememberMe = false
): Response {
  const maxAge = rememberMe
    ? EXTENDED_SESSION_DURATION_MS / 1000
    : SESSION_DURATION_MS / 1000;

  const cookie = `${SESSION_COOKIE}=${token}; HttpOnly; Path=/; SameSite=Lax; Max-Age=${maxAge}${
    process.env.NODE_ENV === 'production' ? '; Secure' : ''
  }`;

  response.headers.append('Set-Cookie', cookie);
  return response;
}

/**
 * Clear session cookie in response
 */
export function clearSessionCookie(response: Response): Response {
  const cookie = `${SESSION_COOKIE}=; HttpOnly; Path=/; SameSite=Lax; Max-Age=0`;
  response.headers.append('Set-Cookie', cookie);
  return response;
}
