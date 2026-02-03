"""
Analytics Views - API endpoints for summary statistics and chart data
"""

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from datasets.models import Dataset
from .services import AnalyticsService


@api_view(['GET'])
def analytics_root(request):
    """
    Analytics API Root - Available analytics endpoints
    """
    return Response({
        'message': 'CHEM•VIZ Analytics API',
        'endpoints': {
            'summary': '/api/analytics/summary/',
            'summary_for_dataset': '/api/analytics/summary/<dataset_id>/',
            'charts': '/api/analytics/charts/',
            'charts_for_dataset': '/api/analytics/charts/<dataset_id>/',
            'chart_type': '/api/analytics/charts/<dataset_id>/<chart_type>/',
            'kpis': '/api/analytics/kpis/',
        }
    })


def _get_analytics_service(dataset_id=None):
    """
    Helper to get analytics service for a dataset.
    
    Args:
        dataset_id: Optional specific dataset ID, otherwise uses active dataset
        
    Returns:
        Tuple of (AnalyticsService, error_response)
        If error, AnalyticsService is None and error_response is the Response to return
    """
    if dataset_id:
        try:
            dataset = Dataset.objects.get(pk=dataset_id)
        except Dataset.DoesNotExist:
            return None, Response(
                {'error': 'Dataset not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    else:
        dataset = Dataset.get_active_dataset()
        if dataset is None:
            return None, Response(
                {'error': 'No active dataset. Please upload a CSV file first.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    if dataset.processing_status != 'completed':
        return None, Response(
            {'error': f'Dataset is not ready. Status: {dataset.processing_status}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not dataset.data_json:
        return None, Response(
            {'error': 'Dataset has no data'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    service = AnalyticsService(
        data=dataset.data_json,
        columns=dataset.columns,
        column_types=dataset.column_types
    )
    
    return service, None


@api_view(['GET'])
def summary(request, dataset_id=None):
    """
    Get summary statistics for a dataset.
    
    If dataset_id is not provided, uses the currently active dataset.
    
    Returns:
        - overview: Basic dataset info (rows, columns, missing values)
        - numeric_summary: Statistics for each numeric column
        - categorical_summary: Value counts for categorical columns
        - kpi_metrics: Key performance indicators for dashboard
    """
    service, error_response = _get_analytics_service(dataset_id)
    if error_response:
        return error_response
    
    try:
        summary_data = service.compute_summary_statistics()
        
        # Add dataset info
        if dataset_id:
            dataset = Dataset.objects.get(pk=dataset_id)
        else:
            dataset = Dataset.get_active_dataset()
        
        summary_data['dataset'] = {
            'id': str(dataset.id),
            'name': dataset.name,
            'uploaded_at': dataset.uploaded_at.isoformat(),
        }
        
        return Response(summary_data)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to compute summary: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def kpis(request, dataset_id=None):
    """
    Get KPI metrics for dashboard cards.
    
    Returns list of KPI objects with:
        - id: Unique identifier
        - label: Display label
        - value: Current value
        - unit: Unit of measurement
        - trend: Percent change
        - trend_direction: 'up', 'down', or 'stable'
    """
    service, error_response = _get_analytics_service(dataset_id)
    if error_response:
        return error_response
    
    try:
        summary_data = service.compute_summary_statistics()
        return Response({
            'kpis': summary_data.get('kpi_metrics', [])
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to compute KPIs: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def charts(request, dataset_id=None):
    """
    Get data for all available chart types.
    
    Returns data formatted for multiple chart types:
        - line: Time series or sequential data
        - bar: Categorical comparisons
        - pie: Distribution of categories
        - scatter: Correlation between two variables
        - histogram: Distribution of a single variable
        - heatmap: Correlation matrix
    """
    service, error_response = _get_analytics_service(dataset_id)
    if error_response:
        return error_response
    
    try:
        chart_data = service.get_all_charts()
        return Response(chart_data)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to generate chart data: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def chart_by_type(request, dataset_id, chart_type):
    """
    Get data for a specific chart type.
    
    Args:
        dataset_id: UUID of the dataset
        chart_type: One of 'line', 'bar', 'pie', 'scatter', 'histogram', 'heatmap'
        
    Query Parameters:
        x_column: Column to use for X axis (optional)
        y_column: Column to use for Y axis (optional)
        bins: Number of bins for histogram (optional, default: 20)
    """
    service, error_response = _get_analytics_service(dataset_id)
    if error_response:
        return error_response
    
    valid_types = ['line', 'bar', 'pie', 'scatter', 'histogram', 'heatmap']
    if chart_type not in valid_types:
        return Response(
            {'error': f'Invalid chart type. Must be one of: {", ".join(valid_types)}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        x_column = request.query_params.get('x_column')
        y_column = request.query_params.get('y_column')
        bins = int(request.query_params.get('bins', 20))
        
        chart_data = service.get_chart_data(
            chart_type=chart_type,
            x_column=x_column,
            y_column=y_column,
            bins=bins
        )
        
        return Response(chart_data)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to generate {chart_type} chart: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def columns_info(request, dataset_id=None):
    """
    Get information about available columns for chart configuration.
    
    Returns:
        - numeric_columns: Columns suitable for Y axis and scatter plots
        - categorical_columns: Columns suitable for X axis and pie charts
        - all_columns: All available columns
    """
    service, error_response = _get_analytics_service(dataset_id)
    if error_response:
        return error_response
    
    return Response({
        'numeric_columns': service.get_numeric_columns(),
        'categorical_columns': service.get_categorical_columns(),
        'all_columns': service.columns,
        'column_types': service.column_types,
    })
