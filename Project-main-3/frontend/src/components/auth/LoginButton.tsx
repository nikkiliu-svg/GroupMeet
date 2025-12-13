/**
 * Login button component.
 */
import React from 'react';
import { useAuth } from '../../hooks/useAuth';

export const LoginButton: React.FC = () => {
  const { login } = useAuth();

  return (
    <button
      onClick={login}
      style={{
        padding: '12px 24px',
        backgroundColor: '#01256E',
        color: 'white',
        border: 'none',
        borderRadius: '4px',
        fontSize: '16px',
        cursor: 'pointer',
        fontWeight: 'bold'
      }}
    >
      Login with PennKey
    </button>
  );
};

