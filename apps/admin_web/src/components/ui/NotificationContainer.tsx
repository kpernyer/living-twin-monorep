import React from 'react'
import { useNotification } from '../../hooks/useNotification'
import { NotificationToast } from './NotificationToast'

export const NotificationContainer: React.FC = () => {
  const { notifications, removeNotification } = useNotification()

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 max-w-sm">
      {notifications.map((notification) => (
        <NotificationToast
          key={notification.id}
          notification={notification}
          onRemove={removeNotification}
        />
      ))}
    </div>
  )
}
