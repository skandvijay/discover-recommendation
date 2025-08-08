import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import {
  companyApi,
  userApi,
  searchApi,
  recommendationApi,
  documentApi,
  healthApi,
} from '../services/api';
import {
  Company,
  CompanyCreate,
  User,
  UserCreate,
  SearchRequest,
  SearchResponse,
  Recommendation,
  Query,
  Document as AppDocument,
} from '../types';

// Companies
export const useCompanies = () => {
  return useQuery<Company[]>('companies', async () => {
    const response = await companyApi.getAll();
    return response.data;
  });
};

export const useCreateCompany = () => {
  const queryClient = useQueryClient();
  
  return useMutation<Company, Error, CompanyCreate>(
    async (data: CompanyCreate) => {
      const response = await companyApi.create(data);
      return response.data;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('companies');
      },
    }
  );
};

// Users
export const useUsers = (company_id?: number) => {
  return useQuery<User[]>(
    ['users', company_id],
    async () => {
      const response = company_id 
        ? await userApi.getByCompany(company_id)
        : await userApi.getAll();
      return response.data;
    },
    {
      enabled: !!company_id, // Only fetch when company_id is provided
    }
  );
};

export const useCreateUser = () => {
  const queryClient = useQueryClient();
  
  return useMutation<User, Error, UserCreate>(
    async (data: UserCreate) => {
      const response = await userApi.create(data);
      return response.data;
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries('users');
      },
    }
  );
};

// Search
export const useSearch = () => {
  const queryClient = useQueryClient();
  
  return useMutation<SearchResponse, Error, SearchRequest>(
    async (data: SearchRequest) => {
      const response = await searchApi.search(data);
      return response.data;
    },
    {
      onSuccess: (_, variables) => {
        // Invalidate related queries after successful search
        queryClient.invalidateQueries(['queries', variables.user_id]);
        queryClient.invalidateQueries(['recommendations', variables.user_id]);
      },
    }
  );
};

export const useQueries = (user_id?: number, company_id?: number) => {
  return useQuery<Query[]>(
    ['queries', user_id, company_id],
    async () => {
      if (!user_id || !company_id) return [];
      const response = await searchApi.getQueries(user_id, company_id, 0, 10);
      return response.data;
    },
    {
      enabled: !!user_id && !!company_id,
    }
  );
};

// Recommendations
export const useRecommendations = (user_id?: number, company_id?: number) => {
  return useQuery<Recommendation[]>(
    ['recommendations', user_id, company_id],
    async () => {
      if (!user_id || !company_id) return [];
      const response = await recommendationApi.getRecommendations(user_id, company_id);
      return response.data;
    },
    {
      enabled: !!user_id && !!company_id,
      staleTime: 30 * 60 * 1000, // 30 minutes
    }
  );
};

export const useRefreshRecommendations = () => {
  const queryClient = useQueryClient();
  
  return useMutation<
    { message: string; count: number },
    Error,
    { user_id: number; company_id: number }
  >(
    async ({ user_id, company_id }) => {
      const response = await recommendationApi.refreshRecommendations(user_id, company_id);
      return response.data;
    },
    {
      onSuccess: (_, variables) => {
        queryClient.invalidateQueries(['recommendations', variables.user_id]);
      },
    }
  );
};

// Health Check
export const useHealthCheck = () => {
  return useQuery(
    'health',
    async () => {
      const response = await healthApi.check();
      return response.data;
    },
    {
      refetchInterval: 30000, // Check every 30 seconds
      retry: 1,
    }
  );
};

// Custom hook for loading state management
// Documents
export const useDocuments = (company_id?: number, user_id?: number) => {
  return useQuery<AppDocument[]>(
    ['documents', company_id, user_id],
    async () => {
      if (!company_id) return [];
      const response = await documentApi.getAll(company_id, user_id);
      return response.data;
    },
    {
      enabled: !!company_id,
    }
  );
};

export const useDeleteDocument = () => {
  const queryClient = useQueryClient();
  
  return useMutation<void, Error, { document_id: number; company_id: number; user_id: number }>(
    async ({ document_id, company_id, user_id }) => {
      await documentApi.delete(document_id, company_id, user_id);
    },
    {
      onSuccess: (_, variables) => {
        // Invalidate documents queries after successful deletion
        queryClient.invalidateQueries(['documents', variables.company_id]);
        queryClient.invalidateQueries(['documents', variables.company_id, variables.user_id]);
        queryClient.invalidateQueries(['recommendations', variables.user_id]);
      },
    }
  );
};

export const useLoadingState = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const withLoading = async <T>(
    promise: Promise<T>
  ): Promise<T | undefined> => {
    try {
      setIsLoading(true);
      setError(null);
      const result = await promise;
      return result;
    } catch (err: any) {
      setError(err.message || 'An error occurred');
      console.error('Loading error:', err);
      return undefined;
    } finally {
      setIsLoading(false);
    }
  };

  return {
    isLoading,
    error,
    setError,
    withLoading,
  };
};