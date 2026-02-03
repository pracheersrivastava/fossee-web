"""
Config Package
FOSSEE Scientific Analytics UI
"""

from .pdf_report_config import (
    PDF_CONFIG,
    PDFReportConfig,
    get_pdf_styles,
    TYPOGRAPHY_SCALE,
    PDF_COLORS,
    SPACING,
    CHART_DEFINITIONS,
    DATA_TABLE_COLUMNS,
)

__all__ = [
    "PDF_CONFIG",
    "PDFReportConfig",
    "get_pdf_styles",
    "TYPOGRAPHY_SCALE",
    "PDF_COLORS",
    "SPACING",
    "CHART_DEFINITIONS",
    "DATA_TABLE_COLUMNS",
]
