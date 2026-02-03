"""
Dataset Admin Configuration
"""

from django.contrib import admin
from .models import Dataset


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    """Admin configuration for Dataset model."""
    
    list_display = [
        'name',
        'original_filename',
        'row_count',
        'column_count',
        'file_size_display',
        'is_active',
        'processing_status',
        'uploaded_at',
    ]
    
    list_filter = [
        'is_active',
        'processing_status',
        'uploaded_at',
    ]
    
    search_fields = [
        'name',
        'original_filename',
    ]
    
    readonly_fields = [
        'id',
        'row_count',
        'column_count',
        'columns',
        'column_types',
        'file_size',
        'file_size_display',
        'data_preview',
        'uploaded_at',
        'updated_at',
        'processing_status',
        'processing_error',
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'original_filename', 'file', 'is_active')
        }),
        ('Dataset Metadata', {
            'fields': ('row_count', 'column_count', 'columns', 'column_types', 'file_size', 'file_size_display')
        }),
        ('Processing', {
            'fields': ('processing_status', 'processing_error')
        }),
        ('Data Preview', {
            'fields': ('data_preview',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('uploaded_at', 'updated_at')
        }),
    )
    
    ordering = ['-uploaded_at']
