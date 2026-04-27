import DOMPurify from 'dompurify';

// Configure DOMPurify for safe HTML sanitization
const DOMPURIFY_CONFIG = {
  ALLOWED_TAGS: [
    'b', 'i', 'em', 'strong', 'a', 'br', 'p', 'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'blockquote', 'code', 'pre', 'hr', 'span', 'div', 'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'img', 'figure', 'figcaption'
  ],
  ALLOWED_ATTR: ['href', 'title', 'alt', 'src', 'width', 'height', 'class'],
  KEEP_CONTENT: true,
  FORCE_BODY: false,
};

/**
 * Sanitize HTML content to prevent XSS attacks
 * Removes dangerous scripts, event handlers, and only allows safe HTML tags/attributes
 */
export function sanitizeHtml(html: string): string {
  if (!html || typeof html !== 'string') {
    return '';
  }

  // Use DOMPurify to clean the HTML
  const cleaned = DOMPurify.sanitize(html, DOMPURIFY_CONFIG);
  return cleaned;
}

/**
 * Sanitize plain text by escaping HTML entities
 * Converts dangerous characters to HTML entities to prevent XSS when displayed as text
 */
export function sanitizeText(text: string): string {
  if (!text || typeof text !== 'string') {
    return '';
  }

  // Create a temporary element to leverage browser's HTML encoding
  const div = typeof document !== 'undefined' ? document.createElement('div') : null;
  
  if (div) {
    div.textContent = text;
    return div.innerHTML;
  }

  // Fallback for server-side rendering - manual escaping
  return escapeHtml(text);
}

/**
 * Manual HTML entity escaping (for SSR environments without DOM)
 */
function escapeHtml(text: string): string {
  const map: Record<string, string> = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;',
  };
  return text.replace(/[&<>"']/g, (char) => map[char]);
}

/**
 * Validate and sanitize URLs to prevent javascript: protocol attacks
 * Returns empty string if URL is invalid or dangerous
 */
export function sanitizeUrl(url: string): string {
  if (!url || typeof url !== 'string') {
    return '';
  }

  const trimmed = url.trim();

  // Block javascript: protocol
  if (trimmed.toLowerCase().startsWith('javascript:')) {
    return '';
  }

  // Block data: protocol (can contain XSS)
  if (trimmed.toLowerCase().startsWith('data:')) {
    return '';
  }

  // Block vbscript: protocol
  if (trimmed.toLowerCase().startsWith('vbscript:')) {
    return '';
  }

  // Allow relative URLs and safe protocols (http, https, mailto, tel)
  if (trimmed.startsWith('/') || trimmed.startsWith('#')) {
    return trimmed;
  }

  try {
    const parsed = new URL(trimmed);
    if (parsed.protocol === 'http:' || parsed.protocol === 'https:' || 
        parsed.protocol === 'mailto:' || parsed.protocol === 'tel:') {
      return trimmed;
    }
  } catch {
    // Invalid URL - might be a relative path, return it
    return trimmed;
  }

  return '';
}

/**
 * Sanitize user input for use in DOM
 * Combines text sanitization with length limits
 */
export function sanitizeUserInput(input: string, maxLength = 5000): string {
  if (!input || typeof input !== 'string') {
    return '';
  }

  // Truncate to max length first
  const truncated = input.substring(0, maxLength);

  // Escape HTML entities
  return sanitizeText(truncated);
}

/**
 * Sanitize filename to prevent directory traversal attacks
 */
export function sanitizeFilename(filename: string): string {
  if (!filename || typeof filename !== 'string') {
    return '';
  }

  // Remove path separators and parent directory references
  return filename
    .replace(/\.\./g, '')
    .replace(/[/\\]/g, '')
    .replace(/[<>:"|?*]/g, '');
}

/**
 * Check if HTML content appears to contain script tags or event handlers
 * Useful for detecting suspicious content before further processing
 */
export function containsScriptContent(html: string): boolean {
  if (!html || typeof html !== 'string') {
    return false;
  }

  const suspiciousPatterns = [
    /<script[^>]*>/i,
    /on\w+\s*=/i, // Event handlers like onclick=, onload=, etc.
    /javascript:/i,
    /vbscript:/i,
    /<iframe[^>]*>/i,
    /<object[^>]*>/i,
    /<embed[^>]*>/i,
  ];

  return suspiciousPatterns.some((pattern) => pattern.test(html));
}
