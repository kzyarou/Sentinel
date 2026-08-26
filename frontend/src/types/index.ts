// API Response Types
export interface ApiResponse<T> {
  data: T;
  error?: string;
  message?: string;
}

export interface ApiError {
  error: string;
  message: string;
  status?: number;
}

// User Types
export interface User {
  id: string;
  username: string;
  email: string;
  role: 'ADMIN' | 'ANALYST' | 'VIEWER';
  status: 'ACTIVE' | 'INACTIVE' | 'SUSPENDED';
  created_at: string;
  updated_at: string;
}

export interface UserCreate {
  username: string;
  email: string;
  password: string;
  role: 'ADMIN' | 'ANALYST' | 'VIEWER';
}

export interface UserLogin {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

// Finding Types
export interface Finding {
  id: string;
  title: string;
  description: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  status: 'OPEN' | 'INVESTIGATING' | 'RESOLVED' | 'FALSE_POSITIVE';
  created_at: string;
  updated_at: string;
  detections?: Detection[];
  ai_analysis?: AIAnalysis;
}

export interface FindingCreate {
  title: string;
  description: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  status?: 'OPEN' | 'INVESTIGATING' | 'RESOLVED' | 'FALSE_POSITIVE';
}

export interface FindingUpdate {
  title?: string;
  description?: string;
  severity?: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  status?: 'OPEN' | 'INVESTIGATING' | 'RESOLVED' | 'FALSE_POSITIVE';
  resolution_notes?: string;
  false_positive_reason?: string;
}

// Event Types
export interface Event {
  id: string;
  event_type: string;
  source: string;
  timestamp: string;
  host: string;
  user?: string;
  ip_address?: string;
  raw_data: Record<string, any>;
  normalized_data?: Record<string, any>;
}

export interface EventCreate {
  event_type: string;
  source: string;
  timestamp: string;
  host: string;
  user?: string;
  ip_address?: string;
  raw_data: Record<string, any>;
}

// Detection Types
export interface Detection {
  id: string;
  finding_id: string;
  rule_id: string;
  rule_name: string;
  confidence: number;
  matched_at: string;
  details: Record<string, any>;
}

export interface DetectionRule {
  id: string;
  name: string;
  description: string;
  rule_type: string;
  enabled: boolean;
  created_at: string;
  updated_at: string;
}

// AI Analysis Types
export interface AIAnalysis {
  id: string;
  finding_id: string;
  analysis: string;
  confidence: number;
  recommendations: string[];
  created_at: string;
}

// Audit Log Types
export interface AuditLog {
  id: string;
  user_id?: string;
  action: string;
  action_category: 'authentication' | 'authorization' | 'finding' | 'detection_rule' | 'user_administration' | 'system';
  resource_type: string;
  resource_id?: string;
  result: 'success' | 'failure' | 'error';
  timestamp: string;
  request_id?: string;
  ip_address?: string;
  user_agent?: string;
  metadata?: Record<string, any>;
}

export interface AuditLogStats {
  total_count: number;
  category_stats: Record<string, number>;
  result_stats: Record<string, number>;
  last_24h_count: number;
}

// Pagination Types
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}

export interface PaginationParams {
  skip?: number;
  limit?: number;
}

// Filter Types
export interface FindingFilters extends PaginationParams {
  severity?: string;
  status?: string;
  search?: string;
}

export interface EventFilters extends PaginationParams {
  event_type?: string;
  source?: string;
  start_time?: string;
  end_time?: string;
}

export interface AuditLogFilters extends PaginationParams {
  user_id?: string;
  action?: string;
  action_category?: string;
  resource_type?: string;
  resource_id?: string;
  result?: string;
  request_id?: string;
  start_time?: string;
  end_time?: string;
}