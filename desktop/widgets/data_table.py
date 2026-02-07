"""
Data Table Widget
FOSSEE Scientific Analytics UI

Equipment data table following design.md Section 5.4:
- Header background: #F1F5F9
- Row height: 44px
- Zebra striping: #FAFAFA
- No vertical grid lines
- Hover highlight only
"""

from typing import List, Dict, Any, Optional

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView, QHeaderView,
    QLabel, QFrame, QStyledItemDelegate, QStyle, QPushButton,
    QAbstractItemView
)
from PyQt5.QtCore import (
    Qt, QAbstractTableModel, QModelIndex, QVariant, 
    pyqtSignal, QSortFilterProxyModel
)
from PyQt5.QtGui import QColor, QFont, QPalette, QBrush

from core.tokens import (
    DEEP_INDIGO, SLATE_GRAY, PURE_WHITE, OFF_WHITE,
    COLOR_TABLE_HEADER, COLOR_TABLE_ZEBRA, COLOR_GRIDLINE,
    COLOR_SUCCESS, COLOR_WARNING, COLOR_ERROR,
    FONT_SIZE_TABLE, FONT_SIZE_H3, FONT_SIZE_CAPTION,
    FONT_WEIGHT_MEDIUM, TABLE_ROW_HEIGHT,
    SPACE_SM, SPACE_MD, SPACE_LG
)


class EquipmentTableModel(QAbstractTableModel):
    """
    Table model for equipment data.
    
    Columns: ID, Type, Temperature, Pressure, Flowrate, Status
    """
    
    COLUMNS = [
        {'key': 'id', 'label': 'Equipment ID', 'align': Qt.AlignLeft},
        {'key': 'type', 'label': 'Type', 'align': Qt.AlignLeft},
        {'key': 'temperature', 'label': 'Temperature (°C)', 'align': Qt.AlignRight},
        {'key': 'pressure', 'label': 'Pressure (bar)', 'align': Qt.AlignRight},
        {'key': 'flowrate', 'label': 'Flowrate (m³/hr)', 'align': Qt.AlignRight},
        {'key': 'status', 'label': 'Status', 'align': Qt.AlignLeft},
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._data: List[Dict[str, Any]] = []
    
    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._data)
    
    def columnCount(self, parent=QModelIndex()) -> int:
        return len(self.COLUMNS)
    
    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid() or not self._data:
            return QVariant()
        
        row = index.row()
        col = index.column()
        col_info = self.COLUMNS[col]
        key = col_info['key']
        value = self._data[row].get(key)
        
        if role == Qt.DisplayRole:
            # Format numeric values
            if key == 'temperature' and value is not None:
                return f"{value:.1f}"
            elif key in ('pressure', 'flowrate') and value is not None:
                return f"{value:.2f}"
            elif value is None:
                return "—"
            return str(value)
        
        elif role == Qt.TextAlignmentRole:
            return col_info['align'] | Qt.AlignVCenter
        
        elif role == Qt.UserRole:
            # Return raw value for sorting
            return value
        
        elif role == Qt.UserRole + 1:
            # Return status for styling
            if key == 'status':
                return value
        
        return QVariant()
    
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if orientation == Qt.Horizontal:
            if role == Qt.DisplayRole:
                return self.COLUMNS[section]['label']
            elif role == Qt.TextAlignmentRole:
                return self.COLUMNS[section]['align'] | Qt.AlignVCenter
        return QVariant()
    
    def set_data(self, data: List[Dict[str, Any]]):
        """Set table data."""
        self.beginResetModel()
        self._data = self._process_data(data)
        self.endResetModel()
    
    def _process_data(self, raw_data: List[Dict]) -> List[Dict]:
        """Process raw data to expected format."""
        processed = []
        for i, row in enumerate(raw_data):
            processed.append({
                'id': row.get('id') or row.get('equipment_id') or f"EQ-{i+1:03d}",
                'type': row.get('type') or row.get('equipment_type') or 'Unknown',
                'temperature': self._safe_float(row.get('temperature')),
                'pressure': self._safe_float(row.get('pressure')),
                'flowrate': self._safe_float(row.get('flowrate')),
                'status': row.get('status') or 'Active',
            })
        return processed
    
    @staticmethod
    def _safe_float(value) -> Optional[float]:
        """Safely convert to float."""
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def get_row(self, index: int) -> Optional[Dict[str, Any]]:
        """Get row data by index."""
        if 0 <= index < len(self._data):
            return self._data[index]
        return None


class ZebraDelegate(QStyledItemDelegate):
    """
    Custom delegate for zebra striping and status badges.
    
    Per design.md Section 5.4:
    - Zebra striping: #FAFAFA on even rows
    - Hover highlight: #EBF4FF
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._hover_row = -1
    
    def paint(self, painter, option, index):
        # Get row for zebra striping
        row = index.row()
        
        # Background colors
        if option.state & QStyle.State_Selected:
            bg_color = QColor("#DBEAFE")
        elif option.state & QStyle.State_MouseOver or row == self._hover_row:
            bg_color = QColor("#EBF4FF")
        elif row % 2 == 1:
            bg_color = QColor(COLOR_TABLE_ZEBRA)
        else:
            bg_color = QColor(PURE_WHITE)
        
        # Fill background
        painter.fillRect(option.rect, bg_color)
        
        # Draw bottom border (no vertical lines per design.md)
        painter.setPen(QColor(COLOR_GRIDLINE))
        painter.drawLine(
            option.rect.bottomLeft(),
            option.rect.bottomRight()
        )
        
        # Check if this is status column
        status = index.data(Qt.UserRole + 1)
        if status:
            self._draw_status_badge(painter, option, status)
        else:
            # Default text drawing
            super().paint(painter, option, index)
    
    def _draw_status_badge(self, painter, option, status: str):
        """Draw status badge."""
        status_lower = status.lower()
        
        # Badge colors
        colors = {
            'active': ('#DCFCE7', '#22C55E'),
            'inactive': ('#FEE2E2', '#DC2626'),
            'maintenance': ('#FEF3C7', '#B45309'),
        }
        bg_color, text_color = colors.get(status_lower, ('#F1F5F9', '#6B7280'))
        
        # Calculate badge rect
        text = status.capitalize()
        font = painter.font()
        font.setPixelSize(FONT_SIZE_CAPTION)
        painter.setFont(font)
        
        text_width = painter.fontMetrics().horizontalAdvance(text)
        badge_width = text_width + 16
        badge_height = 20
        
        badge_x = option.rect.x() + SPACE_MD
        badge_y = option.rect.center().y() - badge_height // 2
        
        # Draw badge background
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(bg_color))
        painter.drawRoundedRect(badge_x, badge_y, badge_width, badge_height, 4, 4)
        
        # Draw badge text
        painter.setPen(QColor(text_color))
        painter.drawText(
            badge_x + 8, badge_y, badge_width - 16, badge_height,
            Qt.AlignCenter, text
        )
    
    def set_hover_row(self, row: int):
        """Set the currently hovered row."""
        self._hover_row = row


class EquipmentTableView(QTableView):
    """
    Styled table view matching React DataTable.
    
    Features:
    - 44px row height
    - Sticky headers with #F1F5F9 background
    - Zebra striping
    - Hover highlight
    - No vertical grid lines
    - Sortable columns
    """
    
    rowClicked = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._setup_delegate()
    
    def _setup_ui(self):
        """Configure table view appearance."""
        # No vertical grid lines, only horizontal
        self.setShowGrid(False)
        self.setGridStyle(Qt.NoPen)
        
        # Selection behavior
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        
        # Enable sorting
        self.setSortingEnabled(True)
        
        # Mouse tracking for hover
        self.setMouseTracking(True)
        
        # Alternating row colors handled by delegate
        self.setAlternatingRowColors(False)
        
        # Vertical header (row numbers) - hide
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setDefaultSectionSize(TABLE_ROW_HEIGHT)
        
        # Horizontal header styling
        header = self.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header.setHighlightSections(False)
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setMinimumSectionSize(100)
        
        # Apply stylesheet for header
        self.setStyleSheet(f"""
            QTableView {{
                background-color: {PURE_WHITE};
                border: none;
                font-size: {FONT_SIZE_TABLE}px;
                color: {DEEP_INDIGO};
            }}
            
            QTableView::item {{
                padding: 0 {SPACE_MD}px;
                border: none;
                border-bottom: 1px solid {COLOR_GRIDLINE};
            }}
            
            QTableView::item:selected {{
                background-color: #DBEAFE;
                color: {DEEP_INDIGO};
            }}
            
            QHeaderView::section {{
                background-color: {COLOR_TABLE_HEADER};
                color: {DEEP_INDIGO};
                font-size: {FONT_SIZE_TABLE}px;
                font-weight: {FONT_WEIGHT_MEDIUM};
                padding: 0 {SPACE_MD}px;
                height: {TABLE_ROW_HEIGHT}px;
                border: none;
                border-bottom: 1px solid {COLOR_GRIDLINE};
            }}
            
            QHeaderView::section:hover {{
                background-color: #E8EDF2;
            }}
            
            QHeaderView::down-arrow {{
                image: none;
            }}
            
            QHeaderView::up-arrow {{
                image: none;
            }}
        """)
    
    def _setup_delegate(self):
        """Set up custom delegate for zebra striping."""
        self._delegate = ZebraDelegate(self)
        self.setItemDelegate(self._delegate)
    
    def mouseMoveEvent(self, event):
        """Track mouse for hover effect."""
        index = self.indexAt(event.pos())
        if index.isValid():
            self._delegate.set_hover_row(index.row())
            self.viewport().update()
        super().mouseMoveEvent(event)
    
    def leaveEvent(self, event):
        """Clear hover when mouse leaves."""
        self._delegate.set_hover_row(-1)
        self.viewport().update()
        super().leaveEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        """Emit row data on double click."""
        index = self.indexAt(event.pos())
        if index.isValid():
            model = self.model()
            if isinstance(model, QSortFilterProxyModel):
                source_index = model.mapToSource(index)
                row = source_index.row()
                source_model = model.sourceModel()
            else:
                row = index.row()
                source_model = model
            
            if hasattr(source_model, 'get_row'):
                row_data = source_model.get_row(row)
                if row_data:
                    self.rowClicked.emit(row_data)
        
        super().mouseDoubleClickEvent(event)


class DataTableCard(QFrame):
    """
    Card wrapper for data table with title and actions.
    
    Matches React TableCard component.
    """
    
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setObjectName("tableCard")
        self.setProperty("class", "card")
        self._title = title
        self._setup_ui()
    
    def _setup_ui(self):
        """Initialize the card UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QWidget()
        header.setStyleSheet(f"""
            background-color: {PURE_WHITE};
            border-bottom: 1px solid {COLOR_GRIDLINE};
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(SPACE_MD, SPACE_MD, SPACE_MD, SPACE_MD)
        
        title_label = QLabel(self._title)
        title_label.setStyleSheet(f"""
            font-size: {FONT_SIZE_H3}px;
            font-weight: {FONT_WEIGHT_MEDIUM};
            color: {DEEP_INDIGO};
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Actions container
        self._actions = QWidget()
        self._actions_layout = QHBoxLayout(self._actions)
        self._actions_layout.setContentsMargins(0, 0, 0, 0)
        self._actions_layout.setSpacing(SPACE_SM)
        header_layout.addWidget(self._actions)
        
        layout.addWidget(header)
        
        # Table container
        self._table_container = QWidget()
        self._table_layout = QVBoxLayout(self._table_container)
        self._table_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._table_container, 1)
    
    def set_table(self, table: QTableView):
        """Set the table widget."""
        self._table_layout.addWidget(table)
    
    def add_action(self, widget: QWidget):
        """Add an action widget to the header."""
        self._actions_layout.addWidget(widget)


class EquipmentDataTable(QWidget):
    """
    Complete equipment data table widget.
    
    Pre-configured with model, view, and card wrapper.
    Matches React EquipmentDataTable component.
    """
    
    rowClicked = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Initialize the data table."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Card wrapper
        self._card = DataTableCard("Equipment Data")
        
        # Model
        self._model = EquipmentTableModel()
        
        # Proxy model for sorting
        self._proxy = QSortFilterProxyModel()
        self._proxy.setSourceModel(self._model)
        self._proxy.setSortRole(Qt.UserRole)
        
        # Table view
        self._table = EquipmentTableView()
        self._table.setModel(self._proxy)
        self._table.rowClicked.connect(self.rowClicked.emit)
        
        # Set column widths
        header = self._table.horizontalHeader()
        header.resizeSection(0, 120)  # ID
        header.resizeSection(1, 140)  # Type
        header.resizeSection(2, 140)  # Temperature
        header.resizeSection(3, 120)  # Pressure
        header.resizeSection(4, 140)  # Flowrate
        
        self._card.set_table(self._table)
        layout.addWidget(self._card)
    
    def set_data(self, data: List[Dict[str, Any]]):
        """Set table data."""
        self._model.set_data(data)
    
    def get_table(self) -> EquipmentTableView:
        """Get the table view."""
        return self._table
    
    def get_card(self) -> DataTableCard:
        """Get the card wrapper."""
        return self._card
