"""
API Client for CHEM•VIZ Desktop Application
Connects to Django REST backend - mirrors Web API calls

IMPORTANT: All requests must include Authorization header when authenticated.
Format: Authorization: Token <token>
"""

import logging
import requests
from typing import Optional, Dict, Any, List
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Backend configuration
API_BASE_URL = "http://localhost:8000/api"
REQUEST_TIMEOUT = 30  # seconds


class APIError(Exception):
    """Custom exception for API errors."""
    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ChemVizAPIClient:
    """
    API client for CHEM•VIZ backend.
    Mirrors the Web version's api.js functionality.
    
    CRITICAL: Token must be set after login and included in ALL authenticated requests.
    """
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url.rstrip('/')
        self._token: Optional[str] = None
        self.session = requests.Session()
        logger.info(f"API Client initialized with base URL: {self.base_url}")
    
    @property
    def token(self) -> Optional[str]:
        """Get the current auth token."""
        return self._token
    
    @token.setter
    def token(self, value: Optional[str]):
        """Set the auth token and log the change."""
        self._token = value
        if value:
            logger.info(f"Auth token SET (length: {len(value)})")
        else:
            logger.info("Auth token CLEARED")
    
    def _get_headers(self) -> Dict[str, str]:
        """
        Get request headers with auth token if available.
        MUST include Authorization header for authenticated requests.
        """
        headers = {
            'Accept': 'application/json',
        }
        if self._token:
            headers['Authorization'] = f'Token {self._token}'
            logger.debug(f"Authorization header attached: Token {self._token[:8]}...")
        else:
            logger.warning("No auth token available - request will be unauthenticated")
        return headers
    
    def _handle_response(self, response: requests.Response, endpoint: str = "") -> Dict[str, Any]:
        """Handle API response and errors with detailed logging."""
        try:
            data = response.json()
        except ValueError:
            data = {'error': 'Invalid JSON response'}
        
        # Log response details
        logger.debug(f"Response from {endpoint}: status={response.status_code}")
        
        if not response.ok:
            error_msg = data.get('error', data.get('detail', 'Unknown error'))
            
            # Specific handling for auth errors
            if response.status_code == 401:
                logger.error(f"AUTHENTICATION FAILED (401) on {endpoint}: {error_msg}")
                logger.error("Token may be invalid, expired, or missing")
            elif response.status_code == 403:
                logger.error(f"PERMISSION DENIED (403) on {endpoint}: {error_msg}")
                logger.error("User may not have access to this resource")
            else:
                logger.error(f"API Error ({response.status_code}) on {endpoint}: {error_msg}")
            
            raise APIError(error_msg, response.status_code)
        
        return data
    
    # =========================================================================
    # AUTHENTICATION
    # =========================================================================
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Login and get auth token.
        POST /api/auth/login/
        
        After successful login, token is automatically stored in the client.
        """
        logger.info(f"Attempting login for user: {username}")
        response = self.session.post(
            f'{self.base_url}/auth/login/',
            json={'username': username, 'password': password},
            headers={'Content-Type': 'application/json'},
            timeout=REQUEST_TIMEOUT
        )
        data = self._handle_response(response, '/auth/login/')
        
        # Store token immediately after successful login
        token = data.get('token')
        if token:
            self.token = token
            logger.info(f"Login successful for user: {username}")
        else:
            logger.error("Login response missing token!")
        
        return data
    
    def register(self, username: str, password: str, email: str = '') -> Dict[str, Any]:
        """
        Register new user.
        POST /api/auth/register/
        
        After successful registration, token is automatically stored in the client.
        """
        logger.info(f"Attempting registration for user: {username}")
        response = self.session.post(
            f'{self.base_url}/auth/register/',
            json={'username': username, 'password': password, 'email': email},
            headers={'Content-Type': 'application/json'},
            timeout=REQUEST_TIMEOUT
        )
        data = self._handle_response(response, '/auth/register/')
        
        # Store token immediately after successful registration
        token = data.get('token')
        if token:
            self.token = token
            logger.info(f"Registration successful for user: {username}")
        else:
            logger.error("Registration response missing token!")
        
        return data
    
    def logout(self, token: str = None) -> Dict[str, Any]:
        """
        Logout and invalidate token.
        POST /api/auth/logout/
        
        Args:
            token: Optional token to use for logout (uses stored token if not provided)
        """
        use_token = token or self.token
        headers = self._get_headers()
        if token:
            headers['Authorization'] = f'Token {token}'
        
        try:
            response = self.session.post(
                f'{self.base_url}/auth/logout/',
                headers=headers,
                timeout=REQUEST_TIMEOUT
            )
            if self._token == use_token:
                self.token = None
            return self._handle_response(response, '/auth/logout/')
        except (requests.RequestException, APIError):
            # Even if logout fails, clear local token
            if self.token == use_token:
                self.token = None
            return {'message': 'Logged out locally'}
    
    def get_user(self, token: str = None) -> Dict[str, Any]:
        """
        Get current user info.
        GET /api/auth/user/
        
        Args:
            token: Optional token to use (uses stored token if not provided)
        """
        headers = self._get_headers()
        if token:
            headers['Authorization'] = f'Token {token}'
        
        try:
            response = self.session.get(
                f'{self.base_url}/auth/user/',
                headers=headers,
                timeout=REQUEST_TIMEOUT
            )
            return self._handle_response(response, '/auth/user/')
        except (requests.RequestException, APIError) as e:
            logger.error(f"Failed to get user info: {e}")
            return {'error': str(e)}
    
    def set_token(self, token: Optional[str]):
        """
        Set auth token manually.
        Called after login/register to ensure token is stored.
        """
        self.token = token
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return self._token is not None
    
    # =========================================================================
    # DATASET UPLOAD
    # =========================================================================
    
    def upload_csv(self, file_path: str, name: str = None) -> Dict[str, Any]:
        """
        Upload CSV file to backend.
        POST /api/datasets/upload/
        
        Returns:
            {
                'dataset_id': str,
                'row_count': int,
                'column_count': int,
                'validation': {...},
                'message': str,
                'name': str,
                'uploaded_at': str
            }
        """
        path = Path(file_path)
        if not path.exists():
            raise APIError(f"File not found: {file_path}")
        
        if not path.suffix.lower() == '.csv':
            raise APIError("Only CSV files are supported")
        
        logger.info(f"Uploading CSV file: {path.name}")
        
        with open(path, 'rb') as f:
            files = {'file': (path.name, f, 'text/csv')}
            data = {}
            if name:
                data['name'] = name
            
            # CRITICAL: Always include auth headers if token is available
            headers = {}
            if self._token:
                headers['Authorization'] = f'Token {self._token}'
                logger.debug(f"Upload request includes auth token")
            else:
                logger.warning("Uploading without authentication - data will not be user-scoped!")
            
            response = self.session.post(
                f'{self.base_url}/datasets/upload/',
                files=files,
                data=data,
                headers=headers if headers else None,
                timeout=REQUEST_TIMEOUT
            )
        
        result = self._handle_response(response, '/datasets/upload/')
        logger.info(f"Upload successful, dataset_id: {result.get('dataset_id')}")
        return result
    
    # =========================================================================
    # DATASET RETRIEVAL
    # =========================================================================
    
    def get_dataset(self, dataset_id: str) -> Dict[str, Any]:
        """
        Get dataset details.
        GET /api/datasets/{id}/
        """
        logger.debug(f"Fetching dataset: {dataset_id}")
        response = self.session.get(
            f'{self.base_url}/datasets/{dataset_id}/',
            headers=self._get_headers(),
            timeout=REQUEST_TIMEOUT
        )
        return self._handle_response(response, f'/datasets/{dataset_id}/')
    
    def get_history(self) -> Dict[str, Any]:
        """
        Get upload history (last 5 datasets) FOR THE CURRENT USER.
        GET /api/history/
        
        IMPORTANT: Backend filters by request.user - token MUST be attached.
        
        Returns:
            {
                'count': int,
                'datasets': [
                    {'id': str, 'filename': str, 'upload_time': str, 'row_count': int},
                    ...
                ]
            }
        """
        logger.info("Fetching user history from backend")
        response = self.session.get(
            f'{self.base_url}/history/',
            headers=self._get_headers(),
            timeout=REQUEST_TIMEOUT
        )
        result = self._handle_response(response, '/history/')
        logger.info(f"History returned {result.get('count', 0)} datasets")
        return result
    
    def delete_dataset(self, dataset_id: str) -> Dict[str, Any]:
        """
        Delete a dataset.
        DELETE /api/datasets/{id}/
        """
        logger.info(f"Deleting dataset: {dataset_id}")
        response = self.session.delete(
            f'{self.base_url}/datasets/{dataset_id}/',
            headers=self._get_headers(),
            timeout=REQUEST_TIMEOUT
        )
        return self._handle_response(response, f'/datasets/{dataset_id}/')
    
    def claim_dataset(self, dataset_id: str) -> Dict[str, Any]:
        """
        Claim an anonymous dataset after login.
        POST /api/datasets/{id}/claim/
        
        This transfers ownership of an anonymous upload to the current user.
        Must be authenticated.
        
        Returns:
            {
                'message': str,
                'dataset_id': str,
                'dataset': {...}
            }
        """
        if not self._token:
            raise APIError("Must be authenticated to claim datasets")
        
        logger.info(f"Claiming dataset: {dataset_id}")
        response = self.session.post(
            f'{self.base_url}/datasets/{dataset_id}/claim/',
            headers=self._get_headers(),
            timeout=REQUEST_TIMEOUT
        )
        return self._handle_response(response, f'/datasets/{dataset_id}/claim/')
    
    # =========================================================================
    # ANALYTICS
    # =========================================================================
    
    def get_summary(self, dataset_id: str) -> Dict[str, Any]:
        """
        Get summary statistics for a dataset.
        GET /api/summary/{dataset_id}/
        
        IMPORTANT: Backend verifies ownership - token MUST be attached.
        
        Returns:
            {
                'dataset_id': str,
                'dataset_name': str,
                'total_equipment': int,
                'average_flowrate': float,
                'average_temperature': float,
                'dominant_equipment_type': str
            }
        """
        logger.info(f"Fetching summary for dataset: {dataset_id}")
        response = self.session.get(
            f'{self.base_url}/summary/{dataset_id}/',
            headers=self._get_headers(),
            timeout=REQUEST_TIMEOUT
        )
        return self._handle_response(response, f'/summary/{dataset_id}/')
    
    def get_analysis(self, dataset_id: str) -> Dict[str, Any]:
        """
        Get analysis data for charts.
        GET /api/analysis/{dataset_id}/
        
        IMPORTANT: Backend verifies ownership - token MUST be attached.
        
        Returns:
            {
                'dataset_id': str,
                'dataset_name': str,
                'equipment_type_distribution': {'labels': [], 'data': [], 'backgroundColor': []},
                'temperature_by_equipment': {'labels': [], 'data': []},
                'pressure_distribution': {'labels': [], 'data': [], 'buckets': []}
            }
        """
        logger.info(f"Fetching analysis for dataset: {dataset_id}")
        response = self.session.get(
            f'{self.base_url}/analysis/{dataset_id}/',
            headers=self._get_headers(),
            timeout=REQUEST_TIMEOUT
        )
        return self._handle_response(response, f'/analysis/{dataset_id}/')
    
    # =========================================================================
    # HEALTH CHECK
    # =========================================================================
    
    def health_check(self) -> bool:
        """Check if backend is reachable."""
        try:
            response = self.session.get(
                f'{self.base_url}/',
                timeout=5
            )
            return response.ok
        except requests.RequestException:
            return False


# Global client instance
api_client = ChemVizAPIClient()
