/**
 * API Service Layer
 * FOSSEE Scientific Analytics UI
 * 
 * Handles all backend communication for CHEM•VIZ.
 * Assumes Django REST API endpoints exist.
 */

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
 * Generic fetch wrapper with error handling
 */
async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const config = {
    ...options,
    headers: {
      ...options.headers,
    },
  };

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

  const response = await request('/upload/', {
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
    fileName: response.name || file.name,
    fileSize: file.size,
    rowCount: response.row_count,
    columnCount: response.column_count,
    headers: validation.found_columns || [],
    validationStatus: validation.is_valid ? 'success' : 'warning',
    issues: issues,
    uploadedAt: response.uploaded_at || new Date().toISOString(),
  };
}

/**
 * Get summary statistics for a dataset (lightweight, for Summary screen)
 * 
 * @param {string} datasetId - Dataset ID from upload
 * @returns {Promise<{
 *   kpis: { totalEquipment: number, avgFlowrate: number, avgTemperature: number, dominantType: string },
 *   previewData: Array<object>
 * }>}
 */
export async function getDatasetSummary(datasetId) {
  const response = await request(`/summary/${datasetId}/`);

  return {
    kpis: {
      totalEquipment: response.total_equipment ?? 0,
      avgFlowrate: response.average_flowrate ?? 0,
      avgTemperature: response.average_temperature ?? 0,
      dominantType: response.dominant_equipment_type ?? '—',
    },
    previewData: [],
    previewHeaders: [],
  };
}

/**
 * Get analysis results for a dataset
 * 
 * @param {string} datasetId - Dataset ID from upload
 * @returns {Promise<{
 *   kpis: { totalEquipment: number, avgFlowrate: number, avgTemperature: number, dominantType: string },
 *   chartData: { equipmentTypes: object, temperatureVsEquipment: object, pressureDistribution: object }
 * }>}
 */
export async function getAnalysis(datasetId) {
  const response = await request(`/analysis/${datasetId}/`);

  return {
    chartData: {
      equipmentTypes: response.equipment_type_distribution || {},
      temperatureVsEquipment: response.temperature_by_equipment || {},
      pressureDistribution: response.pressure_distribution || {},
    },
  };
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
 * API Service singleton with all methods
 */
export const api = {
  uploadCSV,
  getDatasetSummary,
  getAnalysis,
  getDataset,
  getRecentDatasets,
  deleteDataset,
};

export default api;
