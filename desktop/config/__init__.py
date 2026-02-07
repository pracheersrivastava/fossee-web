"""
Config Package
CHEM•VIZ - Chemical Equipment Parameter Visualizer
"""

from config.pdf_report_config import (
    PDF_CONFIG,
    PDFReportConfig,
    get_pdf_styles,
    TYPOGRAPHY_SCALE,
    PDF_COLORS,
    SPACING,
    CHART_DEFINITIONS,
    DATA_TABLE_COLUMNS,
)

from config.pdf_generator import generate_pdf_report

__all__ = [
    "PDF_CONFIG",
    "PDFReportConfig",
    "get_pdf_styles",
    "TYPOGRAPHY_SCALE",
    "PDF_COLORS",
    "SPACING",
    "CHART_DEFINITIONS",
    "DATA_TABLE_COLUMNS",
    "generate_pdf_report",
]
