/**
 * POST /api/auth/forgot-password
 * 
 * Initiates password reset by sending token to email.
 * Always returns success to prevent email enumeration.
 */

import { query, queryOne, generateId } from '@/lib/db';
import { forgotPasswordSchema, generateToken, hashToken, PASSWORD_RESET_DURATION_MS } from '@/lib/auth';
import { success, validationError, errors } from '@/lib/api';

export async function POST(request: Request) {
  try {
    const body = await request.json();

    const parsed = forgotPasswordSchema.safeParse(body);
    if (!parsed.success) {
      return validationError(parsed.error);
    }

    const { email } = parsed.data;

    // Find user (don't reveal if exists)
    const user = await queryOne<{ id: string; email: string }>(
      'SELECT id, email FROM users WHERE email = $1',
      [email]
    );

    if (user) {
      // Delete existing tokens
      await query('DELETE FROM password_reset_tokens WHERE user_id = $1', [user.id]);

      // Create new token
      const token = generateToken();
      const tokenHash = hashToken(token);
      const expiresAt = new Date(Date.now() + PASSWORD_RESET_DURATION_MS);

      await query(
        'INSERT INTO password_reset_tokens (id, user_id, token_hash, expires_at) VALUES ($1, $2, $3, $4)',
        [generateId(), user.id, tokenHash, expiresAt]
      );

      // TODO: Send email with token
      if (process.env.NODE_ENV === 'development') {
        console.log(`[DEV] Password reset token for ${email}: ${token}`);
      }
    }

    // Always return success to prevent enumeration
    return success({
      message: 'If an account exists with this email, a reset link has been sent.',
    });
  } catch (err) {
    console.error('Forgot password error:', err);
    return errors.internal();
  }
}
