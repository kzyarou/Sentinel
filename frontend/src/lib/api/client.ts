import {
  ApiResponse,
  ApiError,
  User,
  UserCreate,
  UserLogin,
  TokenResponse,
  Finding,
  FindingCreate,
  FindingUpdate,
  Event,
  EventCreate,
  DetectionRule,
  AuditLog,
  AuditLogStats,
  PaginatedResponse,
  FindingFilters,
  EventFilters,
  AuditLogFilters
} from '@/types';

class ApiClient {
  private baseUrl: string;
  private apiVersion: string;
  private token: string | null = null;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    this.apiVersion = process.env.NEXT_PUBLIC_API_VERSION || 'v1';
    
    // Load token from localStorage on client side
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('auth_token');
    }
  }

  private get apiUrl(): string {
    return `${this.baseUrl}/api/${this.apiVersion}`;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.apiUrl}${endpoint}`;
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      if (!response.ok) {
        const errorData: ApiError = await response.json().catch(() => ({
          error: 'Unknown error',
          message: 'An error occurred',
          status: response.status,
        }));
        throw new Error(errorData.message || 'Request failed');
      }

      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('An unexpected error occurred');
    }
  }

  // Authentication Methods
  setToken(token: string): void {
    this.token = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token);
    }
  }

  clearToken(): void {
    this.token = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }
  }

  async login(credentials: UserLogin): Promise<TokenResponse> {
    const response = await this.post<TokenResponse>('/auth/login', credentials);
    this.setToken(response.access_token);
    return response;
  }

  async register(userData: UserCreate): Promise<User> {
    return this.post<User>('/auth/register', userData);
  }

  async logout(): Promise<void> {
    await this.post<void>('/auth/logout', {});
    this.clearToken();
  }

  // Finding Methods
  async getFindings(filters?: FindingFilters): Promise<PaginatedResponse<Finding>> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined) {
          params.append(key, String(value));
        }
      });
    }
    const queryString = params.toString();
    return this.get<PaginatedResponse<Finding>>(
      `/findings${queryString ? `?${queryString}` : ''}`
    );
  }

  async getFinding(id: string): Promise<Finding> {
    return this.get<Finding>(`/findings/${id}`);
  }

  async createFinding(data: FindingCreate): Promise<Finding> {
    return this.post<Finding>('/findings', data);
  }

  async updateFinding(id: string, data: FindingUpdate): Promise<Finding> {
    return this.patch<Finding>(`/findings/${id}`, data);
  }

  async requestAIAnalysis(findingId: string): Promise<Finding> {
    return this.post<Finding>(`/findings/${findingId}/analysis`, {});
  }

  // Event Methods
  async getEvents(filters?: EventFilters): Promise<PaginatedResponse<Event>> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined) {
          params.append(key, String(value));
        }
      });
    }
    const queryString = params.toString();
    return this.get<PaginatedResponse<Event>>(
      `/events${queryString ? `?${queryString}` : ''}`
    );
  }

  async getEvent(id: string): Promise<Event> {
    return this.get<Event>(`/events/${id}`);
  }

  async createEvent(data: EventCreate): Promise<Event> {
    return this.post<Event>('/events', data);
  }

  // Detection Rule Methods
  async getDetectionRules(): Promise<DetectionRule[]> {
    return this.get<DetectionRule[]>('/detection-rules');
  }

  async seedDetectionRules(): Promise<{ message: string }> {
    return this.post<{ message: string }>('/detections/seed-rules', {});
  }

  // Audit Log Methods
  async getAuditLogs(filters?: AuditLogFilters): Promise<AuditLog[]> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined) {
          params.append(key, String(value));
        }
      });
    }
    const queryString = params.toString();
    return this.get<AuditLog[]>(
      `/audit-logs${queryString ? `?${queryString}` : ''}`
    );
  }

  async getAuditLogStats(): Promise<AuditLogStats> {
    return this.get<AuditLogStats>('/audit-logs/stats');
  }

  // Health Check
  async getHealth(): Promise<{ status: string; timestamp: string }> {
    return this.get<{ status: string; timestamp: string }>('/health');
  }

  // HTTP Helper Methods
  private async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  private async post<T>(endpoint: string, data: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  private async patch<T>(endpoint: string, data: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  private async put<T>(endpoint: string, data: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  private async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }
}

// Export singleton instance
export const apiClient = new ApiClient();

// Export class for testing
export { ApiClient };