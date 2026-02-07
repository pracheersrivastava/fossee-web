"""
Authentication Views - Token-based authentication for CHEM•VIZ API
"""

from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Login endpoint - Returns authentication token.
    
    Endpoint: POST /api/auth/login/
    
    Request body:
    {
        "username": "your_username",
        "password": "your_password"
    }
    
    Returns:
    {
        "token": "your_auth_token",
        "user_id": 1,
        "username": "your_username"
    }
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Please provide both username and password'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=username, password=password)
    
    if user is None:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    if not user.is_active:
        return Response(
            {'error': 'User account is disabled'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Get or create token for the user
    token, created = Token.objects.get_or_create(user=user)
    
    return Response({
        'token': token.key,
        'user_id': user.id,
        'username': user.username,
        'message': 'Login successful'
    })


@api_view(['POST'])
@permission_classes([AllowAny])  # Allow even with invalid token
def logout(request):
    """
    Logout endpoint - Deletes authentication token.
    
    Endpoint: POST /api/auth/logout/
    
    Headers:
    Authorization: Token your_auth_token
    
    Returns:
    {
        "message": "Logout successful"
    }
    
    NOTE: Always returns success even if not logged in or token invalid.
    """
    try:
        if request.user and request.user.is_authenticated:
            # Delete the user's token
            request.user.auth_token.delete()
        return Response({'message': 'Logout successful'})
    except Exception:
        return Response({'message': 'Logout successful'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user(request):
    """
    Get current user info.
    
    Endpoint: GET /api/auth/user/
    
    Headers:
    Authorization: Token your_auth_token
    
    Returns:
    {
        "user_id": 1,
        "username": "your_username",
        "email": "user@example.com"
    }
    """
    user = request.user
    return Response({
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'is_staff': user.is_staff,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new user.
    
    Endpoint: POST /api/auth/register/
    
    Request body:
    {
        "username": "new_username",
        "password": "your_password",
        "email": "user@example.com" (optional)
    }
    
    Returns:
    {
        "token": "your_auth_token",
        "user_id": 1,
        "username": "new_username"
    }
    """
    from django.contrib.auth.models import User
    
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', '')
    
    if not username or not password:
        return Response(
            {'error': 'Please provide both username and password'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if User.objects.filter(username=username).exists():
        return Response(
            {'error': 'Username already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create user
    user = User.objects.create_user(
        username=username,
        password=password,
        email=email
    )
    
    # Create token
    token = Token.objects.create(user=user)
    
    return Response({
        'token': token.key,
        'user_id': user.id,
        'username': user.username,
        'message': 'User registered successfully'
    }, status=status.HTTP_201_CREATED)
