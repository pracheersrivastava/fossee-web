"""
PDF Report Generator
CHEM•VIZ - Chemical Equipment Parameter Visualizer

Generates PDF reports using ReportLab, following design.md specifications.
Fetches data from backend API and creates professional analysis reports.
"""

import io
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

from PyQt5.QtWidgets import QFileDialog, QMessageBox, QWidget

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, mm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, Image, HRFlowable
    )
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
    from reportlab.graphics.shapes import Drawing, Rect, String
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.graphics.charts.linecharts import HorizontalLineChart
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from config.pdf_report_config import (
    PDF_CONFIG, PDF_COLORS, TYPOGRAPHY_SCALE, SPACING,
    FONT_FAMILY_PRIMARY, PAGE_MARGINS
)
from core.api_client import api_client


def hex_to_color(hex_color: str):
    """Convert hex color to ReportLab color."""
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16) / 255
    g = int(hex_color[2:4], 16) / 255
    b = int(hex_color[4:6], 16) / 255
    return colors.Color(r, g, b)


class PDFReportGenerator:
    """Generates PDF reports from backend analysis data."""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Set up custom paragraph styles."""
        # Report title
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            leading=32,
            textColor=hex_to_color(PDF_COLORS['deepIndigo']),
            spaceAfter=SPACING['lg'],
            alignment=TA_CENTER,
        ))
        
        # Section header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            leading=22,
            textColor=hex_to_color(PDF_COLORS['deepIndigo']),
            spaceBefore=SPACING['xl'],
            spaceAfter=SPACING['md'],
            borderWidth=1,
            borderColor=hex_to_color(PDF_COLORS['tableBorder']),
            borderPadding=SPACING['sm'],
        ))
        
        # Subsection header
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading3'],
            fontSize=13,
            leading=18,
            textColor=hex_to_color(PDF_COLORS['deepIndigo']),
            spaceBefore=SPACING['md'],
            spaceAfter=SPACING['sm'],
        ))
        
        # Body text (override default BodyText style)
        self.styles['BodyText'].fontSize = 11
        self.styles['BodyText'].leading = 16
        self.styles['BodyText'].textColor = hex_to_color(PDF_COLORS['deepIndigo'])
        
        # Caption (override if exists, else add)
        if 'Caption' in self.styles.byName:
            self.styles['Caption'].fontSize = 9
            self.styles['Caption'].leading = 13
            self.styles['Caption'].textColor = hex_to_color(PDF_COLORS['slateGray'])
            self.styles['Caption'].fontName = 'Helvetica-Oblique'
        else:
            self.styles.add(ParagraphStyle(
                name='Caption',
                parent=self.styles['Normal'],
                fontSize=9,
                leading=13,
                textColor=hex_to_color(PDF_COLORS['slateGray']),
                fontName='Helvetica-Oblique',
            ))
        
        # KPI Value
        self.styles.add(ParagraphStyle(
            name='KPIValue',
            parent=self.styles['Normal'],
            fontSize=18,
            leading=24,
            textColor=hex_to_color(PDF_COLORS['deepIndigo']),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
        ))
        
        # KPI Label
        self.styles.add(ParagraphStyle(
            name='KPILabel',
            parent=self.styles['Normal'],
            fontSize=9,
            leading=12,
            textColor=hex_to_color(PDF_COLORS['slateGray']),
            alignment=TA_CENTER,
        ))

    def generate_report(self, dataset_id: str, parent: Optional[QWidget] = None) -> bool:
        """
        Generate a PDF report for a dataset.
        
        Args:
            dataset_id: The backend dataset ID
            parent: Parent widget for file dialog
            
        Returns:
            True if generation succeeded
        """
        if not REPORTLAB_AVAILABLE:
            QMessageBox.warning(
                parent,
                "ReportLab Not Installed",
                "PDF generation requires ReportLab.\n\n"
                "Install it with: pip install reportlab"
            )
            return False
        
        # Fetch data from backend
        summary_data = api_client.get_summary(dataset_id)
        if not summary_data or 'error' in summary_data:
            QMessageBox.warning(
                parent,
                "Data Error",
                f"Could not fetch summary data:\n{summary_data.get('error', 'Unknown error')}"
            )
            return False
        
        analysis_data = api_client.get_analysis(dataset_id)
        if not analysis_data or 'error' in analysis_data:
            QMessageBox.warning(
                parent,
                "Data Error",
                f"Could not fetch analysis data:\n{analysis_data.get('error', 'Unknown error')}"
            )
            return False
        
        # Fetch dataset detail for equipment data table (data_preview)
        dataset_detail = api_client.get_dataset(dataset_id)
        
        # Ask user for save location
        default_name = f"CHEMVIZ_Report_{dataset_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
        file_path, _ = QFileDialog.getSaveFileName(
            parent,
            "Save PDF Report",
            default_name,
            "PDF Files (*.pdf)"
        )
        
        if not file_path:
            return False
        
        try:
            self._build_pdf(file_path, summary_data, analysis_data, dataset_detail)
            QMessageBox.information(
                parent,
                "Report Generated",
                f"PDF report saved to:\n{file_path}"
            )
            return True
        except Exception as e:
            QMessageBox.critical(
                parent,
                "PDF Error",
                f"Failed to generate PDF:\n{str(e)}"
            )
            return False

    def _build_pdf(self, file_path: str, summary_data: Dict[str, Any], analysis_data: Dict[str, Any], dataset_detail: Optional[Dict[str, Any]] = None):
        """Build the PDF document."""
        doc = SimpleDocTemplate(
            file_path,
            pagesize=A4,
            topMargin=PAGE_MARGINS['top'],
            bottomMargin=PAGE_MARGINS['bottom'],
            leftMargin=PAGE_MARGINS['left'],
            rightMargin=PAGE_MARGINS['right'],
        )
        
        story = []
        
        # Title
        story.append(Paragraph("CHEM•VIZ Analysis Report", self.styles['ReportTitle']))
        story.append(Spacer(1, SPACING['md']))
        
        # Metadata section
        story.extend(self._build_metadata_section(summary_data))
        
        # Summary KPIs
        story.extend(self._build_summary_section(summary_data))
        
        # Charts section
        story.extend(self._build_charts_section(analysis_data))
        
        # Data table
        story.append(PageBreak())
        story.extend(self._build_data_table(dataset_detail))
        
        # Build the document
        doc.build(story, onFirstPage=self._add_footer, onLaterPages=self._add_footer)

    def _build_metadata_section(self, summary_data: Dict[str, Any]) -> List:
        """Build the metadata section."""
        elements = []
        
        # Horizontal rule
        elements.append(HRFlowable(
            width="100%", 
            thickness=1, 
            color=hex_to_color(PDF_COLORS['tableBorder']),
            spaceAfter=SPACING['md']
        ))
        
        metadata = [
            ["Generated:", datetime.now().strftime("%Y-%m-%d %H:%M")],
            ["Dataset:", summary_data.get('dataset_name', 'Unknown')],
            ["Records:", str(summary_data.get('total_equipment', 0))],
            ["Status:", "Valid"],
        ]
        
        # Create 2-column layout
        table_data = []
        for i in range(0, len(metadata), 2):
            row = []
            for j in range(2):
                if i + j < len(metadata):
                    label, value = metadata[i + j]
                    row.extend([
                        Paragraph(f"<b>{label}</b>", self.styles['Caption']),
                        Paragraph(value, self.styles['BodyText']),
                    ])
                else:
                    row.extend(["", ""])
            table_data.append(row)
        
        table = Table(table_data, colWidths=[60, 150, 60, 150])
        table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, SPACING['lg']))
        
        return elements

    def _build_summary_section(self, summary_data: Dict[str, Any]) -> List:
        """Build the summary/KPI section."""
        elements = []
        
        elements.append(Paragraph("Summary", self.styles['SectionHeader']))
        
        # Build KPI data from backend /api/summary/<id>/ response
        total_equipment = summary_data.get('total_equipment', 0)
        avg_flowrate = summary_data.get('average_flowrate') or 0
        avg_temperature = summary_data.get('average_temperature') or 0
        dominant_type = summary_data.get('dominant_equipment_type', 'N/A')
        
        kpis = [
            ("Total Equipment", str(total_equipment), None),
            ("Avg Flowrate", f"{avg_flowrate:.1f}", "m³/hr"),
            ("Avg Temperature", f"{avg_temperature:.1f}", "°C"),
            ("Dominant Type", str(dominant_type), None),
        ]
        
        # Create KPI cards as a table
        kpi_row = []
        for title, value, unit in kpis:
            display_value = f"{value} {unit}" if unit else value
            cell = [
                Paragraph(display_value, self.styles['KPIValue']),
                Paragraph(title, self.styles['KPILabel']),
            ]
            kpi_row.append(cell)
        
        # Flatten to table format
        kpi_table_data = [
            [kpi[0] for kpi in kpi_row],
            [kpi[1] for kpi in kpi_row],
        ]
        
        kpi_table = Table(kpi_table_data, colWidths=[110, 110, 110, 110])
        kpi_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (0, -1), 1, hex_to_color(PDF_COLORS['tableBorder'])),
            ('BOX', (1, 0), (1, -1), 1, hex_to_color(PDF_COLORS['tableBorder'])),
            ('BOX', (2, 0), (2, -1), 1, hex_to_color(PDF_COLORS['tableBorder'])),
            ('BOX', (3, 0), (3, -1), 1, hex_to_color(PDF_COLORS['tableBorder'])),
            ('BACKGROUND', (0, 0), (-1, -1), hex_to_color(PDF_COLORS['pureWhite'])),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        
        elements.append(kpi_table)
        elements.append(Spacer(1, SPACING['lg']))
        
        return elements

    def _build_charts_section(self, analysis_data: Dict[str, Any]) -> List:
        """Build the charts section using same data keys as desktop/web charts."""
        elements = []
        
        elements.append(Paragraph("Data Visualization", self.styles['SectionHeader']))
        
        # Equipment Distribution Chart (Muted Violet #8B5CF6)
        equip_dist = analysis_data.get('equipment_type_distribution', {})
        equip_labels = equip_dist.get('labels', [])
        equip_data = equip_dist.get('data', [])
        if equip_labels and equip_data:
            elements.append(Paragraph("Equipment Distribution by Type", self.styles['SubsectionHeader']))
            chart = self._create_bar_chart(
                equip_labels,
                equip_data,
                hex_to_color(PDF_COLORS['equipment']),
                width=450,
                height=180
            )
            elements.append(chart)
            elements.append(Spacer(1, SPACING['md']))
        
        # Temperature and Pressure side by side
        temp_data = analysis_data.get('temperature_by_equipment', {})
        temp_labels = temp_data.get('labels', [])
        temp_values = temp_data.get('data', [])
        
        pressure_data = analysis_data.get('pressure_distribution', {})
        pressure_labels = pressure_data.get('labels', [])
        pressure_values = pressure_data.get('data', [])
        
        if temp_values or pressure_values:
            chart_row = []
            
            if temp_values:
                temp_chart = self._create_line_chart(
                    temp_values[:20],
                    hex_to_color(PDF_COLORS['temperature']),
                    "Temperature vs Equipment",
                    width=210,
                    height=140
                )
                chart_row.append(temp_chart)
            
            if pressure_values:
                pressure_chart = self._create_bar_chart(
                    pressure_labels[:10],
                    pressure_values[:10],
                    hex_to_color(PDF_COLORS['pressure']),
                    width=210,
                    height=140
                )
                chart_row.append(pressure_chart)
            
            if chart_row:
                charts_table = Table([chart_row], colWidths=[215, 215])
                elements.append(charts_table)
                elements.append(Spacer(1, SPACING['lg']))
        
        return elements

    def _create_bar_chart(self, labels: List[str], values: List[float], 
                          color, width: int = 400, height: int = 150) -> Drawing:
        """Create a bar chart drawing."""
        drawing = Drawing(width, height)
        
        chart = VerticalBarChart()
        chart.x = 50
        chart.y = 20
        chart.width = width - 80
        chart.height = height - 40
        
        chart.data = [values]
        chart.categoryAxis.categoryNames = labels
        chart.categoryAxis.labels.fontName = FONT_FAMILY_PRIMARY
        chart.categoryAxis.labels.fontSize = 8
        chart.categoryAxis.labels.angle = 45 if len(labels) > 5 else 0
        
        chart.valueAxis.valueMin = 0
        chart.valueAxis.labels.fontName = FONT_FAMILY_PRIMARY
        chart.valueAxis.labels.fontSize = 8
        
        chart.bars[0].fillColor = color
        chart.bars[0].strokeWidth = 0
        
        drawing.add(chart)
        return drawing

    def _create_line_chart(self, values: List[float], color,
                           title: str = "", width: int = 400, height: int = 150) -> Drawing:
        """Create a line chart drawing."""
        drawing = Drawing(width, height)
        
        chart = HorizontalLineChart()
        chart.x = 40
        chart.y = 20
        chart.width = width - 60
        chart.height = height - 40
        
        chart.data = [values]
        chart.categoryAxis.categoryNames = [str(i+1) for i in range(len(values))]
        chart.categoryAxis.labels.fontName = FONT_FAMILY_PRIMARY
        chart.categoryAxis.labels.fontSize = 7
        
        chart.valueAxis.labels.fontName = FONT_FAMILY_PRIMARY
        chart.valueAxis.labels.fontSize = 8
        
        chart.lines[0].strokeColor = color
        chart.lines[0].strokeWidth = 2
        
        drawing.add(chart)
        return drawing

    def _build_data_table(self, dataset_detail: Optional[Dict[str, Any]] = None) -> List:
        """Build the data table section from dataset detail's data_preview."""
        elements = []
        
        elements.append(Paragraph("Equipment Data", self.styles['SectionHeader']))
        
        # Get table data from dataset detail's data_preview
        table_data = []
        if dataset_detail and isinstance(dataset_detail, dict):
            table_data = dataset_detail.get('data_preview', [])
        
        if not table_data:
            elements.append(Paragraph("No data available.", self.styles['BodyText']))
            return elements
        
        # Limit to 20 rows
        display_data = table_data[:20]
        truncated = len(table_data) > 20
        
        # Use actual column names from the data
        headers = list(display_data[0].keys()) if display_data else []
        
        # Build table data
        pdf_table_data = [headers]
        for row in display_data:
            pdf_table_data.append([
                str(row.get(h, '')) for h in headers
            ])
        
        # Calculate even column widths based on number of columns
        num_cols = len(headers) if headers else 1
        col_width = 450 / num_cols
        table = Table(pdf_table_data, colWidths=[col_width] * num_cols)
        table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), hex_to_color(PDF_COLORS['tableHeader'])),
            ('TEXTCOLOR', (0, 0), (-1, 0), hex_to_color(PDF_COLORS['deepIndigo'])),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), FONT_FAMILY_PRIMARY),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            
            # Zebra striping
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), 
             [hex_to_color(PDF_COLORS['pureWhite']), hex_to_color(PDF_COLORS['tableZebra'])]),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, hex_to_color(PDF_COLORS['tableBorder'])),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(table)
        
        if truncated:
            elements.append(Spacer(1, SPACING['sm']))
            elements.append(Paragraph(
                f"Showing first 20 of {len(table_data)} records.",
                self.styles['Caption']
            ))
        
        return elements

    def _add_footer(self, canvas, doc):
        """Add footer to each page."""
        canvas.saveState()
        
        # Footer line
        canvas.setStrokeColor(hex_to_color(PDF_COLORS['tableBorder']))
        canvas.setLineWidth(1)
        canvas.line(
            PAGE_MARGINS['left'], 
            PAGE_MARGINS['bottom'] - 10,
            A4[0] - PAGE_MARGINS['right'],
            PAGE_MARGINS['bottom'] - 10
        )
        
        # Footer text
        canvas.setFont(FONT_FAMILY_PRIMARY, 8)
        canvas.setFillColor(hex_to_color(PDF_COLORS['slateGray']))
        
        # Left: Project info
        canvas.drawString(
            PAGE_MARGINS['left'],
            PAGE_MARGINS['bottom'] - 25,
            "Generated by CHEM•VIZ"
        )
        
        # Center: Page number
        page_text = f"Page {doc.page}"
        text_width = canvas.stringWidth(page_text, FONT_FAMILY_PRIMARY, 8)
        canvas.drawString(
            (A4[0] - text_width) / 2,
            PAGE_MARGINS['bottom'] - 25,
            page_text
        )
        
        # Right: Date
        canvas.drawRightString(
            A4[0] - PAGE_MARGINS['right'],
            PAGE_MARGINS['bottom'] - 25,
            datetime.now().strftime("%Y-%m-%d")
        )
        
        canvas.restoreState()


# Module-level generator instance
_generator = None


def generate_pdf_report(dataset_id: str, parent: Optional[QWidget] = None) -> bool:
    """
    Generate a PDF report for a dataset.
    
    This is the main entry point called from main_window.py.
    
    Args:
        dataset_id: The backend dataset ID
        parent: Parent widget for dialogs
        
    Returns:
        True if generation succeeded
    """
    global _generator
    
    if not REPORTLAB_AVAILABLE:
        QMessageBox.warning(
            parent,
            "ReportLab Not Installed",
            "PDF generation requires ReportLab.\n\n"
            "Install it with: pip install reportlab"
        )
        return False
    
    if _generator is None:
        _generator = PDFReportGenerator()
    
    return _generator.generate_report(dataset_id, parent)
