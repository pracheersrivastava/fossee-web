/**
 * PDF Report Generator Service
 * CHEM•VIZ - Chemical Equipment Parameter Visualizer
 * 
 * Generates PDF reports using jsPDF following design.md specifications.
 * Fetches analysis data from backend and creates professional reports.
 */

import { jsPDF } from 'jspdf';
import { PDF_REPORT_CONFIG } from '../config/pdfReportConfig';
import { getDatasetSummary, getAnalysis, getDataset } from './api';

/**
 * Convert hex color to RGB array
 */
function hexToRgb(hex) {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result ? [
    parseInt(result[1], 16),
    parseInt(result[2], 16),
    parseInt(result[3], 16)
  ] : [0, 0, 0];
}

/**
 * PDF Report Generator Class
 */
class PDFReportGenerator {
  constructor() {
    this.config = PDF_REPORT_CONFIG;
    this.doc = null;
    this.pageWidth = 0;
    this.pageHeight = 0;
    this.contentWidth = 0;
    this.currentY = 0;
  }

  /**
   * Generate PDF report for a dataset
   * @param {string} datasetId - Dataset ID from backend
   * @returns {Promise<Blob>} PDF file blob
   */
  async generate(datasetId) {
    // Initialize document
    this.doc = new jsPDF({
      orientation: this.config.page.orientation,
      unit: 'pt',
      format: this.config.page.size.toLowerCase(),
    });

    // Get page dimensions
    this.pageWidth = this.doc.internal.pageSize.getWidth();
    this.pageHeight = this.doc.internal.pageSize.getHeight();
    this.contentWidth = this.pageWidth - this.config.page.margins.left - this.config.page.margins.right;
    
    // Reset Y position
    this.currentY = this.config.page.margins.top;

    // Fetch data
    const [datasetInfo, summaryData, analysisData] = await Promise.all([
      getDataset(datasetId),
      getDatasetSummary(datasetId),
      getAnalysis(datasetId),
    ]);

    // Build document sections
    this._drawHeader();
    this._drawMetadata(datasetInfo, summaryData);
    this._drawSummarySection(summaryData.kpis);
    this._drawChartsSection(analysisData.chartData);
    this._addNewPage();
    this._drawDataTable(summaryData.previewData, summaryData.previewHeaders);
    this._drawFooter();

    // Return as blob
    return this.doc.output('blob');
  }

  /**
   * Generate and download PDF
   * @param {string} datasetId - Dataset ID
   * @param {string} [filename] - Optional filename
   */
  async downloadReport(datasetId, filename) {
    const blob = await this.generate(datasetId);
    
    // Create download link
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename || `CHEMVIZ_Report_${datasetId}_${new Date().toISOString().split('T')[0]}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  /**
   * Draw page header
   */
  _drawHeader() {
    const margin = this.config.page.margins;
    const headerConfig = this.config.sections.header;

    // Title
    this.doc.setFont('Helvetica', 'bold');
    this.doc.setFontSize(headerConfig.title.style === 'reportTitle' ? 24 : 16);
    this.doc.setTextColor(...hexToRgb(this.config.colors.deepIndigo));
    this.doc.text(
      headerConfig.title.text,
      this.pageWidth / 2,
      this.currentY,
      { align: 'center' }
    );

    this.currentY += 36;

    // Border line
    this.doc.setDrawColor(...hexToRgb(this.config.colors.tableBorder));
    this.doc.setLineWidth(headerConfig.borderBottom.width);
    this.doc.line(
      margin.left,
      this.currentY,
      this.pageWidth - margin.right,
      this.currentY
    );

    this.currentY += this.config.spacing.md;
  }

  /**
   * Draw metadata section
   */
  _drawMetadata(datasetInfo, summaryData) {
    const margin = this.config.page.margins;
    const metaConfig = this.config.sections.metadata;

    this.currentY += metaConfig.marginTop;

    const metadata = [
      { label: 'Generated', value: new Date().toLocaleString() },
      { label: 'Dataset', value: datasetInfo.original_filename || 'Unknown' },
      { label: 'Records', value: String(datasetInfo.row_count || 0) },
      { label: 'Status', value: summaryData.kpis.totalEquipment > 0 ? 'Valid' : 'Unknown' },
    ];

    // Draw in 2x2 grid
    const cellWidth = this.contentWidth / 2;
    const startX = margin.left;
    let currentX = startX;
    let rowY = this.currentY;

    metadata.forEach((item, idx) => {
      // Label
      this.doc.setFont('Helvetica', 'normal');
      this.doc.setFontSize(9);
      this.doc.setTextColor(...hexToRgb(this.config.colors.slateGray));
      this.doc.text(item.label + ':', currentX, rowY);

      // Value
      this.doc.setFont('Helvetica', 'normal');
      this.doc.setFontSize(11);
      this.doc.setTextColor(...hexToRgb(this.config.colors.deepIndigo));
      this.doc.text(item.value, currentX + 60, rowY);

      // Move to next cell
      if ((idx + 1) % 2 === 0) {
        currentX = startX;
        rowY += 20;
      } else {
        currentX += cellWidth;
      }
    });

    this.currentY = rowY + metaConfig.marginBottom;
  }

  /**
   * Draw summary/KPI section
   */
  _drawSummarySection(kpis) {
    const margin = this.config.page.margins;
    const summaryConfig = this.config.sections.summary;

    // Section title
    this._drawSectionTitle(summaryConfig.title);

    // KPI cards in 4-column layout
    const cardWidth = (this.contentWidth - 3 * 10) / 4; // 10pt gap between cards
    const cardHeight = 60;
    let cardX = margin.left;

    const kpiItems = [
      { label: 'Total Equipment', value: String(kpis.totalEquipment || 0) },
      { label: 'Avg Flowrate', value: `${(kpis.avgFlowrate || 0).toFixed(1)} m³/hr` },
      { label: 'Avg Temperature', value: `${(kpis.avgTemperature || 0).toFixed(1)} °C` },
      { label: 'Dominant Type', value: kpis.dominantType || '—' },
    ];

    kpiItems.forEach((kpi, idx) => {
      // Card border
      this.doc.setDrawColor(...hexToRgb(this.config.colors.tableBorder));
      this.doc.setLineWidth(1);
      this.doc.roundedRect(cardX, this.currentY, cardWidth, cardHeight, 4, 4, 'S');

      // Value
      this.doc.setFont('Helvetica', 'bold');
      this.doc.setFontSize(18);
      this.doc.setTextColor(...hexToRgb(this.config.colors.deepIndigo));
      this.doc.text(
        kpi.value,
        cardX + cardWidth / 2,
        this.currentY + 28,
        { align: 'center' }
      );

      // Label
      this.doc.setFont('Helvetica', 'normal');
      this.doc.setFontSize(9);
      this.doc.setTextColor(...hexToRgb(this.config.colors.slateGray));
      this.doc.text(
        kpi.label,
        cardX + cardWidth / 2,
        this.currentY + 45,
        { align: 'center' }
      );

      cardX += cardWidth + 10;
    });

    this.currentY += cardHeight + summaryConfig.marginBottom;
  }

  /**
   * Draw charts section
   */
  _drawChartsSection(chartData) {
    const margin = this.config.page.margins;
    const chartsConfig = this.config.sections.charts;

    // Section title
    this._drawSectionTitle(chartsConfig.title);

    // Equipment Distribution Bar Chart
    if (chartData.equipmentTypes?.labels?.length > 0) {
      this._drawSubsectionTitle('Equipment Distribution by Type');
      this._drawBarChart(
        chartData.equipmentTypes.labels,
        chartData.equipmentTypes.data,
        this.config.colors.equipment,
        this.contentWidth,
        160
      );
      this.currentY += 20;
    }

    // Check if we have room for the next charts
    if (this.currentY > this.pageHeight - 250) {
      this._addNewPage();
    }

    // Temperature and Pressure side by side
    const chartWidth = (this.contentWidth - 20) / 2;

    if (chartData.temperatureVsEquipment?.data?.length > 0) {
      const tempStartX = margin.left;
      const tempStartY = this.currentY;
      
      this._drawSubsectionTitle('Temperature Profile');
      this._drawBarChart(
        chartData.temperatureVsEquipment.labels.slice(0, 10),
        chartData.temperatureVsEquipment.data.slice(0, 10),
        this.config.colors.temperature,
        chartWidth,
        120,
        tempStartX
      );
    }

    if (chartData.pressureDistribution?.data?.length > 0) {
      const pressStartX = margin.left + chartWidth + 20;
      
      // Reset Y for second chart in row
      if (chartData.temperatureVsEquipment?.data?.length > 0) {
        this.currentY -= 140; // Go back up to draw side by side
      }
      
      this.doc.setFont('Helvetica', 'bold');
      this.doc.setFontSize(10);
      this.doc.setTextColor(...hexToRgb(this.config.colors.deepIndigo));
      this.doc.text('Pressure Distribution', pressStartX, this.currentY);
      this.currentY += 16;
      
      this._drawBarChart(
        chartData.pressureDistribution.labels,
        chartData.pressureDistribution.data,
        this.config.colors.pressure,
        chartWidth,
        120,
        pressStartX
      );
    }

    this.currentY += chartsConfig.marginBottom;
  }

  /**
   * Draw a simple bar chart
   */
  _drawBarChart(labels, values, color, width, height, startX = null) {
    const margin = this.config.page.margins;
    const x = startX || margin.left;
    const y = this.currentY;

    if (!values || values.length === 0) return;

    const maxValue = Math.max(...values);
    const barCount = values.length;
    const barWidth = Math.min(40, (width - 40) / barCount - 5);
    const chartHeight = height - 30;

    // Draw bars
    const barColor = hexToRgb(color);
    this.doc.setFillColor(...barColor);

    values.forEach((value, idx) => {
      const barHeight = (value / maxValue) * chartHeight;
      const barX = x + 30 + idx * (barWidth + 5);
      const barY = y + chartHeight - barHeight;

      this.doc.roundedRect(barX, barY, barWidth, barHeight, 2, 2, 'F');

      // Label
      this.doc.setFontSize(7);
      this.doc.setTextColor(...hexToRgb(this.config.colors.slateGray));
      const label = String(labels[idx]).substring(0, 8);
      this.doc.text(label, barX + barWidth / 2, y + chartHeight + 12, { align: 'center' });
    });

    // Y-axis line
    this.doc.setDrawColor(...hexToRgb(this.config.colors.tableBorder));
    this.doc.setLineWidth(0.5);
    this.doc.line(x + 25, y, x + 25, y + chartHeight);

    // X-axis line
    this.doc.line(x + 25, y + chartHeight, x + width - 10, y + chartHeight);

    this.currentY = y + height;
  }

  /**
   * Draw data table section
   */
  _drawDataTable(data, headers) {
    const margin = this.config.page.margins;
    const tableConfig = this.config.sections.dataTable;

    // Section title
    this._drawSectionTitle(tableConfig.title);

    if (!data || data.length === 0) {
      this.doc.setFont('Helvetica', 'normal');
      this.doc.setFontSize(11);
      this.doc.setTextColor(...hexToRgb(this.config.colors.slateGray));
      this.doc.text('No data available.', margin.left, this.currentY);
      return;
    }

    // Limit rows
    const displayData = data.slice(0, tableConfig.maxRows);
    const displayHeaders = headers.slice(0, 6); // Max 6 columns for width

    const colWidth = this.contentWidth / displayHeaders.length;
    const rowHeight = tableConfig.style.rowHeight || 20;

    // Draw header row
    this.doc.setFillColor(...hexToRgb(tableConfig.style.headerBackground));
    this.doc.rect(margin.left, this.currentY, this.contentWidth, rowHeight, 'F');

    this.doc.setFont('Helvetica', 'bold');
    this.doc.setFontSize(9);
    this.doc.setTextColor(...hexToRgb(tableConfig.style.headerTextColor));

    displayHeaders.forEach((header, idx) => {
      const cellX = margin.left + idx * colWidth + 4;
      this.doc.text(String(header).substring(0, 15), cellX, this.currentY + 14);
    });

    this.currentY += rowHeight;

    // Draw data rows
    displayData.forEach((row, rowIdx) => {
      // Zebra striping
      if (rowIdx % 2 === 1) {
        this.doc.setFillColor(...hexToRgb(tableConfig.style.zebraColor));
        this.doc.rect(margin.left, this.currentY, this.contentWidth, rowHeight, 'F');
      }

      this.doc.setFont('Helvetica', 'normal');
      this.doc.setFontSize(9);
      this.doc.setTextColor(...hexToRgb(this.config.colors.deepIndigo));

      displayHeaders.forEach((header, colIdx) => {
        const cellX = margin.left + colIdx * colWidth + 4;
        const value = row[header] ?? row[colIdx] ?? '';
        const displayValue = String(value).substring(0, 12);
        this.doc.text(displayValue, cellX, this.currentY + 14);
      });

      this.currentY += rowHeight;

      // Page break if needed
      if (this.currentY > this.pageHeight - margin.bottom - 50) {
        this._addNewPage();
      }
    });

    // Draw table border
    this.doc.setDrawColor(...hexToRgb(tableConfig.style.borderColor));
    this.doc.setLineWidth(0.5);
    const tableHeight = (displayData.length + 1) * rowHeight;
    this.doc.rect(margin.left, this.currentY - tableHeight, this.contentWidth, tableHeight, 'S');

    // Truncation notice
    if (data.length > tableConfig.maxRows) {
      this.currentY += 10;
      this.doc.setFont('Helvetica', 'italic');
      this.doc.setFontSize(9);
      this.doc.setTextColor(...hexToRgb(this.config.colors.slateGray));
      this.doc.text(
        `Showing first ${tableConfig.maxRows} of ${data.length} records.`,
        margin.left,
        this.currentY
      );
    }
  }

  /**
   * Draw section title
   */
  _drawSectionTitle(title) {
    const margin = this.config.page.margins;

    this.doc.setFont('Helvetica', 'bold');
    this.doc.setFontSize(16);
    this.doc.setTextColor(...hexToRgb(this.config.colors.deepIndigo));
    this.doc.text(title, margin.left, this.currentY);

    this.currentY += 8;

    // Border line
    this.doc.setDrawColor(...hexToRgb(this.config.colors.tableBorder));
    this.doc.setLineWidth(0.5);
    this.doc.line(margin.left, this.currentY, this.pageWidth - margin.right, this.currentY);

    this.currentY += this.config.spacing.md;
  }

  /**
   * Draw subsection title
   */
  _drawSubsectionTitle(title) {
    const margin = this.config.page.margins;

    this.doc.setFont('Helvetica', 'bold');
    this.doc.setFontSize(10);
    this.doc.setTextColor(...hexToRgb(this.config.colors.deepIndigo));
    this.doc.text(title, margin.left, this.currentY);

    this.currentY += 16;
  }

  /**
   * Add new page
   */
  _addNewPage() {
    this.doc.addPage();
    this.currentY = this.config.page.margins.top;
    this._drawHeader();
  }

  /**
   * Draw page footer
   */
  _drawFooter() {
    const margin = this.config.page.margins;
    const footerConfig = this.config.sections.footer;
    const pageCount = this.doc.internal.getNumberOfPages();

    for (let i = 1; i <= pageCount; i++) {
      this.doc.setPage(i);

      const footerY = this.pageHeight - margin.bottom + 10;

      // Border line
      this.doc.setDrawColor(...hexToRgb(footerConfig.borderTop.color));
      this.doc.setLineWidth(footerConfig.borderTop.width);
      this.doc.line(margin.left, footerY, this.pageWidth - margin.right, footerY);

      // Footer text
      this.doc.setFont('Helvetica', 'normal');
      this.doc.setFontSize(8);
      this.doc.setTextColor(...hexToRgb(this.config.colors.slateGray));

      // Left
      this.doc.text('Generated by CHEM•VIZ', margin.left, footerY + 15);

      // Center
      const pageText = `Page ${i} of ${pageCount}`;
      this.doc.text(pageText, this.pageWidth / 2, footerY + 15, { align: 'center' });

      // Right
      const dateText = new Date().toLocaleDateString();
      this.doc.text(dateText, this.pageWidth - margin.right, footerY + 15, { align: 'right' });
    }
  }
}

// Singleton instance
const pdfGenerator = new PDFReportGenerator();

/**
 * Generate and download PDF report
 * @param {string} datasetId - Dataset ID
 * @param {string} [filename] - Optional filename
 * @returns {Promise<void>}
 */
export async function generatePDFReport(datasetId, filename) {
  return pdfGenerator.downloadReport(datasetId, filename);
}

/**
 * Generate PDF report as blob
 * @param {string} datasetId - Dataset ID
 * @returns {Promise<Blob>}
 */
export async function generatePDFBlob(datasetId) {
  return pdfGenerator.generate(datasetId);
}

export default pdfGenerator;
