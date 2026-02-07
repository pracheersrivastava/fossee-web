"""
KPI Card Widgets
FOSSEE Scientific Analytics UI

Clean, simple KPI cards with no text truncation.
"""

from typing import Optional, Dict, Any

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt


# Colors
COLOR_EQUIPMENT = "#8B5CF6"  # Violet
COLOR_FLOWRATE = "#14B8A6"   # Teal
COLOR_TEMPERATURE = "#F59E0B"  # Amber


class KPICard(QFrame):
    """Single KPI Card - clean and simple."""
    
    def __init__(self, label: str, value: str, unit: str = "", 
                 icon: str = "", accent_color: str = COLOR_EQUIPMENT, parent=None):
        super().__init__(parent)
        self._label = label
        self._value = value
        self._unit = unit
        self._icon = icon
        self._accent = accent_color
        
        self.setMinimumWidth(160)
        self.setMinimumHeight(100)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._setup_ui()
        self._apply_style()
    
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Icon
        if self._icon:
            icon_label = QLabel(self._icon)
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setFixedSize(44, 44)
            icon_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {self._accent}22;
                    color: {self._accent};
                    border-radius: 10px;
                    font-size: 20px;
                }}
            """)
            layout.addWidget(icon_label)
        
        # Content
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(2)
        
        # Value + Unit row
        value_row = QWidget()
        value_layout = QHBoxLayout(value_row)
        value_layout.setContentsMargins(0, 0, 0, 0)
        value_layout.setSpacing(4)
        value_layout.setAlignment(Qt.AlignLeft | Qt.AlignBaseline)
        
        self._value_label = QLabel(self._value)
        self._value_label.setStyleSheet("""
            font-size: 28px;
            font-weight: 700;
            color: #0F172A;
        """)
        value_layout.addWidget(self._value_label)
        
        if self._unit:
            self._unit_label = QLabel(self._unit)
            self._unit_label.setStyleSheet("""
                font-size: 13px;
                font-weight: 500;
                color: #64748B;
            """)
            value_layout.addWidget(self._unit_label)
        
        value_layout.addStretch()
        content_layout.addWidget(value_row)
        
        # Label - NO TRUNCATION
        self._label_label = QLabel(self._label)
        self._label_label.setStyleSheet("""
            font-size: 11px;
            font-weight: 600;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        """)
        self._label_label.setWordWrap(False)
        content_layout.addWidget(self._label_label)
        
        layout.addWidget(content, 1)
    
    def _apply_style(self):
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 12px;
            }
        """)
    
    def set_value(self, value: str, unit: str = ""):
        self._value_label.setText(value)
        if unit and hasattr(self, '_unit_label'):
            self._unit_label.setText(unit)


class KPIGrid(QWidget):
    """Horizontal grid of KPI cards."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._cards = []
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(16)
    
    def add_card(self, card: KPICard):
        self._cards.append(card)
        self._layout.addWidget(card)
    
    def clear(self):
        for card in self._cards:
            self._layout.removeWidget(card)
            card.deleteLater()
        self._cards.clear()


class SummaryKPIs(QWidget):
    """Pre-configured Summary KPIs widget."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = {}
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self._grid = KPIGrid()
        
        # Total Equipment
        self._equipment_card = KPICard(
            label="TOTAL EQUIP.",
            value="0",
            icon="⚙",
            accent_color=COLOR_EQUIPMENT
        )
        self._grid.add_card(self._equipment_card)
        
        # Avg. Flowrate
        self._flowrate_card = KPICard(
            label="AVG. FLOW",
            value="0.0",
            unit="m³/hr",
            icon="◎",
            accent_color=COLOR_FLOWRATE
        )
        self._grid.add_card(self._flowrate_card)
        
        # Avg. Temperature
        self._temp_card = KPICard(
            label="AVG. TEMP",
            value="0.0",
            unit="°C",
            icon="◐",
            accent_color=COLOR_TEMPERATURE
        )
        self._grid.add_card(self._temp_card)
        
        # Dominant Type
        self._type_card = KPICard(
            label="DOM. TYPE",
            value="—",
            icon="▣",
            accent_color=COLOR_EQUIPMENT
        )
        self._grid.add_card(self._type_card)
        
        layout.addWidget(self._grid)
    
    def set_data(self, data: Dict[str, Any]):
        """Update KPIs with new data."""
        self._data = data
        
        total = data.get('totalEquipment') or 0
        flow = data.get('avgFlowrate') or 0.0
        temp = data.get('avgTemperature') or 0.0
        dtype = data.get('dominantType') or '—'
        
        self._equipment_card.set_value(f"{int(total):,}")
        self._flowrate_card.set_value(f"{float(flow):.1f}", "m³/hr")
        self._temp_card.set_value(f"{float(temp):.1f}", "°C")
        self._type_card.set_value(str(dtype) if dtype else '—')
