/**
 * Admin dashboard component.
 */
import React from 'react';
import { useAuth } from '../../hooks/useAuth';

export const AdminDashboard: React.FC = () => {
  const { authStatus } = useAuth();

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
      <h1 style={{ color: '#01256E' }}>Admin Dashboard</h1>
      <p>Welcome, {authStatus.pennkey} (Admin)</p>
      <p>Admin features coming soon...</p>
    </div>
  );
};

