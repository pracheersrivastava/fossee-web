/**
 * Chart Components
 * FOSSEE Scientific Analytics UI
 *
 * React components wrapping Chart.js for:
 * - Equipment Type Distribution (Bar)
 * - Temperature vs Equipment (Line)
 * - Pressure Distribution (Bar)
 *
 * All charts follow design.md Section 5.5
 */

import React, { useMemo } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Bar, Line } from 'react-chartjs-2';

import {
  equipmentDistributionConfig,
  temperatureLineConfig,
  pressureDistributionConfig,
  createDataset,
  CHART_COLORS,
} from './chartConfig';
import './Charts.css';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

/**
 * Chart Card wrapper component
 */
const ChartCard = ({ title, children, className = '' }) => (
  <div className={`chart-card ${className}`}>
    <h3 className="chart-title">{title}</h3>
    <div className="chart-container">
      {children}
    </div>
  </div>
);

/**
 * Equipment Type Distribution Chart (Bar)
 *
 * Displays count of equipment by type.
 * Color: Muted Violet (#8B5CF6)
 *
 * @param {Object} props
 * @param {string[]} props.labels - Equipment type names
 * @param {number[]} props.data - Count values for each type
 */
export const EquipmentDistributionChart = ({ labels = [], data = [] }) => {
  const chartData = useMemo(() => ({
    labels,
    datasets: [
      createDataset(
        equipmentDistributionConfig,
        { data },
        'Equipment Count'
      ),
    ],
  }), [labels, data]);

  return (
    <ChartCard title="Equipment Type Distribution">
      <Bar
        data={chartData}
        options={equipmentDistributionConfig.options}
      />
    </ChartCard>
  );
};

/**
 * Temperature vs Equipment Chart (Line)
 *
 * Displays temperature readings across equipment.
 * Color: Amber (#F59E0B)
 *
 * @param {Object} props
 * @param {string[]} props.labels - Equipment identifiers
 * @param {number[]} props.data - Temperature values in °C
 */
export const TemperatureChart = ({ labels = [], data = [] }) => {
  const chartData = useMemo(() => ({
    labels,
    datasets: [
      createDataset(
        temperatureLineConfig,
        { data },
        'Temperature (°C)'
      ),
    ],
  }), [labels, data]);

  return (
    <ChartCard title="Temperature vs Equipment">
      <Line
        data={chartData}
        options={temperatureLineConfig.options}
      />
    </ChartCard>
  );
};

/**
 * Pressure Distribution Chart (Bar)
 *
 * Displays equipment count by pressure range.
 * Color: Crimson (#EF4444)
 *
 * @param {Object} props
 * @param {string[]} props.labels - Pressure range labels
 * @param {number[]} props.data - Count values for each range
 */
export const PressureDistributionChart = ({ labels = [], data = [] }) => {
  const chartData = useMemo(() => ({
    labels,
    datasets: [
      createDataset(
        pressureDistributionConfig,
        { data },
        'Equipment Count'
      ),
    ],
  }), [labels, data]);

  return (
    <ChartCard title="Pressure Distribution">
      <Bar
        data={chartData}
        options={pressureDistributionConfig.options}
      />
    </ChartCard>
  );
};

/**
 * Charts Grid layout component
 *
 * Displays multiple charts in a responsive grid.
 */
export const ChartsGrid = ({ children }) => (
  <div className="charts-grid">
    {children}
  </div>
);

/**
 * Analysis Charts Screen
 *
 * Pre-configured screen showing all three charts
 * with sample or provided data.
 */
export const AnalysisCharts = ({ equipmentData = null }) => {
  // Process data or use sample data
  const processedData = useMemo(() => {
    if (!equipmentData) {
      // Sample data for demonstration
      return {
        equipmentDistribution: {
          labels: ['Pump', 'Valve', 'Heat Exchanger', 'Reactor', 'Compressor'],
          data: [24, 18, 12, 8, 6],
        },
        temperature: {
          labels: ['EQ-001', 'EQ-002', 'EQ-003', 'EQ-004', 'EQ-005', 'EQ-006', 'EQ-007', 'EQ-008'],
          data: [75, 82, 68, 91, 78, 85, 72, 88],
        },
        pressureDistribution: {
          labels: ['0-2', '2-4', '4-6', '6-8', '8-10', '>10'],
          data: [8, 15, 22, 12, 7, 4],
        },
      };
    }

    // Process actual equipment data
    return processEquipmentData(equipmentData);
  }, [equipmentData]);

  return (
    <div className="analysis-charts">
      <ChartsGrid>
        <EquipmentDistributionChart
          labels={processedData.equipmentDistribution.labels}
          data={processedData.equipmentDistribution.data}
        />
        <TemperatureChart
          labels={processedData.temperature.labels}
          data={processedData.temperature.data}
        />
        <PressureDistributionChart
          labels={processedData.pressureDistribution.labels}
          data={processedData.pressureDistribution.data}
        />
      </ChartsGrid>
    </div>
  );
};

/**
 * Process raw equipment data for charts
 */
const processEquipmentData = (data) => {
  const rows = data.rows || [];

  // Equipment type distribution
  const typeCounts = {};
  rows.forEach(row => {
    const type = row.type || row.equipment_type || 'Unknown';
    typeCounts[type] = (typeCounts[type] || 0) + 1;
  });

  // Temperature data
  const tempData = rows
    .filter(row => row.temperature !== undefined)
    .slice(0, 10)
    .map(row => ({
      label: row.id || row.equipment_id || `EQ-${rows.indexOf(row) + 1}`,
      value: parseFloat(row.temperature) || 0,
    }));

  // Pressure distribution (binned)
  const pressureBins = { '0-2': 0, '2-4': 0, '4-6': 0, '6-8': 0, '8-10': 0, '>10': 0 };
  rows.forEach(row => {
    const pressure = parseFloat(row.pressure) || 0;
    if (pressure <= 2) pressureBins['0-2']++;
    else if (pressure <= 4) pressureBins['2-4']++;
    else if (pressure <= 6) pressureBins['4-6']++;
    else if (pressure <= 8) pressureBins['6-8']++;
    else if (pressure <= 10) pressureBins['8-10']++;
    else pressureBins['>10']++;
  });

  return {
    equipmentDistribution: {
      labels: Object.keys(typeCounts),
      data: Object.values(typeCounts),
    },
    temperature: {
      labels: tempData.map(d => d.label),
      data: tempData.map(d => d.value),
    },
    pressureDistribution: {
      labels: Object.keys(pressureBins),
      data: Object.values(pressureBins),
    },
  };
};

export default AnalysisCharts;
