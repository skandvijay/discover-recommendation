import React from 'react';
import clsx from 'clsx';
import { MagnifyingGlassIcon, SparklesIcon, Cog6ToothIcon } from '@heroicons/react/24/outline';

interface Tab {
  id: 'search' | 'discover' | 'admin';
  name: string;
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>;
  description: string;
}

interface TabNavigationProps {
  activeTab: 'search' | 'discover' | 'admin';
  onTabChange: (tab: 'search' | 'discover' | 'admin') => void;
  disabled?: boolean;
}

const tabs: Tab[] = [
  {
    id: 'search',
    name: 'Search',
    icon: MagnifyingGlassIcon,
    description: 'Query and generate documents',
  },
  {
    id: 'discover',
    name: 'Discover',
    icon: SparklesIcon,
    description: 'Explore recommendations',
  },
  {
    id: 'admin',
    name: 'Admin',
    icon: Cog6ToothIcon,
    description: 'Manage companies and users',
  },
];

const TabNavigation: React.FC<TabNavigationProps> = ({
  activeTab,
  onTabChange,
  disabled = false,
}) => {
  return (
    <div className="border-b border-gray-200 bg-white">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8" aria-label="Tabs">
        <div className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const isActive = activeTab === tab.id;
            const Icon = tab.icon;
            
            return (
              <button
                key={tab.id}
                onClick={() => !disabled && onTabChange(tab.id)}
                disabled={disabled}
                className={clsx(
                  'group inline-flex items-center py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200',
                  isActive
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
                  disabled && 'cursor-not-allowed opacity-50'
                )}
                aria-current={isActive ? 'page' : undefined}
              >
                <Icon
                  className={clsx(
                    'mr-2 h-5 w-5',
                    isActive
                      ? 'text-indigo-500'
                      : 'text-gray-400 group-hover:text-gray-500'
                  )}
                  aria-hidden="true"
                />
                <span className="font-medium">{tab.name}</span>
                <span className="ml-2 text-xs text-gray-400 hidden sm:inline">
                  {tab.description}
                </span>
              </button>
            );
          })}
        </div>
      </nav>
    </div>
  );
};

export default TabNavigation;