/**
 * Auth Modal Component
 * CHEM•VIZ - Chemical Equipment Parameter Visualizer
 *
 * Modal dialog for login and registration with tab switching.
 */

import React, { useState, useCallback } from 'react';
import { authService, AuthError } from '../../services/authService';
import './AuthModal.css';

/**
 * Auth Modal - Login/Register dialog
 *
 * @param {object} props
 * @param {boolean} props.isOpen - Whether modal is visible
 * @param {function} props.onClose - Close handler
 * @param {function} props.onSuccess - Success handler with user info
 */
export function AuthModal({ isOpen, onClose, onSuccess }) {
  const [activeTab, setActiveTab] = useState('login');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Login form state
  const [loginUsername, setLoginUsername] = useState('');
  const [loginPassword, setLoginPassword] = useState('');

  // Register form state
  const [registerUsername, setRegisterUsername] = useState('');
  const [registerEmail, setRegisterEmail] = useState('');
  const [registerPassword, setRegisterPassword] = useState('');
  const [registerConfirm, setRegisterConfirm] = useState('');

  /**
   * Handle login form submit
   */
  const handleLogin = useCallback(async (e) => {
    e.preventDefault();
    setError(null);

    if (!loginUsername.trim() || !loginPassword) {
      setError('Please enter both username and password.');
      return;
    }

    setLoading(true);

    try {
      const result = await authService.login(loginUsername.trim(), loginPassword);
      onSuccess?.({
        username: result.username,
        userId: result.user_id,
      });
      onClose?.();
    } catch (err) {
      if (err instanceof AuthError) {
        setError(err.message);
      } else {
        setError('Login failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  }, [loginUsername, loginPassword, onSuccess, onClose]);

  /**
   * Handle register form submit
   */
  const handleRegister = useCallback(async (e) => {
    e.preventDefault();
    setError(null);

    if (!registerUsername.trim()) {
      setError('Please enter a username.');
      return;
    }

    if (registerUsername.length < 3) {
      setError('Username must be at least 3 characters.');
      return;
    }

    if (!registerPassword) {
      setError('Please enter a password.');
      return;
    }

    if (registerPassword.length < 6) {
      setError('Password must be at least 6 characters.');
      return;
    }

    if (registerPassword !== registerConfirm) {
      setError('Passwords do not match.');
      return;
    }

    setLoading(true);

    try {
      const result = await authService.register(
        registerUsername.trim(),
        registerPassword,
        registerEmail.trim()
      );
      onSuccess?.({
        username: result.username,
        userId: result.user_id,
      });
      onClose?.();
    } catch (err) {
      if (err instanceof AuthError) {
        setError(err.message);
      } else {
        setError('Registration failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  }, [registerUsername, registerEmail, registerPassword, registerConfirm, onSuccess, onClose]);

  /**
   * Handle tab switch
   */
  const switchTab = useCallback((tab) => {
    setActiveTab(tab);
    setError(null);
  }, []);

  /**
   * Handle backdrop click
   */
  const handleBackdropClick = useCallback((e) => {
    if (e.target === e.currentTarget) {
      onClose?.();
    }
  }, [onClose]);

  if (!isOpen) return null;

  return (
    <div className="auth-modal__backdrop" onClick={handleBackdropClick}>
      <div className="auth-modal" role="dialog" aria-labelledby="auth-modal-title">
        {/* Header */}
        <div className="auth-modal__header">
          <div className="auth-modal__brand">
            <span className="auth-modal__logo">⬡</span>
            <h2 id="auth-modal-title" className="auth-modal__title">CHEM•VIZ</h2>
          </div>
          <p className="auth-modal__subtitle">Chemical Equipment Parameter Visualizer</p>
          <button 
            type="button"
            className="auth-modal__close"
            onClick={onClose}
            aria-label="Close"
          >
            ×
          </button>
        </div>

        {/* Tabs */}
        <div className="auth-modal__tabs" role="tablist">
          <button
            type="button"
            role="tab"
            aria-selected={activeTab === 'login'}
            className={`auth-modal__tab ${activeTab === 'login' ? 'auth-modal__tab--active' : ''}`}
            onClick={() => switchTab('login')}
          >
            Login
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={activeTab === 'register'}
            className={`auth-modal__tab ${activeTab === 'register' ? 'auth-modal__tab--active' : ''}`}
            onClick={() => switchTab('register')}
          >
            Register
          </button>
        </div>

        {/* Error message */}
        {error && (
          <div className="auth-modal__error" role="alert">
            {error}
          </div>
        )}

        {/* Login form */}
        {activeTab === 'login' && (
          <form className="auth-modal__form" onSubmit={handleLogin}>
            <div className="auth-modal__field">
              <label htmlFor="login-username">Username</label>
              <input
                id="login-username"
                type="text"
                value={loginUsername}
                onChange={(e) => setLoginUsername(e.target.value)}
                placeholder="Enter your username"
                autoComplete="username"
                disabled={loading}
              />
            </div>
            <div className="auth-modal__field">
              <label htmlFor="login-password">Password</label>
              <input
                id="login-password"
                type="password"
                value={loginPassword}
                onChange={(e) => setLoginPassword(e.target.value)}
                placeholder="Enter your password"
                autoComplete="current-password"
                disabled={loading}
              />
            </div>
            <button
              type="submit"
              className="auth-modal__submit btn btn--primary"
              disabled={loading}
            >
              {loading ? 'Logging in...' : 'Login'}
            </button>
          </form>
        )}

        {/* Register form */}
        {activeTab === 'register' && (
          <form className="auth-modal__form" onSubmit={handleRegister}>
            <div className="auth-modal__field">
              <label htmlFor="register-username">Username</label>
              <input
                id="register-username"
                type="text"
                value={registerUsername}
                onChange={(e) => setRegisterUsername(e.target.value)}
                placeholder="Choose a username"
                autoComplete="username"
                disabled={loading}
              />
            </div>
            <div className="auth-modal__field">
              <label htmlFor="register-email">Email (optional)</label>
              <input
                id="register-email"
                type="email"
                value={registerEmail}
                onChange={(e) => setRegisterEmail(e.target.value)}
                placeholder="your@email.com"
                autoComplete="email"
                disabled={loading}
              />
            </div>
            <div className="auth-modal__field">
              <label htmlFor="register-password">Password</label>
              <input
                id="register-password"
                type="password"
                value={registerPassword}
                onChange={(e) => setRegisterPassword(e.target.value)}
                placeholder="Choose a password (min 6 chars)"
                autoComplete="new-password"
                disabled={loading}
              />
            </div>
            <div className="auth-modal__field">
              <label htmlFor="register-confirm">Confirm Password</label>
              <input
                id="register-confirm"
                type="password"
                value={registerConfirm}
                onChange={(e) => setRegisterConfirm(e.target.value)}
                placeholder="Confirm your password"
                autoComplete="new-password"
                disabled={loading}
              />
            </div>
            <button
              type="submit"
              className="auth-modal__submit btn btn--primary"
              disabled={loading}
            >
              {loading ? 'Registering...' : 'Register'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}

export default AuthModal;
