/**
 * Safe Rendering Utilities
 * 
 * These utilities ensure that untrusted API data is rendered safely
 * without allowing script injection or XSS attacks.
 */

/**
 * Safely render text content by escaping HTML entities
 * This prevents XSS attacks when rendering untrusted content
 */
export function safeText(text: string | null | undefined): string {
  if (text === null || text === undefined) {
    return '';
  }

  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

/**
 * Render potentially unsafe content as plain text
 * This ensures no HTML or scripts are executed
 */
export function renderAsText(content: string | null | undefined): string {
  return safeText(content);
}

/**
 * Truncate text to a maximum length with ellipsis
 * Useful for displaying long content previews
 */
export function truncateText(
  text: string | null | undefined,
  maxLength: number = 100
): string {
  const safe = safeText(text);
  if (safe.length <= maxLength) {
    return safe;
  }
  return safe.substring(0, maxLength) + '...';
}

/**
 * Format a timestamp safely
 * Returns a safe date string representation
 */
export function safeDate(timestamp: string | Date | null | undefined): string {
  if (!timestamp) {
    return 'N/A';
  }

  try {
    const date = typeof timestamp === 'string' ? new Date(timestamp) : timestamp;
    return date.toLocaleString();
  } catch {
    return 'Invalid date';
  }
}

/**
 * Render a JSON object safely as a formatted string
 * Useful for debugging or displaying structured data
 */
export function safeJson(data: any, indent: number = 2): string {
  try {
    const jsonString = JSON.stringify(data, null, indent);
    return safeText(jsonString);
  } catch {
    return '[Invalid JSON]';
  }
}

/**
 * Check if content is likely to be malicious
 * Returns true if content contains suspicious patterns
 */
export function isSuspiciousContent(content: string): boolean {
  const suspiciousPatterns = [
    /<script/i,
    /javascript:/i,
    /on\w+\s*=/i, // Event handlers like onclick=
    /data:text\/html/i,
    /vbscript:/i,
    /fromCharCode/i,
    /eval\(/i,
  ];

  return suspiciousPatterns.some(pattern => pattern.test(content));
}

/**
 * Render content with a warning if it appears suspicious
 */
export function renderWithWarning(content: string | null | undefined): {
  text: string;
  isSuspicious: boolean;
} {
  const safe = safeText(content);
  return {
    text: safe,
    isSuspicious: isSuspiciousContent(content || ''),
  };
}

/**
 * Clean HTML content by removing dangerous elements
 * Note: This is a basic implementation. For production,
 * consider using a library like DOMPurify.
 */
export function sanitizeHtml(html: string): string {
  // Basic sanitization - remove script tags and event handlers
  const dangerousPatterns = [
    /<script\b[^>]*>([\s\S]*?)<\/script>/gi,
    /<iframe\b[^>]*>([\s\S]*?)<\/iframe>/gi,
    /<object\b[^>]*>([\s\S]*?)<\/object>/gi,
    /<embed\b[^>]*>/gi,
    /on\w+\s*=\s*["'][^"']*["']/gi,
    /javascript:[^"']*/gi,
  ];

  let cleaned = html;
  dangerousPatterns.forEach(pattern => {
    cleaned = cleaned.replace(pattern, '');
  });

  return cleaned;
}

/**
 * Render markdown-like content safely
 * Convert basic markdown syntax to safe HTML
 */
export function safeMarkdown(text: string | null | undefined): string {
  if (!text) {
    return '';
  }

  const safe = safeText(text);

  // Basic markdown conversions (safe ones only)
  let html = safe
    // Bold
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    // Italic
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    // Code
    .replace(/`(.*?)`/g, '<code>$1</code>')
    // Line breaks
    .replace(/\n/g, '<br>');

  return html;
}

/**
 * Mask sensitive information for display
 * Useful for showing partial credentials or tokens
 */
export function maskSensitive(
  value: string | null | undefined,
  visibleChars: number = 4,
  maskChar: string = '*'
): string {
  if (!value) {
    return '';
  }

  if (value.length <= visibleChars * 2) {
    return maskChar.repeat(value.length);
  }

  const start = value.substring(0, visibleChars);
  const end = value.substring(value.length - visibleChars);
  const middle = maskChar.repeat(value.length - visibleChars * 2);

  return `${start}${middle}${end}`;
}

/**
 * Render email addresses safely
 */
export function safeEmail(email: string | null | undefined): string {
  if (!email) {
    return 'N/A';
  }

  const safe = safeText(email);
  // Basic email validation
  if (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(safe)) {
    return safe;
  }
  return 'Invalid email';
}

/**
 * Render URLs safely
 */
export function safeUrl(url: string | null | undefined): string {
  if (!url) {
    return 'N/A';
  }

  const safe = safeText(url);
  // Basic URL validation
  try {
    new URL(safe);
    return safe;
  } catch {
    return 'Invalid URL';
  }
}

/**
 * Render API error messages safely
 * Removes stack traces and sensitive information
 */
export function safeErrorMessage(error: any): string {
  if (typeof error === 'string') {
    return safeText(error);
  }

  if (error?.message) {
    return safeText(error.message);
  }

  if (error?.detail) {
    return safeText(error.detail);
  }

  return 'An error occurred';
}