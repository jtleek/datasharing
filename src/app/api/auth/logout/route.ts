/**
 * POST /api/auth/logout
 * 
 * Terminates the current session.
 * Deletes session from database and clears cookie.
 */

import { NextRequest } from 'next/server';
import { deleteSession, clearSessionCookie } from '@/lib/session';
import { success, errors } from '@/lib/api';

export async function POST(request: NextRequest) {
  try {
    const token = request.cookies.get('session_token')?.value;

    if (token) {
      await deleteSession(token);
    }

    const response = success({ message: 'Logged out successfully' });
    return clearSessionCookie(response);
  } catch (err) {
    console.error('Logout error:', err);
    return errors.internal();
  }
}
