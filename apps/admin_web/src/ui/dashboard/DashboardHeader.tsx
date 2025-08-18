import React from 'react'
import { useAuth } from '../../features/auth/AuthProvider'

export const DashboardHeader: React.FC = () => {
  const { user, organization, logout, getUserRole } = useAuth()

  return (
    <header className="bg-white shadow">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              {organization ? organization.name : 'Living Twin'} Admin
            </h1>
            <div className="flex items-center space-x-4 text-sm text-gray-600">
              <span>Welcome, {user?.email}</span>
              {organization && (
                <>
                  <span>•</span>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    {getUserRole()}
                  </span>
                  {organization.adminPortalUrl && (
                    <>
                      <span>•</span>
                      <a
                        href={organization.adminPortalUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-500"
                      >
                        Organization Portal
                      </a>
                    </>
                  )}
                </>
              )}
            </div>
          </div>
          <div className="flex items-center space-x-3">
            {organization && (
              <div className="text-right text-sm">
                <div className="font-medium text-gray-900">{organization.name}</div>
                <div className="text-gray-500">
                  {organization.industry} • {organization.size}
                </div>
              </div>
            )}
            <button
              onClick={logout}
              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium"
            >
              Sign Out
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}
