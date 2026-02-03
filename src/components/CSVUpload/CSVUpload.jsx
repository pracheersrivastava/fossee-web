/**
 * CSV Upload Component
 * FOSSEE Scientific Analytics UI
 * 
 * Upload zone that transforms into summary card after upload.
 * Follows design.md Section 5.2 exactly.
 * 
 * State Flow:
 * 1. User selects/drops file
 * 2. Component calls Django API (/api/upload/)
 * 3. On success: store datasetId, show summary card
 * 4. On error: display error message, allow retry
 */

import React, { useState, useRef, useCallback } from 'react';
import { uploadCSV, APIError } from '../../services/api';
import './CSVUpload.css';

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
 * 
 * Props:
 * - onUploadComplete(data): Called with dataset metadata after successful upload
 * - onClear(): Called when user clears the upload
 * - onError(error): Optional callback for error handling
 */
export function CSVUpload({ onUploadComplete, onClear, onError }) {
  const [dragActive, setDragActive] = useState(false);
  const [uploadState, setUploadState] = useState('idle'); // idle | uploading | success | error
  const [uploadData, setUploadData] = useState(null);
  const [error, setError] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const inputRef = useRef(null);
  const fileRef = useRef(null); // Store file for retry

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  /**
   * Upload file to Django backend API
   */
  const processFile = useCallback(async (file) => {
    if (!file) return;

    // Validate file type
    if (!file.name.endsWith('.csv')) {
      const errorMsg = 'Please upload a CSV file';
      setError(errorMsg);
      setUploadState('error');
      onError?.(new Error(errorMsg));
      return;
    }

    // Store file for potential retry
    fileRef.current = file;
    
    setUploadState('uploading');
    setUploadProgress(10);
    setError(null);

    try {
      // Simulate progress during upload
      setUploadProgress(30);
      
      // Call Django API
      const data = await uploadCSV(file);
      
      setUploadProgress(100);
      setUploadData(data);
      setUploadState('success');
      
      // Notify parent with complete dataset info including datasetId
      onUploadComplete?.(data);
      
    } catch (err) {
      console.error('Upload failed:', err);
      
      // Handle specific error types
      let errorMessage = 'Upload failed. Please try again.';
      
      if (err instanceof APIError) {
        if (err.status === 0) {
          errorMessage = 'Cannot connect to server. Please ensure the backend is running.';
        } else if (err.status === 413) {
          errorMessage = 'File too large. Maximum size is 10MB.';
        } else if (err.status === 400) {
          errorMessage = err.data?.error || err.data?.message || 'Invalid CSV format.';
        } else if (err.status === 500) {
          errorMessage = 'Server error. Please try again later.';
        } else {
          errorMessage = err.message;
        }
      } else {
        errorMessage = err.message || 'Unexpected error occurred.';
      }
      
      setError(errorMessage);
      setUploadState('error');
      setUploadProgress(0);
      onError?.(err);
    }
  }, [onUploadComplete, onError]);

  /**
   * Retry failed upload
   */
  const handleRetry = useCallback(() => {
    if (fileRef.current) {
      processFile(fileRef.current);
    }
  }, [processFile]);

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
    setUploadState('idle');
    setUploadProgress(0);
    fileRef.current = null;
    if (inputRef.current) {
      inputRef.current.value = '';
    }
    onClear?.();
  }, [onClear]);

  // Render Summary Card after successful upload
  if (uploadState === 'success' && uploadData) {
    return (
      <div className="csv-summary-card">
        <div className="csv-summary-card__header">
          <div className="csv-summary-card__file-info">
            <span className="csv-summary-card__icon" aria-hidden="true">📄</span>
            <div className="csv-summary-card__file-details">
              <span className="csv-summary-card__filename">{uploadData.fileName}</span>
              <span className="csv-summary-card__filesize caption">
                {formatFileSize(uploadData.fileSize)} • {uploadData.rowCount} rows • {uploadData.columnCount} columns
              </span>
            </div>
          </div>
          <StatusBadge status={uploadData.validationStatus} />
        </div>

        {uploadData.datasetId && (
          <div className="csv-summary-card__dataset-id">
            <span className="caption">Dataset ID: {uploadData.datasetId}</span>
          </div>
        )}

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

        {uploadData.issues && uploadData.issues.length > 0 && (
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
        className={`csv-upload__dropzone ${dragActive ? 'csv-upload__dropzone--active' : ''} ${uploadState === 'error' ? 'csv-upload__dropzone--error' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={uploadState !== 'uploading' ? handleClick : undefined}
        onKeyDown={uploadState !== 'uploading' ? handleKeyDown : undefined}
        tabIndex={uploadState !== 'uploading' ? 0 : -1}
        role="button"
        aria-label="Upload CSV file"
        aria-busy={uploadState === 'uploading'}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".csv"
          onChange={handleChange}
          className="csv-upload__input"
          aria-hidden="true"
          disabled={uploadState === 'uploading'}
        />

        {uploadState === 'uploading' ? (
          <div className="csv-upload__loading">
            <div className="csv-upload__spinner" />
            <p className="csv-upload__text">Uploading to server...</p>
            <div className="csv-upload__progress">
              <div 
                className="csv-upload__progress-bar" 
                style={{ width: `${uploadProgress}%` }}
                role="progressbar"
                aria-valuenow={uploadProgress}
                aria-valuemin="0"
                aria-valuemax="100"
              />
            </div>
            <p className="csv-upload__subtext caption">{uploadProgress}% complete</p>
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
          {fileRef.current && (
            <button 
              type="button" 
              className="csv-upload__retry-btn"
              onClick={handleRetry}
            >
              Retry
            </button>
          )}
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
