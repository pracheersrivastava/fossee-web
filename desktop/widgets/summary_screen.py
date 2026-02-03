"""
Summary Screen Widget
FOSSEE Scientific Analytics UI

Post-upload summary display matching React SummaryScreen.
Shows file info, KPI cards, and action buttons.
"""

from typing import Optional, Dict, Any

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal

from ..core.tokens import (
    SPACE_SM, SPACE_MD, SPACE_LG, SPACE_XL,
    COLOR_SUCCESS
)
from .kpi_cards import SummaryKPIs


class FileInfoCard(QFrame):
    """
    File information card showing upload summary.
    
    Displays:
    - Status badge (Validated / Issues Found)
    - Filename with icon
    - Row count, file size, columns
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("fileInfoCard")
        self.setProperty("class", "card")
        self._setup_ui()
    
    def _setup_ui(self):
        """Initialize the file info UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_MD, SPACE_MD, SPACE_MD, SPACE_MD)
        layout.setSpacing(SPACE_MD)
        
        # Header row (Status badge + filename)
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(SPACE_MD)
        
        # Status badge
        self._status_badge = QLabel("Validated")
        self._status_badge.setObjectName("validationStatus")
        self._status_badge.setProperty("status", "success")
        header_layout.addWidget(self._status_badge)
        
        header_layout.addStretch()
        layout.addWidget(header)
        
        # File info row
        file_row = QWidget()
        file_layout = QHBoxLayout(file_row)
        file_layout.setContentsMargins(0, 0, 0, 0)
        file_layout.setSpacing(SPACE_SM)
        
        file_icon = QLabel("📄")
        file_icon.setObjectName("fileIcon")
        file_layout.addWidget(file_icon)
        
        self._filename_label = QLabel("No file selected")
        self._filename_label.setObjectName("fileName")
        self._filename_label.setProperty("class", "body")
        file_layout.addWidget(self._filename_label)
        
        file_layout.addStretch()
        layout.addWidget(file_row)
        
        # Stats row
        stats_row = QWidget()
        stats_layout = QHBoxLayout(stats_row)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(SPACE_XL)
        
        # Rows stat
        rows_widget = self._create_stat("Rows", "0")
        self._rows_value = rows_widget.findChild(QLabel, "statValue")
        stats_layout.addWidget(rows_widget)
        
        # Size stat
        size_widget = self._create_stat("Size", "0 KB")
        self._size_value = size_widget.findChild(QLabel, "statValue")
        stats_layout.addWidget(size_widget)
        
        # Columns stat
        cols_widget = self._create_stat("Columns", "0")
        self._cols_value = cols_widget.findChild(QLabel, "statValue")
        stats_layout.addWidget(cols_widget)
        
        stats_layout.addStretch()
        layout.addWidget(stats_row)
    
    def _create_stat(self, label: str, value: str) -> QWidget:
        """Create a stat display widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACE_XS)
        
        value_label = QLabel(value)
        value_label.setObjectName("statValue")
        value_label.setStyleSheet("""
            font-size: 18px;
            font-weight: 600;
            color: #1E2A38;
        """)
        layout.addWidget(value_label)
        
        label_text = QLabel(label)
        label_text.setProperty("class", "caption")
        layout.addWidget(label_text)
        
        return widget
    
    def set_data(self, data: Dict[str, Any]):
        """Update file info with data."""
        filename = data.get('fileName', 'Unknown')
        rows = data.get('rowCount', 0)
        size = data.get('fileSize', 0)
        columns = data.get('columnCount', 0)
        has_issues = data.get('hasIssues', False)
        
        self._filename_label.setText(filename)
        self._rows_value.setText(f"{rows:,}")
        self._size_value.setText(self._format_size(size))
        self._cols_value.setText(str(columns))
        
        if has_issues:
            self._status_badge.setText("Issues Found")
            self._status_badge.setProperty("status", "warning")
        else:
            self._status_badge.setText("Validated")
            self._status_badge.setProperty("status", "success")
        
        # Re-apply styles after property change
        self._status_badge.style().unpolish(self._status_badge)
        self._status_badge.style().polish(self._status_badge)
    
    @staticmethod
    def _format_size(bytes_count: int) -> str:
        """Format byte count to human readable."""
        if bytes_count < 1024:
            return f"{bytes_count} B"
        elif bytes_count < 1024 * 1024:
            return f"{bytes_count / 1024:.1f} KB"
        else:
            return f"{bytes_count / (1024 * 1024):.1f} MB"


# Token constant not in tokens.py
SPACE_XS = 4


class SummaryScreen(QWidget):
    """
    Summary Screen widget.
    
    Displays post-upload summary with:
    - Page header
    - File info card
    - KPI metrics
    - Action buttons
    
    Matches React SummaryScreen component.
    """
    
    # Signals for navigation
    viewChartsClicked = pyqtSignal()
    exportClicked = pyqtSignal()
    uploadNewClicked = pyqtSignal()
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("summaryScreen")
        self._data: Dict[str, Any] = {}
        self._setup_ui()
    
    def _setup_ui(self):
        """Initialize the summary screen UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_LG, SPACE_LG, SPACE_LG, SPACE_LG)
        layout.setSpacing(SPACE_LG)
        
        # Page header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("Data Summary")
        title.setProperty("class", "h1")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: 600;
            color: #1E2A38;
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        layout.addWidget(header)
        
        # File info card
        self._file_info = FileInfoCard()
        layout.addWidget(self._file_info)
        
        # KPIs section
        kpi_section = QWidget()
        kpi_layout = QVBoxLayout(kpi_section)
        kpi_layout.setContentsMargins(0, 0, 0, 0)
        kpi_layout.setSpacing(SPACE_MD)
        
        kpi_title = QLabel("Key Metrics")
        kpi_title.setStyleSheet("""
            font-size: 18px;
            font-weight: 500;
            color: #1E2A38;
        """)
        kpi_layout.addWidget(kpi_title)
        
        self._kpis = SummaryKPIs()
        kpi_layout.addWidget(self._kpis)
        
        layout.addWidget(kpi_section)
        
        # Action buttons
        actions = QWidget()
        actions_layout = QHBoxLayout(actions)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(SPACE_MD)
        
        view_charts_btn = QPushButton("View Charts")
        view_charts_btn.setProperty("class", "primary")
        view_charts_btn.setMinimumWidth(140)
        view_charts_btn.clicked.connect(self.viewChartsClicked.emit)
        actions_layout.addWidget(view_charts_btn)
        
        export_btn = QPushButton("Export Data")
        export_btn.setProperty("class", "secondary")
        export_btn.setMinimumWidth(120)
        export_btn.clicked.connect(self.exportClicked.emit)
        actions_layout.addWidget(export_btn)
        
        actions_layout.addStretch()
        
        upload_new_btn = QPushButton("Upload New File")
        upload_new_btn.setProperty("class", "secondary")
        upload_new_btn.setMinimumWidth(140)
        upload_new_btn.clicked.connect(self.uploadNewClicked.emit)
        actions_layout.addWidget(upload_new_btn)
        
        layout.addWidget(actions)
        
        # Spacer
        layout.addStretch()
    
    def set_data(self, data: Dict[str, Any]):
        """
        Update summary screen with uploaded data.
        
        Expected data keys:
        - fileName: str
        - rowCount: int
        - fileSize: int (bytes)
        - columnCount: int
        - hasIssues: bool
        - totalEquipment: int
        - avgFlowrate: float
        - avgTemperature: float
        - dominantType: str
        """
        self._data = data
        
        # Update file info
        self._file_info.set_data(data)
        
        # Update KPIs
        self._kpis.set_data({
            'totalEquipment': data.get('totalEquipment', 0),
            'avgFlowrate': data.get('avgFlowrate', 0.0),
            'avgTemperature': data.get('avgTemperature', 0.0),
            'dominantType': data.get('dominantType', '—'),
        })
