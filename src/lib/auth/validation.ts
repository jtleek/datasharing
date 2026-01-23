/**
 * Input Validation Schemas
 * 
 * Uses Zod for type-safe validation of auth inputs.
 */

import { z } from 'zod';

/**
 * Email validation with normalization
 */
export const emailSchema = z
  .string()
  .email('Invalid email address')
  .transform((email) => email.toLowerCase().trim());

/**
 * Password requirements:
 * - Minimum 8 characters
 * - At least one uppercase letter
 * - At least one lowercase letter
 * - At least one digit
 */
export const passwordSchema = z
  .string()
  .min(8, 'Password must be at least 8 characters')
  .regex(/[A-Z]/, 'Password must contain an uppercase letter')
  .regex(/[a-z]/, 'Password must contain a lowercase letter')
  .regex(/\d/, 'Password must contain a digit');

/**
 * User role for registration (ADMIN cannot self-register)
 */
export const roleSchema = z.enum(['CANDIDATE', 'EMPLOYER']);

/**
 * Registration input
 */
export const registerSchema = z.object({
  email: emailSchema,
  password: passwordSchema,
  role: roleSchema,
  firstName: z.string().min(1, 'First name is required').max(100),
  lastName: z.string().min(1, 'Last name is required').max(100),
});
export type RegisterInput = z.infer<typeof registerSchema>;

/**
 * Login input
 */
export const loginSchema = z.object({
  email: emailSchema,
  password: z.string().min(1, 'Password is required'),
  rememberMe: z.boolean().optional().default(false),
});
export type LoginInput = z.infer<typeof loginSchema>;

/**
 * Email verification input
 */
export const verifyEmailSchema = z.object({
  token: z.string().min(1, 'Token is required'),
});
export type VerifyEmailInput = z.infer<typeof verifyEmailSchema>;

/**
 * Forgot password input
 */
export const forgotPasswordSchema = z.object({
  email: emailSchema,
});
export type ForgotPasswordInput = z.infer<typeof forgotPasswordSchema>;

/**
 * Reset password input
 */
export const resetPasswordSchema = z.object({
  token: z.string().min(1, 'Token is required'),
  password: passwordSchema,
});
export type ResetPasswordInput = z.infer<typeof resetPasswordSchema>;
