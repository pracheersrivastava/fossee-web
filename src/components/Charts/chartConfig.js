/**
 * Chart.js Configuration
 * FOSSEE Scientific Analytics UI
 *
 * Follows design.md Section 5.5:
 * - No borders
 * - Gridlines: #E5E7EB
 * - Tooltip background: Dark Indigo @ 90%
 * - Max 4 colors per chart
 * - Use opacity (0.7-0.85) instead of new colors
 */

// Design tokens from design.md
export const CHART_COLORS = {
  flowrate: '#14B8A6',      // Teal
  temperature: '#F59E0B',   // Amber
  pressure: '#EF4444',      // Crimson
  equipment: '#8B5CF6',     // Muted Violet
};

export const UI_COLORS = {
  deepIndigo: '#1E2A38',
  slateGray: '#6B7280',
  gridline: '#E5E7EB',
  tooltipBg: 'rgba(30, 42, 56, 0.9)',
  surface: '#FFFFFF',
};

export const FONTS = {
  family: "'Inter', 'Roboto', 'Arial', sans-serif",
  sizeCaption: 12,
  sizeBody: 14,
};

/**
 * Base Chart.js defaults for all charts
 */
export const baseChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  animation: {
    duration: 200, // Per design.md: 150-200ms
    easing: 'linear',
  },
  plugins: {
    legend: {
      display: true,
      position: 'top',
      align: 'end',
      labels: {
        font: {
          family: FONTS.family,
          size: FONTS.sizeCaption,
          weight: 400,
        },
        color: UI_COLORS.slateGray,
        usePointStyle: true,
        pointStyle: 'circle',
        padding: 16,
        boxWidth: 8,
        boxHeight: 8,
      },
    },
    tooltip: {
      backgroundColor: UI_COLORS.tooltipBg,
      titleFont: {
        family: FONTS.family,
        size: FONTS.sizeBody,
        weight: 500,
      },
      bodyFont: {
        family: FONTS.family,
        size: FONTS.sizeCaption,
        weight: 400,
      },
      titleColor: '#FFFFFF',
      bodyColor: '#FFFFFF',
      padding: 12,
      cornerRadius: 6,
      displayColors: true,
      boxWidth: 8,
      boxHeight: 8,
      boxPadding: 4,
    },
  },
};

/**
 * Grid configuration (soft gridlines per design.md)
 */
export const softGridConfig = {
  color: UI_COLORS.gridline,
  drawBorder: false,
  lineWidth: 1,
};

/**
 * Axis configuration
 */
export const axisConfig = {
  ticks: {
    font: {
      family: FONTS.family,
      size: FONTS.sizeCaption,
      weight: 400,
    },
    color: UI_COLORS.slateGray,
    padding: 8,
  },
  title: {
    display: true,
    font: {
      family: FONTS.family,
      size: FONTS.sizeCaption,
      weight: 500,
    },
    color: UI_COLORS.deepIndigo,
    padding: 8,
  },
};

// ============================================
// CHART-SPECIFIC CONFIGURATIONS
// ============================================

/**
 * Equipment Type Distribution (Bar Chart)
 * Uses: equipment color (Muted Violet)
 */
export const equipmentDistributionConfig = {
  type: 'bar',
  options: {
    ...baseChartOptions,
    indexAxis: 'x',
    scales: {
      x: {
        ...axisConfig,
        grid: {
          display: false,
        },
        title: {
          ...axisConfig.title,
          text: 'Equipment Type',
        },
      },
      y: {
        ...axisConfig,
        grid: softGridConfig,
        title: {
          ...axisConfig.title,
          text: 'Count',
        },
        beginAtZero: true,
      },
    },
    plugins: {
      ...baseChartOptions.plugins,
      legend: {
        display: false, // Single dataset, no legend needed
      },
    },
  },
  datasetDefaults: {
    backgroundColor: `${CHART_COLORS.equipment}CC`, // 80% opacity
    hoverBackgroundColor: CHART_COLORS.equipment,
    borderWidth: 0,
    borderRadius: 4,
    maxBarThickness: 60,
  },
};

/**
 * Temperature vs Equipment (Line Chart)
 * Uses: temperature color (Amber)
 */
export const temperatureLineConfig = {
  type: 'line',
  options: {
    ...baseChartOptions,
    scales: {
      x: {
        ...axisConfig,
        grid: {
          display: false,
        },
        title: {
          ...axisConfig.title,
          text: 'Equipment',
        },
      },
      y: {
        ...axisConfig,
        grid: softGridConfig,
        title: {
          ...axisConfig.title,
          text: 'Temperature (°C)',
        },
        beginAtZero: false,
      },
    },
  },
  datasetDefaults: {
    borderColor: CHART_COLORS.temperature,
    backgroundColor: `${CHART_COLORS.temperature}22`, // 13% opacity for fill
    pointBackgroundColor: CHART_COLORS.temperature,
    pointBorderColor: UI_COLORS.surface,
    pointBorderWidth: 2,
    pointRadius: 4,
    pointHoverRadius: 6,
    borderWidth: 2,
    fill: true,
    tension: 0.3, // Smooth curve
  },
};

/**
 * Pressure Distribution (Bar Chart)
 * Uses: pressure color (Crimson)
 */
export const pressureDistributionConfig = {
  type: 'bar',
  options: {
    ...baseChartOptions,
    indexAxis: 'x',
    scales: {
      x: {
        ...axisConfig,
        grid: {
          display: false,
        },
        title: {
          ...axisConfig.title,
          text: 'Pressure Range (bar)',
        },
      },
      y: {
        ...axisConfig,
        grid: softGridConfig,
        title: {
          ...axisConfig.title,
          text: 'Equipment Count',
        },
        beginAtZero: true,
      },
    },
    plugins: {
      ...baseChartOptions.plugins,
      legend: {
        display: false,
      },
    },
  },
  datasetDefaults: {
    backgroundColor: `${CHART_COLORS.pressure}CC`, // 80% opacity
    hoverBackgroundColor: CHART_COLORS.pressure,
    borderWidth: 0,
    borderRadius: 4,
    maxBarThickness: 60,
  },
};

/**
 * Helper to create a complete dataset with defaults
 */
export const createDataset = (config, data, label = '') => ({
  ...config.datasetDefaults,
  ...data,
  label,
});
