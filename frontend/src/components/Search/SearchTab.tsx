import React, { useState } from 'react';
import { PaperAirplaneIcon, DocumentTextIcon, ClockIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import { useSearch, useQueries } from '../../hooks/useApi';
import { Company, User, Query } from '../../types';
import { formatRelativeTime, truncateText } from '../../utils/format';
import clsx from 'clsx';

interface SearchTabProps {
  selectedCompany: Company | null;
  selectedUser: User | null;
}

const SearchTab: React.FC<SearchTabProps> = ({
  selectedCompany,
  selectedUser,
}) => {
  const [query, setQuery] = useState('');
  const [saveAsDocument, setSaveAsDocument] = useState(true);

  const searchMutation = useSearch();
  const { data: recentQueries = [], refetch: refetchQueries } = useQueries(
    selectedUser?.id,
    selectedCompany?.id
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!query.trim() || !selectedUser || !selectedCompany) {
      return;
    }

    try {
      await searchMutation.mutateAsync({
        query: query.trim(),
        user_id: selectedUser.id,
        company_id: selectedCompany.id,
        save_as_document: saveAsDocument,
      });
      
      setQuery('');
      refetchQueries();
    } catch (error) {
      console.error('Search error:', error);
    }
  };

  const isDisabled = !selectedUser || !selectedCompany || searchMutation.isLoading;

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-8">
      {/* Search Form */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="search-query" className="block text-sm font-medium text-gray-700 mb-2">
              Enter your query
            </label>
            <div className="relative">
              <textarea
                id="search-query"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask a question or describe what you're looking for..."
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm resize-none"
                rows={3}
                disabled={isDisabled}
              />
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <input
                id="save-document"
                name="save-document"
                type="checkbox"
                checked={saveAsDocument}
                onChange={(e) => setSaveAsDocument(e.target.checked)}
                className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                disabled={isDisabled}
              />
              <label htmlFor="save-document" className="ml-2 block text-sm text-gray-700">
                Save response as document
              </label>
            </div>

            <button
              type="submit"
              disabled={isDisabled || !query.trim()}
              className={clsx(
                'inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white transition-colors duration-200',
                isDisabled || !query.trim()
                  ? 'bg-gray-300 cursor-not-allowed'
                  : 'bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500'
              )}
            >
              {searchMutation.isLoading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Processing...
                </>
              ) : (
                <>
                  <PaperAirplaneIcon className="h-4 w-4 mr-2" />
                  Search
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Search Results */}
      {searchMutation.data && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 animate-fade-in">
          <div className="flex items-center mb-4">
            <DocumentTextIcon className="h-5 w-5 text-indigo-600 mr-2" />
            <h3 className="text-lg font-medium text-gray-900">Response</h3>
            <span className="ml-auto text-sm text-gray-500">
              Confidence: {Math.round(searchMutation.data.confidence * 100)}%
            </span>
          </div>
          
          <div className="prose max-w-none">
            <div className="bg-gray-50 rounded-lg p-4 mb-4">
              <p className="text-sm font-medium text-gray-700 mb-2">Query:</p>
              <p className="text-gray-900">{searchMutation.data.query}</p>
            </div>
            
            <div className="text-gray-900 whitespace-pre-wrap leading-relaxed">
              {searchMutation.data.answer}
            </div>
          </div>

          {searchMutation.data.sources.length > 0 && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <p className="text-sm font-medium text-gray-700 mb-2">Sources:</p>
              <div className="flex flex-wrap gap-2">
                {searchMutation.data.sources.map((source, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800"
                  >
                    {source}
                  </span>
                ))}
              </div>
            </div>
          )}

          {searchMutation.data.document_id && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="flex items-center text-sm text-green-600">
                <DocumentTextIcon className="h-4 w-4 mr-1" />
                Saved as document (ID: {searchMutation.data.document_id})
              </div>
            </div>
          )}
        </div>
      )}

      {/* Recent Queries */}
      {recentQueries.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center mb-4">
            <ClockIcon className="h-5 w-5 text-gray-600 mr-2" />
            <h3 className="text-lg font-medium text-gray-900">Recent Queries</h3>
          </div>
          
          <div className="space-y-3">
            {recentQueries.slice(0, 5).map((queryItem: Query) => (
              <div
                key={queryItem.id}
                className="flex items-start justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors duration-200"
              >
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-gray-900 line-clamp-2">
                    {truncateText(queryItem.query_text, 150)}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {formatRelativeTime(queryItem.created_at)}
                  </p>
                </div>
                <button
                  onClick={() => setQuery(queryItem.query_text)}
                  className="ml-3 text-xs text-indigo-600 hover:text-indigo-800 font-medium"
                >
                  Reuse
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* No User Selected State */}
      {(!selectedUser || !selectedCompany) && (
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <MagnifyingGlassIcon className="h-12 w-12 mx-auto" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Ready to Search</h3>
          <p className="text-gray-500">
            Select a company and user from the header to start searching.
          </p>
        </div>
      )}
    </div>
  );
};

export default SearchTab;