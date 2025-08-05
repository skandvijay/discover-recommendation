import React, { useState } from 'react';
import { 
  PlusIcon, 
  BuildingOfficeIcon, 
  UserGroupIcon,
  CheckIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import { useCreateCompany, useCreateUser, useCompanies } from '../../hooks/useApi';
import { useQueryClient } from 'react-query';
import { Company } from '../../types';
import { formatDate, getInitials, stringToColor } from '../../utils/format';
import clsx from 'clsx';

interface AdminTabProps {}

const AdminTab: React.FC<AdminTabProps> = () => {
  const [companyName, setCompanyName] = useState('');
  const [userName, setUserName] = useState('');
  const [userEmail, setUserEmail] = useState('');
  const [selectedCompanyId, setSelectedCompanyId] = useState<number | null>(null);
  
  const queryClient = useQueryClient();
  const { data: companies = [], refetch: refetchCompanies } = useCompanies();
  const createCompanyMutation = useCreateCompany();
  const createUserMutation = useCreateUser();

  const handleCreateCompany = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!companyName.trim()) return;

    try {
      await createCompanyMutation.mutateAsync({ name: companyName.trim() });
      setCompanyName('');
      // Invalidate all company-related queries to refresh dropdowns
      queryClient.invalidateQueries('companies');
      queryClient.invalidateQueries('users');
      refetchCompanies();
    } catch (error) {
      console.error('Error creating company:', error);
    }
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userName.trim() || !userEmail.trim() || !selectedCompanyId) return;

    try {
      await createUserMutation.mutateAsync({
        name: userName.trim(),
        email: userEmail.trim(),
        company_id: selectedCompanyId
      });
      setUserName('');
      setUserEmail('');
      setSelectedCompanyId(null);
      // Invalidate user queries to refresh dropdowns
      queryClient.invalidateQueries(['users', selectedCompanyId]);
      queryClient.invalidateQueries('users');
    } catch (error) {
      console.error('Error creating user:', error);
    }
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Admin Panel
        </h2>
        <p className="text-gray-600">
          Manage companies and users for testing the recommendation engine
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Create Company Section */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center mb-6">
            <BuildingOfficeIcon className="h-6 w-6 text-blue-600 mr-3" />
            <h3 className="text-lg font-semibold text-gray-900">Create Company</h3>
          </div>

          <form onSubmit={handleCreateCompany} className="space-y-4">
            <div>
              <label htmlFor="company-name" className="block text-sm font-medium text-gray-700 mb-2">
                Company Name
              </label>
              <input
                id="company-name"
                type="text"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                placeholder="Enter company name..."
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                disabled={createCompanyMutation.isLoading}
              />
            </div>

            <button
              type="submit"
              disabled={createCompanyMutation.isLoading || !companyName.trim()}
              className={clsx(
                'w-full inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm transition-colors duration-200',
                createCompanyMutation.isLoading || !companyName.trim()
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500'
              )}
            >
              {createCompanyMutation.isLoading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Creating...
                </>
              ) : (
                <>
                  <PlusIcon className="h-4 w-4 mr-2" />
                  Create Company
                </>
              )}
            </button>

            {createCompanyMutation.isError && (
              <div className="flex items-center text-sm text-red-600">
                <ExclamationTriangleIcon className="h-4 w-4 mr-1" />
                Failed to create company. Please try again.
              </div>
            )}

            {createCompanyMutation.isSuccess && (
              <div className="flex items-center text-sm text-green-600">
                <CheckIcon className="h-4 w-4 mr-1" />
                Company created successfully!
              </div>
            )}
          </form>
        </div>

        {/* Create User Section */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center mb-6">
            <UserGroupIcon className="h-6 w-6 text-green-600 mr-3" />
            <h3 className="text-lg font-semibold text-gray-900">Create User</h3>
          </div>

          <form onSubmit={handleCreateUser} className="space-y-4">
            <div>
              <label htmlFor="user-name" className="block text-sm font-medium text-gray-700 mb-2">
                Full Name
              </label>
              <input
                id="user-name"
                type="text"
                value={userName}
                onChange={(e) => setUserName(e.target.value)}
                placeholder="Enter full name..."
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 sm:text-sm"
                disabled={createUserMutation.isLoading}
              />
            </div>

            <div>
              <label htmlFor="user-email" className="block text-sm font-medium text-gray-700 mb-2">
                Email Address
              </label>
              <input
                id="user-email"
                type="email"
                value={userEmail}
                onChange={(e) => setUserEmail(e.target.value)}
                placeholder="Enter email address..."
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 sm:text-sm"
                disabled={createUserMutation.isLoading}
              />
            </div>

            <div>
              <label htmlFor="user-company" className="block text-sm font-medium text-gray-700 mb-2">
                Company
              </label>
              <select
                id="user-company"
                value={selectedCompanyId || ''}
                onChange={(e) => setSelectedCompanyId(e.target.value ? parseInt(e.target.value) : null)}
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 sm:text-sm"
                disabled={createUserMutation.isLoading}
              >
                <option value="">Select a company...</option>
                {companies.map((company) => (
                  <option key={company.id} value={company.id}>
                    {company.name}
                  </option>
                ))}
              </select>
            </div>

            <button
              type="submit"
              disabled={createUserMutation.isLoading || !userName.trim() || !userEmail.trim() || !selectedCompanyId}
              className={clsx(
                'w-full inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm transition-colors duration-200',
                createUserMutation.isLoading || !userName.trim() || !userEmail.trim() || !selectedCompanyId
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-green-600 text-white hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500'
              )}
            >
              {createUserMutation.isLoading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Creating...
                </>
              ) : (
                <>
                  <PlusIcon className="h-4 w-4 mr-2" />
                  Create User
                </>
              )}
            </button>

            {createUserMutation.isError && (
              <div className="flex items-center text-sm text-red-600">
                <ExclamationTriangleIcon className="h-4 w-4 mr-1" />
                Failed to create user. Please try again.
              </div>
            )}

            {createUserMutation.isSuccess && (
              <div className="flex items-center text-sm text-green-600">
                <CheckIcon className="h-4 w-4 mr-1" />
                User created successfully!
              </div>
            )}
          </form>
        </div>
      </div>

      {/* Existing Companies and Users Overview */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">Existing Companies</h3>
        
        {companies.length === 0 ? (
          <p className="text-gray-500 text-center py-8">No companies created yet.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {companies.map((company: Company) => (
              <div key={company.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
                <div className="flex items-center mb-2">
                  <div className={clsx(
                    'inline-flex h-8 w-8 items-center justify-center rounded-full text-sm font-medium text-white mr-3',
                    stringToColor(company.name)
                  )}>
                    {getInitials(company.name)}
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">{company.name}</h4>
                    <p className="text-sm text-gray-500">ID: {company.id}</p>
                  </div>
                </div>
                <p className="text-xs text-gray-400">
                  Created: {formatDate(company.created_at)}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminTab;