import axios, { AxiosResponse } from 'axios';
import {
  Company,
  CompanyCreate,
  User,
  UserCreate,
  Document,
  Query,
  SearchRequest,
  SearchResponse,
  Recommendation,
} from '../types';

// Create axios instance
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for debugging
api.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('❌ API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Company API
export const companyApi = {
  getAll: (): Promise<AxiosResponse<Company[]>> =>
    api.get('/companies/'),
  
  getById: (id: number): Promise<AxiosResponse<Company>> =>
    api.get(`/companies/${id}/`),
  
  create: (data: CompanyCreate): Promise<AxiosResponse<Company>> =>
    api.post('/companies/', data),
  
  update: (id: number, data: CompanyCreate): Promise<AxiosResponse<Company>> =>
    api.put(`/companies/${id}/`, data),
  
  delete: (id: number): Promise<AxiosResponse<void>> =>
    api.delete(`/companies/${id}/`),
};

// User API
export const userApi = {
  getAll: (company_id?: number): Promise<AxiosResponse<User[]>> =>
    api.get('/users/', { params: { company_id } }),
  
  getById: (id: number): Promise<AxiosResponse<User>> =>
    api.get(`/users/${id}/`),
  
  getByCompany: (company_id: number): Promise<AxiosResponse<User[]>> =>
    api.get(`/users/company/${company_id}/`),
  
  create: (data: UserCreate): Promise<AxiosResponse<User>> =>
    api.post('/users/', data),
  
  update: (id: number, data: UserCreate): Promise<AxiosResponse<User>> =>
    api.put(`/users/${id}/`, data),
  
  delete: (id: number): Promise<AxiosResponse<void>> =>
    api.delete(`/users/${id}/`),
};

// Search API
export const searchApi = {
  search: (data: SearchRequest): Promise<AxiosResponse<SearchResponse>> =>
    api.post('/search/', data),
  
  getQueries: (
    user_id: number,
    company_id: number,
    skip = 0,
    limit = 10
  ): Promise<AxiosResponse<Query[]>> =>
    api.get(`/search/queries/${user_id}`, {
      params: { company_id, skip, limit },
    }),
  
  deleteQuery: (
    query_id: number,
    user_id: number,
    company_id: number
  ): Promise<AxiosResponse<{ message: string }>> =>
    api.delete(`/search/queries/${query_id}`, {
      params: { user_id, company_id },
    }),
};

// Recommendation API
export const recommendationApi = {
  getRecommendations: (
    user_id: number,
    company_id: number,
    limit = 10
  ): Promise<AxiosResponse<Recommendation[]>> =>
    api.get(`/recommendations/${user_id}`, {
      params: { company_id, limit },
    }),
  
  refreshRecommendations: (
    user_id: number,
    company_id: number
  ): Promise<AxiosResponse<{ message: string; count: number }>> =>
    api.post(`/recommendations/${user_id}/refresh`, null, {
      params: { company_id },
    }),
  
  checkCacheHealth: (): Promise<AxiosResponse<{ status: string; cache: string }>> =>
    api.get('/recommendations/health/cache'),
};

// Document API
export const documentApi = {
  getAll: (
    company_id: number,
    user_id?: number,
    skip = 0,
    limit = 50
  ): Promise<AxiosResponse<Document[]>> =>
    api.get('/documents', {
      params: { company_id, user_id, skip, limit },
    }),
  
  getById: (
    document_id: number,
    company_id: number
  ): Promise<AxiosResponse<Document>> =>
    api.get(`/documents/${document_id}`, {
      params: { company_id },
    }),
  
  getUserDocuments: (
    user_id: number,
    company_id: number,
    skip = 0,
    limit = 50
  ): Promise<AxiosResponse<Document[]>> =>
    api.get(`/documents/user/${user_id}`, {
      params: { company_id, skip, limit },
    }),
  
  delete: (
    document_id: number,
    company_id: number,
    user_id: number
  ): Promise<AxiosResponse<void>> =>
    api.delete(`/documents/${document_id}`, {
      params: { company_id, user_id },
    }),
};

// Health Check API
export const healthApi = {
  check: (): Promise<AxiosResponse<{ status: string; service: string; version: string }>> =>
    api.get('/health', { baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000' }),
  
  getStatus: (): Promise<AxiosResponse<{
    status: string;
    database: string;
    companies: number;
    endpoints: Record<string, string>;
  }>> =>
    api.get('/status'),
};

export default api;