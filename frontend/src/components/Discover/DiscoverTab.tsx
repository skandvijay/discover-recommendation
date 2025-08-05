import React from 'react';
import { 
  SparklesIcon, 
  ArrowPathIcon, 
  ExclamationTriangleIcon,
  LightBulbIcon,
  DocumentTextIcon 
} from '@heroicons/react/24/outline';
import { useRecommendations, useRefreshRecommendations } from '../../hooks/useApi';
import { Company, User, Recommendation } from '../../types';
import { formatRelativeTime, formatRelevanceScore, truncateText } from '../../utils/format';
import clsx from 'clsx';

interface DiscoverTabProps {
  selectedCompany: Company | null;
  selectedUser: User | null;
}

interface RecommendationCardProps {
  recommendation: Recommendation;
}

const RecommendationCard: React.FC<RecommendationCardProps> = ({ recommendation }) => {
  const relevanceScore = formatRelevanceScore(recommendation.relevance_score);
  
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow duration-200 animate-slide-up">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-medium text-gray-900 line-clamp-2 mb-2">
            {recommendation.title}
          </h3>
          <div className="flex items-center space-x-4 text-sm text-gray-500">
            <span className="flex items-center">
              <DocumentTextIcon className="h-4 w-4 mr-1" />
              {recommendation.source}
            </span>
            <span>•</span>
            <span>{formatRelativeTime(recommendation.created_at)}</span>
          </div>
        </div>
        <div className="flex items-center space-x-2 ml-4">
          <span className={clsx('text-sm font-medium', relevanceScore.colorClass)}>
            {relevanceScore.text}
          </span>
          <div className="h-2 w-16 bg-gray-200 rounded-full overflow-hidden">
            <div 
              className={clsx(
                'h-full rounded-full transition-all duration-300',
                recommendation.relevance_score >= 0.8 ? 'bg-green-500' :
                recommendation.relevance_score >= 0.6 ? 'bg-blue-500' :
                recommendation.relevance_score >= 0.4 ? 'bg-yellow-500' :
                recommendation.relevance_score >= 0.2 ? 'bg-orange-500' : 'bg-red-500'
              )}
              style={{ width: `${recommendation.relevance_score * 100}%` }}
            />
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="mb-4">
        <p className="text-gray-700 leading-relaxed">
          {truncateText(recommendation.content, 300)}
        </p>
      </div>

      {/* Footer */}
      <div className="flex items-start justify-between pt-4 border-t border-gray-100">
        <div className="flex items-start space-x-2 flex-1">
          <LightBulbIcon className="h-4 w-4 text-yellow-500 mt-0.5 flex-shrink-0" />
          <p className="text-sm text-gray-600 italic">
            {recommendation.explanation}
          </p>
        </div>
        <div className="ml-4 text-sm text-gray-500">
          {Math.round(recommendation.confidence * 100)}% confidence
        </div>
      </div>
    </div>
  );
};

const DiscoverTab: React.FC<DiscoverTabProps> = ({
  selectedCompany,
  selectedUser,
}) => {
  const { 
    data: recommendations = [], 
    isLoading, 
    error, 
    refetch 
  } = useRecommendations(selectedUser?.id, selectedCompany?.id);
  
  const refreshMutation = useRefreshRecommendations();

  const handleRefresh = async () => {
    if (!selectedUser || !selectedCompany) return;
    
    try {
      await refreshMutation.mutateAsync({
        user_id: selectedUser.id,
        company_id: selectedCompany.id,
      });
      refetch();
    } catch (error) {
      console.error('Refresh error:', error);
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="max-w-6xl mx-auto p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, index) => (
            <div key={index} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
              <div className="space-y-2 mb-4">
                <div className="h-3 bg-gray-200 rounded"></div>
                <div className="h-3 bg-gray-200 rounded w-5/6"></div>
                <div className="h-3 bg-gray-200 rounded w-4/6"></div>
              </div>
              <div className="h-3 bg-gray-200 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // No user selected state
  if (!selectedUser || !selectedCompany) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <SparklesIcon className="h-12 w-12 mx-auto" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Ready to Discover</h3>
          <p className="text-gray-500">
            Select a company and user from the header to see personalized recommendations.
          </p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="text-center py-12">
          <div className="text-red-400 mb-4">
            <ExclamationTriangleIcon className="h-12 w-12 mx-auto" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Something went wrong</h3>
          <p className="text-gray-500 mb-4">
            We couldn't load your recommendations. Please try again.
          </p>
          <button
            onClick={() => refetch()}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-indigo-700 bg-indigo-100 hover:bg-indigo-200"
          >
            <ArrowPathIcon className="h-4 w-4 mr-2" />
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Discover Recommendations
          </h2>
          <p className="text-gray-600">
            Personalized content based on your query history and interests
          </p>
        </div>
        
        <button
          onClick={handleRefresh}
          disabled={refreshMutation.isLoading}
          className={clsx(
            'inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm transition-colors duration-200',
            refreshMutation.isLoading
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-indigo-600 text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500'
          )}
        >
          {refreshMutation.isLoading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Refreshing...
            </>
          ) : (
            <>
              <ArrowPathIcon className="h-4 w-4 mr-2" />
              Refresh
            </>
          )}
        </button>
      </div>

      {/* Recommendations Grid */}
      {recommendations.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {recommendations.map((recommendation) => (
            <RecommendationCard 
              key={recommendation.id} 
              recommendation={recommendation} 
            />
          ))}
        </div>
      ) : (
        // No recommendations state
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <SparklesIcon className="h-12 w-12 mx-auto" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Recommendations Yet</h3>
          <p className="text-gray-500 mb-4">
            Start by making some searches to build your recommendation profile.
          </p>
          <div className="text-sm text-gray-400">
            Your recommendations will appear here based on your query history and interests.
          </div>
        </div>
      )}

      {/* Stats */}
      {recommendations.length > 0 && (
        <div className="mt-8 pt-6 border-t border-gray-200">
          <div className="flex items-center justify-center space-x-8 text-sm text-gray-500">
            <span>
              {recommendations.length} recommendation{recommendations.length !== 1 ? 's' : ''}
            </span>
            <span>•</span>
            <span>
              Updated {selectedUser?.name ? 'for ' + selectedUser.name : 'recently'}
            </span>
            <span>•</span>
            <span>
              Based on query patterns
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default DiscoverTab;