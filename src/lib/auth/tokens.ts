/**
 * Token Utilities
 * 
 * Secure token generation for sessions and verification flows.
 * Tokens are hashed before storage to prevent theft if DB is compromised.
 */

import { createHash, randomBytes } from 'crypto';

/**
 * Generate a cryptographically secure random token
 */
export function generateToken(bytes: number = 32): string {
  return randomBytes(bytes).toString('hex');
}

/**
 * Hash a token for secure storage
 */
export function hashToken(token: string): string {
  return createHash('sha256').update(token).digest('hex');
}

/**
 * Check if a timestamp has expired
 */
export function isExpired(expiresAt: Date): boolean {
  return new Date() > expiresAt;
}

/**
 * Session token config
 * 7 days for regular, 30 days for "remember me"
 */
export const SESSION_DURATION_MS = 7 * 24 * 60 * 60 * 1000;
export const EXTENDED_SESSION_DURATION_MS = 30 * 24 * 60 * 60 * 1000;

/**
 * Email verification token: 24 hours
 */
export const EMAIL_VERIFICATION_DURATION_MS = 24 * 60 * 60 * 1000;

/**
 * Password reset token: 1 hour (per MVP recommendation)
 */
export const PASSWORD_RESET_DURATION_MS = 60 * 60 * 1000;
