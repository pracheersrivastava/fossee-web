"""
PDF Report Layout Configuration
FOSSEE Scientific Analytics UI - CHEM•VIZ

Defines the full layout and styling for generated PDF reports.
Follows design.md specifications for academic, data-first presentation.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


# =============================================================================
# Page Setup
# =============================================================================

PAGE_SIZE = "A4"
PAGE_ORIENTATION = "portrait"
PAGE_MARGINS = {
    "top": 72,      # 1 inch = 72pt
    "bottom": 72,
    "left": 56,     # ~0.78 inch
    "right": 56,
}
# Content area: 483pt width (≈170mm)


# =============================================================================
# Typography
# PDF-safe fonts with fallbacks
# =============================================================================

FONT_FAMILY_PRIMARY = "Helvetica"
FONT_FAMILY_FALLBACK = "Arial"
FONT_FAMILY_MONOSPACE = "Courier"

# Type scale (in points)
TYPOGRAPHY_SCALE = {
    "reportTitle": {"size": 24, "weight": "bold", "lineHeight": 32, "color": "#1E2A38"},
    "sectionHeader": {"size": 16, "weight": "bold", "lineHeight": 22, "color": "#1E2A38"},
    "subsectionHeader": {"size": 13, "weight": "bold", "lineHeight": 18, "color": "#1E2A38"},
    "body": {"size": 11, "weight": "normal", "lineHeight": 16, "color": "#1E2A38"},
    "tableHeader": {"size": 10, "weight": "bold", "lineHeight": 14, "color": "#1E2A38"},
    "tableCell": {"size": 10, "weight": "normal", "lineHeight": 14, "color": "#1E2A38"},
    "caption": {"size": 9, "weight": "normal", "lineHeight": 13, "color": "#6B7280"},
    "footer": {"size": 8, "weight": "normal", "lineHeight": 12, "color": "#6B7280"},
}


# =============================================================================
# Color Palette (CMYK-safe versions of design tokens)
# =============================================================================

PDF_COLORS = {
    # Core
    "deepIndigo": "#1E2A38",
    "academicBlue": "#2F80ED",
    "slateGray": "#6B7280",
    "offWhite": "#F8FAFC",
    "pureWhite": "#FFFFFF",
    
    # Data Visualization
    "flowrate": "#14B8A6",
    "temperature": "#F59E0B",
    "pressure": "#EF4444",
    "equipment": "#8B5CF6",
    
    # Status
    "success": "#22C55E",
    "warning": "#F59E0B",
    "error": "#DC2626",
    
    # Table
    "tableHeader": "#F1F5F9",
    "tableZebra": "#FAFAFA",
    "tableBorder": "#E5E7EB",
}


# =============================================================================
# Spacing (in points, base unit: 8pt)
# =============================================================================

SPACING = {
    "xs": 4,
    "sm": 8,
    "md": 16,
    "lg": 24,
    "xl": 32,
    "xxl": 48,
}


# =============================================================================
# Section Configurations
# =============================================================================

@dataclass
class HeaderConfig:
    """PDF header configuration (every page)."""
    height: int = 48
    logo_width: int = 100
    title: str = "CHEM•VIZ Analysis Report"
    badge_text: str = "FOSSEE"
    badge_bg_color: str = "#2F80ED"
    badge_text_color: str = "#FFFFFF"
    border_color: str = "#E5E7EB"
    border_width: int = 1


@dataclass
class MetadataField:
    """Report metadata field."""
    label: str
    key: str


@dataclass
class MetadataConfig:
    """Report metadata section configuration."""
    margin_top: int = 24
    margin_bottom: int = 32
    fields: List[MetadataField] = field(default_factory=lambda: [
        MetadataField("Generated", "timestamp"),
        MetadataField("Dataset", "filename"),
        MetadataField("Records", "rowCount"),
        MetadataField("Status", "validationStatus"),
    ])
    layout: str = "twoColumn"


@dataclass
class KPIMetric:
    """KPI card metric definition."""
    key: str
    label: str
    unit: Optional[str] = None
    icon: str = ""


@dataclass
class SummaryConfig:
    """Summary/KPI section configuration."""
    title: str = "Summary"
    margin_bottom: int = 24
    metrics: List[KPIMetric] = field(default_factory=lambda: [
        KPIMetric("totalEquipment", "Total Equipment", icon="⚙"),
        KPIMetric("avgFlowrate", "Avg Flowrate", "m³/hr", "◎"),
        KPIMetric("avgTemperature", "Avg Temperature", "°C", "◐"),
        KPIMetric("dominantType", "Dominant Type", icon="▤"),
    ])
    card_bg_color: str = "#FFFFFF"
    card_border_radius: int = 6
    card_border_color: str = "#E5E7EB"
    card_padding: int = 12
    value_size: int = 18
    label_size: int = 9


@dataclass
class ChartDefinition:
    """Single chart definition."""
    id: str
    title: str
    chart_type: str  # 'bar' or 'line'
    color: str
    width: str
    height: int
    position: Optional[str] = None
    fill_opacity: Optional[float] = None


CHART_DEFINITIONS = [
    ChartDefinition(
        id="equipmentDistribution",
        title="Equipment Distribution by Type",
        chart_type="bar",
        color="#8B5CF6",
        width="100%",
        height=200,
    ),
    ChartDefinition(
        id="temperatureProfile",
        title="Temperature Profile",
        chart_type="line",
        color="#F59E0B",
        width="48%",
        height=160,
        position="left",
        fill_opacity=0.15,
    ),
    ChartDefinition(
        id="pressureDistribution",
        title="Pressure Distribution",
        chart_type="bar",
        color="#EF4444",
        width="48%",
        height=160,
        position="right",
    ),
]


@dataclass
class ChartStyleConfig:
    """Chart styling configuration."""
    background_color: str = "#FFFFFF"
    gridline_color: str = "#E5E7EB"
    gridline_width: float = 0.5
    axis_color: str = "#6B7280"
    font_size: int = 9
    bar_border_radius: int = 2
    bar_border_width: int = 0
    bar_opacity: float = 0.85
    line_stroke_width: int = 2
    line_point_radius: int = 0
    line_fill_opacity: float = 0.15


@dataclass
class TableColumn:
    """Data table column definition."""
    key: str
    label: str
    width: str
    align: str = "left"


DATA_TABLE_COLUMNS = [
    TableColumn("id", "ID", "12%", "left"),
    TableColumn("type", "Type", "18%", "left"),
    TableColumn("temperature", "Temp (°C)", "17%", "right"),
    TableColumn("pressure", "Pressure (bar)", "17%", "right"),
    TableColumn("flowrate", "Flowrate (m³/hr)", "18%", "right"),
    TableColumn("status", "Status", "18%", "center"),
]


@dataclass
class DataTableConfig:
    """Data table section configuration."""
    title: str = "Equipment Data"
    margin_bottom: int = 24
    max_rows: int = 20
    columns: List[TableColumn] = field(default_factory=lambda: DATA_TABLE_COLUMNS)
    header_bg_color: str = "#F1F5F9"
    header_text_color: str = "#1E2A38"
    row_height: int = 24
    zebra_color: str = "#FAFAFA"
    border_color: str = "#E5E7EB"
    
    # Status badge colors
    status_badges: Dict[str, Dict[str, str]] = field(default_factory=lambda: {
        "active": {"background": "#DCFCE7", "text": "#22C55E"},
        "inactive": {"background": "#FEE2E2", "text": "#DC2626"},
        "maintenance": {"background": "#FEF3C7", "text": "#B45309"},
    })


@dataclass
class FooterConfig:
    """PDF footer configuration (every page)."""
    height: int = 36
    border_color: str = "#E5E7EB"
    border_width: int = 1
    left_text: str = "FOSSEE Project, IIT Bombay"
    center_text: str = "Page {page} of {pages}"
    right_text: str = "Generated by CHEM•VIZ"


# =============================================================================
# Page Break Rules
# =============================================================================

PAGE_BREAK_RULES = {
    "forceBreakBefore": ["dataTable"],
    "keepTogether": ["kpiCards", "chart"],
    "orphanThreshold": 72,  # 1 inch
}


# =============================================================================
# Complete PDF Report Configuration
# =============================================================================

@dataclass
class PDFReportConfig:
    """Complete PDF report configuration."""
    page_size: str = PAGE_SIZE
    page_orientation: str = PAGE_ORIENTATION
    page_margins: Dict[str, int] = field(default_factory=lambda: PAGE_MARGINS)
    
    header: HeaderConfig = field(default_factory=HeaderConfig)
    metadata: MetadataConfig = field(default_factory=MetadataConfig)
    summary: SummaryConfig = field(default_factory=SummaryConfig)
    charts: List[ChartDefinition] = field(default_factory=lambda: CHART_DEFINITIONS)
    chart_style: ChartStyleConfig = field(default_factory=ChartStyleConfig)
    data_table: DataTableConfig = field(default_factory=DataTableConfig)
    footer: FooterConfig = field(default_factory=FooterConfig)
    
    def get_typography(self, style_name: str) -> Dict[str, Any]:
        """Get typography settings for a style name."""
        return TYPOGRAPHY_SCALE.get(style_name, TYPOGRAPHY_SCALE["body"])
    
    def get_color(self, color_name: str) -> str:
        """Get color by name."""
        return PDF_COLORS.get(color_name, "#1E2A38")
    
    def get_spacing(self, size: str) -> int:
        """Get spacing value."""
        return SPACING.get(size, 8)


# Default configuration instance
PDF_CONFIG = PDFReportConfig()


def get_pdf_styles() -> Dict[str, Dict[str, Any]]:
    """
    Generate PDF-ready styles dictionary.
    
    Returns:
        Dictionary of style definitions for PDF rendering.
    """
    return {
        "reportTitle": {
            "font": FONT_FAMILY_PRIMARY,
            "fontSize": TYPOGRAPHY_SCALE["reportTitle"]["size"],
            "fontWeight": TYPOGRAPHY_SCALE["reportTitle"]["weight"],
            "color": TYPOGRAPHY_SCALE["reportTitle"]["color"],
            "lineHeight": TYPOGRAPHY_SCALE["reportTitle"]["lineHeight"],
            "marginBottom": SPACING["lg"],
        },
        "sectionHeader": {
            "font": FONT_FAMILY_PRIMARY,
            "fontSize": TYPOGRAPHY_SCALE["sectionHeader"]["size"],
            "fontWeight": TYPOGRAPHY_SCALE["sectionHeader"]["weight"],
            "color": TYPOGRAPHY_SCALE["sectionHeader"]["color"],
            "lineHeight": TYPOGRAPHY_SCALE["sectionHeader"]["lineHeight"],
            "marginTop": SPACING["xl"],
            "marginBottom": SPACING["md"],
            "borderBottom": f"1px solid {PDF_COLORS['tableBorder']}",
            "paddingBottom": SPACING["sm"],
        },
        "body": {
            "font": FONT_FAMILY_PRIMARY,
            "fontSize": TYPOGRAPHY_SCALE["body"]["size"],
            "color": TYPOGRAPHY_SCALE["body"]["color"],
            "lineHeight": TYPOGRAPHY_SCALE["body"]["lineHeight"],
        },
        "caption": {
            "font": FONT_FAMILY_PRIMARY,
            "fontSize": TYPOGRAPHY_SCALE["caption"]["size"],
            "color": PDF_COLORS["slateGray"],
            "lineHeight": TYPOGRAPHY_SCALE["caption"]["lineHeight"],
            "fontStyle": "italic",
        },
        "tableHeader": {
            "font": FONT_FAMILY_PRIMARY,
            "fontSize": TYPOGRAPHY_SCALE["tableHeader"]["size"],
            "fontWeight": TYPOGRAPHY_SCALE["tableHeader"]["weight"],
            "color": PDF_COLORS["deepIndigo"],
            "backgroundColor": PDF_COLORS["tableHeader"],
        },
        "tableCell": {
            "font": FONT_FAMILY_PRIMARY,
            "fontSize": TYPOGRAPHY_SCALE["tableCell"]["size"],
            "color": PDF_COLORS["deepIndigo"],
        },
        "footer": {
            "font": FONT_FAMILY_PRIMARY,
            "fontSize": TYPOGRAPHY_SCALE["footer"]["size"],
            "color": PDF_COLORS["slateGray"],
        },
    }
