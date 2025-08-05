import React from 'react';
import { Fragment } from 'react';
import { Listbox, Transition } from '@headlessui/react';
import { ChevronUpDownIcon, CheckIcon, ArrowPathIcon } from '@heroicons/react/20/solid';
import { Company, User } from '../../types';
import { getInitials, stringToColor } from '../../utils/format';
import clsx from 'clsx';

interface HeaderProps {
  companies: Company[];
  users: User[];
  selectedCompany: Company | null;
  selectedUser: User | null;
  onCompanyChange: (company: Company) => void;
  onUserChange: (user: User) => void;
  onRefresh?: () => void;
  isLoading?: boolean;
}

const Header: React.FC<HeaderProps> = ({
  companies,
  users,
  selectedCompany,
  selectedUser,
  onCompanyChange,
  onUserChange,
  onRefresh,
  isLoading = false,
}) => {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo and Title */}
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <h1 className="text-xl font-semibold text-gray-900">
                Discover vNext
              </h1>
            </div>
            <div className="ml-4 text-sm text-gray-500">
              Recommendation Engine Testing
            </div>
          </div>

          {/* Company and User Selection */}
          <div className="flex items-center space-x-4">
            {/* Company Selector */}
            <div className="w-48">
              <Listbox value={selectedCompany} onChange={onCompanyChange} disabled={isLoading}>
                <div className="relative">
                  <Listbox.Button className="relative w-full cursor-default rounded-lg bg-white py-2 pl-3 pr-10 text-left shadow-md focus:outline-none focus-visible:border-indigo-500 focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-opacity-75 focus-visible:ring-offset-2 focus-visible:ring-offset-orange-300 sm:text-sm border border-gray-300">
                    <span className="block truncate">
                      {selectedCompany ? selectedCompany.name : 'Select Company'}
                    </span>
                    <span className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
                      <ChevronUpDownIcon
                        className="h-5 w-5 text-gray-400"
                        aria-hidden="true"
                      />
                    </span>
                  </Listbox.Button>
                  <Transition
                    as={Fragment}
                    leave="transition ease-in duration-100"
                    leaveFrom="opacity-100"
                    leaveTo="opacity-0"
                  >
                    <Listbox.Options className="absolute mt-1 max-h-60 w-full overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm z-50">
                      {companies.map((company) => (
                        <Listbox.Option
                          key={company.id}
                          className={({ active }) =>
                            clsx(
                              'relative cursor-default select-none py-2 pl-10 pr-4',
                              active ? 'bg-indigo-100 text-indigo-900' : 'text-gray-900'
                            )
                          }
                          value={company}
                        >
                          {({ selected }) => (
                            <>
                              <span
                                className={clsx(
                                  'block truncate',
                                  selected ? 'font-medium' : 'font-normal'
                                )}
                              >
                                {company.name}
                              </span>
                              {selected ? (
                                <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-indigo-600">
                                  <CheckIcon className="h-5 w-5" aria-hidden="true" />
                                </span>
                              ) : null}
                            </>
                          )}
                        </Listbox.Option>
                      ))}
                    </Listbox.Options>
                  </Transition>
                </div>
              </Listbox>
            </div>

            {/* User Selector */}
            <div className="w-64">
              <Listbox value={selectedUser} onChange={onUserChange} disabled={isLoading || !selectedCompany}>
                <div className="relative">
                  <Listbox.Button className="relative w-full cursor-default rounded-lg bg-white py-2 pl-3 pr-10 text-left shadow-md focus:outline-none focus-visible:border-indigo-500 focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-opacity-75 focus-visible:ring-offset-2 focus-visible:ring-offset-orange-300 sm:text-sm border border-gray-300">
                    <span className="flex items-center">
                      {selectedUser ? (
                        <>
                          <span className={clsx(
                            'inline-flex h-6 w-6 items-center justify-center rounded-full text-xs font-medium text-white mr-3',
                            stringToColor(selectedUser.name)
                          )}>
                            {getInitials(selectedUser.name)}
                          </span>
                          <span className="block truncate">
                            {selectedUser.name}
                          </span>
                        </>
                      ) : (
                        <span className="text-gray-500">Select User</span>
                      )}
                    </span>
                    <span className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
                      <ChevronUpDownIcon
                        className="h-5 w-5 text-gray-400"
                        aria-hidden="true"
                      />
                    </span>
                  </Listbox.Button>
                  <Transition
                    as={Fragment}
                    leave="transition ease-in duration-100"
                    leaveFrom="opacity-100"
                    leaveTo="opacity-0"
                  >
                    <Listbox.Options className="absolute mt-1 max-h-60 w-full overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm z-50">
                      {users.map((user) => (
                        <Listbox.Option
                          key={user.id}
                          className={({ active }) =>
                            clsx(
                              'relative cursor-default select-none py-2 pl-10 pr-4',
                              active ? 'bg-indigo-100 text-indigo-900' : 'text-gray-900'
                            )
                          }
                          value={user}
                        >
                          {({ selected }) => (
                            <>
                              <div className="flex items-center">
                                <span className={clsx(
                                  'inline-flex h-6 w-6 items-center justify-center rounded-full text-xs font-medium text-white mr-3',
                                  stringToColor(user.name)
                                )}>
                                  {getInitials(user.name)}
                                </span>
                                <span
                                  className={clsx(
                                    'block truncate',
                                    selected ? 'font-medium' : 'font-normal'
                                  )}
                                >
                                  {user.name}
                                </span>
                              </div>
                              {selected ? (
                                <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-indigo-600">
                                  <CheckIcon className="h-5 w-5" aria-hidden="true" />
                                </span>
                              ) : null}
                            </>
                          )}
                        </Listbox.Option>
                      ))}
                    </Listbox.Options>
                  </Transition>
                </div>
              </Listbox>
            </div>

            {/* Refresh Button */}
            {onRefresh && (
              <button
                onClick={onRefresh}
                className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                title="Refresh company and user data"
              >
                <ArrowPathIcon className="h-4 w-4" />
              </button>
            )}

            {/* Status Indicator */}
            {isLoading && (
              <div className="flex items-center text-sm text-gray-500">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-indigo-600 mr-2"></div>
                Loading...
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;