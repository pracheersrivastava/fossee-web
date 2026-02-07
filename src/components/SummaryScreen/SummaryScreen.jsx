/**
 * Summary Screen Component
 * CHEM•VIZ - Chemical Equipment Parameter Visualizer
 * 
 * Displays data summary after CSV upload:
 * - Summary card with file info
 * - KPI cards (Total equipment, Avg flowrate, Avg temperature, Dominant type)
 * - Data preview table
 * - Actions: Generate Analysis, Export PDF, Upload Different File
 * 
 * Visual hierarchy per design.md Section 6:
 * 1. Summary Card
 * 2. KPI Cards
 * 3. Data Preview
 * 4. Action Buttons
 * 
 * Data Flow:
 * 1. Upload returns datasetId + basic metadata
 * 2. SummaryScreen fetches /api/summary/{id}/ for KPIs
 * 3. KPIs bound to UI, updates on dataset change
 */

import React, { useState, useEffect, useCallback } from 'react';
import { SummaryKPIs } from '../KPICards';
import { getDatasetSummary, APIError } from '../../services/api';
import { generatePDFReport } from '../../services/pdfGenerator';
import './SummaryScreen.css';

/**
 * Format file size for display
 */
function formatFileSize(bytes) {
  if (!bytes) return '0 B';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

/**
 * Default KPI values when loading or no data
 */
const DEFAULT_KPIS = {
  totalEquipment: 0,
  avgFlowrate: 0,
  avgTemperature: 0,
  dominantType: '—',
};

/**
 * Summary Screen
 * 
 * @param {object} uploadData - Data from CSV upload (includes datasetId)
 * @param {function} onGenerateAnalysis - Handler for Generate Analysis action
 * @param {function} onUploadDifferent - Handler for Upload Different File action
 */
export function SummaryScreen({ uploadData, onGenerateAnalysis, onUploadDifferent }) {
  const [kpiData, setKpiData] = useState(DEFAULT_KPIS);
  const [previewData, setPreviewData] = useState([]);
  const [previewHeaders, setPreviewHeaders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [exportingPdf, setExportingPdf] = useState(false);

  /**
   * Handle PDF export
   */
  const handleExportPDF = useCallback(async () => {
    if (!uploadData?.datasetId) {
      return;
    }

    setExportingPdf(true);
    try {
      await generatePDFReport(uploadData.datasetId, `${uploadData.fileName || 'report'}.pdf`);
    } catch (err) {
      console.error('PDF export failed:', err);
      setError('Failed to generate PDF report. Please try again.');
    } finally {
      setExportingPdf(false);
    }
  }, [uploadData]);

  /**
   * Fetch summary data from API when datasetId changes
   */
  const fetchSummary = useCallback(async (datasetId) => {
    if (!datasetId) {
      setError('No dataset ID available. Please upload a CSV file.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const summary = await getDatasetSummary(datasetId);
      setKpiData(summary.kpis);
      setPreviewData(summary.previewData || []);
      setPreviewHeaders(summary.previewHeaders || []);
    } catch (err) {
      console.error('Failed to fetch summary:', err);
      
      if (err instanceof APIError && err.status === 0) {
        setError('Could not connect to server. Please ensure the backend is running.');
      } else if (err instanceof APIError && err.status === 404) {
        setError('Dataset not found. It may have been deleted.');
      } else {
        setError(err.message || 'Failed to load summary data');
      }
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Effect: Fetch summary when uploadData changes
   */
  useEffect(() => {
    if (uploadData?.datasetId) {
      fetchSummary(uploadData.datasetId);
    }
  }, [uploadData?.datasetId, fetchSummary]);

  /**
   * Retry handler for failed API calls
   */
  const handleRetry = useCallback(() => {
    if (uploadData?.datasetId) {
      fetchSummary(uploadData.datasetId);
    }
  }, [uploadData?.datasetId, fetchSummary]);

  // Empty state
  if (!uploadData) {
    return (
      <div className="summary-screen__empty">
        <div className="summary-screen__empty-icon" aria-hidden="true">📊</div>
        <p className="summary-screen__empty-text">No data uploaded yet</p>
        <p className="summary-screen__empty-hint caption">
          Upload a CSV file to see the summary
        </p>
        <button 
          type="button" 
          className="btn btn--primary"
          onClick={onUploadDifferent}
        >
          Upload CSV File
        </button>
      </div>
    );
  }

  return (
    <div className="summary-screen">
      {/* File Summary Card */}
      <section className="summary-screen__section">
        <div className="summary-card">
          <div className="summary-card__header">
            <div className="summary-card__file-info">
              <span className="summary-card__icon" aria-hidden="true">📄</span>
              <div className="summary-card__file-details">
                <span className="summary-card__filename">{uploadData.fileName}</span>
                <span className="summary-card__meta caption">
                  {formatFileSize(uploadData.fileSize)} • {uploadData.rowCount?.toLocaleString()} rows • {uploadData.columnCount} columns
                </span>
              </div>
            </div>
            <StatusBadge status={uploadData.validationStatus} />
          </div>
        </div>
      </section>

      {/* KPI Cards */}
      <section className="summary-screen__section">
        <h2 className="summary-screen__section-title">Key Metrics</h2>
        
        {error && (
          <div className="summary-screen__error" role="alert">
            <span>{error}</span>
            <button 
              type="button" 
              className="summary-screen__retry-btn"
              onClick={handleRetry}
            >
              Retry
            </button>
          </div>
        )}
        
        {loading ? (
          <div className="summary-screen__loading">
            <KPILoadingSkeleton />
          </div>
        ) : (
          <SummaryKPIs data={kpiData} />
        )}
      </section>

      {/* Data Preview */}
      <section className="summary-screen__section">
        <h2 className="summary-screen__section-title">Data Preview</h2>
        {loading ? (
          <div className="summary-screen__preview-loading">
            <TableLoadingSkeleton />
          </div>
        ) : previewData.length > 0 ? (
          <DataPreviewTable headers={previewHeaders} rows={previewData} />
        ) : (
          <div className="summary-screen__preview-placeholder">
            <p className="text-secondary">
              No preview data available
            </p>
          </div>
        )}
      </section>

      {/* Actions */}
      <section className="summary-screen__actions">
        <button 
          type="button" 
          className="btn btn--primary"
          onClick={onGenerateAnalysis}
          disabled={loading}
        >
          Generate Analysis
        </button>
        <button 
          type="button" 
          className="btn btn--secondary"
          onClick={handleExportPDF}
          disabled={loading || exportingPdf}
        >
          {exportingPdf ? 'Generating PDF...' : 'Export PDF'}
        </button>
        <button 
          type="button" 
          className="btn btn--outline"
          onClick={onUploadDifferent}
        >
          Upload Different File
        </button>
      </section>
    </div>
  );
}

/**
 * Status Badge Component
 */
function StatusBadge({ status }) {
  const labels = {
    success: 'Valid',
    warning: 'Partial Issues',
    error: 'Invalid',
  };

  return (
    <span className={`status-badge status-badge--${status}`}>
      {labels[status] || status}
    </span>
  );
}

/**
 * Loading skeleton for KPI cards
 */
function KPILoadingSkeleton() {
  return (
    <div className="kpi-grid">
      {[1, 2, 3, 4].map((i) => (
        <div key={i} className="kpi-card kpi-card--skeleton">
          <div className="skeleton skeleton--icon" />
          <div className="kpi-card__content">
            <div className="skeleton skeleton--value" />
            <div className="skeleton skeleton--label" />
          </div>
        </div>
      ))}
    </div>
  );
}

/**
 * Loading skeleton for data table
 */
function TableLoadingSkeleton() {
  return (
    <div className="table-skeleton">
      <div className="skeleton skeleton--row skeleton--header" />
      {[1, 2, 3, 4, 5].map((i) => (
        <div key={i} className="skeleton skeleton--row" />
      ))}
    </div>
  );
}

/**
 * Data Preview Table Component
 */
function DataPreviewTable({ headers, rows }) {
  if (!headers.length || !rows.length) return null;

  return (
    <div className="data-preview-table-wrapper">
      <table className="data-preview-table">
        <thead>
          <tr>
            {headers.map((header, idx) => (
              <th key={idx}>{header}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.slice(0, 5).map((row, rowIdx) => (
            <tr key={rowIdx}>
              {headers.map((header, colIdx) => (
                <td key={colIdx}>{row[header] ?? row[colIdx] ?? '—'}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      {rows.length > 5 && (
        <p className="data-preview-table__more caption">
          Showing 5 of {rows.length} rows
        </p>
      )}
    </div>
  );
}

export default SummaryScreen;
