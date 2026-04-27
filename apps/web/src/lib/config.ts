/**
 * Configuration validation for the ForgeOS frontend
 * Ensures required environment variables are set on app startup
 */

export function validateConfig(): void {
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;

  if (!apiBaseUrl) {
    console.error(
      'Missing required environment variable: NEXT_PUBLIC_API_BASE_URL\n' +
      'Please set this in your .env.local or environment before running the app.\n' +
      'Example: NEXT_PUBLIC_API_BASE_URL=http://localhost:8000'
    );
    throw new Error('NEXT_PUBLIC_API_BASE_URL is required');
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
