/**
 * Authentication Service
 * CHEM•VIZ - Chemical Equipment Parameter Visualizer
 *
 * Handles user authentication, token storage, and auth state management.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
const TOKEN_KEY = 'chemviz_auth_token';
const USER_KEY = 'chemviz_user';

/**
 * API error class
 */
export class AuthError extends Error {
  constructor(message, status = null) {
    super(message);
    this.name = 'AuthError';
    this.status = status;
  }
}

/**
 * Auth state change listeners
 */
const listeners = new Set();

/**
 * Current auth state
 */
let currentUser = null;
let currentToken = null;

/**
 * Initialize auth state from localStorage
 */
function initAuthState() {
  try {
    currentToken = localStorage.getItem(TOKEN_KEY);
    const userJson = localStorage.getItem(USER_KEY);
    if (userJson) {
      currentUser = JSON.parse(userJson);
    }
  } catch (e) {
    console.error('Failed to restore auth state:', e);
    clearAuthState();
  }
}

/**
 * Clear auth state
 */
function clearAuthState() {
  currentToken = null;
  currentUser = null;
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

/**
 * Save auth state to localStorage
 */
function saveAuthState(token, user) {
  currentToken = token;
  currentUser = user;
  if (token) {
    localStorage.setItem(TOKEN_KEY, token);
  }
  if (user) {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  }
}

/**
 * Notify all listeners of auth state change
 */
function notifyListeners() {
  listeners.forEach(listener => {
    try {
      listener({ user: currentUser, token: currentToken });
    } catch (e) {
      console.error('Auth listener error:', e);
    }
  });
}

/**
 * Make an authenticated API request
 */
async function authRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  
  if (currentToken) {
    headers['Authorization'] = `Token ${currentToken}`;
  }
  
  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new AuthError(
        data.error || data.detail || `HTTP ${response.status}`,
        response.status
      );
    }
    
    return data;
  } catch (error) {
    if (error instanceof AuthError) throw error;
    throw new AuthError(error.message || 'Network error', 0);
  }
}

// Initialize on module load
initAuthState();

/**
 * Authentication Service API
 */
export const authService = {
  /**
   * Login with username and password
   * @param {string} username
   * @param {string} password
   * @returns {Promise<{token: string, user_id: number, username: string}>}
   */
  async login(username, password) {
    const data = await authRequest('/auth/login/', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
    
    saveAuthState(data.token, {
      id: data.user_id,
      username: data.username,
    });
    notifyListeners();
    
    return data;
  },
  
  /**
   * Register a new user
   * @param {string} username
   * @param {string} password
   * @param {string} [email]
   * @returns {Promise<{token: string, user_id: number, username: string}>}
   */
  async register(username, password, email = '') {
    const data = await authRequest('/auth/register/', {
      method: 'POST',
      body: JSON.stringify({ username, password, email }),
    });
    
    saveAuthState(data.token, {
      id: data.user_id,
      username: data.username,
    });
    notifyListeners();
    
    return data;
  },
  
  /**
   * Logout current user
   */
  async logout() {
    try {
      await authRequest('/auth/logout/', {
        method: 'POST',
      });
    } catch (e) {
      // Ignore logout errors, still clear local state
      console.warn('Logout API error:', e);
    }
    
    clearAuthState();
    notifyListeners();
  },
  
  /**
   * Get current user info from server
   * @returns {Promise<object>}
   */
  async getUser() {
    return authRequest('/auth/user/');
  },
  
  /**
   * Verify if current token is still valid
   * @returns {Promise<boolean>}
   */
  async verifyToken() {
    if (!currentToken) return false;
    
    try {
      await this.getUser();
      return true;
    } catch (e) {
      if (e.status === 401) {
        clearAuthState();
        notifyListeners();
      }
      return false;
    }
  },
  
  /**
   * Check if user is authenticated
   * @returns {boolean}
   */
  isAuthenticated() {
    return !!currentToken;
  },
  
  /**
   * Get current user
   * @returns {object|null}
   */
  getCurrentUser() {
    return currentUser;
  },
  
  /**
   * Get current token
   * @returns {string|null}
   */
  getToken() {
    return currentToken;
  },
  
  /**
   * Subscribe to auth state changes
   * @param {function} listener
   * @returns {function} Unsubscribe function
   */
  subscribe(listener) {
    listeners.add(listener);
    return () => listeners.delete(listener);
  },
};

export default authService;
