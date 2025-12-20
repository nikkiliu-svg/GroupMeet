/**
 * Main App component.
 */
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './hooks/useAuth';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { LoadingSpinner } from './components/common/LoadingSpinner';
import { LoginButton } from './components/auth/LoginButton';
import { StudentDashboard } from './components/dashboard/StudentDashboard';
import { AdminDashboard } from './components/dashboard/AdminDashboard';
import { FeedbackForm } from './components/forms/FeedbackForm';

const LoginPage: React.FC = () => {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        backgroundColor: '#f5f5f5',
      }}
    >
      <div style={{ textAlign: 'center', padding: '40px', backgroundColor: 'white', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
        <h1 style={{ color: '#01256E', marginBottom: '10px' }}>GroupMeet</h1>
        <p style={{ marginBottom: '30px', color: '#666' }}>Penn Study Group Matching Platform</p>
        <LoginButton />
      </div>
    </div>
  );
};

const App: React.FC = () => {
  const { authStatus, loading } = useAuth();

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <LoadingSpinner message="Loading..." />
      </div>
    );
  }

  return (
    <Router>
      <Routes>
        <Route
          path="/login"
          element={authStatus.authenticated ? <Navigate to="/dashboard" replace /> : <LoginPage />}
        />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <StudentDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admin"
          element={
            <ProtectedRoute>
              {authStatus.is_admin ? <AdminDashboard /> : <Navigate to="/dashboard" replace />}
            </ProtectedRoute>
          }
        />
        <Route
          path="/feedback"
          element={
            <ProtectedRoute>
              <FeedbackForm />
            </ProtectedRoute>
          }
        />
        <Route path="/" element={<Navigate to={authStatus.authenticated ? '/dashboard' : '/login'} replace />} />
      </Routes>
    </Router>
  );
};

export default App;

