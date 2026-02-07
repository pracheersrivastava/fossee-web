/**
 * Header Component
 * CHEM•VIZ - Chemical Equipment Parameter Visualizer
 * 
 * Persistent header with app title, subtitle, and user authentication.
 * Height: 56px, Background: Deep Indigo (#1E2A38)
 */

import React, { useState, useEffect, useCallback } from 'react';
import { authService } from '../../services/authService';
import { AuthModal } from '../Auth';
import './Header.css';

export function Header() {
  const [user, setUser] = useState(authService.getCurrentUser());
  const [showAuthModal, setShowAuthModal] = useState(false);

  // Subscribe to auth state changes
  useEffect(() => {
    const unsubscribe = authService.subscribe(({ user }) => {
      setUser(user);
    });
    return unsubscribe;
  }, []);

  // Handle login click
  const handleLoginClick = useCallback(() => {
    setShowAuthModal(true);
  }, []);

  // Handle auth success
  const handleAuthSuccess = useCallback((userInfo) => {
    // Auth state is already updated by authService
    setShowAuthModal(false);
  }, []);

  // Handle logout
  const handleLogout = useCallback(async () => {
    await authService.logout();
  }, []);

  return (
    <>
      <header className="header">
        <div className="header__brand">
          <span className="header__logo">⬡</span>
          <h1 className="header__title">CHEM•VIZ</h1>
          <span className="header__subtitle">Chemical Equipment Parameter Visualizer</span>
        </div>
        
        <div className="header__actions">
          {user ? (
            <div className="header__user">
              <span className="header__user-icon">👤</span>
              <span className="header__username">{user.username}</span>
              <button
                type="button"
                className="header__logout-btn"
                onClick={handleLogout}
              >
                Logout
              </button>
            </div>
          ) : (
            <button
              type="button"
              className="header__login-btn"
              onClick={handleLoginClick}
            >
              Login
            </button>
          )}
        </div>
      </header>

      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        onSuccess={handleAuthSuccess}
      />
    </>
  );
}

export default Header;
