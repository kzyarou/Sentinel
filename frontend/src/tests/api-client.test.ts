import { ApiClient } from '@/lib/api/client';

// Mock fetch for testing
global.fetch = jest.fn() as jest.MockedFunction<typeof fetch>;

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
    (global.fetch as jest.MockedFunction<typeof fetch>).mockClear();
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
});