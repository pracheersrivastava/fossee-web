/**
 * API Service Layer
 * FOSSEE Scientific Analytics UI
 * 
 * Handles all backend communication for CHEM•VIZ.
 * Assumes Django REST API endpoints exist.
 * 
 * IMPORTANT: All requests include Authorization header when user is logged in.
 */

import { authService } from './authService';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

/**
 * API error class for consistent error handling
 */
export class APIError extends Error {
  constructor(message, status, data = null) {
    super(message);
    this.name = 'APIError';
    this.status = status;
    this.data = data;
  }
}

/**
 * Generic fetch wrapper with error handling and authentication
 */
async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const config = {
    ...options,
    headers: {
      ...options.headers,
    },
  };

  // Add auth token if available
  const token = authService.getToken();
  if (token) {
    config.headers['Authorization'] = `Token ${token}`;
  }

  // Don't set Content-Type for FormData (browser sets it with boundary)
  if (!(options.body instanceof FormData)) {
    config.headers['Content-Type'] = 'application/json';
  }

  try {
    const response = await fetch(url, config);
    
    // Handle non-JSON responses
    const contentType = response.headers.get('content-type');
    const isJson = contentType && contentType.includes('application/json');
    const data = isJson ? await response.json() : await response.text();

    if (!response.ok) {
      throw new APIError(
        data.message || data.error || `HTTP ${response.status}`,
        response.status,
        data
      );
    }

    return data;
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    // Network or other errors
    throw new APIError(
      error.message || 'Network error',
      0,
      null
    );
  }
}

/**
 * Upload CSV file to Django backend
 * 
 * @param {File} file - CSV file to upload
 * @returns {Promise<{
 *   datasetId: string,
 *   fileName: string,
 *   fileSize: number,
 *   rowCount: number,
 *   columnCount: number,
 *   headers: string[],
 *   validationStatus: 'success' | 'warning' | 'error',
 *   issues: string[],
 *   uploadedAt: string
 * }>}
 */
export async function uploadCSV(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await request('/datasets/upload/', {
    method: 'POST',
    body: formData,
  });

  // Extract validation info
  const validation = response.validation || {};
  const issues = [];
  if (validation.missing_columns && validation.missing_columns.length > 0) {
    issues.push(`Missing columns: ${validation.missing_columns.join(', ')}`);
  }

  // Normalize backend response to expected shape
  return {
    datasetId: response.dataset_id || response.id,
    fileName: response.original_filename || response.name || file.name,
    fileSize: response.file_size || file.size,
    rowCount: response.row_count,
    columnCount: response.column_count,
    headers: response.columns || validation.found_columns || [],
    validationStatus: validation.is_valid !== false ? 'success' : 'warning',
    issues: issues,
    uploadedAt: response.uploaded_at || new Date().toISOString(),
  };
}

/**
 * Get summary statistics for a dataset (lightweight, for Summary screen)
 * Uses dataset detail endpoint and computes KPIs from data_preview
 * 
 * @param {string} datasetId - Dataset ID from upload
 * @returns {Promise<{
 *   kpis: { totalEquipment: number, avgFlowrate: number, avgTemperature: number, dominantType: string },
 *   previewData: Array<object>,
 *   previewHeaders: Array<string>
 * }>}
 */
export async function getDatasetSummary(datasetId) {
  const response = await request(`/datasets/${datasetId}/`);
  
  const preview = response.data_preview || [];
  const headers = response.columns || [];
  
  // Compute KPIs from preview data
  const kpis = computeKPIsFromData(preview, headers);

  return {
    kpis,
    previewData: preview,
    previewHeaders: headers,
  };
}

/**
 * Compute KPIs from dataset preview data
 */
function computeKPIsFromData(data, headers) {
  if (!data || data.length === 0) {
    return {
      totalEquipment: 0,
      avgFlowrate: 0,
      avgTemperature: 0,
      dominantType: '—',
    };
  }

  const totalEquipment = data.length;
  
  // Calculate average flowrate (look for flowrate column)
  const flowrateKey = headers.find(h => 
    h.toLowerCase().includes('flowrate') || h.toLowerCase().includes('flow_rate')
  );
  const avgFlowrate = flowrateKey 
    ? average(data.map(row => parseFloat(row[flowrateKey]) || 0))
    : 0;

  // Calculate average temperature
  const tempKey = headers.find(h => 
    h.toLowerCase().includes('temperature') || h.toLowerCase().includes('temp')
  );
  const avgTemperature = tempKey 
    ? average(data.map(row => parseFloat(row[tempKey]) || 0))
    : 0;

  // Find dominant equipment type
  const typeKey = headers.find(h => 
    h.toLowerCase().includes('type') || h.toLowerCase().includes('equipment_type')
  );
  const dominantType = typeKey 
    ? findMode(data.map(row => row[typeKey]).filter(Boolean))
    : '—';

  return {
    totalEquipment,
    avgFlowrate: Math.round(avgFlowrate * 100) / 100,
    avgTemperature: Math.round(avgTemperature * 100) / 100,
    dominantType: dominantType || '—',
  };
}

/**
 * Calculate average of an array of numbers
 */
function average(arr) {
  if (!arr || arr.length === 0) return 0;
  const valid = arr.filter(n => !isNaN(n));
  return valid.length > 0 ? valid.reduce((a, b) => a + b, 0) / valid.length : 0;
}

/**
 * Find the most common value in an array (mode)
 */
function findMode(arr) {
  if (!arr || arr.length === 0) return null;
  const counts = {};
  arr.forEach(val => { counts[val] = (counts[val] || 0) + 1; });
  return Object.entries(counts).sort((a, b) => b[1] - a[1])[0]?.[0] || null;
}

/**
 * Get analysis results for a dataset
 * Uses the dedicated analysis endpoint which returns pre-computed chart data
 * 
 * @param {string} datasetId - Dataset ID from upload
 * @returns {Promise<{
 *   chartData: { equipmentTypes: object, temperatureVsEquipment: object, pressureDistribution: object }
 * }>}
 */
export async function getAnalysis(datasetId) {
  // Use the dedicated analysis endpoint
  const response = await request(`/analysis/${datasetId}/`);
  
  // Map backend field names to frontend expected format
  const chartData = {
    equipmentTypes: response.equipment_type_distribution || { labels: [], data: [] },
    temperatureVsEquipment: response.temperature_by_equipment || { labels: [], data: [] },
    pressureDistribution: response.pressure_distribution || { labels: [], data: [] },
  };

  return { chartData };
}

/**
 * Compute chart data from dataset preview
 */
function computeChartDataFromPreview(data, headers) {
  if (!data || data.length === 0) {
    return {
      equipmentTypes: { labels: [], data: [] },
      temperatureVsEquipment: { labels: [], data: [] },
      pressureDistribution: { labels: [], data: [] },
    };
  }

  // Equipment Type Distribution
  const typeKey = headers.find(h => 
    h.toLowerCase().includes('type') || h.toLowerCase() === 'equipment_type'
  );
  const equipmentTypes = countByField(data, typeKey);

  // Temperature vs Equipment
  const nameKey = headers.find(h => 
    h.toLowerCase().includes('name') || h.toLowerCase().includes('equipment')
  );
  const tempKey = headers.find(h => 
    h.toLowerCase().includes('temperature') || h.toLowerCase().includes('temp')
  );
  const temperatureVsEquipment = {
    labels: nameKey ? data.map(row => row[nameKey] || 'Unknown') : data.map((_, i) => `Equipment ${i + 1}`),
    data: tempKey ? data.map(row => parseFloat(row[tempKey]) || 0) : [],
  };

  // Pressure Distribution (binned)
  const pressureKey = headers.find(h => 
    h.toLowerCase().includes('pressure')
  );
  const pressureDistribution = pressureKey 
    ? computePressureBins(data.map(row => parseFloat(row[pressureKey]) || 0))
    : { labels: [], data: [] };

  return {
    equipmentTypes,
    temperatureVsEquipment,
    pressureDistribution,
  };
}

/**
 * Count occurrences of each unique value in a field
 */
function countByField(data, fieldKey) {
  if (!fieldKey || !data) return { labels: [], data: [] };
  
  const counts = {};
  data.forEach(row => {
    const val = row[fieldKey] || 'Unknown';
    counts[val] = (counts[val] || 0) + 1;
  });
  
  const sorted = Object.entries(counts).sort((a, b) => b[1] - a[1]);
  return {
    labels: sorted.map(([label]) => label),
    data: sorted.map(([, count]) => count),
  };
}

/**
 * Compute pressure distribution bins
 */
function computePressureBins(values) {
  if (!values || values.length === 0) return { labels: [], data: [] };
  
  const validValues = values.filter(v => !isNaN(v) && v > 0);
  if (validValues.length === 0) return { labels: [], data: [] };
  
  const min = Math.min(...validValues);
  const max = Math.max(...validValues);
  const range = max - min || 1;
  const binSize = range / 5; // 5 bins
  
  const bins = [0, 0, 0, 0, 0];
  const labels = [];
  
  for (let i = 0; i < 5; i++) {
    const binMin = Math.round(min + i * binSize);
    const binMax = Math.round(min + (i + 1) * binSize);
    labels.push(`${binMin}-${binMax}`);
  }
  
  validValues.forEach(v => {
    const binIdx = Math.min(Math.floor((v - min) / binSize), 4);
    bins[binIdx]++;
  });
  
  return { labels, data: bins };
}

/**
 * Get dataset metadata
 * 
 * @param {string} datasetId - Dataset ID
 * @returns {Promise<object>}
 */
export async function getDataset(datasetId) {
  return request(`/datasets/${datasetId}/`);
}

/**
 * Get list of recent datasets (history)
 * 
 * @param {number} limit - Max number of datasets to return (default 5)
 * @returns {Promise<Array>}
 */
export async function getRecentDatasets(limit = 5) {
  const response = await request('/history/');
  return response.datasets || [];
}

/**
 * Delete a dataset
 * 
 * @param {string} datasetId - Dataset ID to delete
 * @returns {Promise<void>}
 */
export async function deleteDataset(datasetId) {
  return request(`/datasets/${datasetId}/`, {
    method: 'DELETE',
  });
}

/**
 * Claim an anonymous dataset after login.
 * This syncs uploads made while logged out to the user's history.
 * 
 * @param {string} datasetId - Dataset ID to claim
 * @returns {Promise<{message: string, dataset_id: string}>}
 */
export async function claimDataset(datasetId) {
  return request(`/datasets/${datasetId}/claim/`, {
    method: 'POST',
  });
}

/**
 * API Service singleton with all methods
 */
export const api = {
  uploadCSV,
  getDatasetSummary,
  getAnalysis,
  getDataset,
  getRecentDatasets,
  deleteDataset,
  claimDataset,
};

export default api;
