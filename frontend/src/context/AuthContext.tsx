import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface AuthContextType {
  isAuthenticated: boolean;
  login: (token?: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);

  useEffect(() => {
    // Check if token exists on initial load (e.g., page refresh)
    const token = localStorage.getItem('omnicrew_token');
    if (token) {
      setIsAuthenticated(true);
    }
  }, []);

  const login = (token?: string) => {
    // Only set the token if it's passed in. AuthScreen handles setting it to localStorage.
    if (token) {
      localStorage.setItem('omnicrew_token', token);
    }
    setIsAuthenticated(true);
  };

  const logout = () => {
    // ONLY remove the token, keep the user record so they can log in again
    localStorage.removeItem('omnicrew_token');
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};