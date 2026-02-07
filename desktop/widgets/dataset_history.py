"""
Dataset History Widget
FOSSEE Scientific Analytics UI

Displays recent datasets in sidebar - matches Web implementation exactly.

Per design.md tokens:
- Deep Indigo (text): #1E2A38
- Slate Gray (secondary): #6B7280
- Academic Blue (active): #2F80ED
- Off-White (hover): #F8FAFC
- Success (reanalyze): #22C55E
- Error (clear): #DC2626
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtGui import QCursor

from core.api_client import api_client, APIError


class HistoryFetchWorker(QThread):
    """Background worker for fetching history from backend."""
    
    fetch_success = pyqtSignal(list)
    fetch_error = pyqtSignal(str)
    
    def run(self):
        """Fetch history from backend."""
        try:
            result = api_client.get_history()
            datasets = result.get('datasets', [])
            self.fetch_success.emit(datasets)
        except APIError as e:
            self.fetch_error.emit(str(e.message))
        except Exception as e:
            self.fetch_error.emit(f"Failed to load history: {str(e)}")


class HistoryItem(QFrame):
    """Single history item row."""
    
    clicked = pyqtSignal(str)
    reanalyze_clicked = pyqtSignal(str)
    compare_clicked = pyqtSignal(str)
    
    def __init__(self, dataset_id: str, filename: str, timestamp: datetime, 
                 row_count: int = None, is_selected: bool = False, parent=None):
        super().__init__(parent)
        self._id = dataset_id
        self._filename = filename
        self._timestamp = timestamp
        self._row_count = row_count
        self._is_selected = is_selected
        
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setFixedHeight(52)
        self._setup_ui()
        self._apply_style()
    
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 8, 8)
        layout.setSpacing(8)
        
        # Info column
        info = QWidget()
        info_layout = QVBoxLayout(info)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)
        
        # Filename - Deep Indigo per design.md
        name_label = QLabel(self._truncate(self._filename, 20))
        name_label.setToolTip(self._filename)
        name_label.setStyleSheet("""
            font-size: 13px;
            font-weight: 500;
            color: #1E2A38;
        """)
        info_layout.addWidget(name_label)
        
        # Meta row
        meta = QWidget()
        meta_layout = QHBoxLayout(meta)
        meta_layout.setContentsMargins(0, 0, 0, 0)
        meta_layout.setSpacing(4)
        
        # Slate Gray for meta text per design.md
        time_label = QLabel(self._format_time(self._timestamp))
        time_label.setStyleSheet("font-size: 11px; color: #6B7280;")
        meta_layout.addWidget(time_label)
        
        if self._row_count:
            dot = QLabel("·")
            dot.setStyleSheet("font-size: 11px; color: #6B7280;")
            meta_layout.addWidget(dot)
            
            rows = QLabel(f"{self._row_count} rows")
            rows.setStyleSheet("font-size: 11px; color: #6B7280;")
            meta_layout.addWidget(rows)
        
        meta_layout.addStretch()
        info_layout.addWidget(meta)
        
        layout.addWidget(info, 1)
        
        # Actions (always visible for simplicity)
        self._reanalyze_btn = QPushButton("↻")
        self._reanalyze_btn.setFixedSize(24, 24)
        self._reanalyze_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self._reanalyze_btn.setToolTip("Re-analyze")
        self._reanalyze_btn.clicked.connect(lambda: self.reanalyze_clicked.emit(self._id))
        self._reanalyze_btn.setStyleSheet("""
            QPushButton {
                background: white;
                border: 1px solid #E5E7EB;
                border-radius: 4px;
                font-size: 12px;
                color: #6B7280;
            }
            QPushButton:hover {
                border-color: #22C55E;
                color: #22C55E;
            }
        """)
        layout.addWidget(self._reanalyze_btn)
    
    def _truncate(self, text: str, max_len: int) -> str:
        if len(text) <= max_len:
            return text
        ext_idx = text.rfind('.')
        if ext_idx > 0:
            ext = text[ext_idx:]
            base = text[:ext_idx]
            return base[:max_len - len(ext) - 3] + "..." + ext
        return text[:max_len - 3] + "..."
    
    def _format_time(self, ts: datetime) -> str:
        if ts.tzinfo:
            ts = ts.replace(tzinfo=None)
        now = datetime.now()
        diff = now - ts
        mins = diff.total_seconds() / 60
        hours = mins / 60
        days = hours / 24
        
        if mins < 1:
            return "Just now"
        elif mins < 60:
            return f"{int(mins)}m ago"
        elif hours < 24:
            return f"{int(hours)}h ago"
        elif days < 7:
            return f"{int(days)}d ago"
        return ts.strftime("%b %d")
    
    def _apply_style(self):
        # Academic Blue border for selected per design.md
        if self._is_selected:
            self.setStyleSheet("""
                QFrame {
                    background-color: #F8FAFC;
                    border-left: 3px solid #2F80ED;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border-bottom: 1px solid #E5E7EB;
                }
                QFrame:hover {
                    background-color: #F8FAFC;
                }
            """)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self._id)
        super().mousePressEvent(event)
    
    def set_selected(self, selected: bool):
        self._is_selected = selected
        self._apply_style()


class DatasetHistory(QWidget):
    """Dataset History List - matches Web implementation."""
    
    dataset_selected = pyqtSignal(str)
    reanalyze_clicked = pyqtSignal(str)
    compare_clicked = pyqtSignal(str)
    clear_history_clicked = pyqtSignal()
    
    def __init__(self, max_items: int = 5, parent=None):
        super().__init__(parent)
        self._max_items = max_items
        self._datasets: List[Dict[str, Any]] = []
        self._selected_id: Optional[str] = None
        self._items: List[HistoryItem] = []
        self._fetch_worker: Optional[HistoryFetchWorker] = None
        self._is_authenticated = False
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 12, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 0, 16, 8)
        
        title = QLabel("RECENT DATASETS")
        title.setStyleSheet("""
            font-size: 11px;
            font-weight: 600;
            color: #6B7280;
            letter-spacing: 0.5px;
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Refresh button
        self._refresh_btn = QPushButton("↻")
        self._refresh_btn.setFixedSize(20, 20)
        self._refresh_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self._refresh_btn.clicked.connect(self.refresh_from_backend)
        self._refresh_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 12px;
                color: #6B7280;
            }
            QPushButton:hover { color: #2F80ED; }
        """)
        header_layout.addWidget(self._refresh_btn)
        
        # Clear button
        self._clear_btn = QPushButton("Clear")
        self._clear_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self._clear_btn.clicked.connect(self.clear_history_clicked.emit)
        self._clear_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 11px;
                color: #6B7280;
                padding: 2px 4px;
            }
            QPushButton:hover { color: #DC2626; }
        """)
        self._clear_btn.setVisible(False)
        header_layout.addWidget(self._clear_btn)
        
        layout.addWidget(header)
        
        # List container
        self._list_widget = QWidget()
        self._list_layout = QVBoxLayout(self._list_widget)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(0)
        self._list_layout.setAlignment(Qt.AlignTop)
        layout.addWidget(self._list_widget, 1)
        
        # Empty/Loading/Login labels
        self._empty_label = QLabel("No recent datasets")
        self._empty_label.setStyleSheet("""
            font-size: 12px;
            color: #6B7280;
            font-style: italic;
            padding: 12px 16px;
        """)
        self._list_layout.addWidget(self._empty_label)
        
        self._loading_label = QLabel("Loading...")
        self._loading_label.setStyleSheet("""
            font-size: 12px;
            color: #6B7280;
            font-style: italic;
            padding: 12px 16px;
        """)
        self._loading_label.setVisible(False)
        self._list_layout.addWidget(self._loading_label)
        
        self._login_label = QLabel("Login to see your datasets")
        self._login_label.setStyleSheet("""
            font-size: 12px;
            color: #6B7280;
            font-style: italic;
            padding: 12px 16px;
        """)
        self._login_label.setVisible(False)
        self._list_layout.addWidget(self._login_label)
    
    def set_authenticated(self, is_authenticated: bool):
        """Set auth state and refresh if authenticated."""
        self._is_authenticated = is_authenticated
        
        if not is_authenticated:
            self._clear_items()
            self._login_label.setVisible(True)
            self._empty_label.setVisible(False)
            self._clear_btn.setVisible(False)
            self._refresh_btn.setEnabled(False)
        else:
            self._login_label.setVisible(False)
            self._refresh_btn.setEnabled(True)
            self.refresh_from_backend()
    
    def refresh_from_backend(self):
        """Fetch history from backend."""
        if not self._is_authenticated:
            return
        
        if self._fetch_worker and self._fetch_worker.isRunning():
            return
        
        self._loading_label.setVisible(True)
        self._empty_label.setVisible(False)
        
        self._fetch_worker = HistoryFetchWorker()
        self._fetch_worker.fetch_success.connect(self._on_fetch_success)
        self._fetch_worker.fetch_error.connect(self._on_fetch_error)
        self._fetch_worker.start()
    
    @pyqtSlot(list)
    def _on_fetch_success(self, datasets: List[Dict[str, Any]]):
        """Handle fetch success."""
        self._loading_label.setVisible(False)
        
        converted = []
        for ds in datasets:
            ts_str = ds.get('upload_time', '')
            try:
                timestamp = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
            except:
                timestamp = datetime.now()
            
            converted.append({
                'id': str(ds.get('id', '')),
                'filename': ds.get('filename', 'Unknown'),
                'timestamp': timestamp,
                'row_count': ds.get('row_count'),
            })
        
        self._datasets = converted
        self._rebuild_list()
    
    @pyqtSlot(str)
    def _on_fetch_error(self, error: str):
        """Handle fetch error."""
        self._loading_label.setVisible(False)
        self._empty_label.setText(f"Error loading history")
        self._empty_label.setVisible(True)
    
    def _clear_items(self):
        """Remove all history items."""
        for item in self._items:
            self._list_layout.removeWidget(item)
            item.deleteLater()
        self._items.clear()
        self._datasets.clear()
    
    def _rebuild_list(self):
        """Rebuild the list from datasets."""
        # Clear existing
        for item in self._items:
            self._list_layout.removeWidget(item)
            item.deleteLater()
        self._items.clear()
        
        if not self._is_authenticated:
            self._login_label.setVisible(True)
            self._empty_label.setVisible(False)
            self._clear_btn.setVisible(False)
            return
        
        self._login_label.setVisible(False)
        
        displayed = self._datasets[:self._max_items]
        has_data = len(displayed) > 0
        
        self._empty_label.setVisible(not has_data)
        self._clear_btn.setVisible(has_data)
        
        for data in displayed:
            item = HistoryItem(
                dataset_id=data['id'],
                filename=data['filename'],
                timestamp=data['timestamp'],
                row_count=data.get('row_count'),
                is_selected=(data['id'] == self._selected_id)
            )
            item.clicked.connect(self._on_item_clicked)
            item.reanalyze_clicked.connect(self.reanalyze_clicked.emit)
            item.compare_clicked.connect(self.compare_clicked.emit)
            
            self._items.append(item)
            # Insert before labels
            self._list_layout.insertWidget(len(self._items) - 1, item)
    
    def _on_item_clicked(self, dataset_id: str):
        """Handle item click."""
        self.set_selected(dataset_id)
        self.dataset_selected.emit(dataset_id)
    
    def set_selected(self, dataset_id: Optional[str]):
        """Set selected dataset."""
        self._selected_id = dataset_id
        for item in self._items:
            item.set_selected(item._id == dataset_id)
    
    def set_datasets(self, datasets: List[Dict[str, Any]]):
        """Manually set datasets."""
        self._datasets = datasets
        self._rebuild_list()
    
    def add_dataset(self, dataset: Dict[str, Any]):
        """Add a dataset to the list."""
        self._datasets.insert(0, dataset)
        self._rebuild_list()
    
    def clear(self):
        """Clear all datasets."""
        self._clear_items()
        self._rebuild_list()
