import {
  ApiClient,
  ApiRequestError,
  NetworkError,
  AuthenticationError,
  AuthorizationError,
  NotFoundError,
  ValidationError,
  RateLimitError,
  ServerError
} from '@/lib/api/client';

// Mock fetch for testing
const mockFetch = jest.fn();
global.fetch = mockFetch as any;

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock as any;

describe('ApiClient', () => {
  let apiClient: ApiClient;

  beforeEach(() => {
    apiClient = new ApiClient();
    mockFetch.mockClear();
    localStorageMock.getItem.mockClear();
    localStorageMock.setItem.mockClear();
    localStorageMock.removeItem.mockClear();
  });

  describe('Initialization', () => {
    it('should initialize with default API URL', () => {
      expect(apiClient).toBeDefined();
    });

    it('should have correct API URL structure', () => {
      // Test that the client properly constructs URLs
      expect(process.env.NEXT_PUBLIC_API_URL).toBeDefined();
    });
  });

  describe('Token Management', () => {
    it('should set and get token', () => {
      const testToken = 'test-token-123';
      apiClient.setToken(testToken);
      expect(localStorageMock.setItem).toHaveBeenCalledWith('auth_token', testToken);
    });

    it('should clear token', () => {
      apiClient.setToken('test-token');
      apiClient.clearToken();
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('auth_token');
    });
  });

  describe('API Endpoints', () => {
    it('should have health check method', () => {
      expect(typeof apiClient.getHealth).toBe('function');
    });

    it('should have authentication methods', () => {
      expect(typeof apiClient.login).toBe('function');
      expect(typeof apiClient.register).toBe('function');
      expect(typeof apiClient.logout).toBe('function');
    });

    it('should have finding methods', () => {
      expect(typeof apiClient.getFindings).toBe('function');
      expect(typeof apiClient.getFinding).toBe('function');
      expect(typeof apiClient.createFinding).toBe('function');
      expect(typeof apiClient.updateFinding).toBe('function');
    });

    it('should have event methods', () => {
      expect(typeof apiClient.getEvents).toBe('function');
      expect(typeof apiClient.getEvent).toBe('function');
      expect(typeof apiClient.createEvent).toBe('function');
    });

    it('should have detection rule methods', () => {
      expect(typeof apiClient.getDetectionRules).toBe('function');
      expect(typeof apiClient.seedDetectionRules).toBe('function');
    });

    it('should have audit log methods', () => {
      expect(typeof apiClient.getAuditLogs).toBe('function');
      expect(typeof apiClient.getAuditLogStats).toBe('function');
    });
  });

  describe('Error Handling', () => {
    it('should throw ValidationError on 400 status', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({ message: 'Validation error', details: { field: 'invalid' } }),
      } as Response);

      await expect(apiClient.getHealth()).rejects.toThrow(ValidationError);
    });

    it('should throw AuthenticationError on 401 status', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ message: 'Unauthorized' }),
      } as Response);

      await expect(apiClient.getHealth()).rejects.toThrow(AuthenticationError);
    });

    it('should clear token on 401 status', async () => {
      apiClient.setToken('test-token');
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ message: 'Unauthorized' }),
      } as Response);

      await expect(apiClient.getHealth()).rejects.toThrow(AuthenticationError);
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('auth_token');
    });

    it('should throw AuthorizationError on 403 status', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 403,
        json: async () => ({ message: 'Forbidden' }),
      } as Response);

      await expect(apiClient.getHealth()).rejects.toThrow(AuthorizationError);
    });

    it('should throw NotFoundError on 404 status', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({ message: 'Not found' }),
      } as Response);

      await expect(apiClient.getHealth()).rejects.toThrow(NotFoundError);
    });

    it('should throw ValidationError on 409 status', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 409,
        json: async () => ({ message: 'Conflict', details: { resource: 'exists' } }),
      } as Response);

      await expect(apiClient.getHealth()).rejects.toThrow(ValidationError);
    });

    it('should throw RateLimitError on 429 status', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 429,
        json: async () => ({ message: 'Too many requests' }),
      } as Response);

      await expect(apiClient.getHealth()).rejects.toThrow(RateLimitError);
    });

    it('should throw ServerError on 500 status', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({ message: 'Internal server error' }),
      } as Response);

      await expect(apiClient.getHealth()).rejects.toThrow(ServerError);
    });

    it('should throw ServerError on 502 status', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 502,
        json: async () => ({ message: 'Bad gateway' }),
      } as Response);

      await expect(apiClient.getHealth()).rejects.toThrow(ServerError);
    });

    it('should throw ServerError on 503 status', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 503,
        json: async () => ({ message: 'Service unavailable' }),
      } as Response);

      await expect(apiClient.getHealth()).rejects.toThrow(ServerError);
    });

    it('should throw ServerError on 504 status', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 504,
        json: async () => ({ message: 'Gateway timeout' }),
      } as Response);

      await expect(apiClient.getHealth()).rejects.toThrow(ServerError);
    });

    it('should throw NetworkError on network failure', async () => {
      mockFetch.mockRejectedValueOnce(
        new TypeError('Failed to fetch')
      );

      await expect(apiClient.getHealth()).rejects.toThrow(NetworkError);
    });

    it('should throw ApiRequestError on unknown status codes', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 418,
        statusText: "I'm a teapot",
        json: async () => ({ message: 'Unknown error' }),
      } as Response);

      await expect(apiClient.getHealth()).rejects.toThrow(ApiRequestError);
    });

    it('should handle successful responses', async () => {
      const mockResponse = { status: 'healthy', timestamp: '2024-01-01T00:00:00Z' };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response);

      const result = await apiClient.getHealth();
      expect(result).toEqual(mockResponse);
    });
  });

  describe('Error Types', () => {
    it('should create ApiRequestError with correct properties', () => {
      const error = new ApiRequestError('Test error', 400, 'Bad Request', { field: 'test' });
      expect(error.message).toBe('Test error');
      expect(error.status).toBe(400);
      expect(error.statusText).toBe('Bad Request');
      expect(error.details).toEqual({ field: 'test' });
      expect(error.name).toBe('ApiRequestError');
    });

    it('should create NetworkError with correct properties', () => {
      const error = new NetworkError('Network failed');
      expect(error.message).toBe('Network failed');
      expect(error.name).toBe('NetworkError');
    });

    it('should create AuthenticationError with default message', () => {
      const error = new AuthenticationError();
      expect(error.message).toBe('Authentication required');
      expect(error.name).toBe('AuthenticationError');
    });

    it('should create AuthenticationError with custom message', () => {
      const error = new AuthenticationError('Custom auth error');
      expect(error.message).toBe('Custom auth error');
      expect(error.name).toBe('AuthenticationError');
    });

    it('should create AuthorizationError with default message', () => {
      const error = new AuthorizationError();
      expect(error.message).toBe('Insufficient permissions');
      expect(error.name).toBe('AuthorizationError');
    });

    it('should create NotFoundError with default message', () => {
      const error = new NotFoundError();
      expect(error.message).toBe('Resource not found');
      expect(error.name).toBe('NotFoundError');
    });

    it('should create ValidationError with details', () => {
      const error = new ValidationError('Validation failed', { field: 'required' });
      expect(error.message).toBe('Validation failed');
      expect(error.validationErrors).toEqual({ field: 'required' });
      expect(error.name).toBe('ValidationError');
    });

    it('should create RateLimitError with default message', () => {
      const error = new RateLimitError();
      expect(error.message).toBe('Too many requests, please try again later');
      expect(error.name).toBe('RateLimitError');
    });

    it('should create ServerError with default message', () => {
      const error = new ServerError();
      expect(error.message).toBe('Server error occurred');
      expect(error.name).toBe('ServerError');
    });
  });
});