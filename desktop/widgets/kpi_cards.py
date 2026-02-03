"""
KPI Card Widgets
FOSSEE Scientific Analytics UI

Summary KPI cards following design.md Section 5.3:
- Background: White (#FFFFFF)
- Radius: 8px
- Padding: 16px
- Shadow: 0px 2px 6px rgba(0,0,0,0.05)

Visual parity with React implementation.
"""

from typing import Optional, List, Dict, Any

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QGridLayout, QSizePolicy
)
from PyQt5.QtCore import Qt

from ..core.tokens import (
    SPACE_XS, SPACE_SM, SPACE_MD, SPACE_LG, SPACE_XL,
    COLOR_FLOWRATE, COLOR_TEMPERATURE, COLOR_PRESSURE, COLOR_EQUIPMENT
)


class KPICard(QFrame):
    """
    Individual KPI Card widget.
    
    Displays a single KPI with:
    - Icon (optional, with accent color)
    - Value (large, semibold)
    - Unit (small, gray)
    - Label (caption)
    
    Styling per design.md Section 5.3.
    """
    
    def __init__(
        self,
        label: str,
        value: str,
        unit: str = "",
        icon: str = "",
        accent_color: str = COLOR_EQUIPMENT,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        self.setObjectName("kpiCard")
        self.setProperty("class", "card")
        
        self._label = label
        self._value = value
        self._unit = unit
        self._icon = icon
        self._accent_color = accent_color
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Initialize the KPI card UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(SPACE_MD, SPACE_MD, SPACE_MD, SPACE_MD)
        layout.setSpacing(SPACE_MD)
        
        # Icon (if provided)
        if self._icon:
            icon_label = QLabel(self._icon)
            icon_label.setObjectName("kpiIcon")
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setFixedSize(40, 40)
            # Apply accent color via inline style
            icon_label.setStyleSheet(f"""
                background-color: {self._accent_color}15;
                color: {self._accent_color};
                border-radius: 8px;
                font-size: 18px;
            """)
            layout.addWidget(icon_label)
        
        # Content (value + label)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(SPACE_XS)
        
        # Value row (value + unit)
        value_widget = QWidget()
        value_layout = QHBoxLayout(value_widget)
        value_layout.setContentsMargins(0, 0, 0, 0)
        value_layout.setSpacing(2)
        value_layout.setAlignment(Qt.AlignLeft | Qt.AlignBaseline)
        
        value_label = QLabel(self._value)
        value_label.setObjectName("kpiValue")
        value_layout.addWidget(value_label)
        
        if self._unit:
            unit_label = QLabel(self._unit)
            unit_label.setObjectName("kpiUnit")
            unit_label.setProperty("class", "caption")
            value_layout.addWidget(unit_label)
        
        value_layout.addStretch()
        content_layout.addWidget(value_widget)
        
        # Label
        label_label = QLabel(self._label)
        label_label.setObjectName("kpiLabel")
        label_label.setProperty("class", "caption")
        content_layout.addWidget(label_label)
        
        layout.addWidget(content)
        layout.addStretch()
    
    def set_value(self, value: str, unit: str = ""):
        """Update the KPI value."""
        # Find and update the value label
        value_label = self.findChild(QLabel, "kpiValue")
        if value_label:
            value_label.setText(value)
        
        if unit:
            unit_label = self.findChild(QLabel, "kpiUnit")
            if unit_label:
                unit_label.setText(unit)


class KPIGrid(QWidget):
    """
    Responsive grid layout for KPI cards.
    
    Displays KPI cards in a 4-column grid with proper spacing.
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("kpiGrid")
        self._cards: List[KPICard] = []
        self._setup_ui()
    
    def _setup_ui(self):
        """Initialize the grid layout."""
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(SPACE_LG)
    
    def add_card(self, card: KPICard):
        """Add a KPI card to the grid."""
        self._cards.append(card)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._layout.addWidget(card)
    
    def clear(self):
        """Remove all cards from the grid."""
        for card in self._cards:
            self._layout.removeWidget(card)
            card.deleteLater()
        self._cards.clear()


class SummaryKPIs(QWidget):
    """
    Pre-configured Summary KPIs widget.
    
    Displays equipment data KPIs:
    - Total Equipment (Violet)
    - Avg. Flowrate (Teal)
    - Avg. Temperature (Amber)
    - Dominant Type (Violet)
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._data: Dict[str, Any] = {}
        self._setup_ui()
    
    def _setup_ui(self):
        """Initialize the Summary KPIs."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self._grid = KPIGrid()
        
        # Total Equipment
        self._equipment_card = KPICard(
            label="Total Equipment",
            value="0",
            icon="⚙",
            accent_color=COLOR_EQUIPMENT
        )
        self._grid.add_card(self._equipment_card)
        
        # Avg. Flowrate
        self._flowrate_card = KPICard(
            label="Avg. Flowrate",
            value="0.0",
            unit=" m³/hr",
            icon="◎",
            accent_color=COLOR_FLOWRATE
        )
        self._grid.add_card(self._flowrate_card)
        
        # Avg. Temperature
        self._temperature_card = KPICard(
            label="Avg. Temperature",
            value="0.0",
            unit="°C",
            icon="◐",
            accent_color=COLOR_TEMPERATURE
        )
        self._grid.add_card(self._temperature_card)
        
        # Dominant Type
        self._type_card = KPICard(
            label="Dominant Type",
            value="—",
            icon="▣",
            accent_color=COLOR_EQUIPMENT
        )
        self._grid.add_card(self._type_card)
        
        layout.addWidget(self._grid)
    
    def set_data(self, data: Dict[str, Any]):
        """
        Update KPIs with new data.
        
        Expected data keys:
        - totalEquipment: int
        - avgFlowrate: float
        - avgTemperature: float
        - dominantType: str
        """
        self._data = data
        
        total_equipment = data.get('totalEquipment', 0)
        avg_flowrate = data.get('avgFlowrate', 0.0)
        avg_temperature = data.get('avgTemperature', 0.0)
        dominant_type = data.get('dominantType', '—')
        
        self._equipment_card.set_value(f"{total_equipment:,}")
        self._flowrate_card.set_value(f"{avg_flowrate:.1f}", " m³/hr")
        self._temperature_card.set_value(f"{avg_temperature:.1f}", "°C")
        self._type_card.set_value(dominant_type)
