/**
 * Summary Screen Component
 * FOSSEE Scientific Analytics UI
 * 
 * Displays data summary after CSV upload:
 * - Summary card with file info
 * - KPI cards (Total equipment, Avg flowrate, Avg temperature, Dominant type)
 * - Data preview table (future)
 * - Actions: Generate Analysis, Upload Different File
 * 
 * Visual hierarchy per design.md Section 6:
 * 1. Summary Card
 * 2. KPI Cards
 * 3. Data Preview
 * 4. Action Buttons
 */

import React from 'react';
import { SummaryKPIs } from '../KPICards';
import './SummaryScreen.css';

/**
 * Compute KPIs from CSV headers
 * In a real app, this would analyze the actual data
 * For now, generates mock data based on file info
 */
function computeKPIs(uploadData) {
  if (!uploadData) {
    return {
      totalEquipment: 0,
      avgFlowrate: 0,
      avgTemperature: 0,
      dominantType: '—',
    };
  }

  // Mock KPI computation based on row count
  // In production, this would parse and analyze actual CSV data
  const rowCount = uploadData.rowCount || 0;
  
  return {
    totalEquipment: rowCount,
    avgFlowrate: rowCount > 0 ? 45.2 + (rowCount % 10) : 0,
    avgTemperature: rowCount > 0 ? 78.5 + (rowCount % 5) : 0,
    dominantType: rowCount > 0 ? 'Heat Exchanger' : '—',
  };
}

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
 * Summary Screen
 * 
 * @param {object} uploadData - Data from CSV upload
 * @param {function} onGenerateAnalysis - Handler for Generate Analysis action
 * @param {function} onUploadDifferent - Handler for Upload Different File action
 */
export function SummaryScreen({ uploadData, onGenerateAnalysis, onUploadDifferent }) {
  const kpiData = computeKPIs(uploadData);

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
                  {formatFileSize(uploadData.fileSize)} • {uploadData.rowCount.toLocaleString()} rows • {uploadData.columnCount} columns
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
        <SummaryKPIs data={kpiData} />
      </section>

      {/* Data Preview Placeholder */}
      <section className="summary-screen__section">
        <h2 className="summary-screen__section-title">Data Preview</h2>
        <div className="summary-screen__preview-placeholder">
          <p className="text-secondary">Data table preview will appear here</p>
        </div>
      </section>

      {/* Actions */}
      <section className="summary-screen__actions">
        <button 
          type="button" 
          className="btn btn--primary"
          onClick={onGenerateAnalysis}
        >
          Generate Analysis
        </button>
        <button 
          type="button" 
          className="btn btn--secondary"
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

export default SummaryScreen;
