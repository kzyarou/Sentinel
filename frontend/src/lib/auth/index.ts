import { User, TokenResponse } from '@/types';
import { apiClient } from '@/lib/api/client';

export class AuthService {
  private static currentUser: User | null = null;
  private static token: string | null = null;

  static getCurrentUser(): User | null {
    return this.currentUser;
  }

  static getToken(): string | null {
    return this.token;
  }

  static isAuthenticated(): boolean {
    return this.token !== null;
  }

  static async login(username: string, password: string): Promise<User> {
    try {
      const response = await apiClient.login({ username, password });
      this.token = response.access_token;
      this.currentUser = response.user;
      return this.currentUser;
    } catch (error) {
      this.clearAuth();
      throw error;
    }
  }

  static async register(
    username: string,
    email: string,
    password: string,
    role: 'ADMIN' | 'ANALYST' | 'VIEWER'
  ): Promise<User> {
    try {
      const user = await apiClient.register({
        username,
        email,
        password,
        role,
      });
      return user;
    } catch (error) {
      throw error;
    }
  }

  static async logout(): Promise<void> {
    try {
      await apiClient.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      this.clearAuth();
    }
  }

  static clearAuth(): void {
    this.currentUser = null;
    this.token = null;
    apiClient.clearToken();
  }

  static hasRole(role: 'ADMIN' | 'ANALYST' | 'VIEWER'): boolean {
    return this.currentUser?.role === role;
  }

  static hasPermission(permission: string): boolean {
    if (!this.currentUser) return false;
    
    const role = this.currentUser.role;
    
    // Define permission matrix
    const permissions: Record<string, string[]> = {
      ADMIN: ['view_findings', 'modify_findings', 'view_events', 'view_detections', 'manage_rules', 'manage_users', 'view_audit_logs'],
      ANALYST: ['view_findings', 'modify_findings', 'view_events', 'view_detections', 'request_ai_analysis'],
      VIEWER: ['view_findings', 'view_events', 'view_detections'],
    };

    return permissions[role]?.includes(permission) || false;
  }

  static canViewAuditLogs(): boolean {
    return this.hasPermission('view_audit_logs');
  }

  static canManageDetectionRules(): boolean {
    return this.hasPermission('manage_rules');
  }

  static canManageUsers(): boolean {
    return this.hasPermission('manage_users');
  }

  static canModifyFindings(): boolean {
    return this.hasPermission('modify_findings');
  }

  static canRequestAIAnalysis(): boolean {
    return this.hasPermission('request_ai_analysis');
  }
}

export default AuthService;