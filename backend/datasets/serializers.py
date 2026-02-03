"""
Dataset Serializers - API serialization for dataset models
"""

from rest_framework import serializers
from .models import Dataset


# Required columns for chemical equipment datasets
REQUIRED_COLUMNS = [
    'Equipment Name',
    'Type',
    'Flowrate',
    'Pressure',
    'Temperature',
]


class DatasetListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing datasets (minimal data for performance)
    """
    file_size_display = serializers.ReadOnlyField()
    
    class Meta:
        model = Dataset
        fields = [
            'id',
            'name',
            'original_filename',
            'row_count',
            'column_count',
            'columns',
            'file_size',
            'file_size_display',
            'uploaded_at',
            'is_active',
            'processing_status',
        ]
        read_only_fields = fields


class DatasetDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed dataset view (includes data preview)
    """
    file_size_display = serializers.ReadOnlyField()
    
    class Meta:
        model = Dataset
        fields = [
            'id',
            'name',
            'original_filename',
            'row_count',
            'column_count',
            'columns',
            'column_types',
            'file_size',
            'file_size_display',
            'data_preview',
            'uploaded_at',
            'updated_at',
            'is_active',
            'processing_status',
            'processing_error',
        ]
        read_only_fields = fields


class DatasetDataSerializer(serializers.ModelSerializer):
    """
    Serializer for dataset with full data (for analysis)
    """
    file_size_display = serializers.ReadOnlyField()
    
    class Meta:
        model = Dataset
        fields = [
            'id',
            'name',
            'row_count',
            'column_count',
            'columns',
            'column_types',
            'data_json',
            'uploaded_at',
        ]
        read_only_fields = fields


class DatasetUploadSerializer(serializers.ModelSerializer):
    """
    Serializer for uploading new datasets
    """
    file = serializers.FileField(
        required=True,
        help_text="CSV file to upload"
    )
    name = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Optional display name (defaults to filename)"
    )
    
    class Meta:
        model = Dataset
        fields = ['file', 'name']

    def validate_file(self, value):
        """Validate the uploaded file."""
        # Check file extension
        if not value.name.lower().endswith('.csv'):
            raise serializers.ValidationError("Only CSV files are allowed.")
        
        # Check file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if value.size > max_size:
            raise serializers.ValidationError(
                f"File size ({value.size / 1024 / 1024:.1f}MB) exceeds maximum allowed size (10MB)."
            )
        
        return value

    def create(self, validated_data):
        """Create a new dataset from the uploaded file."""
        file = validated_data['file']
        name = validated_data.get('name') or file.name.rsplit('.', 1)[0]
        
        dataset = Dataset.objects.create(
            name=name,
            original_filename=file.name,
            file=file,
            processing_status='pending'
        )
        
        return dataset


class DatasetActivateSerializer(serializers.Serializer):
    """
    Serializer for activating a specific dataset
    """
    dataset_id = serializers.UUIDField(
        required=True,
        help_text="ID of the dataset to activate"
    )


class ColumnValidationSerializer(serializers.Serializer):
    """
    Serializer for column validation results
    """
    is_valid = serializers.BooleanField()
    required_columns = serializers.ListField(child=serializers.CharField())
    found_columns = serializers.ListField(child=serializers.CharField())
    missing_columns = serializers.ListField(child=serializers.CharField())
    extra_columns = serializers.ListField(child=serializers.CharField())


class CSVUploadResponseSerializer(serializers.Serializer):
    """
    Serializer for CSV upload response
    Returns: dataset_id, row_count, column_count, validation status
    """
    dataset_id = serializers.UUIDField(help_text="Unique identifier for the uploaded dataset")
    row_count = serializers.IntegerField(help_text="Number of rows in the dataset")
    column_count = serializers.IntegerField(help_text="Number of columns in the dataset")
    validation = ColumnValidationSerializer(help_text="Column validation results")
    message = serializers.CharField(help_text="Status message")
    name = serializers.CharField(help_text="Dataset name")
    uploaded_at = serializers.DateTimeField(help_text="Upload timestamp")


class CSVUploadSerializer(serializers.Serializer):
    """
    Serializer for CSV file upload at /api/upload/
    Validates file and required columns
    """
    file = serializers.FileField(
        required=True,
        help_text="CSV file containing chemical equipment parameters"
    )
    name = serializers.CharField(
        required=False,
        allow_blank=True,
        default='',
        help_text="Optional display name for the dataset"
    )

    def validate_file(self, value):
        """Validate the uploaded CSV file."""
        # Check file extension
        if not value.name.lower().endswith('.csv'):
            raise serializers.ValidationError("Only CSV files are allowed. Please upload a .csv file.")
        
        # Check file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if value.size > max_size:
            raise serializers.ValidationError(
                f"File size ({value.size / 1024 / 1024:.1f}MB) exceeds maximum allowed size (10MB)."
            )
        
        # Check file is not empty
        if value.size == 0:
            raise serializers.ValidationError("The uploaded file is empty.")
        
        return value


# =============================================================================
# PROMPT 4 — SUMMARY STATISTICS SERIALIZER
# =============================================================================

class SummaryStatisticsSerializer(serializers.Serializer):
    """
    Serializer for summary statistics response.
    GET /api/summary/<dataset_id>/
    """
    dataset_id = serializers.UUIDField(help_text="Dataset identifier")
    dataset_name = serializers.CharField(help_text="Dataset name")
    total_equipment = serializers.IntegerField(help_text="Total number of equipment entries")
    average_flowrate = serializers.FloatField(allow_null=True, help_text="Mean flowrate value")
    average_temperature = serializers.FloatField(allow_null=True, help_text="Mean temperature value")
    dominant_equipment_type = serializers.CharField(allow_null=True, help_text="Most common equipment type")


# =============================================================================
# PROMPT 5 — ANALYSIS SERIALIZERS (FOR CHARTS)
# =============================================================================

class ChartDataSerializer(serializers.Serializer):
    """Serializer for chart data (labels + data arrays)"""
    labels = serializers.ListField(child=serializers.CharField())
    data = serializers.ListField(child=serializers.FloatField())


class EquipmentTypeDistributionSerializer(serializers.Serializer):
    """Serializer for equipment type distribution (pie/bar chart)"""
    labels = serializers.ListField(child=serializers.CharField())
    data = serializers.ListField(child=serializers.IntegerField())
    backgroundColor = serializers.ListField(child=serializers.CharField())


class PressureBucketSerializer(serializers.Serializer):
    """Serializer for pressure distribution bucket"""
    min = serializers.FloatField()
    max = serializers.FloatField()
    count = serializers.IntegerField()


class PressureDistributionSerializer(serializers.Serializer):
    """Serializer for pressure distribution histogram"""
    labels = serializers.ListField(child=serializers.CharField())
    data = serializers.ListField(child=serializers.IntegerField())
    buckets = PressureBucketSerializer(many=True)


class AnalysisResponseSerializer(serializers.Serializer):
    """
    Serializer for analysis response.
    GET /api/analysis/<dataset_id>/
    """
    dataset_id = serializers.UUIDField(help_text="Dataset identifier")
    dataset_name = serializers.CharField(help_text="Dataset name")
    equipment_type_distribution = EquipmentTypeDistributionSerializer()
    temperature_by_equipment = ChartDataSerializer()
    pressure_distribution = PressureDistributionSerializer()


# =============================================================================
# PROMPT 6 — DATASET HISTORY SERIALIZER
# =============================================================================

class DatasetHistoryItemSerializer(serializers.Serializer):
    """Serializer for a single history item"""
    id = serializers.UUIDField(help_text="Dataset identifier")
    filename = serializers.CharField(help_text="Original filename")
    upload_time = serializers.DateTimeField(help_text="Upload timestamp")
    row_count = serializers.IntegerField(help_text="Number of rows")


class DatasetHistoryResponseSerializer(serializers.Serializer):
    """
    Serializer for dataset history response.
    GET /api/history/
    """
    count = serializers.IntegerField(help_text="Number of datasets returned")
    datasets = DatasetHistoryItemSerializer(many=True)

