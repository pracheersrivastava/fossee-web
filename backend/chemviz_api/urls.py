"""
URL configuration for CHEM•VIZ API project.

The `urlpatterns` list routes URLs to views.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response

from datasets.views import upload_csv, get_summary, get_analysis, get_history
from datasets.auth_views import login, logout, get_user, register


@api_view(['GET'])
def api_root(request):
    """
    API Root - Welcome endpoint with available endpoints list
    """
    return Response({
        'message': 'Welcome to CHEM•VIZ API - Chemical Equipment Parameter Visualizer',
        'version': '1.0.0',
        'endpoints': {
            'auth': {
                'login': 'POST /api/auth/login/',
                'logout': 'POST /api/auth/logout/',
                'register': 'POST /api/auth/register/',
                'user': 'GET /api/auth/user/',
            },
            'upload': 'POST /api/upload/',
            'summary': 'GET /api/summary/<dataset_id>/',
            'analysis': 'GET /api/analysis/<dataset_id>/',
            'history': 'GET /api/history/',
            'datasets': '/api/datasets/',
            'analytics': '/api/analytics/',
            'admin': '/admin/',
        },
        'required_columns': [
            'Equipment Name',
            'Type', 
            'Flowrate',
            'Pressure',
            'Temperature',
        ]
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api_root, name='api-root'),
    
    # Authentication endpoints
    path('api/auth/login/', login, name='auth-login'),
    path('api/auth/logout/', logout, name='auth-logout'),
    path('api/auth/register/', register, name='auth-register'),
    path('api/auth/user/', get_user, name='auth-user'),
    
    # Data endpoints
    path('api/upload/', upload_csv, name='csv-upload'),
    path('api/summary/<uuid:dataset_id>/', get_summary, name='dataset-summary'),
    path('api/analysis/<uuid:dataset_id>/', get_analysis, name='dataset-analysis'),
    path('api/history/', get_history, name='dataset-history'),
    path('api/datasets/', include('datasets.urls')),
    path('api/analytics/', include('analytics.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
