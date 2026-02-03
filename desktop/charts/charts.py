"""
Matplotlib Chart Widgets
FOSSEE Scientific Analytics UI

PyQt5 widgets wrapping Matplotlib charts that visually match
the Chart.js versions exactly.

Charts:
- Equipment Type Distribution (Bar)
- Temperature vs Equipment (Line)
- Pressure Distribution (Bar)

All charts follow design.md Section 5.5
"""

from typing import List, Optional, Dict, Any

import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QSizePolicy
)
from PyQt5.QtCore import Qt

from ..core.tokens import (
    SPACE_MD, SPACE_LG, DEEP_INDIGO, PURE_WHITE,
    FONT_SIZE_H3, FONT_SIZE_CAPTION
)
from .chart_config import (
    apply_chart_style,
    EQUIPMENT_DISTRIBUTION_CONFIG,
    TEMPERATURE_LINE_CONFIG,
    PRESSURE_DISTRIBUTION_CONFIG,
    CHART_COLORS, UI_COLORS,
    get_bar_color, get_fill_color,
)


# Apply global style on module load
apply_chart_style()


class ChartCanvas(FigureCanvas):
    """Base Matplotlib canvas for PyQt5."""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.set_facecolor(PURE_WHITE)
        self.axes = self.fig.add_subplot(111)
        
        super().__init__(self.fig)
        self.setParent(parent)
        
        # Set size policy
        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )
        self.updateGeometry()
    
    def clear(self):
        """Clear the axes for redrawing."""
        self.axes.clear()


class ChartCard(QFrame):
    """
    Chart card wrapper matching React ChartCard.
    
    Card styles per design.md Section 5.3:
    - Background: White
    - Radius: 8px
    - Padding: 16px
    """
    
    def __init__(self, title: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("chartCard")
        self.setProperty("class", "card")
        self._title = title
        self._canvas: Optional[ChartCanvas] = None
        self._setup_ui()
    
    def _setup_ui(self):
        """Initialize the chart card UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_MD, SPACE_MD, SPACE_MD, SPACE_MD)
        layout.setSpacing(SPACE_MD)
        
        # Title
        title_label = QLabel(self._title)
        title_label.setStyleSheet(f"""
            font-size: {FONT_SIZE_H3}px;
            font-weight: 500;
            color: {DEEP_INDIGO};
        """)
        layout.addWidget(title_label)
        
        # Chart container
        self._chart_container = QWidget()
        self._chart_layout = QVBoxLayout(self._chart_container)
        self._chart_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._chart_container, 1)
    
    def set_canvas(self, canvas: ChartCanvas):
        """Set the chart canvas."""
        if self._canvas:
            self._chart_layout.removeWidget(self._canvas)
            self._canvas.deleteLater()
        
        self._canvas = canvas
        self._chart_layout.addWidget(canvas)
    
    def get_canvas(self) -> Optional[ChartCanvas]:
        """Get the current canvas."""
        return self._canvas


class EquipmentDistributionChart(QWidget):
    """
    Equipment Type Distribution Chart (Bar).
    
    Color: Muted Violet (#8B5CF6) at 80% opacity
    Matches Chart.js equipmentDistributionConfig.
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._labels: List[str] = []
        self._data: List[int] = []
        self._setup_ui()
    
    def _setup_ui(self):
        """Initialize the chart UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self._card = ChartCard("Equipment Type Distribution")
        self._canvas = ChartCanvas(width=6, height=4)
        self._card.set_canvas(self._canvas)
        
        layout.addWidget(self._card)
    
    def set_data(self, labels: List[str], data: List[int]):
        """Update chart with new data."""
        self._labels = labels
        self._data = data
        self._draw()
    
    def _draw(self):
        """Draw the bar chart."""
        ax = self._canvas.axes
        ax.clear()
        
        config = EQUIPMENT_DISTRIBUTION_CONFIG
        
        if not self._labels or not self._data:
            return
        
        x = np.arange(len(self._labels))
        
        # Bar chart
        bars = ax.bar(
            x,
            self._data,
            width=config['bar_width'],
            color=config['color'],
            edgecolor=config['edgecolor'],
        )
        
        # Round bar tops (approximate with zorder)
        for bar in bars:
            bar.set_linewidth(0)
        
        # X-axis
        ax.set_xticks(x)
        ax.set_xticklabels(self._labels)
        ax.set_xlabel(config['xlabel'])
        
        # Y-axis
        ax.set_ylabel(config['ylabel'])
        ax.set_ylim(bottom=0)
        
        # Grid
        ax.yaxis.grid(config['show_y_grid'], color=UI_COLORS['gridline'], linewidth=1)
        ax.xaxis.grid(config['show_x_grid'])
        ax.set_axisbelow(True)
        
        # Remove spines
        for spine in ax.spines.values():
            spine.set_visible(False)
        
        self._canvas.fig.tight_layout()
        self._canvas.draw()


class TemperatureChart(QWidget):
    """
    Temperature vs Equipment Chart (Line).
    
    Color: Amber (#F59E0B) with 13% opacity fill
    Matches Chart.js temperatureLineConfig.
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._labels: List[str] = []
        self._data: List[float] = []
        self._setup_ui()
    
    def _setup_ui(self):
        """Initialize the chart UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self._card = ChartCard("Temperature vs Equipment")
        self._canvas = ChartCanvas(width=6, height=4)
        self._card.set_canvas(self._canvas)
        
        layout.addWidget(self._card)
    
    def set_data(self, labels: List[str], data: List[float]):
        """Update chart with new data."""
        self._labels = labels
        self._data = data
        self._draw()
    
    def _draw(self):
        """Draw the line chart."""
        ax = self._canvas.axes
        ax.clear()
        
        config = TEMPERATURE_LINE_CONFIG
        
        if not self._labels or not self._data:
            return
        
        x = np.arange(len(self._labels))
        
        # Line with fill
        line, = ax.plot(
            x,
            self._data,
            color=config['line_color'],
            linewidth=2,
            marker=config['marker'],
            markersize=config['marker_size'],
            markerfacecolor=config['marker_face_color'],
            markeredgecolor=config['marker_edge_color'],
            markeredgewidth=config['marker_edge_width'],
            label=config['legend_label'],
            zorder=3,
        )
        
        # Fill under line
        if config['fill']:
            ax.fill_between(
                x,
                self._data,
                alpha=0.13,
                color=config['line_color'],
                zorder=2,
            )
        
        # X-axis
        ax.set_xticks(x)
        ax.set_xticklabels(self._labels)
        ax.set_xlabel(config['xlabel'])
        
        # Y-axis
        ax.set_ylabel(config['ylabel'])
        
        # Grid
        ax.yaxis.grid(config['show_y_grid'], color=UI_COLORS['gridline'], linewidth=1)
        ax.xaxis.grid(config['show_x_grid'])
        ax.set_axisbelow(True)
        
        # Legend (top right)
        if config['show_legend']:
            ax.legend(loc='upper right', frameon=False)
        
        # Remove spines
        for spine in ax.spines.values():
            spine.set_visible(False)
        
        self._canvas.fig.tight_layout()
        self._canvas.draw()


class PressureDistributionChart(QWidget):
    """
    Pressure Distribution Chart (Bar).
    
    Color: Crimson (#EF4444) at 80% opacity
    Matches Chart.js pressureDistributionConfig.
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._labels: List[str] = []
        self._data: List[int] = []
        self._setup_ui()
    
    def _setup_ui(self):
        """Initialize the chart UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self._card = ChartCard("Pressure Distribution")
        self._canvas = ChartCanvas(width=6, height=4)
        self._card.set_canvas(self._canvas)
        
        layout.addWidget(self._card)
    
    def set_data(self, labels: List[str], data: List[int]):
        """Update chart with new data."""
        self._labels = labels
        self._data = data
        self._draw()
    
    def _draw(self):
        """Draw the bar chart."""
        ax = self._canvas.axes
        ax.clear()
        
        config = PRESSURE_DISTRIBUTION_CONFIG
        
        if not self._labels or not self._data:
            return
        
        x = np.arange(len(self._labels))
        
        # Bar chart
        bars = ax.bar(
            x,
            self._data,
            width=config['bar_width'],
            color=config['color'],
            edgecolor=config['edgecolor'],
        )
        
        for bar in bars:
            bar.set_linewidth(0)
        
        # X-axis
        ax.set_xticks(x)
        ax.set_xticklabels(self._labels)
        ax.set_xlabel(config['xlabel'])
        
        # Y-axis
        ax.set_ylabel(config['ylabel'])
        ax.set_ylim(bottom=0)
        
        # Grid
        ax.yaxis.grid(config['show_y_grid'], color=UI_COLORS['gridline'], linewidth=1)
        ax.xaxis.grid(config['show_x_grid'])
        ax.set_axisbelow(True)
        
        # Remove spines
        for spine in ax.spines.values():
            spine.set_visible(False)
        
        self._canvas.fig.tight_layout()
        self._canvas.draw()


class ChartsGrid(QWidget):
    """
    Charts grid layout matching React ChartsGrid.
    
    First chart full width, remaining in 2-column grid.
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._charts: List[QWidget] = []
        self._setup_ui()
    
    def _setup_ui(self):
        """Initialize the grid layout."""
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(SPACE_LG)
    
    def add_chart(self, chart: QWidget, full_width: bool = False):
        """Add a chart to the grid."""
        self._charts.append(chart)
        
        if full_width or len(self._charts) == 1:
            self._layout.addWidget(chart)
        else:
            # Check if we need a new row
            if len(self._charts) % 2 == 0:
                # Add to existing row
                row = self._layout.itemAt(self._layout.count() - 1)
                if row and isinstance(row.widget(), QWidget):
                    row_layout = row.widget().layout()
                    if row_layout:
                        row_layout.addWidget(chart)
            else:
                # Create new row
                row_widget = QWidget()
                row_layout = QHBoxLayout(row_widget)
                row_layout.setContentsMargins(0, 0, 0, 0)
                row_layout.setSpacing(SPACE_LG)
                row_layout.addWidget(chart)
                self._layout.addWidget(row_widget)
    
    def clear(self):
        """Remove all charts."""
        for chart in self._charts:
            chart.deleteLater()
        self._charts.clear()


class AnalysisCharts(QWidget):
    """
    Pre-configured Analysis Charts screen.
    
    Displays all three charts with sample or provided data.
    Matches React AnalysisCharts component.
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._data: Optional[Dict[str, Any]] = None
        self._setup_ui()
        self._load_sample_data()
    
    def _setup_ui(self):
        """Initialize the analysis charts UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_LG, SPACE_LG, SPACE_LG, SPACE_LG)
        layout.setSpacing(SPACE_LG)
        
        # Equipment Distribution (full width)
        self._equipment_chart = EquipmentDistributionChart()
        layout.addWidget(self._equipment_chart)
        
        # Row for Temperature and Pressure
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(SPACE_LG)
        
        self._temperature_chart = TemperatureChart()
        row_layout.addWidget(self._temperature_chart)
        
        self._pressure_chart = PressureDistributionChart()
        row_layout.addWidget(self._pressure_chart)
        
        layout.addWidget(row)
        layout.addStretch()
    
    def _load_sample_data(self):
        """Load sample data for demonstration."""
        # Equipment distribution
        self._equipment_chart.set_data(
            labels=['Pump', 'Valve', 'Heat Exchanger', 'Reactor', 'Compressor'],
            data=[24, 18, 12, 8, 6]
        )
        
        # Temperature trend
        self._temperature_chart.set_data(
            labels=['EQ-001', 'EQ-002', 'EQ-003', 'EQ-004', 'EQ-005', 'EQ-006', 'EQ-007', 'EQ-008'],
            data=[75, 82, 68, 91, 78, 85, 72, 88]
        )
        
        # Pressure distribution
        self._pressure_chart.set_data(
            labels=['0-2', '2-4', '4-6', '6-8', '8-10', '>10'],
            data=[8, 15, 22, 12, 7, 4]
        )
    
    def set_data(self, data: Dict[str, Any]):
        """
        Update charts with equipment data.
        
        Expected data keys:
        - rows: List of equipment records
        """
        self._data = data
        
        if not data or 'rows' not in data:
            return
        
        processed = self._process_data(data['rows'])
        
        self._equipment_chart.set_data(
            labels=processed['equipment']['labels'],
            data=processed['equipment']['data']
        )
        
        self._temperature_chart.set_data(
            labels=processed['temperature']['labels'],
            data=processed['temperature']['data']
        )
        
        self._pressure_chart.set_data(
            labels=processed['pressure']['labels'],
            data=processed['pressure']['data']
        )
    
    def _process_data(self, rows: List[Dict]) -> Dict[str, Dict]:
        """Process raw equipment data for charts."""
        # Equipment type distribution
        type_counts = {}
        for row in rows:
            eq_type = row.get('type') or row.get('equipment_type') or 'Unknown'
            type_counts[eq_type] = type_counts.get(eq_type, 0) + 1
        
        # Temperature data (first 10)
        temp_data = []
        for i, row in enumerate(rows[:10]):
            if 'temperature' in row:
                temp_data.append({
                    'label': row.get('id') or row.get('equipment_id') or f'EQ-{i+1:03d}',
                    'value': float(row.get('temperature', 0))
                })
        
        # Pressure distribution (binned)
        pressure_bins = {'0-2': 0, '2-4': 0, '4-6': 0, '6-8': 0, '8-10': 0, '>10': 0}
        for row in rows:
            pressure = float(row.get('pressure', 0))
            if pressure <= 2:
                pressure_bins['0-2'] += 1
            elif pressure <= 4:
                pressure_bins['2-4'] += 1
            elif pressure <= 6:
                pressure_bins['4-6'] += 1
            elif pressure <= 8:
                pressure_bins['6-8'] += 1
            elif pressure <= 10:
                pressure_bins['8-10'] += 1
            else:
                pressure_bins['>10'] += 1
        
        return {
            'equipment': {
                'labels': list(type_counts.keys()),
                'data': list(type_counts.values()),
            },
            'temperature': {
                'labels': [d['label'] for d in temp_data],
                'data': [d['value'] for d in temp_data],
            },
            'pressure': {
                'labels': list(pressure_bins.keys()),
                'data': list(pressure_bins.values()),
            },
        }
