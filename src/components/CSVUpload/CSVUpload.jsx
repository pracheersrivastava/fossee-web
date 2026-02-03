/**
 * CSV Upload Component
 * FOSSEE Scientific Analytics UI
 * 
 * Upload zone that transforms into summary card after upload.
 * Follows design.md Section 5.2 exactly.
 */

import React, { useState, useRef, useCallback } from 'react';
import './CSVUpload.css';

/**
 * Parse CSV file and extract metadata
 */
function parseCSV(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    
    reader.onload = (event) => {
      try {
        const text = event.target.result;
        const lines = text.split('\n').filter(line => line.trim());
        const headers = lines[0]?.split(',').map(h => h.trim()) || [];
        const rowCount = Math.max(0, lines.length - 1); // Exclude header
        
        // Basic validation
        const issues = [];
        if (headers.length === 0) {
          issues.push('No headers found');
        }
        if (rowCount === 0) {
          issues.push('No data rows found');
        }
        
        // Check for empty cells in first few rows
        const sampleRows = lines.slice(1, 6);
        let hasEmptyCells = false;
        sampleRows.forEach((row, idx) => {
          const cells = row.split(',');
          if (cells.some(cell => cell.trim() === '')) {
            hasEmptyCells = true;
          }
        });
        if (hasEmptyCells) {
          issues.push('Some cells contain empty values');
        }

        resolve({
          fileName: file.name,
          fileSize: file.size,
          rowCount,
          columnCount: headers.length,
          headers,
          validationStatus: issues.length === 0 ? 'success' : issues.length === 1 && hasEmptyCells ? 'warning' : 'error',
          issues,
        });
      } catch (error) {
        reject(new Error('Failed to parse CSV file'));
      }
    };
    
    reader.onerror = () => reject(new Error('Failed to read file'));
    reader.readAsText(file);
  });
}

/**
 * Format file size for display
 */
function formatFileSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

/**
 * CSV Upload Component
 */
export function CSVUpload({ onUploadComplete, onClear }) {
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadData, setUploadData] = useState(null);
  const [error, setError] = useState(null);
  const inputRef = useRef(null);

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const processFile = useCallback(async (file) => {
    if (!file) return;

    // Validate file type
    if (!file.name.endsWith('.csv')) {
      setError('Please upload a CSV file');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const data = await parseCSV(file);
      setUploadData(data);
      onUploadComplete?.(data);
    } catch (err) {
      setError(err.message || 'Failed to process file');
    } finally {
      setUploading(false);
    }
  }, [onUploadComplete]);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const file = e.dataTransfer?.files?.[0];
    processFile(file);
  }, [processFile]);

  const handleChange = useCallback((e) => {
    const file = e.target.files?.[0];
    processFile(file);
  }, [processFile]);

  const handleClick = useCallback(() => {
    inputRef.current?.click();
  }, []);

  const handleKeyDown = useCallback((e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleClick();
    }
  }, [handleClick]);

  const handleClear = useCallback(() => {
    setUploadData(null);
    setError(null);
    if (inputRef.current) {
      inputRef.current.value = '';
    }
    onClear?.();
  }, [onClear]);

  // Render Summary Card after upload
  if (uploadData) {
    return (
      <div className="csv-summary-card">
        <div className="csv-summary-card__header">
          <div className="csv-summary-card__file-info">
            <span className="csv-summary-card__icon" aria-hidden="true">📄</span>
            <div className="csv-summary-card__file-details">
              <span className="csv-summary-card__filename">{uploadData.fileName}</span>
              <span className="csv-summary-card__filesize caption">{formatFileSize(uploadData.fileSize)}</span>
            </div>
          </div>
          <StatusBadge status={uploadData.validationStatus} />
        </div>

        <div className="csv-summary-card__stats">
          <div className="csv-summary-card__stat">
            <span className="csv-summary-card__stat-value">{uploadData.rowCount.toLocaleString()}</span>
            <span className="csv-summary-card__stat-label caption">Rows</span>
          </div>
          <div className="csv-summary-card__stat">
            <span className="csv-summary-card__stat-value">{uploadData.columnCount}</span>
            <span className="csv-summary-card__stat-label caption">Columns</span>
          </div>
        </div>

        {uploadData.issues.length > 0 && (
          <div className="csv-summary-card__issues">
            {uploadData.issues.map((issue, idx) => (
              <p key={idx} className="csv-summary-card__issue caption">{issue}</p>
            ))}
          </div>
        )}

        <div className="csv-summary-card__actions">
          <button 
            type="button" 
            className="btn btn--secondary"
            onClick={handleClear}
          >
            Upload Different File
          </button>
        </div>
      </div>
    );
  }

  // Render Upload Zone
  return (
    <div className="csv-upload">
      <div
        className={`csv-upload__dropzone ${dragActive ? 'csv-upload__dropzone--active' : ''} ${error ? 'csv-upload__dropzone--error' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        tabIndex={0}
        role="button"
        aria-label="Upload CSV file"
      >
        <input
          ref={inputRef}
          type="file"
          accept=".csv"
          onChange={handleChange}
          className="csv-upload__input"
          aria-hidden="true"
        />

        {uploading ? (
          <div className="csv-upload__loading">
            <div className="csv-upload__spinner" />
            <p className="csv-upload__text">Processing file...</p>
          </div>
        ) : (
          <>
            <div className="csv-upload__icon" aria-hidden="true">↑</div>
            <p className="csv-upload__text">
              {dragActive ? 'Drop your CSV file here' : 'Drag and drop your CSV file here'}
            </p>
            <p className="csv-upload__subtext caption">or click to browse</p>
          </>
        )}
      </div>

      {error && (
        <div className="csv-upload__error" role="alert">
          <span className="csv-upload__error-icon" aria-hidden="true">!</span>
          <span>{error}</span>
        </div>
      )}

      <p className="csv-upload__formats caption">
        Supported format: CSV (comma-separated values)
      </p>
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

export default CSVUpload;
