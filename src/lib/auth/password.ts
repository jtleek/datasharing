/**
 * Password Utilities
 * 
 * Uses bcrypt for hashing (per MVP recommendation in AUTHENTICATION_FLOWS.md)
 * Cost factor 12 provides good security/performance balance
 */

import bcrypt from 'bcrypt';

const SALT_ROUNDS = 12;

/**
 * Hash a plain-text password
 */
export async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, SALT_ROUNDS);
}

/**
 * Verify a password against a stored hash
 */
export async function verifyPassword(password: string, hash: string): Promise<boolean> {
  return bcrypt.compare(password, hash);
}
