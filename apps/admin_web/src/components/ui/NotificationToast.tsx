import React from 'react'
import { Notification, NotificationType } from '../../hooks/useNotification'
import { X, CheckCircle, AlertCircle, AlertTriangle, Info } from 'lucide-react'

interface NotificationToastProps {
  notification: Notification
  onRemove: (id: string) => void
}

const getIcon = (type: NotificationType) => {
  switch (type) {
    case 'success':
      return <CheckCircle className="h-5 w-5 text-green-400" />
    case 'error':
      return <AlertCircle className="h-5 w-5 text-red-400" />
    case 'warning':
      return <AlertTriangle className="h-5 w-5 text-yellow-400" />
    case 'info':
      return <Info className="h-5 w-5 text-blue-400" />
  }
}

const getBackgroundColor = (type: NotificationType) => {
  switch (type) {
    case 'success':
      return 'bg-green-50 border-green-200'
    case 'error':
      return 'bg-red-50 border-red-200'
    case 'warning':
      return 'bg-yellow-50 border-yellow-200'
    case 'info':
      return 'bg-blue-50 border-blue-200'
  }
}

export const NotificationToast: React.FC<NotificationToastProps> = ({ notification, onRemove }) => {
  return (
    <div className={`rounded-lg border p-4 ${getBackgroundColor(notification.type)} shadow-lg`}>
      <div className="flex items-start">
        <div className="flex-shrink-0">{getIcon(notification.type)}</div>
        <div className="ml-3 flex-1">
          <p className="text-sm font-medium text-gray-900">{notification.title}</p>
          <p className="mt-1 text-sm text-gray-600">{notification.message}</p>
        </div>
        <div className="ml-4 flex flex-shrink-0">
          <button
            onClick={() => onRemove(notification.id)}
            className="inline-flex rounded-md text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  )
}
