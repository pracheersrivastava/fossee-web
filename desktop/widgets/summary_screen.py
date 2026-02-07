"""
Summary Screen Widget
FOSSEE Scientific Analytics UI

Post-upload summary display matching React SummaryScreen.
Shows file info, KPI cards, and action buttons.

UPDATED: Now fetches summary from backend API.
"""

from typing import Optional, Dict, Any

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QSizePolicy, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, pyqtSlot

from core.tokens import (
    SPACE_SM, SPACE_MD, SPACE_LG, SPACE_XL,
    COLOR_SUCCESS
)
from widgets.kpi_cards import SummaryKPIs
from core.api_client import api_client, APIError


class SummaryFetchWorker(QThread):
    """Background worker for fetching summary data from backend."""
    
    fetch_success = pyqtSignal(dict)
    fetch_error = pyqtSignal(str)
    
    def __init__(self, dataset_id: str):
        super().__init__()
        self.dataset_id = dataset_id
    
    def run(self):
        """Fetch summary data from backend."""
        try:
            result = api_client.get_summary(self.dataset_id)
            self.fetch_success.emit(result)
        except APIError as e:
            self.fetch_error.emit(str(e.message))
        except Exception as e:
            self.fetch_error.emit(f"Failed to load summary: {str(e)}")


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
            font-size: 24px;
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
    
    UPDATED: Now fetches summary from backend API.
    """
    
    # Signals for navigation
    viewChartsClicked = pyqtSignal()
    exportClicked = pyqtSignal()
    uploadNewClicked = pyqtSignal()
    summaryLoaded = pyqtSignal(dict)
    summaryError = pyqtSignal(str)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("summaryScreen")
        self._data: Dict[str, Any] = {}
        self._dataset_id: Optional[str] = None
        self._fetch_worker: Optional[SummaryFetchWorker] = None
        self._setup_ui()
    
    def _setup_ui(self):
        """Initialize the summary screen UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_LG, SPACE_LG, SPACE_LG, SPACE_LG)
        layout.setSpacing(SPACE_LG)
        
        # Page header - H1: 24px/600 per design.md
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("Data Summary")
        title.setProperty("class", "h1")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: 600;
            color: #1E2A38;
            padding-bottom: 8px;
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        layout.addWidget(header)
        
        # Loading label - Academic Blue per design.md
        self._loading_label = QLabel("Loading summary...")
        self._loading_label.setAlignment(Qt.AlignCenter)
        self._loading_label.setStyleSheet("color: #2F80ED; font-size: 16px; padding: 40px;")
        self._loading_label.setVisible(False)
        layout.addWidget(self._loading_label)
        
        # Error label
        self._error_label = QLabel()
        self._error_label.setAlignment(Qt.AlignCenter)
        self._error_label.setStyleSheet("color: #DC2626; font-size: 14px; padding: 20px;")
        self._error_label.setVisible(False)
        layout.addWidget(self._error_label)
        
        # Content container
        self._content = QWidget()
        content_layout = QVBoxLayout(self._content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(SPACE_LG)
        
        # File info card
        self._file_info = FileInfoCard()
        content_layout.addWidget(self._file_info)
        
        # KPIs section - H2: 18px/500 per design.md
        kpi_section = QWidget()
        kpi_layout = QVBoxLayout(kpi_section)
        kpi_layout.setContentsMargins(0, 0, 0, 0)
        kpi_layout.setSpacing(SPACE_MD)
        
        kpi_title = QLabel("Key Metrics")
        kpi_title.setStyleSheet("""
            font-size: 18px;
            font-weight: 500;
            color: #1E2A38;
            padding-bottom: 8px;
        """)
        kpi_layout.addWidget(kpi_title)
        
        self._kpis = SummaryKPIs()
        kpi_layout.addWidget(self._kpis)
        
        content_layout.addWidget(kpi_section)
        
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
        
        export_btn = QPushButton("Export PDF")
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
        
        content_layout.addWidget(actions)
        
        # Spacer
        content_layout.addStretch()
        
        layout.addWidget(self._content)
    
    def load_from_backend(self, dataset_id: str, file_info: Dict[str, Any] = None):
        """Load summary data from backend for the given dataset."""
        if not dataset_id:
            self._show_error("No dataset ID provided")
            return
        
        self._dataset_id = dataset_id
        
        # Store file info for display
        if file_info:
            self._file_info.set_data(file_info)
        
        # Show loading state
        self._loading_label.setVisible(True)
        self._error_label.setVisible(False)
        self._content.setVisible(bool(file_info))  # Show file info while loading KPIs
        QApplication.processEvents()
        
        # Fetch from backend
        self._fetch_worker = SummaryFetchWorker(dataset_id)
        self._fetch_worker.fetch_success.connect(self._on_fetch_success)
        self._fetch_worker.fetch_error.connect(self._on_fetch_error)
        self._fetch_worker.start()
    
    @pyqtSlot(dict)
    def _on_fetch_success(self, data: Dict[str, Any]):
        """Handle successful summary fetch."""
        self._loading_label.setVisible(False)
        self._content.setVisible(True)
        
        # Update KPIs with backend data (handle None values)
        self._kpis.set_data({
            'totalEquipment': data.get('total_equipment') or 0,
            'avgFlowrate': data.get('average_flowrate') or 0.0,
            'avgTemperature': data.get('average_temperature') or 0.0,
            'dominantType': data.get('dominant_equipment_type') or '—',
        })
        
        self.summaryLoaded.emit(data)
    
    @pyqtSlot(str)
    def _on_fetch_error(self, error_message: str):
        """Handle fetch error."""
        self._loading_label.setVisible(False)
        self._content.setVisible(True)  # Still show content with default values
        self._show_error(error_message)
        self.summaryError.emit(error_message)
    
    def _show_error(self, message: str):
        """Display error message."""
        self._error_label.setText(f"⚠ {message}")
        self._error_label.setVisible(True)
    
    def get_dataset_id(self) -> Optional[str]:
        """Get the current dataset ID."""
        return self._dataset_id
    
    def set_data(self, data: Dict[str, Any]):
        """
        Update summary screen with uploaded data.
        
        For backward compatibility - prefer load_from_backend.
        
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
