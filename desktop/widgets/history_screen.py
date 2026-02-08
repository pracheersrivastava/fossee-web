"""
History Screen Widget
FOSSEE Scientific Analytics UI

Full-page dataset history view matching Web HistoryScreen.
Shows all user datasets with filename, row count, timestamp,
and Analyze button.

Per design.md tokens:
- Deep Indigo (#1E2A38) for text
- Slate Gray (#6B7280) for secondary/meta
- Academic Blue (#2F80ED) for primary action
- Off-White (#F8FAFC) for background
- Card: white, 8px radius, 1px border #E5E7EB
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtGui import QCursor

from core.tokens import SPACE_SM, SPACE_MD, SPACE_LG
from core.api_client import api_client, APIError


class HistoryFetchWorker(QThread):
    """Background worker for fetching history from backend."""
    
    fetch_success = pyqtSignal(list)
    fetch_error = pyqtSignal(str)
    
    def run(self):
        try:
            result = api_client.get_history()
            datasets = result.get('datasets', [])
            self.fetch_success.emit(datasets)
        except APIError as e:
            self.fetch_error.emit(str(e.message))
        except Exception as e:
            self.fetch_error.emit(f"Failed to load history: {str(e)}")


class HistoryCard(QFrame):
    """Single dataset history card matching web history-screen__item."""
    
    analyze_clicked = pyqtSignal(str)
    
    def __init__(self, dataset_id: str, filename: str, 
                 row_count: int, timestamp: datetime, parent=None):
        super().__init__(parent)
        self._id = dataset_id
        self._filename = filename
        self._row_count = row_count
        self._timestamp = timestamp
        self._setup_ui()
    
    def _setup_ui(self):
        self.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
            }
            QFrame:hover {
                border-color: #CBD5E1;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # File icon
        icon = QLabel("📄")
        icon.setStyleSheet("font-size: 24px; border: none;")
        icon.setFixedWidth(32)
        layout.addWidget(icon)
        
        # Details column
        details = QWidget()
        details.setStyleSheet("border: none;")
        details_layout = QVBoxLayout(details)
        details_layout.setContentsMargins(0, 0, 0, 0)
        details_layout.setSpacing(4)
        
        # Filename - Body 14px, medium weight, Deep Indigo
        name_label = QLabel(self._filename)
        name_label.setStyleSheet("""
            font-size: 14px;
            font-weight: 500;
            color: #1E2A38;
            border: none;
        """)
        details_layout.addWidget(name_label)
        
        # Meta line - Caption 12px, Slate Gray
        meta_parts = []
        if self._row_count:
            meta_parts.append(f"{self._row_count:,} rows")
        meta_parts.append(self._format_time(self._timestamp))
        
        meta_label = QLabel(" · ".join(meta_parts))
        meta_label.setStyleSheet("""
            font-size: 12px;
            color: #6B7280;
            border: none;
        """)
        details_layout.addWidget(meta_label)
        
        layout.addWidget(details, 1)
        
        # Analyze button - Primary small per design.md
        analyze_btn = QPushButton("Analyze")
        analyze_btn.setCursor(QCursor(Qt.PointingHandCursor))
        analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #2F80ED;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-size: 13px;
                font-weight: 500;
                min-height: 32px;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
            QPushButton:pressed {
                background-color: #1D4ED8;
            }
        """)
        analyze_btn.clicked.connect(lambda: self.analyze_clicked.emit(self._id))
        layout.addWidget(analyze_btn)
    
    def _format_time(self, ts: datetime) -> str:
        if ts.tzinfo:
            ts = ts.astimezone(tz=None).replace(tzinfo=None)
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


class HistoryScreen(QWidget):
    """
    Full-page history screen matching Web HistoryScreen.
    
    Shows all user datasets as cards with Analyze action.
    Fetches data from backend /api/history/ endpoint.
    
    Signals:
        dataset_selected: emitted with dataset_id when Analyze clicked
    """
    
    dataset_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._datasets: List[Dict[str, Any]] = []
        self._cards: List[HistoryCard] = []
        self._fetch_worker: Optional[HistoryFetchWorker] = None
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_LG, SPACE_LG, SPACE_LG, SPACE_LG)
        layout.setSpacing(SPACE_LG)
        
        # Header row with count + clear button
        self._header = QWidget()
        header_layout = QHBoxLayout(self._header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        self._count_label = QLabel("")
        self._count_label.setStyleSheet("""
            font-size: 14px;
            color: #6B7280;
        """)
        header_layout.addWidget(self._count_label)
        header_layout.addStretch()
        self._header.setVisible(False)
        layout.addWidget(self._header)
        
        # Loading state
        self._loading_label = QLabel("Loading history...")
        self._loading_label.setAlignment(Qt.AlignCenter)
        self._loading_label.setStyleSheet("""
            font-size: 14px;
            color: #2F80ED;
            padding: 40px;
        """)
        layout.addWidget(self._loading_label)
        
        # Empty state container
        self._empty_widget = QWidget()
        empty_layout = QVBoxLayout(self._empty_widget)
        empty_layout.setAlignment(Qt.AlignCenter)
        empty_layout.setSpacing(SPACE_SM)
        
        empty_icon = QLabel("📋")
        empty_icon.setStyleSheet("font-size: 64px; opacity: 0.3;")
        empty_icon.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(empty_icon)
        
        empty_title = QLabel("No datasets yet")
        empty_title.setStyleSheet("""
            font-size: 18px;
            font-weight: 500;
            color: #1E2A38;
        """)
        empty_title.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(empty_title)
        
        empty_text = QLabel("Upload a CSV file to start tracking your dataset history.")
        empty_text.setStyleSheet("""
            font-size: 14px;
            color: #6B7280;
        """)
        empty_text.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(empty_text)
        
        self._empty_widget.setVisible(False)
        layout.addWidget(self._empty_widget)
        
        # Not authenticated state
        self._login_widget = QWidget()
        login_layout = QVBoxLayout(self._login_widget)
        login_layout.setAlignment(Qt.AlignCenter)
        login_layout.setSpacing(SPACE_SM)
        
        login_icon = QLabel("🔒")
        login_icon.setStyleSheet("font-size: 48px;")
        login_icon.setAlignment(Qt.AlignCenter)
        login_layout.addWidget(login_icon)
        
        login_title = QLabel("Login required")
        login_title.setStyleSheet("""
            font-size: 18px;
            font-weight: 500;
            color: #1E2A38;
        """)
        login_title.setAlignment(Qt.AlignCenter)
        login_layout.addWidget(login_title)
        
        login_text = QLabel("Login to see your dataset history.")
        login_text.setStyleSheet("""
            font-size: 14px;
            color: #6B7280;
        """)
        login_text.setAlignment(Qt.AlignCenter)
        login_layout.addWidget(login_text)
        
        self._login_widget.setVisible(False)
        layout.addWidget(self._login_widget)
        
        # Scrollable list of history cards
        self._list_widget = QWidget()
        self._list_layout = QVBoxLayout(self._list_widget)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(SPACE_SM)
        self._list_layout.setAlignment(Qt.AlignTop)
        self._list_widget.setVisible(False)
        layout.addWidget(self._list_widget, 1)
        
        layout.addStretch()
    
    def load(self, is_authenticated: bool):
        """Load history data from backend. Always fetches fresh data."""
        if not is_authenticated:
            self._loading_label.setVisible(False)
            self._empty_widget.setVisible(False)
            self._header.setVisible(False)
            self._list_widget.setVisible(False)
            self._login_widget.setVisible(True)
            return
        
        self._login_widget.setVisible(False)
        self._loading_label.setVisible(True)
        self._empty_widget.setVisible(False)
        self._header.setVisible(False)
        self._list_widget.setVisible(False)
        
        # Cancel any running fetch worker before starting a new one
        if self._fetch_worker and self._fetch_worker.isRunning():
            self._fetch_worker.fetch_success.disconnect()
            self._fetch_worker.fetch_error.disconnect()
            self._fetch_worker.wait(500)
        
        self._fetch_worker = HistoryFetchWorker()
        self._fetch_worker.fetch_success.connect(self._on_fetch_success)
        self._fetch_worker.fetch_error.connect(self._on_fetch_error)
        self._fetch_worker.start()
    
    @pyqtSlot(list)
    def _on_fetch_success(self, datasets: List[Dict[str, Any]]):
        self._loading_label.setVisible(False)
        
        if not datasets:
            self._empty_widget.setVisible(True)
            self._header.setVisible(False)
            self._list_widget.setVisible(False)
            return
        
        # Show header with count
        count = len(datasets)
        suffix = "s" if count != 1 else ""
        self._count_label.setText(f"{count} dataset{suffix} in history")
        self._header.setVisible(True)
        
        # Clear old cards
        self._clear_cards()
        
        # Build cards
        for ds in datasets:
            ts_str = ds.get('upload_time', '')
            try:
                timestamp = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
            except Exception:
                timestamp = datetime.now()
            
            card = HistoryCard(
                dataset_id=str(ds.get('id', '')),
                filename=ds.get('filename', ds.get('original_filename', 'Unknown')),
                row_count=ds.get('row_count', 0),
                timestamp=timestamp,
            )
            card.analyze_clicked.connect(self._on_analyze)
            self._cards.append(card)
            self._list_layout.addWidget(card)
        
        self._list_widget.setVisible(True)
    
    @pyqtSlot(str)
    def _on_fetch_error(self, error: str):
        self._loading_label.setVisible(False)
        self._empty_widget.setVisible(True)
    
    def _on_analyze(self, dataset_id: str):
        self.dataset_selected.emit(dataset_id)
    
    def _clear_cards(self):
        for card in self._cards:
            self._list_layout.removeWidget(card)
            card.deleteLater()
        self._cards.clear()
