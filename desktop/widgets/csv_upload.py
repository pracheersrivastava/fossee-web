"""
CSV Upload Widget
FOSSEE Scientific Analytics UI

Upload zone that transforms into summary card after upload.
Follows design.md Section 5.2 exactly.

Visual hierarchy matches React implementation:
- Drag/drop zone with dashed border
- Hover state: border changes to Academic Blue
- Post-upload: Summary card with file info, stats, validation status

UPDATED: Now uploads to backend API instead of parsing locally.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QFileDialog, QSizePolicy, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

from core.tokens import (
    SPACE_XS, SPACE_SM, SPACE_MD, SPACE_LG, SPACE_XL,
    COLOR_SUCCESS, COLOR_WARNING, COLOR_ERROR
)
from core.api_client import api_client, APIError


class UploadWorker(QThread):
    """Background worker for uploading CSV to backend."""
    
    upload_success = pyqtSignal(dict)
    upload_error = pyqtSignal(str)
    
    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path
    
    def run(self):
        """Upload file to backend API."""
        try:
            result = api_client.upload_csv(self.file_path)
            self.upload_success.emit(result)
        except APIError as e:
            self.upload_error.emit(str(e.message))
        except Exception as e:
            self.upload_error.emit(f"Upload failed: {str(e)}")


def format_file_size(bytes_size: int) -> str:
    """Format file size for display."""
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.1f} KB"
    else:
        return f"{bytes_size / (1024 * 1024):.1f} MB"


class DropZone(QFrame):
    """
    Drag and drop zone for CSV files.
    
    Styling per design.md Section 5.2:
    - Border: 2px dashed #CBD5E1
    - Radius: 8px
    - Background: #F8FAFC
    - Hover: border → #2F80ED
    """
    
    file_dropped = pyqtSignal(str)  # Emits file path
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("uploadDropZone")
        self.setAcceptDrops(True)
        self.setMinimumHeight(200)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self._setup_ui()
    
    def _setup_ui(self):
        """Initialize the drop zone UI."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        layout.setSpacing(SPACE_MD)
        
        # Upload icon - centered in a container
        icon_label = QLabel("↑")
        icon_label.setObjectName("uploadIcon")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFixedSize(64, 64)  # Fixed size for centering
        layout.addWidget(icon_label, 0, Qt.AlignHCenter)
        
        # Main text
        text_label = QLabel("Drag and drop your CSV file here")
        text_label.setObjectName("uploadText")
        text_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(text_label)
        
        # Sub text
        subtext_label = QLabel("or click to browse")
        subtext_label.setObjectName("uploadSubtext")
        subtext_label.setProperty("class", "caption")
        subtext_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtext_label)
        
        # Store references for state updates
        self._text_label = text_label
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and urls[0].toLocalFile().endswith('.csv'):
                event.acceptProposedAction()
                self.setProperty("dragActive", True)
                self._update_style()
                self._text_label.setText("Drop your CSV file here")
                return
        event.ignore()
    
    def dragLeaveEvent(self, event):
        """Handle drag leave event."""
        self.setProperty("dragActive", False)
        self._update_style()
        self._text_label.setText("Drag and drop your CSV file here")
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop event."""
        self.setProperty("dragActive", False)
        self._update_style()
        self._text_label.setText("Drag and drop your CSV file here")
        
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.endswith('.csv'):
                self.file_dropped.emit(file_path)
                event.acceptProposedAction()
                return
        event.ignore()
    
    def mousePressEvent(self, event):
        """Handle click to open file dialog."""
        if event.button() == Qt.LeftButton:
            self._open_file_dialog()
    
    def keyPressEvent(self, event):
        """Handle keyboard interaction."""
        if event.key() in (Qt.Key_Return, Qt.Key_Space):
            self._open_file_dialog()
    
    def _open_file_dialog(self):
        """Open file picker dialog."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV File",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        if file_path:
            self.file_dropped.emit(file_path)
    
    def _update_style(self):
        """Force style update after property change."""
        self.style().unpolish(self)
        self.style().polish(self)


class StatusBadge(QLabel):
    """Status badge for validation status."""
    
    def __init__(self, status: str, parent=None):
        super().__init__(parent)
        self.set_status(status)
    
    def set_status(self, status: str):
        """Set the status and update styling."""
        labels = {
            'success': 'Valid',
            'warning': 'Partial Issues',
            'error': 'Invalid',
        }
        self.setText(labels.get(status, status))
        self.setObjectName(f"statusBadge_{status}")
        self.setProperty("status", status)
        
        # Force style update
        self.style().unpolish(self)
        self.style().polish(self)


class SummaryCard(QFrame):
    """
    Summary card displayed after successful upload.
    
    Shows:
    - File name and size
    - Row count and column count
    - Validation status badge
    - Issues list (if any)
    - Action to upload different file
    """
    
    clear_requested = pyqtSignal()
    
    def __init__(self, data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.setObjectName("summaryCard")
        self.setProperty("class", "card")
        self._data = data
        self._setup_ui()
    
    def _setup_ui(self):
        """Initialize the summary card UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_MD, SPACE_MD, SPACE_MD, SPACE_MD)
        layout.setSpacing(SPACE_MD)
        
        # Header row: file info + status badge
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(SPACE_MD)
        
        # File info
        file_info = QWidget()
        file_info_layout = QHBoxLayout(file_info)
        file_info_layout.setContentsMargins(0, 0, 0, 0)
        file_info_layout.setSpacing(SPACE_SM)
        
        # File icon
        icon_label = QLabel("📄")
        icon_label.setStyleSheet("font-size: 24px;")
        file_info_layout.addWidget(icon_label)
        
        # File details
        details = QWidget()
        details_layout = QVBoxLayout(details)
        details_layout.setContentsMargins(0, 0, 0, 0)
        details_layout.setSpacing(0)
        
        filename_label = QLabel(self._data['fileName'])
        filename_label.setObjectName("summaryFilename")
        filename_label.setProperty("class", "body")
        filename_label.setStyleSheet("font-weight: 500;")
        details_layout.addWidget(filename_label)
        
        filesize_label = QLabel(format_file_size(self._data['fileSize']))
        filesize_label.setProperty("class", "caption")
        details_layout.addWidget(filesize_label)
        
        file_info_layout.addWidget(details)
        header_layout.addWidget(file_info)
        
        header_layout.addStretch()
        
        # Status badge
        status_badge = StatusBadge(self._data['validationStatus'])
        header_layout.addWidget(status_badge)
        
        layout.addWidget(header)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #E5E7EB; max-height: 1px;")
        layout.addWidget(separator)
        
        # Stats row
        stats = QWidget()
        stats_layout = QHBoxLayout(stats)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(SPACE_XL)
        
        # Row count stat
        row_stat = self._create_stat(
            str(f"{self._data['rowCount']:,}"),
            "Rows"
        )
        stats_layout.addWidget(row_stat)
        
        # Column count stat
        col_stat = self._create_stat(
            str(self._data['columnCount']),
            "Columns"
        )
        stats_layout.addWidget(col_stat)
        
        stats_layout.addStretch()
        layout.addWidget(stats)
        
        # Issues (if any)
        if self._data['issues']:
            issues_frame = QFrame()
            issues_frame.setObjectName("issuesFrame")
            issues_layout = QVBoxLayout(issues_frame)
            issues_layout.setContentsMargins(SPACE_SM, SPACE_SM, SPACE_SM, SPACE_SM)
            issues_layout.setSpacing(SPACE_XS)
            
            for issue in self._data['issues']:
                issue_label = QLabel(issue)
                issue_label.setProperty("class", "caption")
                issue_label.setStyleSheet("color: #92400E;")
                issues_layout.addWidget(issue_label)
            
            layout.addWidget(issues_frame)
        
        # Separator before actions
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setStyleSheet("background-color: #E5E7EB; max-height: 1px;")
        layout.addWidget(separator2)
        
        # Actions
        actions = QWidget()
        actions_layout = QHBoxLayout(actions)
        actions_layout.setContentsMargins(0, SPACE_SM, 0, 0)
        actions_layout.setSpacing(SPACE_MD)
        
        clear_btn = QPushButton("Upload Different File")
        clear_btn.setProperty("class", "secondary")
        clear_btn.setCursor(Qt.PointingHandCursor)
        clear_btn.clicked.connect(self.clear_requested.emit)
        actions_layout.addWidget(clear_btn)
        
        actions_layout.addStretch()
        layout.addWidget(actions)
    
    def _create_stat(self, value: str, label: str) -> QWidget:
        """Create a stat display widget."""
        stat = QWidget()
        stat_layout = QVBoxLayout(stat)
        stat_layout.setContentsMargins(0, 0, 0, 0)
        stat_layout.setSpacing(0)
        
        value_label = QLabel(value)
        value_label.setObjectName("statValue")
        stat_layout.addWidget(value_label)
        
        label_label = QLabel(label)
        label_label.setProperty("class", "caption")
        stat_layout.addWidget(label_label)
        
        return stat


class CSVUpload(QWidget):
    """
    CSV Upload Component.
    
    Combines DropZone and SummaryCard with state management.
    Matches React implementation visual hierarchy.
    
    UPDATED: Now uploads to backend API instead of parsing locally.
    """
    
    upload_complete = pyqtSignal(dict)  # Emits backend response with dataset_id
    upload_cleared = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._upload_data: Optional[Dict[str, Any]] = None
        self._upload_worker: Optional[UploadWorker] = None
        self._setup_ui()
    
    def _setup_ui(self):
        """Initialize the component UI."""
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(SPACE_MD)
        
        # Create drop zone (initial state)
        self._drop_zone = DropZone()
        self._drop_zone.file_dropped.connect(self._handle_file)
        self._layout.addWidget(self._drop_zone)
        
        # Loading label (hidden by default) - Academic Blue per design.md
        self._loading_label = QLabel("Uploading to server...")
        self._loading_label.setAlignment(Qt.AlignCenter)
        self._loading_label.setStyleSheet("color: #2F80ED; font-weight: 500; font-size: 14px;")
        self._loading_label.setVisible(False)
        self._layout.addWidget(self._loading_label)
        
        # Error label (hidden by default)
        self._error_label = QLabel()
        self._error_label.setObjectName("uploadError")
        self._error_label.setVisible(False)
        self._layout.addWidget(self._error_label)
        
        # Format hint
        self._format_hint = QLabel("Supported format: CSV (comma-separated values)")
        self._format_hint.setProperty("class", "caption")
        self._format_hint.setAlignment(Qt.AlignCenter)
        self._format_hint.setStyleSheet("color: #6B7280;")
        self._layout.addWidget(self._format_hint)
        
        # Summary card (created on upload)
        self._summary_card: Optional[SummaryCard] = None
    
    def _handle_file(self, file_path: str):
        """Handle file selection - upload to backend."""
        # Validate file extension
        if not file_path.lower().endswith('.csv'):
            self._show_error("Please upload a CSV file")
            return
        
        # Check file exists
        if not os.path.exists(file_path):
            self._show_error("File not found")
            return
        
        # Check backend connectivity
        if not api_client.health_check():
            self._show_error("Cannot connect to server. Please ensure backend is running.")
            return
        
        # Show loading state
        self._hide_error()
        self._drop_zone.setVisible(False)
        self._loading_label.setVisible(True)
        self._format_hint.setVisible(False)
        QApplication.processEvents()
        
        # Store file path for summary card
        self._current_file_path = file_path
        self._current_file_size = Path(file_path).stat().st_size
        
        # Start upload in background thread
        self._upload_worker = UploadWorker(file_path)
        self._upload_worker.upload_success.connect(self._on_upload_success)
        self._upload_worker.upload_error.connect(self._on_upload_error)
        self._upload_worker.start()
    
    @pyqtSlot(dict)
    def _on_upload_success(self, result: Dict[str, Any]):
        """Handle successful upload."""
        self._loading_label.setVisible(False)
        
        # Build display data from backend response
        validation = result.get('validation', {})
        issues = validation.get('missing_columns', [])
        
        display_data = {
            'fileName': result.get('name', Path(self._current_file_path).name),
            'fileSize': self._current_file_size,
            'rowCount': result.get('row_count', 0),
            'columnCount': result.get('column_count', 0),
            'validationStatus': 'success' if validation.get('is_valid', True) else 'warning',
            'issues': [f"Missing column: {col}" for col in issues] if issues else [],
            # Backend data
            'dataset_id': result.get('dataset_id'),
            'uploaded_at': result.get('uploaded_at'),
        }
        
        self._upload_data = display_data
        self._show_summary(display_data)
        self.upload_complete.emit(display_data)
    
    @pyqtSlot(str)
    def _on_upload_error(self, error_message: str):
        """Handle upload error."""
        self._loading_label.setVisible(False)
        self._drop_zone.setVisible(True)
        self._format_hint.setVisible(True)
        self._show_error(error_message)
    
    def _show_error(self, message: str):
        """Display error message. Error color from design.md."""
        self._error_label.setText(f"⚠ {message}")
        self._error_label.setStyleSheet("color: #DC2626; font-size: 14px;")
        self._error_label.setVisible(True)
    
    def _hide_error(self):
        """Hide error message."""
        self._error_label.setVisible(False)
    
    def _show_summary(self, data: Dict[str, Any]):
        """Show summary card, hide drop zone."""
        self._hide_error()
        
        # Hide drop zone and format hint
        self._drop_zone.setVisible(False)
        self._format_hint.setVisible(False)
        
        # Create and show summary card
        self._summary_card = SummaryCard(data)
        self._summary_card.clear_requested.connect(self._handle_clear)
        self._layout.insertWidget(0, self._summary_card)
    
    def _handle_clear(self):
        """Clear upload and return to drop zone."""
        self._upload_data = None
        
        # Remove summary card
        if self._summary_card:
            self._summary_card.deleteLater()
            self._summary_card = None
        
        # Show drop zone and format hint
        self._drop_zone.setVisible(True)
        self._format_hint.setVisible(True)
        self._hide_error()
        
        self.upload_cleared.emit()
    
    def get_upload_data(self) -> Optional[Dict[str, Any]]:
        """Get the current upload data including dataset_id."""
        return self._upload_data
    
    def get_dataset_id(self) -> Optional[str]:
        """Get the dataset_id from the last upload."""
        if self._upload_data:
            return self._upload_data.get('dataset_id')
        return None
    
    def clear(self):
        """Programmatically clear the upload."""
        self._handle_clear()
