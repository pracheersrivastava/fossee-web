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

UPDATED: Now fetches chart data from backend API.
"""

from typing import List, Optional, Dict, Any

import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import FancyBboxPatch
from scipy.interpolate import make_interp_spline
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QSizePolicy, QApplication
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot

from core.tokens import (
    SPACE_MD, SPACE_LG, DEEP_INDIGO, PURE_WHITE,
    FONT_SIZE_H3, FONT_SIZE_CAPTION
)
from charts.chart_config import (
    apply_chart_style,
    EQUIPMENT_DISTRIBUTION_CONFIG,
    TEMPERATURE_LINE_CONFIG,
    PRESSURE_DISTRIBUTION_CONFIG,
    CHART_COLORS, UI_COLORS,
    get_bar_color, get_fill_color,
)
from core.api_client import api_client, APIError


class AnalysisFetchWorker(QThread):
    """Background worker for fetching analysis data from backend."""
    
    fetch_success = pyqtSignal(dict)
    fetch_error = pyqtSignal(str)
    
    def __init__(self, dataset_id: str):
        super().__init__()
        self.dataset_id = dataset_id
    
    def run(self):
        """Fetch analysis data from backend."""
        try:
            result = api_client.get_analysis(self.dataset_id)
            self.fetch_success.emit(result)
        except APIError as e:
            self.fetch_error.emit(str(e.message))
        except Exception as e:
            self.fetch_error.emit(f"Failed to load analysis: {str(e)}")


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
    - Shadow: 0 1px 3px rgba(0,0,0,0.08)
    - Min height: 320px
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
        self.setStyleSheet("""
            QFrame#chartCard {
                background-color: #FFFFFF;
                border-radius: 8px;
                border: 1px solid #E5E7EB;
                min-height: 320px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_MD, SPACE_MD, SPACE_MD, SPACE_MD)
        layout.setSpacing(SPACE_MD)
        
        # Title
        title_label = QLabel(self._title)
        title_label.setStyleSheet(f"""
            font-size: 20px;
            font-weight: 500;
            color: {DEEP_INDIGO};
            padding-bottom: 8px;
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
        """Draw the bar chart with rounded top corners (matching Chart.js borderRadius: 4)."""
        ax = self._canvas.axes
        ax.clear()
        
        config = EQUIPMENT_DISTRIBUTION_CONFIG
        
        if not self._labels or not self._data:
            return
        
        x = np.arange(len(self._labels))
        
        # Draw bars with rounded top corners
        bar_width = config['bar_width']
        radius = config.get('bar_radius', 4)
        color = config['color']
        
        for i, (xi, val) in enumerate(zip(x, self._data)):
            if val <= 0:
                continue
            # FancyBboxPatch for rounded top corners
            fancy = FancyBboxPatch(
                (xi - bar_width / 2, 0),
                bar_width,
                val,
                boxstyle=f"round,pad=0,rounding_size={radius / 72}",
                facecolor=color,
                edgecolor='none',
                zorder=3,
            )
            ax.add_patch(fancy)
        
        # Set axis limits
        ax.set_xlim(-0.5, len(self._labels) - 0.5)
        ax.set_ylim(0, max(self._data) * 1.1 if self._data else 1)
        
        # X-axis — truncate long labels and rotate to avoid smudging
        ax.set_xticks(x)
        short = [l[:10] + '…' if len(l) > 10 else l for l in self._labels]
        ax.set_xticklabels(short, rotation=45 if len(short) > 4 else 0,
                           ha='right' if len(short) > 4 else 'center',
                           fontsize=10)
        ax.set_xlabel(config['xlabel'])
        
        # Y-axis
        ax.set_ylabel(config['ylabel'])
        
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
        """Draw the line chart with smooth Bézier curve (matching Chart.js tension: 0.3)."""
        ax = self._canvas.axes
        ax.clear()
        
        config = TEMPERATURE_LINE_CONFIG
        
        if not self._labels or not self._data:
            return
        
        x = np.arange(len(self._labels))
        y = np.array(self._data, dtype=float)
        
        # Smooth curve using cubic spline (matches Chart.js tension: 0.3)
        if config.get('smooth', False) and len(x) > 2:
            x_smooth = np.linspace(x.min(), x.max(), 300)
            try:
                spl = make_interp_spline(x, y, k=3)
                y_smooth = spl(x_smooth)
            except Exception:
                x_smooth = x
                y_smooth = y
        else:
            x_smooth = x
            y_smooth = y
        
        # Smooth line (no markers on smooth curve)
        ax.plot(
            x_smooth,
            y_smooth,
            color=config['line_color'],
            linewidth=2,
            zorder=3,
        )
        
        # Markers on actual data points only
        ax.plot(
            x, y,
            linestyle='none',
            marker=config['marker'],
            markersize=config['marker_size'],
            markerfacecolor=config['marker_face_color'],
            markeredgecolor=config['marker_edge_color'],
            markeredgewidth=config['marker_edge_width'],
            zorder=4,
        )
        
        # Fill under smooth curve
        if config['fill']:
            ax.fill_between(
                x_smooth,
                y_smooth,
                alpha=0.13,
                color=config['line_color'],
                zorder=2,
            )
        
        # X-axis — truncate long labels and rotate to avoid smudging
        ax.set_xticks(x)
        short = [l[:10] + '…' if len(l) > 10 else l for l in self._labels]
        ax.set_xticklabels(short, rotation=45 if len(short) > 4 else 0,
                           ha='right' if len(short) > 4 else 'center',
                           fontsize=10)
        ax.set_xlabel(config['xlabel'])
        
        # Y-axis
        ax.set_ylabel(config['ylabel'])
        
        # Grid
        ax.yaxis.grid(config['show_y_grid'], color=UI_COLORS['gridline'], linewidth=1)
        ax.xaxis.grid(config['show_x_grid'])
        ax.set_axisbelow(True)
        
        # Legend with circle marker (matching Chart.js pointStyle: 'circle')
        if config['show_legend']:
            legend_marker = mlines.Line2D(
                [], [],
                color=config['line_color'],
                marker='o',
                markersize=4,
                markerfacecolor=config['line_color'],
                markeredgecolor=config['line_color'],
                linestyle='-',
                linewidth=2,
                label=config['legend_label'],
            )
            ax.legend(
                handles=[legend_marker],
                loc=config.get('legend_loc', 'upper right'),
                frameon=False,
                handlelength=2.5,
            )
        
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
        """Draw the bar chart with rounded top corners (matching Chart.js borderRadius: 4)."""
        ax = self._canvas.axes
        ax.clear()
        
        config = PRESSURE_DISTRIBUTION_CONFIG
        
        if not self._labels or not self._data:
            return
        
        x = np.arange(len(self._labels))
        
        # Draw bars with rounded top corners
        bar_width = config['bar_width']
        radius = config.get('bar_radius', 4)
        color = config['color']
        
        for i, (xi, val) in enumerate(zip(x, self._data)):
            if val <= 0:
                continue
            fancy = FancyBboxPatch(
                (xi - bar_width / 2, 0),
                bar_width,
                val,
                boxstyle=f"round,pad=0,rounding_size={radius / 72}",
                facecolor=color,
                edgecolor='none',
                zorder=3,
            )
            ax.add_patch(fancy)
        
        # Set axis limits
        ax.set_xlim(-0.5, len(self._labels) - 0.5)
        ax.set_ylim(0, max(self._data) * 1.1 if self._data else 1)
        
        # X-axis — truncate long labels and rotate to avoid smudging
        ax.set_xticks(x)
        short = [l[:10] + '…' if len(l) > 10 else l for l in self._labels]
        ax.set_xticklabels(short, rotation=45 if len(short) > 4 else 0,
                           ha='right' if len(short) > 4 else 'center',
                           fontsize=10)
        ax.set_xlabel(config['xlabel'])
        
        # Y-axis
        ax.set_ylabel(config['ylabel'])
        
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
    
    Displays all three charts with backend data.
    Matches React AnalysisCharts component.
    
    UPDATED: Now fetches analysis data from backend API.
    """
    
    analysis_loaded = pyqtSignal(dict)
    analysis_error = pyqtSignal(str)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._dataset_id: Optional[str] = None
        self._analysis_data: Optional[Dict[str, Any]] = None
        self._fetch_worker: Optional[AnalysisFetchWorker] = None
        self._setup_ui()
    
    def _setup_ui(self):
        """Initialize the analysis charts UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(SPACE_LG, SPACE_LG, SPACE_LG, SPACE_LG)
        layout.setSpacing(SPACE_LG)
        
        # Loading label
        self._loading_label = QLabel("Loading analysis...")
        self._loading_label.setAlignment(Qt.AlignCenter)
        self._loading_label.setStyleSheet("color: #2F80ED; font-size: 16px; padding: 40px;")
        self._loading_label.setVisible(False)
        layout.addWidget(self._loading_label)
        
        # Error label
        self._error_label = QLabel()
        self._error_label.setAlignment(Qt.AlignCenter)
        self._error_label.setStyleSheet("color: #DC2626; font-size: 14px; padding: 20px;")
        self._error_label.setVisible(False)
        layout.addWidget(self._error_label)
        
        # Charts container
        self._charts_container = QWidget()
        charts_layout = QVBoxLayout(self._charts_container)
        charts_layout.setContentsMargins(0, 0, 0, 0)
        charts_layout.setSpacing(SPACE_LG)
        
        # Equipment Distribution (full width)
        self._equipment_chart = EquipmentDistributionChart()
        charts_layout.addWidget(self._equipment_chart)
        
        # Row for Temperature and Pressure
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(SPACE_LG)
        
        self._temperature_chart = TemperatureChart()
        row_layout.addWidget(self._temperature_chart)
        
        self._pressure_chart = PressureDistributionChart()
        row_layout.addWidget(self._pressure_chart)
        
        charts_layout.addWidget(row)
        charts_layout.addStretch()
        
        layout.addWidget(self._charts_container)
    
    def load_from_backend(self, dataset_id: str):
        """Load analysis data from backend for the given dataset."""
        if not dataset_id:
            self._show_error("No dataset ID provided")
            return
        
        self._dataset_id = dataset_id
        
        # Show loading state
        self._loading_label.setVisible(True)
        self._error_label.setVisible(False)
        self._charts_container.setVisible(False)
        QApplication.processEvents()
        
        # Fetch from backend
        self._fetch_worker = AnalysisFetchWorker(dataset_id)
        self._fetch_worker.fetch_success.connect(self._on_fetch_success)
        self._fetch_worker.fetch_error.connect(self._on_fetch_error)
        self._fetch_worker.start()
    
    @pyqtSlot(dict)
    def _on_fetch_success(self, data: Dict[str, Any]):
        """Handle successful analysis fetch."""
        self._loading_label.setVisible(False)
        self._charts_container.setVisible(True)
        
        self._analysis_data = data
        
        # Update charts with backend data
        equipment_dist = data.get('equipment_type_distribution', {})
        self._equipment_chart.set_data(
            labels=equipment_dist.get('labels', []),
            data=equipment_dist.get('data', [])
        )
        
        temp_by_equip = data.get('temperature_by_equipment', {})
        self._temperature_chart.set_data(
            labels=temp_by_equip.get('labels', []),
            data=temp_by_equip.get('data', [])
        )
        
        pressure_dist = data.get('pressure_distribution', {})
        self._pressure_chart.set_data(
            labels=pressure_dist.get('labels', []),
            data=pressure_dist.get('data', [])
        )
        
        self.analysis_loaded.emit(data)
    
    @pyqtSlot(str)
    def _on_fetch_error(self, error_message: str):
        """Handle fetch error."""
        self._loading_label.setVisible(False)
        self._show_error(error_message)
        self.analysis_error.emit(error_message)
    
    def _show_error(self, message: str):
        """Display error message."""
        self._error_label.setText(f"⚠ {message}")
        self._error_label.setVisible(True)
        self._charts_container.setVisible(False)
    
    def get_analysis_data(self) -> Optional[Dict[str, Any]]:
        """Get the current analysis data."""
        return self._analysis_data
    
    def get_dataset_id(self) -> Optional[str]:
        """Get the current dataset ID."""
        return self._dataset_id
    
    def set_data(self, data: Dict[str, Any]):
        """
        Update charts directly with data.
        
        For backward compatibility - but prefer load_from_backend.
        """
        self._analysis_data = data
        
        equipment_dist = data.get('equipment_type_distribution', {})
        self._equipment_chart.set_data(
            labels=equipment_dist.get('labels', []),
            data=equipment_dist.get('data', [])
        )
        
        temp_by_equip = data.get('temperature_by_equipment', {})
        self._temperature_chart.set_data(
            labels=temp_by_equip.get('labels', []),
            data=temp_by_equip.get('data', [])
        )
        
        pressure_dist = data.get('pressure_distribution', {})
        self._pressure_chart.set_data(
            labels=pressure_dist.get('labels', []),
            data=pressure_dist.get('data', [])
        )
