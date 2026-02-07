"""
Custom Authentication Classes for CHEM•VIZ API

Provides lenient token authentication that treats invalid tokens as anonymous
requests instead of returning 401 errors. This allows:
- Anonymous uploads and analysis
- Graceful handling of expired/invalid tokens
"""

from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token


class LenientTokenAuthentication(TokenAuthentication):
    """
    Token authentication that treats invalid tokens as anonymous.
    
    Unlike standard TokenAuthentication which raises AuthenticationFailed
    for invalid tokens, this class returns None (anonymous) instead.
    
    This allows endpoints with AllowAny permission to work even when
    a stale/invalid token is sent in the Authorization header.
    """
    
    def authenticate(self, request):
        """
        Authenticate the request and return a (user, token) tuple or None.
        
        Returns None for:
        - No Authorization header
        - Invalid token format
        - Token not found in database
        - User not active
        
        This allows the request to proceed as anonymous.
        """
        auth_header = self.get_authorization_header(request)
        
        if not auth_header:
            return None
        
        try:
            auth = auth_header.decode('utf-8').split()
        except UnicodeDecodeError:
            return None
        
        if len(auth) != 2:
            return None
        
        keyword = auth[0]
        token_key = auth[1]
        
        # Check keyword (Token or Bearer)
        if keyword.lower() not in ('token', 'bearer'):
            return None
        
        try:
            token = Token.objects.select_related('user').get(key=token_key)
        except Token.DoesNotExist:
            # Invalid token - treat as anonymous
            return None
        
        if not token.user.is_active:
            # Inactive user - treat as anonymous
            return None
        
        return (token.user, token)
    
    def get_authorization_header(self, request):
        """Get the Authorization header value."""
        auth = request.META.get('HTTP_AUTHORIZATION', '')
        return auth.encode('utf-8') if auth else b''
