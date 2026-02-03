"""
Dataset URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DatasetViewSet

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'', DatasetViewSet, basename='dataset')

urlpatterns = [
    path('', include(router.urls)),
]
