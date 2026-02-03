"""
Widgets Package
FOSSEE Scientific Analytics UI
"""

from .header import Header
from .sidebar import Sidebar
from .main_content import MainContent, ScreenPlaceholder
from .csv_upload import CSVUpload, DropZone, SummaryCard, StatusBadge
from .kpi_cards import KPICard, KPIGrid, SummaryKPIs
from .summary_screen import SummaryScreen, FileInfoCard
from .data_table import (
    EquipmentTableModel,
    EquipmentTableView,
    DataTableCard,
    EquipmentDataTable,
)
from .dataset_history import (
    DatasetHistory,
    HistoryItem,
    Sparkline,
)

__all__ = [
    "Header",
    "Sidebar", 
    "MainContent",
    "ScreenPlaceholder",
    "CSVUpload",
    "DropZone",
    "SummaryCard",
    "StatusBadge",
    "KPICard",
    "KPIGrid",
    "SummaryKPIs",
    "SummaryScreen",
    "FileInfoCard",
    "EquipmentTableModel",
    "EquipmentTableView",
    "DataTableCard",
    "EquipmentDataTable",
    "DatasetHistory",
    "HistoryItem",
    "Sparkline",
]
