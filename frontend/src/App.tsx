import React, { useState, useEffect } from 'react';
import { QueryClient, QueryClientProvider } from 'react-query';
import Header from './components/Layout/Header';
import TabNavigation from './components/Layout/TabNavigation';
import SearchTab from './components/Search/SearchTab';
import DiscoverTab from './components/Discover/DiscoverTab';
import AdminTab from './components/Admin/AdminTab';
import { useCompanies, useUsers, useHealthCheck } from './hooks/useApi';
import { Company, User } from './types';
import { useQueryClient } from 'react-query';

// Create a query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

const AppContent: React.FC = () => {
  const [selectedCompany, setSelectedCompany] = useState<Company | null>(null);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [activeTab, setActiveTab] = useState<'search' | 'discover' | 'admin'>('search');

  // API hooks
  const queryClient = useQueryClient();
  const { data: companies = [], isLoading: companiesLoading, refetch: refetchCompanies } = useCompanies();
  const { data: users = [], isLoading: usersLoading, refetch: refetchUsers } = useUsers(selectedCompany?.id);
  const { data: healthStatus } = useHealthCheck();

  // Manual refresh function
  const handleRefresh = () => {
    queryClient.invalidateQueries('companies');
    queryClient.invalidateQueries('users');
    refetchCompanies();
    refetchUsers();
  };

  // Auto-select first company and user when data loads
  useEffect(() => {
    if (companies.length > 0 && !selectedCompany) {
      setSelectedCompany(companies[0]);
    }
  }, [companies, selectedCompany]);

  useEffect(() => {
    if (users.length > 0 && !selectedUser && selectedCompany) {
      setSelectedUser(users[0]);
    }
  }, [users, selectedUser, selectedCompany]);

  // Reset user when company changes
  const handleCompanyChange = (company: Company) => {
    setSelectedCompany(company);
    setSelectedUser(null); // Reset user selection
  };

  const handleUserChange = (user: User) => {
    setSelectedUser(user);
  };

  const isLoading = companiesLoading || usersLoading;
  const isContextReady = selectedCompany && selectedUser;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <Header
        companies={companies}
        users={users}
        selectedCompany={selectedCompany}
        selectedUser={selectedUser}
        onCompanyChange={handleCompanyChange}
        onUserChange={handleUserChange}
        onRefresh={handleRefresh}
        isLoading={isLoading}
      />

      {/* Tab Navigation */}
      <TabNavigation
        activeTab={activeTab}
        onTabChange={setActiveTab}
        disabled={!isContextReady && activeTab !== 'admin'}
      />

      {/* Main Content */}
      <main className="py-8">
        {activeTab === 'search' ? (
          <SearchTab
            selectedCompany={selectedCompany}
            selectedUser={selectedUser}
          />
        ) : activeTab === 'discover' ? (
          <DiscoverTab
            selectedCompany={selectedCompany}
            selectedUser={selectedUser}
          />
        ) : (
          <AdminTab />
        )}
      </main>

      {/* Health Status (Development) */}
      {process.env.NODE_ENV === 'development' && healthStatus && (
        <div className="fixed bottom-4 right-4 z-50">
          <div className={`px-3 py-2 rounded-lg text-sm ${
            healthStatus.status === 'healthy' 
              ? 'bg-green-100 text-green-800 border border-green-200'
              : 'bg-red-100 text-red-800 border border-red-200'
          }`}>
            API: {healthStatus.status}
          </div>
        </div>
      )}
    </div>
  );
};

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <AppContent />
    </QueryClientProvider>
  );
};

export default App;