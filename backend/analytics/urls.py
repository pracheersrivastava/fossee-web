"""
Analytics URL Configuration
"""

from django.urls import path
from . import views

urlpatterns = [
    # Root endpoint
    path('', views.analytics_root, name='analytics-root'),
    
    # Summary statistics
    path('summary/', views.summary, name='analytics-summary'),
    path('summary/<uuid:dataset_id>/', views.summary, name='analytics-summary-dataset'),
    
    # KPI metrics
    path('kpis/', views.kpis, name='analytics-kpis'),
    path('kpis/<uuid:dataset_id>/', views.kpis, name='analytics-kpis-dataset'),
    
    # Chart data
    path('charts/', views.charts, name='analytics-charts'),
    path('charts/<uuid:dataset_id>/', views.charts, name='analytics-charts-dataset'),
    path('charts/<uuid:dataset_id>/<str:chart_type>/', views.chart_by_type, name='analytics-chart-type'),
    
    # Column information
    path('columns/', views.columns_info, name='analytics-columns'),
    path('columns/<uuid:dataset_id>/', views.columns_info, name='analytics-columns-dataset'),
]
