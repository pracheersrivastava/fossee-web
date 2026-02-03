"""
Dataset History Widget
FOSSEE Scientific Analytics UI

Displays last 5 uploads in sidebar with:
- Filename and timestamp
- Small sparkline preview
- Hover actions: Re-analyze / Compare

Per design.md:
- Meta text: 11px
- Caption: 12px
- Spacing: 8px base
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QRectF, QPointF
from PyQt5.QtGui import (
    QColor, QPainter, QPen, QPainterPath, QFont, QCursor
)

from ..core.tokens import (
    DEEP_INDIGO, SLATE_GRAY, ACADEMIC_BLUE, PURE_WHITE, OFF_WHITE,
    COLOR_BORDER, COLOR_SUCCESS, COLOR_INFO, COLOR_ERROR,
    FONT_SIZE_META, FONT_SIZE_CAPTION,
    FONT_WEIGHT_MEDIUM, FONT_WEIGHT_REGULAR,
    SPACE_XS, SPACE_SM, SPACE_MD, SPACE_LG
)


class Sparkline(QWidget):
    """
    Mini sparkline widget.
    Renders a small line chart from data points.
    """
    
    def __init__(self, data: List[float] = None, color: str = ACADEMIC_BLUE, parent=None):
        super().__init__(parent)
        self._data = data or []
        self._color = QColor(color)
        self.setFixedSize(48, 16)
    
    def set_data(self, data: List[float]):
        """Update sparkline data."""
        self._data = data or []
        self.update()
    
    def set_color(self, color: str):
        """Update sparkline color."""
        self._color = QColor(color)
        self.update()
    
    def paintEvent(self, event):
        """Draw the sparkline."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if not self._data or len(self._data) < 2:
            # Draw empty placeholder
            painter.fillRect(self.rect(), QColor("#FAFAFA"))
            return
        
        # Calculate bounds
        min_val = min(self._data)
        max_val = max(self._data)
        range_val = max_val - min_val or 1
        
        width = self.width()
        height = self.height()
        
        # Build path
        path = QPainterPath()
        for i, value in enumerate(self._data):
            x = (i / (len(self._data) - 1)) * width
            y = height - ((value - min_val) / range_val) * height
            
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
        
        # Draw line
        pen = QPen(self._color)
        pen.setWidthF(1.5)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)
        painter.drawPath(path)


class HistoryItemAction(QPushButton):
    """Small action button for history items."""
    
    def __init__(self, icon: str, tooltip: str, hover_color: str, parent=None):
        super().__init__(icon, parent)
        self._hover_color = hover_color
        self._is_hovered = False
        
        self.setFixedSize(24, 24)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setToolTip(tooltip)
        self._update_style()
    
    def _update_style(self):
        """Update button style."""
        if self._is_hovered:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {PURE_WHITE};
                    border: 1px solid {self._hover_color};
                    border-radius: 4px;
                    color: {self._hover_color};
                    font-size: 14px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {PURE_WHITE};
                    border: 1px solid {COLOR_BORDER};
                    border-radius: 4px;
                    color: {SLATE_GRAY};
                    font-size: 14px;
                }}
            """)
    
    def enterEvent(self, event):
        self._is_hovered = True
        self._update_style()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        self._is_hovered = False
        self._update_style()
        super().leaveEvent(event)


class HistoryItem(QFrame):
    """
    Single history item with hover actions.
    
    Displays:
    - Filename
    - Timestamp
    - Row count
    - Sparkline preview
    - Hover actions: Re-analyze / Compare
    """
    
    reanalyze_clicked = pyqtSignal(str)
    compare_clicked = pyqtSignal(str)
    
    def __init__(self, 
                 item_id: str,
                 filename: str,
                 timestamp: datetime,
                 row_count: int = None,
                 sparkline_data: List[float] = None,
                 is_selected: bool = False,
                 parent=None):
        super().__init__(parent)
        
        self._id = item_id
        self._filename = filename
        self._timestamp = timestamp
        self._row_count = row_count
        self._sparkline_data = sparkline_data
        self._is_selected = is_selected
        self._is_hovered = False
        
        self.setMouseTracking(True)
        self._setup_ui()
        self._update_style()
    
    def _setup_ui(self):
        """Initialize the item UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(SPACE_LG, SPACE_SM, SPACE_SM, SPACE_SM)
        layout.setSpacing(SPACE_SM)
        
        # Info section (filename + meta)
        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)
        
        # Filename
        self._filename_label = QLabel(self._truncate_filename(self._filename))
        self._filename_label.setToolTip(self._filename)
        self._filename_label.setStyleSheet(f"""
            font-size: {FONT_SIZE_CAPTION}px;
            font-weight: {FONT_WEIGHT_MEDIUM};
            color: {DEEP_INDIGO};
        """)
        info_layout.addWidget(self._filename_label)
        
        # Meta (timestamp + row count)
        meta_widget = QWidget()
        meta_layout = QHBoxLayout(meta_widget)
        meta_layout.setContentsMargins(0, 0, 0, 0)
        meta_layout.setSpacing(SPACE_XS)
        
        timestamp_label = QLabel(self._format_timestamp(self._timestamp))
        timestamp_label.setStyleSheet(f"""
            font-size: {FONT_SIZE_META}px;
            color: {SLATE_GRAY};
        """)
        meta_layout.addWidget(timestamp_label)
        
        if self._row_count:
            separator = QLabel("·")
            separator.setStyleSheet(f"color: {SLATE_GRAY}; font-size: {FONT_SIZE_META}px;")
            meta_layout.addWidget(separator)
            
            rows_label = QLabel(f"{self._row_count} rows")
            rows_label.setStyleSheet(f"""
                font-size: {FONT_SIZE_META}px;
                color: {SLATE_GRAY};
            """)
            meta_layout.addWidget(rows_label)
        
        meta_layout.addStretch()
        info_layout.addWidget(meta_widget)
        
        layout.addWidget(info_widget, 1)
        
        # Sparkline
        if self._sparkline_data and len(self._sparkline_data) >= 2:
            self._sparkline = Sparkline(self._sparkline_data)
            layout.addWidget(self._sparkline)
        
        # Actions container (hidden by default)
        self._actions = QWidget()
        actions_layout = QHBoxLayout(self._actions)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(SPACE_XS)
        
        self._reanalyze_btn = HistoryItemAction("↻", "Re-analyze", COLOR_SUCCESS)
        self._reanalyze_btn.clicked.connect(lambda: self.reanalyze_clicked.emit(self._id))
        actions_layout.addWidget(self._reanalyze_btn)
        
        self._compare_btn = HistoryItemAction("⇋", "Compare", COLOR_INFO)
        self._compare_btn.clicked.connect(lambda: self.compare_clicked.emit(self._id))
        actions_layout.addWidget(self._compare_btn)
        
        self._actions.setVisible(False)
        layout.addWidget(self._actions)
    
    def _truncate_filename(self, name: str, max_length: int = 18) -> str:
        """Truncate filename if too long."""
        if len(name) <= max_length:
            return name
        
        ext_index = name.rfind('.')
        if ext_index > 0:
            ext = name[ext_index:]
            base = name[:ext_index]
            truncated = base[:max_length - len(ext) - 3]
            return f"{truncated}...{ext}"
        
        return name[:max_length - 3] + "..."
    
    def _format_timestamp(self, ts: datetime) -> str:
        """Format timestamp relative or absolute."""
        now = datetime.now()
        diff = now - ts
        
        minutes = diff.total_seconds() / 60
        hours = minutes / 60
        days = hours / 24
        
        if minutes < 1:
            return "Just now"
        elif minutes < 60:
            return f"{int(minutes)}m ago"
        elif hours < 24:
            return f"{int(hours)}h ago"
        elif days < 7:
            return f"{int(days)}d ago"
        else:
            return ts.strftime("%b %d")
    
    def _update_style(self):
        """Update item style based on state."""
        if self._is_selected:
            self.setStyleSheet(f"""
                HistoryItem {{
                    background-color: {OFF_WHITE};
                    border-left: 2px solid {ACADEMIC_BLUE};
                }}
            """)
        elif self._is_hovered:
            self.setStyleSheet(f"""
                HistoryItem {{
                    background-color: {OFF_WHITE};
                    border-left: none;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                HistoryItem {{
                    background-color: transparent;
                    border-left: none;
                }}
            """)
    
    def enterEvent(self, event):
        """Show actions on hover."""
        self._is_hovered = True
        self._actions.setVisible(True)
        self._update_style()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Hide actions when not hovered."""
        self._is_hovered = False
        self._actions.setVisible(False)
        self._update_style()
        super().leaveEvent(event)
    
    def set_selected(self, selected: bool):
        """Set selection state."""
        self._is_selected = selected
        self._update_style()


class DatasetHistory(QWidget):
    """
    Dataset History List
    Shows last 5 uploads with actions.
    """
    
    reanalyze_clicked = pyqtSignal(str)
    compare_clicked = pyqtSignal(str)
    clear_history_clicked = pyqtSignal()
    
    def __init__(self, max_items: int = 5, parent=None):
        super().__init__(parent)
        self._max_items = max_items
        self._datasets: List[Dict[str, Any]] = []
        self._selected_id: Optional[str] = None
        self._items: List[HistoryItem] = []
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Initialize the history UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, SPACE_MD, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(SPACE_LG, 0, SPACE_LG, SPACE_SM)
        
        title = QLabel("Recent Datasets")
        title.setStyleSheet(f"""
            font-size: {FONT_SIZE_CAPTION}px;
            font-weight: {FONT_WEIGHT_MEDIUM};
            color: {SLATE_GRAY};
            text-transform: uppercase;
            letter-spacing: 0.5px;
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        self._clear_btn = QPushButton("Clear")
        self._clear_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self._clear_btn.clicked.connect(self.clear_history_clicked.emit)
        self._clear_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                font-size: {FONT_SIZE_META}px;
                color: {SLATE_GRAY};
                padding: 2px 6px;
            }}
            QPushButton:hover {{
                color: {COLOR_ERROR};
                background-color: rgba(220, 38, 38, 0.1);
                border-radius: 4px;
            }}
        """)
        self._clear_btn.setVisible(False)
        header_layout.addWidget(self._clear_btn)
        
        layout.addWidget(header)
        
        # List container
        self._list_container = QWidget()
        self._list_layout = QVBoxLayout(self._list_container)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(0)
        
        # Empty state
        self._empty_label = QLabel("No recent datasets")
        self._empty_label.setStyleSheet(f"""
            font-size: {FONT_SIZE_CAPTION}px;
            color: {SLATE_GRAY};
            font-style: italic;
            padding: {SPACE_MD}px {SPACE_LG}px;
        """)
        self._list_layout.addWidget(self._empty_label)
        
        layout.addWidget(self._list_container)
        
        # More indicator
        self._more_label = QLabel()
        self._more_label.setStyleSheet(f"""
            font-size: {FONT_SIZE_META}px;
            color: {SLATE_GRAY};
            padding: {SPACE_XS}px {SPACE_LG}px;
        """)
        self._more_label.setAlignment(Qt.AlignCenter)
        self._more_label.setVisible(False)
        layout.addWidget(self._more_label)
        
        layout.addStretch()
    
    def set_datasets(self, datasets: List[Dict[str, Any]]):
        """
        Set the dataset history.
        
        Each dataset dict should have:
        - id: str
        - filename: str
        - timestamp: datetime
        - row_count: int (optional)
        - sparkline_data: List[float] (optional)
        """
        self._datasets = datasets
        self._rebuild_list()
    
    def set_selected(self, dataset_id: Optional[str]):
        """Set the selected dataset."""
        self._selected_id = dataset_id
        for item in self._items:
            item.set_selected(item._id == dataset_id)
    
    def _rebuild_list(self):
        """Rebuild the history list."""
        # Clear existing items
        for item in self._items:
            item.deleteLater()
        self._items.clear()
        
        displayed = self._datasets[:self._max_items]
        has_datasets = len(displayed) > 0
        
        # Update visibility
        self._empty_label.setVisible(not has_datasets)
        self._clear_btn.setVisible(has_datasets)
        
        # Create items
        for data in displayed:
            item = HistoryItem(
                item_id=data.get('id', ''),
                filename=data.get('filename', 'Unknown'),
                timestamp=data.get('timestamp', datetime.now()),
                row_count=data.get('row_count'),
                sparkline_data=data.get('sparkline_data'),
                is_selected=data.get('id') == self._selected_id
            )
            item.reanalyze_clicked.connect(self.reanalyze_clicked.emit)
            item.compare_clicked.connect(self.compare_clicked.emit)
            
            self._items.append(item)
            self._list_layout.insertWidget(self._list_layout.count() - 1, item)
        
        # Show "more" indicator
        remaining = len(self._datasets) - self._max_items
        if remaining > 0:
            self._more_label.setText(f"+{remaining} more")
            self._more_label.setVisible(True)
        else:
            self._more_label.setVisible(False)
    
    def add_dataset(self, dataset: Dict[str, Any]):
        """Add a new dataset to the beginning of the list."""
        self._datasets.insert(0, dataset)
        self._rebuild_list()
    
    def clear(self):
        """Clear all datasets."""
        self._datasets.clear()
        self._rebuild_list()
