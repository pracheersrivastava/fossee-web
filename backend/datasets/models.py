"""
Dataset Models - Core data structures for chemical equipment datasets
"""

import os
import uuid
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator


def dataset_upload_path(instance, filename):
    """
    Generate upload path for dataset files.
    Files are stored as: media/datasets/YYYY/MM/<uuid>_<filename>
    """
    ext = filename.split('.')[-1]
    unique_filename = f"{uuid.uuid4().hex[:8]}_{filename}"
    return os.path.join('datasets', unique_filename)


class Dataset(models.Model):
    """
    Model representing an uploaded CSV dataset for chemical equipment parameters.
    
    Stores metadata about the uploaded file and parsed data statistics.
    Only the last MAX_DATASETS_HISTORY (default: 5) datasets are kept per user.
    
    User field is optional - anonymous uploads don't get persisted to history.
    """
    
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text="Unique identifier for the dataset"
    )
    
    # User who uploaded this dataset (optional for anonymous uploads)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='datasets',
        help_text="User who uploaded this dataset (null for anonymous)"
    )
    
    name = models.CharField(
        max_length=255,
        help_text="Display name for the dataset"
    )
    
    original_filename = models.CharField(
        max_length=255,
        help_text="Original uploaded filename"
    )
    
    file = models.FileField(
        upload_to=dataset_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['csv'])],
        help_text="The uploaded CSV file"
    )
    
    file_size = models.PositiveIntegerField(
        default=0,
        help_text="File size in bytes"
    )
    
    # Dataset metadata
    row_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of rows in the dataset"
    )
    
    column_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of columns in the dataset"
    )
    
    columns = models.JSONField(
        default=list,
        help_text="List of column names"
    )
    
    column_types = models.JSONField(
        default=dict,
        help_text="Dictionary mapping column names to their data types"
    )
    
    # Parsed data stored as JSON for quick access
    data_preview = models.JSONField(
        default=list,
        help_text="First 10 rows of data for preview"
    )
    
    data_json = models.JSONField(
        default=list,
        help_text="Complete dataset as JSON (for small datasets)"
    )
    
    # Timestamps
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the dataset was uploaded"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the dataset was last updated"
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this is the currently active dataset"
    )
    
    processing_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending',
        help_text="Current processing status"
    )
    
    processing_error = models.TextField(
        blank=True,
        null=True,
        help_text="Error message if processing failed"
    )
    
    # Track temporary/anonymous uploads
    is_temporary = models.BooleanField(
        default=False,
        help_text="Temporary upload that should be auto-deleted (anonymous users)"
    )

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Dataset'
        verbose_name_plural = 'Datasets'
        indexes = [
            models.Index(fields=['-uploaded_at']),
            models.Index(fields=['is_active']),
            models.Index(fields=['user', '-uploaded_at']),
        ]

    def __str__(self):
        return f"{self.name} ({self.row_count} rows, {self.column_count} cols)"

    def save(self, *args, **kwargs):
        """Override save to update file_size if file is present."""
        if self.file and hasattr(self.file, 'size'):
            self.file_size = self.file.size
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Override delete to also remove the file from storage."""
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super().delete(*args, **kwargs)

    @property
    def file_size_display(self):
        """Return human-readable file size."""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    @classmethod
    def get_active_dataset(cls):
        """Get the currently active dataset."""
        return cls.objects.filter(is_active=True).first()

    @classmethod
    def enforce_history_limit(cls, user=None):
        """
        Enforce the maximum number of datasets in history.
        Deletes oldest datasets beyond the limit.
        
        If user is specified, only enforces limit for that user's datasets.
        Also cleans up old temporary datasets.
        """
        max_history = getattr(settings, 'MAX_DATASETS_HISTORY', 5)
        
        if user:
            # User-scoped history limit
            datasets = cls.objects.filter(user=user).order_by('-uploaded_at')
            if datasets.count() > max_history:
                datasets_to_delete = datasets[max_history:]
                for dataset in datasets_to_delete:
                    dataset.delete()
        
        # Clean up old temporary datasets (older than 1 hour)
        from django.utils import timezone
        from datetime import timedelta
        cutoff = timezone.now() - timedelta(hours=1)
        cls.objects.filter(is_temporary=True, uploaded_at__lt=cutoff).delete()
