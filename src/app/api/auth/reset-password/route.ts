/**
 * POST /api/auth/reset-password
 * 
 * Completes password reset with token.
 * Per AUTHENTICATION_FLOWS.md: 1-hour expiry, invalidates all sessions.
 */

import { query, queryOne } from '@/lib/db';
import { resetPasswordSchema, hashToken, hashPassword, isExpired } from '@/lib/auth';
import { deleteAllUserSessions, clearSessionCookie } from '@/lib/session';
import { success, validationError, errors, error } from '@/lib/api';

export async function POST(request: Request) {
  try {
    const body = await request.json();

    const parsed = resetPasswordSchema.safeParse(body);
    if (!parsed.success) {
      return validationError(parsed.error);
    }

    const { token, password } = parsed.data;
    const tokenHash = hashToken(token);

    // Find token
    const tokenRow = await queryOne<{
      id: string;
      user_id: string;
      expires_at: Date;
      used_at: Date | null;
    }>(
      'SELECT id, user_id, expires_at, used_at FROM password_reset_tokens WHERE token_hash = $1',
      [tokenHash]
    );

    if (!tokenRow) {
      return errors.invalidToken();
    }

    if (tokenRow.used_at) {
      return errors.invalidToken();
    }

    if (isExpired(tokenRow.expires_at)) {
      await query('DELETE FROM password_reset_tokens WHERE id = $1', [tokenRow.id]);
      return error('TOKEN_EXPIRED', 'Reset token has expired', 400);
    }

    // Hash new password
    const passwordHash = await hashPassword(password);

    // Update password and mark token used
    await query('BEGIN');
    try {
      await query('UPDATE users SET password = $1, updated_at = NOW() WHERE id = $2', [
        passwordHash,
        tokenRow.user_id,
      ]);
      await query('UPDATE password_reset_tokens SET used_at = NOW() WHERE id = $1', [tokenRow.id]);
      await query('COMMIT');
    } catch (err) {
      await query('ROLLBACK');
      throw err;
    }

    // Invalidate all sessions
    await deleteAllUserSessions(tokenRow.user_id);

    const response = success({
      message: 'Password reset successful. Please log in with your new password.',
    });

    return clearSessionCookie(response);
  } catch (err) {
    console.error('Reset password error:', err);
    return errors.internal();
  }
}
