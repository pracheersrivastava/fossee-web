/**
 * PDF Report Layout Configuration
 * FOSSEE Scientific Analytics UI - CHEM•VIZ
 * 
 * Defines the full layout and styling for generated PDF reports.
 * Follows design.md specifications for academic, data-first presentation.
 */

export const PDF_REPORT_CONFIG = {
  /**
   * Page Setup
   */
  page: {
    size: 'A4',
    orientation: 'portrait',
    margins: {
      top: 72,      // 1 inch = 72pt
      bottom: 72,
      left: 56,     // ~0.78 inch
      right: 56,
    },
    // Content area: 483pt width (≈170mm)
  },

  /**
   * Typography
   * Uses PDF-safe fonts with fallbacks
   */
  typography: {
    fontFamily: {
      primary: 'Helvetica',
      fallback: 'Arial, sans-serif',
      monospace: 'Courier',
    },
    
    // Type scale (in points)
    scale: {
      reportTitle: { size: 24, weight: 'bold', lineHeight: 32, color: '#1E2A38' },
      sectionHeader: { size: 16, weight: 'bold', lineHeight: 22, color: '#1E2A38' },
      subsectionHeader: { size: 13, weight: 'bold', lineHeight: 18, color: '#1E2A38' },
      body: { size: 11, weight: 'normal', lineHeight: 16, color: '#1E2A38' },
      tableHeader: { size: 10, weight: 'bold', lineHeight: 14, color: '#1E2A38' },
      tableCell: { size: 10, weight: 'normal', lineHeight: 14, color: '#1E2A38' },
      caption: { size: 9, weight: 'normal', lineHeight: 13, color: '#6B7280' },
      footer: { size: 8, weight: 'normal', lineHeight: 12, color: '#6B7280' },
    },
  },

  /**
   * Color Palette (CMYK-safe versions of design tokens)
   */
  colors: {
    // Core
    deepIndigo: '#1E2A38',
    academicBlue: '#2F80ED',
    slateGray: '#6B7280',
    offWhite: '#F8FAFC',
    pureWhite: '#FFFFFF',
    
    // Data Visualization
    flowrate: '#14B8A6',
    temperature: '#F59E0B',
    pressure: '#EF4444',
    equipment: '#8B5CF6',
    
    // Status
    success: '#22C55E',
    warning: '#F59E0B',
    error: '#DC2626',
    
    // Table
    tableHeader: '#F1F5F9',
    tableZebra: '#FAFAFA',
    tableBorder: '#E5E7EB',
  },

  /**
   * Spacing (in points)
   * Base unit: 8pt
   */
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
    xxl: 48,
  },

  /**
   * Section Hierarchy & Structure
   */
  sections: {
    /**
     * 1. Header (every page)
     */
    header: {
      height: 48,
      logo: {
        width: 100,
        position: 'left',
      },
      title: {
        text: 'CHEM•VIZ Analysis Report',
        style: 'reportTitle',
        position: 'center',
      },
      badge: {
        text: 'FOSSEE',
        backgroundColor: '#2F80ED',
        textColor: '#FFFFFF',
        position: 'right',
      },
      borderBottom: {
        width: 1,
        color: '#E5E7EB',
      },
    },

    /**
     * 2. Report Metadata
     */
    metadata: {
      marginTop: 24,
      marginBottom: 32,
      fields: [
        { label: 'Generated', key: 'timestamp' },
        { label: 'Dataset', key: 'filename' },
        { label: 'Records', key: 'rowCount' },
        { label: 'Status', key: 'validationStatus' },
      ],
      layout: 'twoColumn', // 2x2 grid
      labelStyle: 'caption',
      valueStyle: 'body',
    },

    /**
     * 3. Executive Summary / KPIs
     */
    summary: {
      title: 'Summary',
      marginBottom: 24,
      kpiCards: {
        layout: 'fourColumn',
        cardStyle: {
          backgroundColor: '#FFFFFF',
          borderRadius: 6,
          border: '1px solid #E5E7EB',
          padding: 12,
        },
        metrics: [
          { key: 'totalEquipment', label: 'Total Equipment', icon: '⚙' },
          { key: 'avgFlowrate', label: 'Avg Flowrate', unit: 'm³/hr', icon: '◎' },
          { key: 'avgTemperature', label: 'Avg Temperature', unit: '°C', icon: '◐' },
          { key: 'dominantType', label: 'Dominant Type', icon: '▤' },
        ],
        valueStyle: { size: 18, weight: 'bold', color: '#1E2A38' },
        labelStyle: { size: 9, weight: 'normal', color: '#6B7280' },
      },
    },

    /**
     * 4. Charts Section
     */
    charts: {
      title: 'Data Visualization',
      marginBottom: 24,
      layout: [
        {
          id: 'equipmentDistribution',
          title: 'Equipment Distribution by Type',
          type: 'bar',
          color: '#8B5CF6',
          width: '100%',
          height: 200,
          captionStyle: 'caption',
        },
        {
          id: 'temperatureProfile',
          title: 'Temperature Profile',
          type: 'line',
          color: '#F59E0B',
          fillOpacity: 0.15,
          width: '48%',
          height: 160,
          position: 'left',
        },
        {
          id: 'pressureDistribution',
          title: 'Pressure Distribution',
          type: 'bar',
          color: '#EF4444',
          width: '48%',
          height: 160,
          position: 'right',
        },
      ],
      chartStyle: {
        backgroundColor: '#FFFFFF',
        gridlineColor: '#E5E7EB',
        axisColor: '#6B7280',
        fontSize: 9,
      },
    },

    /**
     * 5. Data Table
     */
    dataTable: {
      title: 'Equipment Data',
      marginBottom: 24,
      maxRows: 20, // Show first 20 rows, indicate if truncated
      columns: [
        { key: 'id', label: 'ID', width: '12%', align: 'left' },
        { key: 'type', label: 'Type', width: '18%', align: 'left' },
        { key: 'temperature', label: 'Temp (°C)', width: '17%', align: 'right' },
        { key: 'pressure', label: 'Pressure (bar)', width: '17%', align: 'right' },
        { key: 'flowrate', label: 'Flowrate (m³/hr)', width: '18%', align: 'right' },
        { key: 'status', label: 'Status', width: '18%', align: 'center' },
      ],
      style: {
        headerBackground: '#F1F5F9',
        headerTextColor: '#1E2A38',
        rowHeight: 24,
        zebraColor: '#FAFAFA',
        borderColor: '#E5E7EB',
      },
      statusBadges: {
        active: { background: '#DCFCE7', text: '#22C55E' },
        inactive: { background: '#FEE2E2', text: '#DC2626' },
        maintenance: { background: '#FEF3C7', text: '#B45309' },
      },
    },

    /**
     * 6. Footer (every page)
     */
    footer: {
      height: 36,
      borderTop: {
        width: 1,
        color: '#E5E7EB',
      },
      left: {
        text: 'FOSSEE Project, IIT Bombay',
        style: 'footer',
      },
      center: {
        text: 'Page {page} of {pages}',
        style: 'footer',
      },
      right: {
        text: 'Generated by CHEM•VIZ',
        style: 'footer',
      },
    },
  },

  /**
   * Chart Rendering Rules
   */
  chartRules: {
    // No borders on chart areas
    borderWidth: 0,
    
    // Gridlines
    gridline: {
      color: '#E5E7EB',
      width: 0.5,
      dashArray: null, // Solid lines
    },
    
    // Axis styling
    axis: {
      color: '#6B7280',
      fontSize: 9,
      tickLength: 4,
    },
    
    // Bar charts
    bar: {
      borderRadius: 2,
      borderWidth: 0,
      opacity: 0.85,
    },
    
    // Line charts
    line: {
      strokeWidth: 2,
      pointRadius: 0, // No data points
      fillOpacity: 0.15,
    },
    
    // Legend
    legend: {
      position: 'bottom',
      fontSize: 9,
      itemSpacing: 16,
    },
  },

  /**
   * Page Break Rules
   */
  pageBreaks: {
    // Always start these sections on a new page
    forceBreakBefore: ['dataTable'],
    
    // Avoid breaking inside these elements
    keepTogether: ['kpiCards', 'chart'],
    
    // Minimum space before breaking
    orphanThreshold: 72, // 1 inch
  },
};

/**
 * Helper: Generate PDF-ready styles object
 */
export function getPdfStyles() {
  const { typography, colors, spacing } = PDF_REPORT_CONFIG;
  
  return {
    reportTitle: {
      font: typography.fontFamily.primary,
      fontSize: typography.scale.reportTitle.size,
      fontWeight: typography.scale.reportTitle.weight,
      color: typography.scale.reportTitle.color,
      lineHeight: typography.scale.reportTitle.lineHeight,
      marginBottom: spacing.lg,
    },
    sectionHeader: {
      font: typography.fontFamily.primary,
      fontSize: typography.scale.sectionHeader.size,
      fontWeight: typography.scale.sectionHeader.weight,
      color: typography.scale.sectionHeader.color,
      lineHeight: typography.scale.sectionHeader.lineHeight,
      marginTop: spacing.xl,
      marginBottom: spacing.md,
      borderBottom: `1px solid ${colors.tableBorder}`,
      paddingBottom: spacing.sm,
    },
    body: {
      font: typography.fontFamily.primary,
      fontSize: typography.scale.body.size,
      color: typography.scale.body.color,
      lineHeight: typography.scale.body.lineHeight,
    },
    caption: {
      font: typography.fontFamily.primary,
      fontSize: typography.scale.caption.size,
      color: colors.slateGray,
      lineHeight: typography.scale.caption.lineHeight,
      fontStyle: 'italic',
    },
  };
}

export default PDF_REPORT_CONFIG;
