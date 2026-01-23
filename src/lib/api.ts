/**
 * API Response Utilities
 * 
 * Standardized response format for all API endpoints.
 */

import { NextResponse } from 'next/server';
import { ZodError } from 'zod';

export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: Record<string, string[]>;
  };
}

/**
 * Success response
 */
export function success<T>(data: T, status = 200): NextResponse<ApiResponse<T>> {
  return NextResponse.json({ success: true, data }, { status });
}

/**
 * Error response
 */
export function error(
  code: string,
  message: string,
  status = 400,
  details?: Record<string, string[]>
): NextResponse<ApiResponse<never>> {
  return NextResponse.json(
    { success: false, error: { code, message, details } },
    { status }
  );
}

/**
 * Validation error from Zod
 */
export function validationError(err: ZodError): NextResponse<ApiResponse<never>> {
  const details: Record<string, string[]> = {};
  for (const issue of err.issues) {
    const path = issue.path.join('.') || 'root';
    if (!details[path]) details[path] = [];
    details[path].push(issue.message);
  }
  return error('VALIDATION_ERROR', 'Invalid request data', 400, details);
}

/**
 * Common error responses
 */
export const errors = {
  unauthorized: () => error('UNAUTHORIZED', 'Authentication required', 401),
  invalidCredentials: () => error('INVALID_CREDENTIALS', 'Invalid email or password', 401),
  emailExists: () => error('EMAIL_EXISTS', 'An account with this email already exists', 409),
  invalidToken: () => error('INVALID_TOKEN', 'Invalid or expired token', 400),
  internal: () => error('INTERNAL_ERROR', 'An unexpected error occurred', 500),
};
