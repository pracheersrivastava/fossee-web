"""
CSV Upload Widget
FOSSEE Scientific Analytics UI

Upload zone that transforms into summary card after upload.
Follows design.md Section 5.2 exactly.

Visual hierarchy matches React implementation:
- Drag/drop zone with dashed border
- Hover state: border changes to Academic Blue
- Post-upload: Summary card with file info, stats, validation status
"""

import csv
import os
from pathlib import Path
from typing import Optional, Callable, List, Dict, Any

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QFileDialog, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QMimeData
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

from ..core.tokens import (
    SPACE_XS, SPACE_SM, SPACE_MD, SPACE_LG, SPACE_XL,
    COLOR_SUCCESS, COLOR_WARNING, COLOR_ERROR
)


def parse_csv(file_path: str) -> Dict[str, Any]:
    """
    Parse CSV file and extract metadata.
    
    Returns dict with:
    - fileName: str
    - fileSize: int (bytes)
    - rowCount: int
    - columnCount: int
    - headers: List[str]
    - validationStatus: 'success' | 'warning' | 'error'
    - issues: List[str]
    """
    file_path = Path(file_path)
    file_size = file_path.stat().st_size
    
    issues = []
    headers = []
    row_count = 0
    has_empty_cells = False
    
    try:
        with open(file_path, 'r', encoding='utf-8', newline='') as f:
            reader = csv.reader(f)
            
            # Read header
            try:
                headers = next(reader)
                headers = [h.strip() for h in headers]
            except StopIteration:
                issues.append('No headers found')
                return {
                    'fileName': file_path.name,
                    'fileSize': file_size,
                    'rowCount': 0,
                    'columnCount': 0,
                    'headers': [],
                    'validationStatus': 'error',
                    'issues': issues,
                }
            
            if len(headers) == 0:
                issues.append('No headers found')
            
            # Read data rows (sample first 5 for validation)
            sample_count = 0
            for row in reader:
                row_count += 1
                if sample_count < 5:
                    if any(cell.strip() == '' for cell in row):
                        has_empty_cells = True
                    sample_count += 1
            
            if row_count == 0:
                issues.append('No data rows found')
            
            if has_empty_cells:
                issues.append('Some cells contain empty values')
        
        # Determine validation status
        if len(issues) == 0:
            status = 'success'
        elif len(issues) == 1 and has_empty_cells:
            status = 'warning'
        else:
            status = 'error'
        
        return {
            'fileName': file_path.name,
            'fileSize': file_size,
            'rowCount': row_count,
            'columnCount': len(headers),
            'headers': headers,
            'validationStatus': status,
            'issues': issues,
        }
    
    except Exception as e:
        return {
            'fileName': file_path.name,
            'fileSize': file_size,
            'rowCount': 0,
            'columnCount': 0,
            'headers': [],
            'validationStatus': 'error',
            'issues': [f'Failed to parse CSV: {str(e)}'],
        }


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
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(SPACE_MD)
        
        # Upload icon
        icon_label = QLabel("↑")
        icon_label.setObjectName("uploadIcon")
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
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
    """
    
    upload_complete = pyqtSignal(dict)  # Emits parsed data
    upload_cleared = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._upload_data: Optional[Dict[str, Any]] = None
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
        """Handle uploaded file."""
        # Validate file extension
        if not file_path.lower().endswith('.csv'):
            self._show_error("Please upload a CSV file")
            return
        
        # Check file exists
        if not os.path.exists(file_path):
            self._show_error("File not found")
            return
        
        # Parse CSV
        try:
            data = parse_csv(file_path)
            self._upload_data = data
            self._show_summary(data)
            self.upload_complete.emit(data)
        except Exception as e:
            self._show_error(f"Failed to process file: {str(e)}")
    
    def _show_error(self, message: str):
        """Display error message."""
        self._error_label.setText(f"⚠ {message}")
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
        """Get the current upload data."""
        return self._upload_data
    
    def clear(self):
        """Programmatically clear the upload."""
        self._handle_clear()
