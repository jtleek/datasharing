/**
 * POST /api/auth/verify-email
 * 
 * Verifies user's email address using token.
 * Stub implementation - validates token structure only.
 */

import { query, queryOne, generateId } from '@/lib/db';
import { verifyEmailSchema, hashToken, isExpired, EMAIL_VERIFICATION_DURATION_MS, generateToken } from '@/lib/auth';
import { getSession } from '@/lib/session';
import { success, validationError, errors, error } from '@/lib/api';

/**
 * POST - Verify email with token
 */
export async function POST(request: Request) {
  try {
    const body = await request.json();

    const parsed = verifyEmailSchema.safeParse(body);
    if (!parsed.success) {
      return validationError(parsed.error);
    }

    const { token } = parsed.data;
    const tokenHash = hashToken(token);

    // Find token
    const tokenRow = await queryOne<{
      id: string;
      user_id: string;
      expires_at: Date;
    }>(
      'SELECT id, user_id, expires_at FROM email_verification_tokens WHERE token_hash = $1',
      [tokenHash]
    );

    if (!tokenRow) {
      return errors.invalidToken();
    }

    if (isExpired(tokenRow.expires_at)) {
      await query('DELETE FROM email_verification_tokens WHERE id = $1', [tokenRow.id]);
      return error('TOKEN_EXPIRED', 'Verification token has expired', 400);
    }

    // Verify email and delete token
    await query('BEGIN');
    try {
      await query('UPDATE users SET email_verified = NOW() WHERE id = $1', [tokenRow.user_id]);
      await query('DELETE FROM email_verification_tokens WHERE user_id = $1', [tokenRow.user_id]);
      await query('COMMIT');
    } catch (err) {
      await query('ROLLBACK');
      throw err;
    }

    return success({ message: 'Email verified successfully' });
  } catch (err) {
    console.error('Verify email error:', err);
    return errors.internal();
  }
}

/**
 * GET - Resend verification email (requires auth)
 */
export async function GET() {
  try {
    const session = await getSession();
    if (!session) {
      return errors.unauthorized();
    }

    // Check if already verified
    const user = await queryOne<{ email_verified: Date | null; email: string }>(
      'SELECT email_verified, email FROM users WHERE id = $1',
      [session.user.id]
    );

    if (user?.email_verified) {
      return error('ALREADY_VERIFIED', 'Email is already verified', 400);
    }

    // Delete existing tokens
    await query('DELETE FROM email_verification_tokens WHERE user_id = $1', [session.user.id]);

    // Create new token
    const token = generateToken();
    const tokenHash = hashToken(token);
    const expiresAt = new Date(Date.now() + EMAIL_VERIFICATION_DURATION_MS);

    await query(
      'INSERT INTO email_verification_tokens (id, user_id, token_hash, expires_at) VALUES ($1, $2, $3, $4)',
      [generateId(), session.user.id, tokenHash, expiresAt]
    );

    // TODO: Send email with token
    if (process.env.NODE_ENV === 'development') {
      console.log(`[DEV] Verification token for ${user?.email}: ${token}`);
    }

    return success({ message: 'Verification email sent' });
  } catch (err) {
    console.error('Resend verification error:', err);
    return errors.internal();
  }
}
