"""
Matplotlib Chart Configuration
FOSSEE Scientific Analytics UI

Matches Chart.js configurations exactly per design.md Section 5.5:
- No borders on bars
- Gridlines: #E5E7EB
- Max 4 colors per chart
- Use opacity (0.7-0.85) instead of new colors

Desktop Font: Source Sans 3
"""

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from typing import Dict, Any

from core.tokens import (
    DEEP_INDIGO, SLATE_GRAY, PURE_WHITE, OFF_WHITE,
    COLOR_FLOWRATE, COLOR_TEMPERATURE, COLOR_PRESSURE, COLOR_EQUIPMENT,
    COLOR_GRIDLINE, FONT_PRIMARY, FONT_FALLBACK,
    FONT_SIZE_CAPTION, FONT_SIZE_BODY, FONT_SIZE_H3,
)


# ===================
# CHART COLORS
# ===================
CHART_COLORS = {
    'flowrate': COLOR_FLOWRATE,      # Teal #14B8A6
    'temperature': COLOR_TEMPERATURE, # Amber #F59E0B
    'pressure': COLOR_PRESSURE,       # Crimson #EF4444
    'equipment': COLOR_EQUIPMENT,     # Muted Violet #8B5CF6
}

UI_COLORS = {
    'deepIndigo': DEEP_INDIGO,
    'slateGray': SLATE_GRAY,
    'gridline': COLOR_GRIDLINE,
    'surface': PURE_WHITE,
    'background': OFF_WHITE,
}


def hex_to_rgba(hex_color: str, alpha: float = 1.0) -> tuple:
    """Convert hex color to RGBA tuple."""
    rgb = mcolors.hex2color(hex_color)
    return (*rgb, alpha)


def get_bar_color(hex_color: str, opacity: float = 0.8) -> tuple:
    """Get bar color with opacity (design.md: 0.7-0.85)."""
    return hex_to_rgba(hex_color, opacity)


def get_fill_color(hex_color: str, opacity: float = 0.13) -> tuple:
    """Get fill color with light opacity for line charts."""
    return hex_to_rgba(hex_color, opacity)


# ===================
# FONT CONFIGURATION
# ===================
FONT_CONFIG = {
    'family': 'sans-serif',
    'sans-serif': [FONT_PRIMARY, 'Roboto', 'Arial', 'sans-serif'],
}

FONT_SIZES = {
    'title': FONT_SIZE_H3,      # 16px
    'label': FONT_SIZE_BODY,    # 14px
    'tick': FONT_SIZE_CAPTION,  # 12px
    'legend': FONT_SIZE_CAPTION, # 12px
}


def apply_chart_style():
    """
    Apply global matplotlib style matching design.md.
    Call this before creating any charts.
    """
    plt.rcParams.update({
        # Font
        'font.family': FONT_CONFIG['family'],
        'font.sans-serif': FONT_CONFIG['sans-serif'],
        'font.size': FONT_SIZES['tick'],
        
        # Figure
        'figure.facecolor': PURE_WHITE,
        'figure.edgecolor': 'none',
        'figure.dpi': 100,
        
        # Axes
        'axes.facecolor': PURE_WHITE,
        'axes.edgecolor': 'none',
        'axes.labelcolor': DEEP_INDIGO,
        'axes.labelsize': FONT_SIZES['label'],
        'axes.labelweight': 'medium',
        'axes.titlesize': FONT_SIZES['title'],
        'axes.titleweight': 'medium',
        'axes.titlecolor': DEEP_INDIGO,
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.spines.left': False,
        'axes.spines.bottom': False,
        
        # Grid - soft gridlines per design.md
        'axes.grid': True,
        'axes.grid.axis': 'y',
        'grid.color': COLOR_GRIDLINE,
        'grid.linewidth': 1,
        'grid.linestyle': '-',
        'grid.alpha': 1.0,
        
        # Ticks
        'xtick.color': SLATE_GRAY,
        'ytick.color': SLATE_GRAY,
        'xtick.labelsize': FONT_SIZES['tick'],
        'ytick.labelsize': FONT_SIZES['tick'],
        'xtick.major.pad': 8,
        'ytick.major.pad': 8,
        'xtick.major.size': 0,
        'ytick.major.size': 0,
        
        # Legend
        'legend.fontsize': FONT_SIZES['legend'],
        'legend.frameon': False,
        'legend.labelcolor': SLATE_GRAY,
        
        # Lines
        'lines.linewidth': 2,
        'lines.markersize': 8,
    })


# ===================
# CHART-SPECIFIC CONFIGURATIONS
# ===================

EQUIPMENT_DISTRIBUTION_CONFIG = {
    'type': 'bar',
    'color': get_bar_color(CHART_COLORS['equipment'], 0.8),
    'edgecolor': 'none',
    'xlabel': 'Equipment Type',
    'ylabel': 'Count',
    'title': 'Equipment Type Distribution',
    'bar_width': 0.6,
    'show_legend': False,
    'show_x_grid': False,
    'show_y_grid': True,
}

TEMPERATURE_LINE_CONFIG = {
    'type': 'line',
    'line_color': CHART_COLORS['temperature'],
    'fill_color': get_fill_color(CHART_COLORS['temperature'], 0.13),
    'marker_face_color': CHART_COLORS['temperature'],
    'marker_edge_color': PURE_WHITE,
    'marker_edge_width': 2,
    'marker_size': 8,
    'marker': 'o',
    'xlabel': 'Equipment',
    'ylabel': 'Temperature (°C)',
    'title': 'Temperature vs Equipment',
    'show_legend': True,
    'legend_label': 'Temperature (°C)',
    'show_x_grid': False,
    'show_y_grid': True,
    'fill': True,
}

PRESSURE_DISTRIBUTION_CONFIG = {
    'type': 'bar',
    'color': get_bar_color(CHART_COLORS['pressure'], 0.8),
    'edgecolor': 'none',
    'xlabel': 'Pressure Range (bar)',
    'ylabel': 'Equipment Count',
    'title': 'Pressure Distribution',
    'bar_width': 0.6,
    'show_legend': False,
    'show_x_grid': False,
    'show_y_grid': True,
}


def get_chart_config(chart_type: str) -> Dict[str, Any]:
    """Get configuration for a specific chart type."""
    configs = {
        'equipment_distribution': EQUIPMENT_DISTRIBUTION_CONFIG,
        'temperature_line': TEMPERATURE_LINE_CONFIG,
        'pressure_distribution': PRESSURE_DISTRIBUTION_CONFIG,
    }
    return configs.get(chart_type, {})
