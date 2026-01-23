/**
 * GET /api/auth/me
 * 
 * Returns the current authenticated user.
 * Requires valid session.
 */

import { queryOne } from '@/lib/db';
import { getSession } from '@/lib/session';
import { success, errors } from '@/lib/api';

export async function GET() {
  try {
    const session = await getSession();

    if (!session) {
      return errors.unauthorized();
    }

    // Get user with profile
    const user = await queryOne<{
      id: string;
      email: string;
      role: string;
      email_verified: Date | null;
      created_at: Date;
      last_login: Date | null;
      first_name: string;
      last_name: string;
      display_name: string | null;
      avatar_url: string | null;
    }>(
      `SELECT 
         u.id, u.email, u.role, u.email_verified, u.created_at, u.last_login,
         p.first_name, p.last_name, p.display_name, p.avatar_url
       FROM users u
       LEFT JOIN user_profiles p ON p.user_id = u.id
       WHERE u.id = $1`,
      [session.user.id]
    );

    if (!user) {
      return errors.unauthorized();
    }

    return success({
      user: {
        id: user.id,
        email: user.email,
        role: user.role,
        emailVerified: user.email_verified !== null,
        createdAt: user.created_at,
        lastLogin: user.last_login,
        profile: {
          firstName: user.first_name,
          lastName: user.last_name,
          displayName: user.display_name,
          avatarUrl: user.avatar_url,
        },
      },
      session: {
        expiresAt: session.expiresAt,
      },
    });
  } catch (err) {
    console.error('Get me error:', err);
    return errors.internal();
  }
}
