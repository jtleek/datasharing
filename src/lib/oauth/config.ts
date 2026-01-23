/**
 * OAuth Provider Configuration
 * 
 * Scaffolding for Google and GitHub OAuth providers.
 * NOT ENABLED BY DEFAULT - requires environment variables.
 * 
 * Per AUTHENTICATION_FLOWS.md:
 * - OAuth deferred to post-MVP
 * - Uses OIDC standard for no vendor lock-in
 */

export interface OAuthProvider {
  id: string;
  name: string;
  authorizationUrl: string;
  tokenUrl: string;
  userInfoUrl: string;
  scopes: string[];
  clientId: string | undefined;
  clientSecret: string | undefined;
}

/**
 * Google OAuth configuration
 * Requires: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
 */
export const googleProvider: OAuthProvider = {
  id: 'google',
  name: 'Google',
  authorizationUrl: 'https://accounts.google.com/o/oauth2/v2/auth',
  tokenUrl: 'https://oauth2.googleapis.com/token',
  userInfoUrl: 'https://www.googleapis.com/oauth2/v2/userinfo',
  scopes: ['openid', 'email', 'profile'],
  clientId: process.env.GOOGLE_CLIENT_ID,
  clientSecret: process.env.GOOGLE_CLIENT_SECRET,
};

/**
 * GitHub OAuth configuration
 * Requires: GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET
 */
export const githubProvider: OAuthProvider = {
  id: 'github',
  name: 'GitHub',
  authorizationUrl: 'https://github.com/login/oauth/authorize',
  tokenUrl: 'https://github.com/login/oauth/access_token',
  userInfoUrl: 'https://api.github.com/user',
  scopes: ['read:user', 'user:email'],
  clientId: process.env.GITHUB_CLIENT_ID,
  clientSecret: process.env.GITHUB_CLIENT_SECRET,
};

/**
 * Get all configured providers
 */
export function getEnabledProviders(): OAuthProvider[] {
  const providers: OAuthProvider[] = [];

  if (googleProvider.clientId && googleProvider.clientSecret) {
    providers.push(googleProvider);
  }

  if (githubProvider.clientId && githubProvider.clientSecret) {
    providers.push(githubProvider);
  }

  return providers;
}

/**
 * Check if OAuth is enabled
 */
export function isOAuthEnabled(): boolean {
  return getEnabledProviders().length > 0;
}

/**
 * Get provider by ID
 */
export function getProvider(id: string): OAuthProvider | null {
  const providers = [googleProvider, githubProvider];
  return providers.find((p) => p.id === id && p.clientId && p.clientSecret) ?? null;
}
