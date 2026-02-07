"""
Charts Package
FOSSEE Scientific Analytics UI

Matplotlib chart widgets matching Chart.js versions.
"""

from charts.charts import (
    ChartCanvas,
    ChartCard,
    EquipmentDistributionChart,
    TemperatureChart,
    PressureDistributionChart,
    ChartsGrid,
    AnalysisCharts,
)

from charts.chart_config import (
    CHART_COLORS,
    UI_COLORS,
    apply_chart_style,
    get_chart_config,
    EQUIPMENT_DISTRIBUTION_CONFIG,
    TEMPERATURE_LINE_CONFIG,
    PRESSURE_DISTRIBUTION_CONFIG,
)

__all__ = [
    # Widgets
    "ChartCanvas",
    "ChartCard",
    "EquipmentDistributionChart",
    "TemperatureChart",
    "PressureDistributionChart",
    "ChartsGrid",
    "AnalysisCharts",
    # Config
    "CHART_COLORS",
    "UI_COLORS",
    "apply_chart_style",
    "get_chart_config",
    "EQUIPMENT_DISTRIBUTION_CONFIG",
    "TEMPERATURE_LINE_CONFIG",
    "PRESSURE_DISTRIBUTION_CONFIG",
]
