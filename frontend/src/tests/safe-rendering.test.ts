import {
  safeText,
  renderAsText,
  truncateText,
  safeDate,
  safeJson,
  isSuspiciousContent,
  renderWithWarning,
  sanitizeHtml,
  safeMarkdown,
  maskSensitive,
  safeEmail,
  safeUrl,
  safeErrorMessage
} from '@/lib/safe-rendering';

describe('Safe Rendering Utilities', () => {
  describe('safeText', () => {
    it('should escape HTML entities', () => {
      const input = '<script>alert("xss")</script>';
      const result = safeText(input);
      expect(result).not.toContain('<script>');
      expect(result).toContain('&lt;script&gt;');
    });

    it('should handle null and undefined', () => {
      expect(safeText(null)).toBe('');
      expect(safeText(undefined)).toBe('');
    });

    it('should handle normal text', () => {
      const input = 'Hello, World!';
      const result = safeText(input);
      expect(result).toBe('Hello, World!');
    });

    it('should escape various HTML entities', () => {
      const input = '<div>&"\'</div>';
      const result = safeText(input);
      expect(result).toContain('&lt;div&gt;');
      expect(result).toContain('&amp;');
      expect(result).toContain('&quot;');
    });
  });

  describe('renderAsText', () => {
    it('should render content as plain text', () => {
      const input = '<b>Bold</b> text';
      const result = renderAsText(input);
      expect(result).toContain('&lt;b&gt;');
    });

    it('should handle null and undefined', () => {
      expect(renderAsText(null)).toBe('');
      expect(renderAsText(undefined)).toBe('');
    });
  });

  describe('truncateText', () => {
    it('should truncate text longer than max length', () => {
      const input = 'This is a very long text that should be truncated';
      const result = truncateText(input, 20);
      expect(result.length).toBeLessThanOrEqual(23); // 20 + '...'
      expect(result).toContain('...');
    });

    it('should not truncate text shorter than max length', () => {
      const input = 'Short text';
      const result = truncateText(input, 20);
      expect(result).toBe('Short text');
      expect(result).not.toContain('...');
    });

    it('should handle null and undefined', () => {
      expect(truncateText(null, 20)).toBe('');
      expect(truncateText(undefined, 20)).toBe('');
    });

    it('should escape HTML before truncating', () => {
      const input = '<script>alert("xss")</script>This is text';
      const result = truncateText(input, 20);
      expect(result).not.toContain('<script>');
    });
  });

  describe('safeDate', () => {
    it('should format valid dates', () => {
      const input = '2024-01-15T10:30:00Z';
      const result = safeDate(input);
      expect(result).not.toBe('Invalid date');
      expect(result).not.toBe('N/A');
    });

    it('should handle Date objects', () => {
      const input = new Date('2024-01-15T10:30:00Z');
      const result = safeDate(input);
      expect(result).not.toBe('Invalid date');
    });

    it('should handle null and undefined', () => {
      expect(safeDate(null)).toBe('N/A');
      expect(safeDate(undefined)).toBe('N/A');
    });

    it('should handle invalid dates', () => {
      const input = 'invalid-date';
      const result = safeDate(input);
      expect(result).toBe('Invalid date');
    });
  });

  describe('safeJson', () => {
    it('should format valid JSON', () => {
      const input = { name: 'test', value: 123 };
      const result = safeJson(input);
      expect(result).toContain('name');
      expect(result).toContain('test');
    });

    it('should handle invalid JSON', () => {
      const input = { circular: null };
      input.circular = input; // Create circular reference
      const result = safeJson(input);
      expect(result).toBe('[Invalid JSON]');
    });

    it('should escape HTML in JSON', () => {
      const input = { html: '<script>alert("xss")</script>' };
      const result = safeJson(input);
      expect(result).not.toContain('<script>');
    });
  });

  describe('isSuspiciousContent', () => {
    it('should detect script tags', () => {
      expect(isSuspiciousContent('<script>alert("xss")</script>')).toBe(true);
    });

    it('should detect javascript: protocol', () => {
      expect(isSuspiciousContent('javascript:alert("xss")')).toBe(true);
    });

    it('should detect event handlers', () => {
      expect(isSuspiciousContent('<div onclick="alert(1)">')).toBe(true);
    });

    it('should detect data:text/html', () => {
      expect(isSuspiciousContent('data:text/html,<script>alert(1)</script>')).toBe(true);
    });

    it('should detect vbscript: protocol', () => {
      expect(isSuspiciousContent('vbscript:msgbox("xss")')).toBe(true);
    });

    it('should detect fromCharCode', () => {
      expect(isSuspiciousContent('String.fromCharCode(60,115,99,114,105,112,116)')).toBe(true);
    });

    it('should detect eval()', () => {
      expect(isSuspiciousContent('eval("alert(1)")')).toBe(true);
    });

    it('should not flag safe content', () => {
      expect(isSuspiciousContent('This is safe content')).toBe(false);
      expect(isSuspiciousContent('<div>Safe HTML</div>')).toBe(false);
    });
  });

  describe('renderWithWarning', () => {
    it('should render text with suspicious flag for dangerous content', () => {
      const input = '<script>alert("xss")</script>';
      const result = renderWithWarning(input);
      expect(result.text).not.toContain('<script>');
      expect(result.isSuspicious).toBe(true);
    });

    it('should render text without suspicious flag for safe content', () => {
      const input = 'This is safe content';
      const result = renderWithWarning(input);
      expect(result.text).toBe('This is safe content');
      expect(result.isSuspicious).toBe(false);
    });

    it('should handle null and undefined', () => {
      const result1 = renderWithWarning(null);
      expect(result1.text).toBe('');
      expect(result1.isSuspicious).toBe(false);

      const result2 = renderWithWarning(undefined);
      expect(result2.text).toBe('');
      expect(result2.isSuspicious).toBe(false);
    });
  });

  describe('sanitizeHtml', () => {
    it('should remove script tags', () => {
      const input = '<script>alert("xss")</script>Safe content';
      const result = sanitizeHtml(input);
      expect(result).not.toContain('<script>');
      expect(result).toContain('Safe content');
    });

    it('should remove iframe tags', () => {
      const input = '<iframe src="evil.com"></iframe>Safe content';
      const result = sanitizeHtml(input);
      expect(result).not.toContain('<iframe>');
      expect(result).toContain('Safe content');
    });

    it('should remove object tags', () => {
      const input = '<object data="evil.com"></object>Safe content';
      const result = sanitizeHtml(input);
      expect(result).not.toContain('<object>');
      expect(result).toContain('Safe content');
    });

    it('should remove embed tags', () => {
      const input = '<embed src="evil.com">Safe content';
      const result = sanitizeHtml(input);
      expect(result).not.toContain('<embed>');
      expect(result).toContain('Safe content');
    });

    it('should remove event handlers', () => {
      const input = '<div onclick="alert(1)">Safe content</div>';
      const result = sanitizeHtml(input);
      expect(result).not.toContain('onclick');
    });

    it('should remove javascript: protocols', () => {
      const input = '<a href="javascript:alert(1)">Link</a>';
      const result = sanitizeHtml(input);
      expect(result).not.toContain('javascript:');
    });
  });

  describe('safeMarkdown', () => {
    it('should convert bold markdown', () => {
      const input = '**Bold text**';
      const result = safeMarkdown(input);
      expect(result).toContain('<strong>Bold text</strong>');
    });

    it('should convert italic markdown', () => {
      const input = '*Italic text*';
      const result = safeMarkdown(input);
      expect(result).toContain('<em>Italic text</em>');
    });

    it('should convert code markdown', () => {
      const input = '`code`';
      const result = safeMarkdown(input);
      expect(result).toContain('<code>code</code>');
    });

    it('should convert line breaks', () => {
      const input = 'Line 1\nLine 2';
      const result = safeMarkdown(input);
      expect(result).toContain('<br>');
    });

    it('should escape HTML in markdown', () => {
      const input = '**Bold** <script>alert("xss")</script>';
      const result = safeMarkdown(input);
      expect(result).not.toContain('<script>');
    });

    it('should handle null and undefined', () => {
      expect(safeMarkdown(null)).toBe('');
      expect(safeMarkdown(undefined)).toBe('');
    });
  });

  describe('maskSensitive', () => {
    it('should mask sensitive information', () => {
      const input = 'my-secret-token-12345';
      const result = maskSensitive(input, 4);
      expect(result).toBe('my-s****-12345');
    });

    it('should handle short strings', () => {
      const input = 'abc';
      const result = maskSensitive(input, 4);
      expect(result).toBe('***');
    });

    it('should handle null and undefined', () => {
      expect(maskSensitive(null)).toBe('');
      expect(maskSensitive(undefined)).toBe('');
    });

    it('should use custom mask character', () => {
      const input = 'my-secret-token';
      const result = maskSensitive(input, 2, '#');
      expect(result).toBe('my#########en');
    });
  });

  describe('safeEmail', () => {
    it('should render valid email', () => {
      const input = 'user@example.com';
      const result = safeEmail(input);
      expect(result).toBe('user@example.com');
    });

    it('should escape HTML in email', () => {
      const input = '<script>alert("xss")</script>@example.com';
      const result = safeEmail(input);
      expect(result).not.toContain('<script>');
    });

    it('should handle null and undefined', () => {
      expect(safeEmail(null)).toBe('N/A');
      expect(safeEmail(undefined)).toBe('N/A');
    });

    it('should handle invalid email', () => {
      const input = 'invalid-email';
      const result = safeEmail(input);
      expect(result).toBe('Invalid email');
    });
  });

  describe('safeUrl', () => {
    it('should render valid URL', () => {
      const input = 'https://example.com';
      const result = safeUrl(input);
      expect(result).toBe('https://example.com');
    });

    it('should escape HTML in URL', () => {
      const input = 'https://example.com/<script>alert("xss")</script>';
      const result = safeUrl(input);
      expect(result).not.toContain('<script>');
    });

    it('should handle null and undefined', () => {
      expect(safeUrl(null)).toBe('N/A');
      expect(safeUrl(undefined)).toBe('N/A');
    });

    it('should handle invalid URL', () => {
      const input = 'not-a-url';
      const result = safeUrl(input);
      expect(result).toBe('Invalid URL');
    });
  });

  describe('safeErrorMessage', () => {
    it('should render string error message', () => {
      const input = 'Error occurred';
      const result = safeErrorMessage(input);
      expect(result).toBe('Error occurred');
    });

    it('should render error object message', () => {
      const input = { message: 'Error occurred' };
      const result = safeErrorMessage(input);
      expect(result).toBe('Error occurred');
    });

    it('should render error object detail', () => {
      const input = { detail: 'Detailed error' };
      const result = safeErrorMessage(input);
      expect(result).toBe('Detailed error');
    });

    it('should escape HTML in error message', () => {
      const input = '<script>alert("xss")</script> error';
      const result = safeErrorMessage(input);
      expect(result).not.toContain('<script>');
    });

    it('should handle null and undefined', () => {
      expect(safeErrorMessage(null)).toBe('An error occurred');
      expect(safeErrorMessage(undefined)).toBe('An error occurred');
    });

    it('should handle generic error', () => {
      const input = { other: 'field' };
      const result = safeErrorMessage(input);
      expect(result).toBe('An error occurred');
    });
  });
});