"""
Dataset Views - API endpoints for dataset management
"""

import pandas as pd
from io import StringIO
from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, parser_classes, action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Dataset
from .serializers import (
    DatasetListSerializer,
    DatasetDetailSerializer,
    DatasetDataSerializer,
    DatasetUploadSerializer,
    CSVUploadSerializer,
    REQUIRED_COLUMNS,
)


def validate_columns(df_columns):
    """
    Validate that all required columns are present in the dataframe.
    
    Args:
        df_columns: List of column names from the CSV
        
    Returns:
        Dictionary with validation results
    """
    found_columns = list(df_columns)
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in found_columns]
    extra_columns = [col for col in found_columns if col not in REQUIRED_COLUMNS]
    
    return {
        'is_valid': len(missing_columns) == 0,
        'required_columns': REQUIRED_COLUMNS,
        'found_columns': found_columns,
        'missing_columns': missing_columns,
        'extra_columns': extra_columns,
    }


def parse_csv_file(file_content):
    """
    Parse CSV content using Pandas.
    
    Args:
        file_content: String content of the CSV file
        
    Returns:
        Tuple of (DataFrame, columns, column_types)
    """
    df = pd.read_csv(StringIO(file_content))
    
    # Clean column names (strip whitespace)
    df.columns = df.columns.str.strip()
    
    columns = df.columns.tolist()
    column_types = {}
    
    for col in columns:
        dtype = str(df[col].dtype)
        if 'int' in dtype:
            column_types[col] = 'integer'
        elif 'float' in dtype:
            column_types[col] = 'float'
        elif 'datetime' in dtype:
            column_types[col] = 'datetime'
        elif 'bool' in dtype:
            column_types[col] = 'boolean'
        else:
            column_types[col] = 'string'
    
    return df, columns, column_types


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_csv(request):
    """
    Upload a CSV file with chemical equipment parameters.
    
    Endpoint: POST /api/upload/
    Accept: multipart/form-data
    
    Required columns:
    - Equipment Name
    - Type
    - Flowrate
    - Pressure
    - Temperature
    
    Returns:
    - dataset_id: UUID of the created dataset
    - row_count: Number of rows in the dataset
    - column_count: Number of columns
    - validation: Column validation status
    
    NOTE: If user is authenticated, dataset is saved to their history.
    If anonymous, dataset is marked as temporary (auto-deleted after 1 hour).
    """
    serializer = CSVUploadSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {
                'error': 'Invalid request',
                'details': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    uploaded_file = serializer.validated_data['file']
    dataset_name = serializer.validated_data.get('name') or uploaded_file.name.rsplit('.', 1)[0]
    
    try:
        # Read and parse CSV content
        uploaded_file.seek(0)
        content = uploaded_file.read().decode('utf-8')
        
        # Parse CSV using Pandas
        df, columns, column_types = parse_csv_file(content)
        
        # Validate required columns
        validation = validate_columns(columns)
        
        # Determine processing status based on validation
        if validation['is_valid']:
            processing_status = 'completed'
            message = 'CSV file uploaded and validated successfully'
        else:
            processing_status = 'completed'  # Still store the data
            missing = ', '.join(validation['missing_columns'])
            message = f'CSV uploaded with warnings: Missing required columns: {missing}'
        
        # Prepare data for storage
        df_clean = df.fillna('')
        data_preview = df_clean.head(10).to_dict(orient='records')
        data_json = df_clean.to_dict(orient='records')
        
        # Reset file pointer for storage
        uploaded_file.seek(0)
        
        # Determine user - check if authenticated
        user = None
        is_temporary = True
        if request.user and request.user.is_authenticated:
            user = request.user
            is_temporary = False
        
        # Create dataset record
        dataset = Dataset.objects.create(
            name=dataset_name,
            user=user,
            original_filename=uploaded_file.name,
            file=uploaded_file,
            file_size=uploaded_file.size,
            row_count=len(df),
            column_count=len(columns),
            columns=columns,
            column_types=column_types,
            data_preview=data_preview,
            data_json=data_json,
            processing_status=processing_status,
            is_active=True,
            is_temporary=is_temporary,
        )
        
        # Deactivate other datasets (for this user or globally if anonymous)
        if user:
            Dataset.objects.filter(user=user).exclude(pk=dataset.pk).update(is_active=False)
        else:
            Dataset.objects.filter(user__isnull=True).exclude(pk=dataset.pk).update(is_active=False)
        
        # Enforce history limit (per user)
        Dataset.enforce_history_limit(user=user)
        
        # Build response
        response_data = {
            'dataset_id': str(dataset.id),
            'row_count': dataset.row_count,
            'column_count': dataset.column_count,
            'validation': validation,
            'message': message,
            'name': dataset.name,
            'uploaded_at': dataset.uploaded_at.isoformat(),
            'is_authenticated': user is not None,
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    except pd.errors.EmptyDataError:
        return Response(
            {
                'error': 'CSV parsing error',
                'details': 'The CSV file is empty or contains no valid data.'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    except pd.errors.ParserError as e:
        return Response(
            {
                'error': 'CSV parsing error',
                'details': f'Failed to parse CSV file: {str(e)}'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    except UnicodeDecodeError:
        return Response(
            {
                'error': 'Encoding error',
                'details': 'File encoding not supported. Please upload a UTF-8 encoded CSV file.'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {
                'error': 'Upload failed',
                'details': str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# =============================================================================
# PROMPT 4 — SUMMARY STATISTICS API (KPIs)
# =============================================================================

@api_view(['GET'])
def get_summary(request, dataset_id):
    """
    Get summary statistics for a dataset.
    
    Endpoint: GET /api/summary/<dataset_id>/
    
    Returns:
    - total_equipment: Total number of equipment entries
    - average_flowrate: Mean flowrate value
    - average_temperature: Mean temperature value
    - dominant_equipment_type: Most common equipment type
    """
    try:
        dataset = Dataset.objects.get(pk=dataset_id)
    except Dataset.DoesNotExist:
        return Response(
            {'error': 'Dataset not found', 'dataset_id': str(dataset_id)},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if not dataset.data_json:
        return Response(
            {'error': 'Dataset has no data'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Load data into Pandas DataFrame
        df = pd.DataFrame(dataset.data_json)
        
        # Compute total equipment
        total_equipment = len(df)
        
        # Compute average flowrate
        average_flowrate = None
        if 'Flowrate' in df.columns:
            flowrate_series = pd.to_numeric(df['Flowrate'], errors='coerce')
            avg = flowrate_series.mean()
            average_flowrate = round(float(avg), 2) if pd.notna(avg) else None
        
        # Compute average temperature
        average_temperature = None
        if 'Temperature' in df.columns:
            temp_series = pd.to_numeric(df['Temperature'], errors='coerce')
            avg = temp_series.mean()
            average_temperature = round(float(avg), 2) if pd.notna(avg) else None
        
        # Compute dominant equipment type
        dominant_equipment_type = None
        if 'Type' in df.columns:
            type_counts = df['Type'].value_counts()
            if len(type_counts) > 0:
                dominant_equipment_type = str(type_counts.index[0])
        
        return Response({
            'dataset_id': str(dataset_id),
            'dataset_name': dataset.name,
            'total_equipment': total_equipment,
            'average_flowrate': average_flowrate,
            'average_temperature': average_temperature,
            'dominant_equipment_type': dominant_equipment_type,
        })
        
    except Exception as e:
        return Response(
            {'error': 'Failed to compute summary', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# =============================================================================
# PROMPT 5 — ANALYSIS API (FOR CHARTS)
# =============================================================================

@api_view(['GET'])
def get_analysis(request, dataset_id):
    """
    Get analysis data for charts.
    
    Endpoint: GET /api/analysis/<dataset_id>/
    
    Returns:
    1. equipment_type_distribution: For pie/bar charts
    2. temperature_by_equipment: For bar charts
    3. pressure_distribution: Bucketed histogram data
    
    Format: Clean JSON suitable for Chart.js and Matplotlib
    """
    try:
        dataset = Dataset.objects.get(pk=dataset_id)
    except Dataset.DoesNotExist:
        return Response(
            {'error': 'Dataset not found', 'dataset_id': str(dataset_id)},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if not dataset.data_json:
        return Response(
            {'error': 'Dataset has no data'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        df = pd.DataFrame(dataset.data_json)
        
        # 1. Equipment Type Distribution (for Pie/Bar charts)
        equipment_type_distribution = {'labels': [], 'data': [], 'backgroundColor': []}
        if 'Type' in df.columns:
            type_counts = df['Type'].value_counts()
            equipment_type_distribution['labels'] = type_counts.index.tolist()
            equipment_type_distribution['data'] = type_counts.values.tolist()
            # Generate colors for each type
            colors = [
                '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6',
                '#EC4899', '#06B6D4', '#84CC16', '#F97316', '#6366F1'
            ]
            equipment_type_distribution['backgroundColor'] = colors[:len(type_counts)]
        
        # 2. Temperature vs Equipment (for Bar charts)
        temperature_by_equipment = {'labels': [], 'data': []}
        if 'Equipment Name' in df.columns and 'Temperature' in df.columns:
            df['Temperature_numeric'] = pd.to_numeric(df['Temperature'], errors='coerce')
            temp_by_equip = df.groupby('Equipment Name')['Temperature_numeric'].mean()
            temperature_by_equipment['labels'] = temp_by_equip.index.tolist()
            temperature_by_equipment['data'] = [
                round(float(v), 2) if pd.notna(v) else 0 
                for v in temp_by_equip.values
            ]
        
        # 3. Pressure Distribution (bucketed histogram)
        pressure_distribution = {'labels': [], 'data': [], 'buckets': []}
        if 'Pressure' in df.columns:
            pressure_series = pd.to_numeric(df['Pressure'], errors='coerce').dropna()
            if len(pressure_series) > 0:
                # Create 5 buckets
                min_p, max_p = pressure_series.min(), pressure_series.max()
                if min_p == max_p:
                    # All same value
                    pressure_distribution['labels'] = [f'{min_p:.1f}']
                    pressure_distribution['data'] = [len(pressure_series)]
                    pressure_distribution['buckets'] = [{'min': min_p, 'max': max_p, 'count': len(pressure_series)}]
                else:
                    counts, bin_edges = pd.cut(pressure_series, bins=5, retbins=True)
                    bin_counts = counts.value_counts().sort_index()
                    
                    labels = []
                    data = []
                    buckets = []
                    for i, (interval, count) in enumerate(bin_counts.items()):
                        label = f'{interval.left:.1f}-{interval.right:.1f}'
                        labels.append(label)
                        data.append(int(count))
                        buckets.append({
                            'min': float(interval.left),
                            'max': float(interval.right),
                            'count': int(count)
                        })
                    
                    pressure_distribution['labels'] = labels
                    pressure_distribution['data'] = data
                    pressure_distribution['buckets'] = buckets
        
        return Response({
            'dataset_id': str(dataset_id),
            'dataset_name': dataset.name,
            'equipment_type_distribution': equipment_type_distribution,
            'temperature_by_equipment': temperature_by_equipment,
            'pressure_distribution': pressure_distribution,
        })
        
    except Exception as e:
        return Response(
            {'error': 'Failed to compute analysis', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# =============================================================================
# PROMPT 6 — DATASET HISTORY API
# =============================================================================

@api_view(['GET'])
def get_history(request):
    """
    Get dataset upload history.
    
    Endpoint: GET /api/history/
    
    Returns:
    - Last 5 datasets ordered by most recent first
    - Each entry: id, filename, upload_time, row_count
    
    NOTE: Only returns datasets for the authenticated user.
    Returns empty list for anonymous users.
    """
    # Check if user is authenticated
    if not request.user or not request.user.is_authenticated:
        return Response({
            'count': 0,
            'datasets': [],
            'message': 'Login to see your dataset history'
        })
    
    # Get user's datasets only
    datasets = Dataset.objects.filter(
        user=request.user,
        is_temporary=False
    ).order_by('-uploaded_at')[:5]
    
    history = []
    for ds in datasets:
        history.append({
            'id': str(ds.id),
            'filename': ds.original_filename,
            'upload_time': ds.uploaded_at.isoformat(),
            'row_count': ds.row_count,
        })
    
    return Response({
        'count': len(history),
        'datasets': history,
    })


class DatasetViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing chemical equipment datasets.
    
    Endpoints:
    - GET /api/datasets/ - List all datasets
    - POST /api/datasets/upload/ - Upload a new CSV file
    - GET /api/datasets/{id}/ - Get dataset details
    - GET /api/datasets/{id}/data/ - Get full dataset data
    - POST /api/datasets/{id}/activate/ - Set as active dataset
    - DELETE /api/datasets/{id}/ - Delete a dataset
    - GET /api/datasets/active/ - Get the currently active dataset
    """
    
    queryset = Dataset.objects.all()
    parser_classes = (MultiPartParser, FormParser)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return DatasetListSerializer
        elif self.action == 'upload':
            return DatasetUploadSerializer
        elif self.action == 'data':
            return DatasetDataSerializer
        return DatasetDetailSerializer

    def list(self, request):
        """
        List all datasets in upload history for the authenticated user.
        Returns the last N datasets based on MAX_DATASETS_HISTORY setting.
        
        For anonymous users, returns empty list.
        """
        max_history = getattr(settings, 'MAX_DATASETS_HISTORY', 5)
        
        # Check if user is authenticated
        if not request.user or not request.user.is_authenticated:
            return Response({
                'count': 0,
                'max_history': max_history,
                'datasets': [],
                'message': 'Login to see your dataset history'
            })
        
        # Get user's datasets only
        datasets = Dataset.objects.filter(
            user=request.user,
            is_temporary=False
        ).order_by('-uploaded_at')[:max_history]
        
        serializer = DatasetListSerializer(datasets, many=True)
        return Response({
            'count': len(serializer.data),
            'max_history': max_history,
            'datasets': serializer.data
        })

    def retrieve(self, request, pk=None):
        """Get detailed information about a specific dataset."""
        try:
            dataset = Dataset.objects.get(pk=pk)
            serializer = DatasetDetailSerializer(dataset)
            return Response(serializer.data)
        except Dataset.DoesNotExist:
            return Response(
                {'error': 'Dataset not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'], url_path='upload')
    def upload(self, request):
        """
        Upload a new CSV file and parse it.
        
        The file is parsed using pandas to extract:
        - Column names and types
        - Row count
        - Data preview (first 10 rows)
        - Full data as JSON
        
        If user is authenticated, saves to their history.
        If anonymous, marks as temporary (auto-deleted after 1 hour).
        """
        serializer = DatasetUploadSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Determine user - check if authenticated
            user = None
            is_temporary = True
            if request.user and request.user.is_authenticated:
                user = request.user
                is_temporary = False
            
            # Create the dataset record
            dataset = serializer.save(user=user, is_temporary=is_temporary)
            
            # Parse the CSV file
            self._parse_csv(dataset)
            
            # Set as active dataset (deactivate others for this user)
            if user:
                Dataset.objects.filter(user=user).exclude(pk=dataset.pk).update(is_active=False)
            else:
                Dataset.objects.filter(user__isnull=True).exclude(pk=dataset.pk).update(is_active=False)
            dataset.is_active = True
            dataset.save()
            
            # Enforce history limit
            Dataset.enforce_history_limit(user=user)
            
            # Return the created dataset with dataset_id for compatibility
            response_serializer = DatasetDetailSerializer(dataset)
            response_data = response_serializer.data
            # Add dataset_id alias for desktop/web compatibility
            response_data['dataset_id'] = str(dataset.id)
            return Response(
                response_data,
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            # If parsing fails, update the dataset status
            if 'dataset' in locals():
                dataset.processing_status = 'failed'
                dataset.processing_error = str(e)
                dataset.save()
            
            return Response(
                {'error': f'Failed to process CSV file: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    def _parse_csv(self, dataset):
        """
        Parse the uploaded CSV file using pandas.
        
        Updates the dataset with:
        - Column names and types
        - Row and column counts
        - Data preview and full data as JSON
        """
        dataset.processing_status = 'processing'
        dataset.save()
        
        try:
            # Read CSV with pandas
            dataset.file.seek(0)
            content = dataset.file.read().decode('utf-8')
            df = pd.read_csv(StringIO(content))
            
            # Clean column names
            df.columns = df.columns.str.strip()
            
            # Get column information
            columns = df.columns.tolist()
            column_types = {}
            
            for col in columns:
                dtype = str(df[col].dtype)
                if 'int' in dtype:
                    column_types[col] = 'integer'
                elif 'float' in dtype:
                    column_types[col] = 'float'
                elif 'datetime' in dtype:
                    column_types[col] = 'datetime'
                elif 'bool' in dtype:
                    column_types[col] = 'boolean'
                else:
                    column_types[col] = 'string'
            
            # Convert data to JSON-serializable format
            # Handle NaN values
            df_clean = df.fillna('')
            
            # Get preview (first 10 rows)
            data_preview = df_clean.head(10).to_dict(orient='records')
            
            # Get full data
            data_json = df_clean.to_dict(orient='records')
            
            # Update dataset
            dataset.columns = columns
            dataset.column_types = column_types
            dataset.row_count = len(df)
            dataset.column_count = len(columns)
            dataset.data_preview = data_preview
            dataset.data_json = data_json
            dataset.processing_status = 'completed'
            dataset.save()
            
        except Exception as e:
            dataset.processing_status = 'failed'
            dataset.processing_error = str(e)
            dataset.save()
            raise

    @action(detail=True, methods=['get'], url_path='data')
    def data(self, request, pk=None):
        """Get the full dataset data for analysis."""
        try:
            dataset = Dataset.objects.get(pk=pk)
            serializer = DatasetDataSerializer(dataset)
            return Response(serializer.data)
        except Dataset.DoesNotExist:
            return Response(
                {'error': 'Dataset not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'], url_path='activate')
    def activate(self, request, pk=None):
        """Set a specific dataset as the active dataset."""
        try:
            dataset = Dataset.objects.get(pk=pk)
            
            # Deactivate all other datasets
            Dataset.objects.exclude(pk=pk).update(is_active=False)
            
            # Activate this dataset
            dataset.is_active = True
            dataset.save()
            
            serializer = DatasetDetailSerializer(dataset)
            return Response({
                'message': f'Dataset "{dataset.name}" is now active',
                'dataset': serializer.data
            })
        except Dataset.DoesNotExist:
            return Response(
                {'error': 'Dataset not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'], url_path='active')
    def active(self, request):
        """Get the currently active dataset."""
        dataset = Dataset.get_active_dataset()
        
        if dataset is None:
            return Response(
                {'message': 'No active dataset. Please upload a CSV file.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = DatasetDetailSerializer(dataset)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        """Delete a specific dataset."""
        try:
            dataset = Dataset.objects.get(pk=pk)
            name = dataset.name
            dataset.delete()
            
            # If deleted dataset was active, activate the most recent one
            if Dataset.objects.exists():
                latest = Dataset.objects.order_by('-uploaded_at').first()
                latest.is_active = True
                latest.save()
            
            return Response({
                'message': f'Dataset "{name}" has been deleted'
            })
        except Dataset.DoesNotExist:
            return Response(
                {'error': 'Dataset not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'], url_path='claim')
    def claim(self, request, pk=None):
        """
        Claim an anonymous dataset after login.
        
        POST /api/datasets/{id}/claim/
        
        This allows a user who uploaded while anonymous to claim the dataset
        after logging in. The dataset must be anonymous (user=null) and
        marked as temporary.
        """
        # Must be authenticated to claim
        if not request.user or not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required to claim datasets'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            dataset = Dataset.objects.get(pk=pk)
            
            # Check if dataset is already owned
            if dataset.user is not None:
                if dataset.user == request.user:
                    return Response({
                        'message': 'Dataset already belongs to you',
                        'dataset_id': str(dataset.id)
                    })
                else:
                    return Response(
                        {'error': 'Dataset belongs to another user'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            # Claim the dataset
            dataset.user = request.user
            dataset.is_temporary = False
            dataset.save()
            
            # Enforce history limit for this user
            Dataset.enforce_history_limit(user=request.user)
            
            return Response({
                'message': 'Dataset claimed successfully',
                'dataset_id': str(dataset.id),
                'dataset': DatasetDetailSerializer(dataset).data
            })
            
        except Dataset.DoesNotExist:
            return Response(
                {'error': 'Dataset not found'},
                status=status.HTTP_404_NOT_FOUND
            )
