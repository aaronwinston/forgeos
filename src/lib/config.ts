/**
 * Configuration validation for the ForgeOS frontend
 * Ensures required environment variables are set on app startup
 */

export function validateConfig(): void {
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;

  // API URL is optional - app can work in demo mode without it
  if (!apiBaseUrl) {
    if (typeof window !== 'undefined') {
      console.warn(
        'NEXT_PUBLIC_API_BASE_URL not set. Running in demo mode without API connectivity.'
      );
    }
    return;
  }

  // Validate API base URL format
  try {
    const url = new URL(apiBaseUrl);
    if (url.protocol !== 'http:' && url.protocol !== 'https:') {
      throw new Error('Invalid protocol');
    }
  } catch {
    console.error(
      `Invalid NEXT_PUBLIC_API_BASE_URL: "${apiBaseUrl}"\n` +
      'Must be a valid HTTP or HTTPS URL (e.g., http://localhost:8000)'
    );
    throw new Error('Invalid NEXT_PUBLIC_API_BASE_URL format');
  }
}
