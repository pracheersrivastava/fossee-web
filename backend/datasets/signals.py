"""
Dataset Signals - Post-save and pre-delete signals for dataset management
"""

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.conf import settings
import os

from .models import Dataset


@receiver(post_save, sender=Dataset)
def enforce_dataset_limit(sender, instance, created, **kwargs):
    """
    After saving a dataset, enforce the maximum history limit.
    This ensures we never have more than MAX_DATASETS_HISTORY datasets.
    """
    if created:
        Dataset.enforce_history_limit()


@receiver(pre_delete, sender=Dataset)
def cleanup_dataset_file(sender, instance, **kwargs):
    """
    Before deleting a dataset, remove the associated file from storage.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            try:
                os.remove(instance.file.path)
            except OSError:
                pass  # File already removed or inaccessible
