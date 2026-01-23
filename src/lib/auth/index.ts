/**
 * Auth Module Exports
 */

export { hashPassword, verifyPassword } from './password';

export {
  generateToken,
  hashToken,
  isExpired,
  SESSION_DURATION_MS,
  EXTENDED_SESSION_DURATION_MS,
  EMAIL_VERIFICATION_DURATION_MS,
  PASSWORD_RESET_DURATION_MS,
} from './tokens';

export {
  emailSchema,
  passwordSchema,
  roleSchema,
  registerSchema,
  loginSchema,
  verifyEmailSchema,
  forgotPasswordSchema,
  resetPasswordSchema,
  type RegisterInput,
  type LoginInput,
  type VerifyEmailInput,
  type ForgotPasswordInput,
  type ResetPasswordInput,
} from './validation';
