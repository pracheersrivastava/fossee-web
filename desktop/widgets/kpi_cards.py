"""
KPI Card Widgets
FOSSEE Scientific Analytics UI

Per design.md Section 5.3:
- Card: White bg, 8px radius, 16px padding
- Shadow: 0px 2px 6px rgba(0,0,0,0.05)
- Value: 24px semibold, Deep Indigo
- Label: 12px regular, Slate Gray

Design tokens:
- Deep Indigo (text): #1E2A38
- Slate Gray (secondary): #6B7280
- Equipment (violet): #8B5CF6
- Flowrate (teal): #14B8A6
- Temperature (amber): #F59E0B
"""

from typing import Optional, Dict, Any

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt


# Data Visualization Colors from design.md Section 2.2
COLOR_EQUIPMENT = "#8B5CF6"   # Muted Violet
COLOR_FLOWRATE = "#14B8A6"    # Teal
COLOR_TEMPERATURE = "#F59E0B" # Amber


class KPICard(QFrame):
    """
    Single KPI Card - per design.md Section 5.3.
    
    Clean card with icon, value, and label.
    No truncation, proper sizing.
    """
    
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
        layout.setContentsMargins(16, 16, 16, 16)  # Card padding per design.md
        layout.setSpacing(12)
        
        # Icon container - 48x48 per web CSS
        if self._icon:
            icon_label = QLabel(self._icon)
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setFixedSize(48, 48)
            icon_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {self._accent}1A;
                    color: {self._accent};
                    border-radius: 10px;
                    font-size: 22px;
                }}
            """)
            layout.addWidget(icon_label)
        
        # Content column
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(4)  # xs spacing
        
        # Value + Unit row
        value_row = QWidget()
        value_layout = QHBoxLayout(value_row)
        value_layout.setContentsMargins(0, 0, 0, 0)
        value_layout.setSpacing(2)
        value_layout.setAlignment(Qt.AlignLeft | Qt.AlignBaseline)
        
        # Value: 24px semibold, Deep Indigo per design.md
        self._value_label = QLabel(self._value)
        self._value_label.setStyleSheet("""
            font-size: 24px;
            font-weight: 600;
            color: #1E2A38;
        """)
        value_layout.addWidget(self._value_label)
        
        # Unit: Caption (12px), Slate Gray per design.md
        if self._unit:
            self._unit_label = QLabel(self._unit)
            self._unit_label.setStyleSheet("""
                font-size: 12px;
                font-weight: 400;
                color: #6B7280;
                margin-left: 2px;
            """)
            value_layout.addWidget(self._unit_label)
        
        value_layout.addStretch()
        content_layout.addWidget(value_row)
        
        # Label: Caption (12px), Slate Gray per design.md
        self._label_label = QLabel(self._label)
        self._label_label.setStyleSheet("""
            font-size: 12px;
            font-weight: 400;
            color: #6B7280;
        """)
        self._label_label.setWordWrap(False)
        content_layout.addWidget(self._label_label)
        
        layout.addWidget(content, 1)
    
    def _apply_style(self):
        # Card style per design.md Section 5.3
        self.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
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
