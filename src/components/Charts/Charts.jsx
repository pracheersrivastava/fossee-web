/**
 * Chart Components
 * FOSSEE Scientific Analytics UI
 *
 * React components wrapping Chart.js for:
 * - Equipment Type Distribution (Bar)
 * - Temperature vs Equipment (Line)
 * - Pressure Distribution (Bar)
 *
 * All charts follow design.md Section 5.5:
 * - No borders
 * - Gridlines: #E5E7EB
 * - Tooltip background: Dark Indigo @ 90%
 * - Max 4 colors per chart
 * 
 * Data Flow:
 * 1. AnalysisCharts receives datasetId from parent
 * 2. useEffect calls getAnalysis(datasetId) API
 * 3. API response mapped to Chart.js format
 * 4. Charts render with real data
 */

import React, { useState, useEffect, useMemo, useCallback } from 'react';
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
import { getAnalysis, APIError } from '../../services/api';
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
 * Default empty chart data structure
 */
const EMPTY_CHART_DATA = {
  equipmentDistribution: { labels: [], data: [] },
  temperature: { labels: [], data: [] },
  pressureDistribution: { labels: [], data: [] },
};

/**
 * Analysis Charts Screen
 *
 * Fetches analysis data from API and renders all three charts.
 * 
 * @param {string} datasetId - Dataset ID for fetching analysis data
 * @param {object} equipmentData - Upload metadata (fallback info)
 */
export const AnalysisCharts = ({ datasetId, equipmentData = null }) => {
  const [chartData, setChartData] = useState(EMPTY_CHART_DATA);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Fetch analysis data from backend API
   */
  const fetchAnalysis = useCallback(async (id) => {
    if (!id) {
      setError('No dataset selected. Please upload a CSV file first.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await getAnalysis(id);
      
      // Map API response to Chart.js format
      const mapped = mapApiToChartData(response.chartData);
      setChartData(mapped);
      
    } catch (err) {
      console.error('Failed to fetch analysis:', err);
      
      if (err instanceof APIError && err.status === 0) {
        setError('Cannot connect to server. Please check your connection.');
      } else if (err instanceof APIError && err.status === 404) {
        setError('Dataset not found. It may have been deleted.');
      } else {
        setError(err.message || 'Failed to load analysis data');
      }
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Effect: Fetch analysis when datasetId changes
   */
  useEffect(() => {
    if (datasetId) {
      fetchAnalysis(datasetId);
    }
  }, [datasetId, fetchAnalysis]);

  /**
   * Retry handler
   */
  const handleRetry = useCallback(() => {
    if (datasetId) {
      fetchAnalysis(datasetId);
    }
  }, [datasetId, fetchAnalysis]);

  // Error state
  if (error) {
    return (
      <div className="analysis-charts">
        <div className="analysis-charts__error">
          <div className="analysis-charts__error-icon" aria-hidden="true">⚠</div>
          <p className="analysis-charts__error-text">{error}</p>
          {datasetId && (
            <button 
              type="button" 
              className="btn btn--secondary"
              onClick={handleRetry}
            >
              Retry
            </button>
          )}
        </div>
      </div>
    );
  }

  // Loading state
  if (loading) {
    return (
      <div className="analysis-charts">
        <ChartsGrid>
          <ChartLoadingSkeleton title="Equipment Type Distribution" />
          <ChartLoadingSkeleton title="Temperature vs Equipment" />
          <ChartLoadingSkeleton title="Pressure Distribution" />
        </ChartsGrid>
      </div>
    );
  }

  // No data state
  if (!datasetId) {
    return (
      <div className="analysis-charts">
        <div className="analysis-charts__empty">
          <div className="analysis-charts__empty-icon" aria-hidden="true">📊</div>
          <p className="analysis-charts__empty-text">No dataset loaded</p>
          <p className="analysis-charts__empty-hint caption">
            Upload a CSV file and generate analysis to see charts
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="analysis-charts">
      <ChartsGrid>
        <EquipmentDistributionChart
          labels={chartData.equipmentDistribution.labels}
          data={chartData.equipmentDistribution.data}
        />
        <TemperatureChart
          labels={chartData.temperature.labels}
          data={chartData.temperature.data}
        />
        <PressureDistributionChart
          labels={chartData.pressureDistribution.labels}
          data={chartData.pressureDistribution.data}
        />
      </ChartsGrid>
    </div>
  );
};

/**
 * Loading skeleton for chart cards
 */
function ChartLoadingSkeleton({ title }) {
  return (
    <div className="chart-card chart-card--skeleton">
      <h3 className="chart-title">{title}</h3>
      <div className="chart-container">
        <div className="chart-skeleton">
          <div className="chart-skeleton__bars">
            {[60, 80, 45, 90, 55].map((height, i) => (
              <div 
                key={i} 
                className="chart-skeleton__bar" 
                style={{ height: `${height}%` }}
              />
            ))}
          </div>
          <div className="chart-skeleton__axis-x" />
          <div className="chart-skeleton__axis-y" />
        </div>
      </div>
    </div>
  );
}

/**
 * Map API response to Chart.js data format
 * 
 * Handles the backend response structure from /api/analysis/<id>/
 * Backend returns: equipmentTypes, temperatureVsEquipment, pressureDistribution
 */
function mapApiToChartData(apiData) {
  if (!apiData) {
    return EMPTY_CHART_DATA;
  }

  // Equipment Type Distribution (from equipmentTypes in api response)
  const equipmentTypes = apiData.equipmentTypes || {};
  const equipmentDistribution = {
    labels: equipmentTypes.labels || [],
    data: equipmentTypes.data || [],
  };

  // Temperature vs Equipment (from temperatureVsEquipment in api response)
  const tempData = apiData.temperatureVsEquipment || {};
  const temperature = {
    labels: tempData.labels || [],
    data: tempData.data || [],
  };

  // Pressure Distribution (from pressureDistribution in api response)
  const pressureData = apiData.pressureDistribution || {};
  const pressureDistribution = {
    labels: pressureData.labels || [],
    data: pressureData.data || [],
  };

  return {
    equipmentDistribution,
    temperature,
    pressureDistribution,
  };
}

export default AnalysisCharts;
