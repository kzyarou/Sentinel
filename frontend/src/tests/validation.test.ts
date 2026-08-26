import {
  validateEmail,
  validatePassword,
  validateUsername,
  validateRequired,
  validateMinLength,
  validateMaxLength,
  validateUrl,
  validateIsoDate,
} from '@/lib/validation';

describe('Validation Utilities', () => {
  describe('validateEmail', () => {
    it('should validate correct email addresses', () => {
      expect(validateEmail('test@example.com')).toBe(true);
      expect(validateEmail('user.name+tag@example.co.uk')).toBe(true);
    });

    it('should reject invalid email addresses', () => {
      expect(validateEmail('invalid')).toBe(false);
      expect(validateEmail('test@')).toBe(false);
      expect(validateEmail('@example.com')).toBe(false);
    });
  });

  describe('validatePassword', () => {
    it('should validate strong passwords', () => {
      const result = validatePassword('StrongP@ssw0rd!');
      expect(result.valid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should reject weak passwords', () => {
      const result = validatePassword('weak');
      expect(result.valid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
    });

    it('should require uppercase letters', () => {
      const result = validatePassword('lowercase123!');
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Password must contain at least one uppercase letter');
    });

    it('should require lowercase letters', () => {
      const result = validatePassword('UPPERCASE123!');
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Password must contain at least one lowercase letter');
    });

    it('should require numbers', () => {
      const result = validatePassword('NoNumbers!');
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Password must contain at least one number');
    });

    it('should require special characters', () => {
      const result = validatePassword('NoSpecialChars123');
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Password must contain at least one special character');
    });
  });

  describe('validateUsername', () => {
    it('should validate correct usernames', () => {
      const result = validateUsername('valid_user');
      expect(result.valid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should reject short usernames', () => {
      const result = validateUsername('ab');
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Username must be at least 3 characters long');
    });

    it('should reject long usernames', () => {
      const result = validateUsername('a'.repeat(51));
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Username must be less than 50 characters');
    });

    it('should reject invalid characters', () => {
      const result = validateUsername('invalid@username');
      expect(result.valid).toBe(false);
      expect(result.errors).toContain('Username can only contain letters, numbers, underscores, and hyphens');
    });
  });

  describe('validateRequired', () => {
    it('should return null for valid values', () => {
      expect(validateRequired('value', 'Field')).toBeNull();
      expect(validateRequired('  value  ', 'Field')).toBeNull();
    });

    it('should return error for empty values', () => {
      expect(validateRequired('', 'Field')).toBe('Field is required');
      expect(validateRequired('   ', 'Field')).toBe('Field is required');
    });
  });

  describe('validateMinLength', () => {
    it('should return null for valid length', () => {
      expect(validateMinLength('12345', 3, 'Field')).toBeNull();
    });

    it('should return error for short values', () => {
      expect(validateMinLength('12', 3, 'Field')).toBe('Field must be at least 3 characters');
    });
  });

  describe('validateMaxLength', () => {
    it('should return null for valid length', () => {
      expect(validateMaxLength('123', 5, 'Field')).toBeNull();
    });

    it('should return error for long values', () => {
      expect(validateMaxLength('123456', 5, 'Field')).toBe('Field must be less than 5 characters');
    });
  });

  describe('validateUrl', () => {
    it('should validate correct URLs', () => {
      expect(validateUrl('https://example.com')).toBe(true);
      expect(validateUrl('http://localhost:8000')).toBe(true);
    });

    it('should reject invalid URLs', () => {
      expect(validateUrl('not-a-url')).toBe(false);
      expect(validateUrl('example.com')).toBe(false);
    });
  });

  describe('validateIsoDate', () => {
    it('should validate correct ISO dates', () => {
      expect(validateIsoDate('2024-01-01T00:00:00Z')).toBe(true);
      expect(validateIsoDate('2024-01-01T00:00:00.000Z')).toBe(true);
      expect(validateIsoDate('2024-01-01T00:00:00+00:00')).toBe(true);
    });

    it('should reject invalid dates', () => {
      expect(validateIsoDate('2024-01-01')).toBe(false);
      expect(validateIsoDate('invalid-date')).toBe(false);
    });
  });
});