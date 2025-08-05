// Company Types
export interface Company {
  id: number;
  name: string;
  created_at: string;
}

export interface CompanyCreate {
  name: string;
}

// User Types
export interface User {
  id: number;
  name: string;
  email: string;
  company_id: number;
  created_at: string;
  company: Company;
}

export interface UserCreate {
  name: string;
  email: string;
  company_id: number;
}

// Document Types
export interface Document {
  id: number;
  title: string;
  content: string;
  source: string;
  confidence: number;
  created_by_user_id: number;
  company_id: number;
  created_at: string;
  created_by_user: User;
}

export interface DocumentCreate {
  title: string;
  content: string;
  source?: string;
  confidence?: number;
  created_by_user_id: number;
  company_id: number;
}

// Query Types
export interface Query {
  id: number;
  query_text: string;
  user_id: number;
  company_id: number;
  created_at: string;
  user: User;
}

// Search Types
export interface SearchRequest {
  query: string;
  user_id: number;
  company_id: number;
  save_as_document?: boolean;
}

export interface SearchResponse {
  query: string;
  answer: string;
  sources: string[];
  confidence: number;
  document_id?: number;
}

// Recommendation Types
export interface Recommendation {
  id: number;
  title: string;
  content: string;
  source: string;
  confidence: number;
  relevance_score: number;
  explanation: string;
  created_at: string;
}

// UI State Types
export interface AppState {
  selectedCompany: Company | null;
  selectedUser: User | null;
  activeTab: 'search' | 'discover';
  isLoading: boolean;
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  has_next: boolean;
  has_prev: boolean;
}