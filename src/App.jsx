/**
 * App Component
 * CHEM•VIZ - Chemical Equipment Parameter Visualizer
 * 
 * Main application shell with Header, Sidebar, and MainContent.
 * Follows design.md specifications exactly.
 * 
 * State Flow:
 * 1. Upload CSV → API returns datasetId + metadata
 * 2. Summary shows KPIs (can call API for analysis preview)
 * 3. Analysis fetches full chart data using datasetId
 * 4. History tracks last 5 uploads (USER-SCOPED - only visible when logged in)
 */

import React, { useState, useCallback, useEffect, useRef } from 'react';
import { Header, Sidebar, MainContent } from './components/Layout';
import { CSVUpload } from './components/CSVUpload';
import { SummaryScreen } from './components/SummaryScreen';
import { AnalysisCharts } from './components/Charts';
import { DatasetHistory } from './components/DatasetHistory';
import { getRecentDatasets, claimDataset } from './services/api';
import { authService } from './services/authService';
import './App.css';

const PAGE_TITLES = {
  upload: 'Upload Equipment Data',
  summary: 'Data Summary',
  analysis: 'Parameter Analysis',
  history: 'Dataset History',
};

const MAX_HISTORY_ITEMS = 5;

function App() {
  const [activeScreen, setActiveScreen] = useState('upload');
  // Store both metadata and datasetId from upload response
  const [uploadedData, setUploadedData] = useState(null);
  const [uploadError, setUploadError] = useState(null);
  // Track recent datasets for history (USER-SCOPED)
  const [recentDatasets, setRecentDatasets] = useState([]);
  // Track auth state
  const [isAuthenticated, setIsAuthenticated] = useState(authService.isAuthenticated());
  // Track pending dataset to claim after login (anonymous uploads)
  const pendingClaimDatasetRef = useRef(null);

  const handleNavigate = useCallback((screenId) => {
    setActiveScreen(screenId);
  }, []);

  /**
   * Load recent datasets from API - ONLY when authenticated
   */
  const loadHistory = useCallback(async () => {
    if (!authService.isAuthenticated()) {
      setRecentDatasets([]);
      return;
    }
    
    try {
      const datasets = await getRecentDatasets(MAX_HISTORY_ITEMS);
      // Transform API response to match DatasetHistory format
      const formatted = datasets.map(d => ({
        id: d.id,
        filename: d.filename || d.original_filename || 'Unknown',
        timestamp: d.upload_time || d.uploaded_at,
        rowCount: d.row_count,
      }));
      setRecentDatasets(formatted);
    } catch (err) {
      console.warn('Could not load recent datasets:', err);
      setRecentDatasets([]);
    }
  }, []);

  /**
   * Subscribe to auth state changes
   */
  useEffect(() => {
    // Load history on mount if authenticated
    loadHistory();
    
    // Subscribe to auth changes
    const unsubscribe = authService.subscribe(async ({ user, token }) => {
      const authenticated = !!token;
      setIsAuthenticated(authenticated);
      
      if (authenticated) {
        // User logged in - claim any pending anonymous dataset
        if (pendingClaimDatasetRef.current) {
          const datasetId = pendingClaimDatasetRef.current;
          pendingClaimDatasetRef.current = null;
          
          try {
            await claimDataset(datasetId);
            console.log(`Dataset ${datasetId} claimed successfully`);
          } catch (err) {
            console.warn('Failed to claim dataset:', err);
            // Non-fatal - user can still use the app
          }
        }
        
        // Load their history (including newly claimed dataset)
        loadHistory();
      } else {
        // User logged out - clear history and uploaded data
        setRecentDatasets([]);
        setUploadedData(null);
        setActiveScreen('upload');
      }
    });
    
    return unsubscribe;
  }, [loadHistory]);

  /**
   * Handle successful upload
   * Receives full response from API including datasetId
   */
  const handleUploadComplete = useCallback((data) => {
    setUploadedData(data);
    setUploadError(null);
    
    // If not authenticated, mark this dataset for claiming after login
    if (!authService.isAuthenticated() && data.datasetId) {
      pendingClaimDatasetRef.current = data.datasetId;
      console.log(`Anonymous upload - dataset ${data.datasetId} pending claim after login`);
    }
    
    // Refresh history from backend (only matters if authenticated)
    loadHistory();
    
    // Auto-navigate to summary after upload
    setActiveScreen('summary');
  }, [loadHistory]);

  /**
   * Handle upload error
   */
  const handleUploadError = useCallback((error) => {
    setUploadError(error.message || 'Upload failed');
    console.error('Upload error:', error);
  }, []);

  const handleUploadClear = useCallback(() => {
    setUploadedData(null);
    setUploadError(null);
  }, []);

  const handleGenerateAnalysis = useCallback(() => {
    setActiveScreen('analysis');
  }, []);

  const handleUploadDifferent = useCallback(() => {
    setUploadedData(null);
    setUploadError(null);
    setActiveScreen('upload');
  }, []);

  /**
   * Handle selecting a dataset from history (show summary)
   */
  const handleSelectDataset = useCallback((datasetId) => {
    const dataset = recentDatasets.find(d => d.id === datasetId);
    if (dataset) {
      setUploadedData({
        datasetId: dataset.id,
        fileName: dataset.filename,
        rowCount: dataset.rowCount,
      });
      setActiveScreen('summary');
    }
  }, [recentDatasets]);

  /**
   * Handle re-analyze from history (go directly to analysis)
   */
  const handleReanalyze = useCallback((datasetId) => {
    const dataset = recentDatasets.find(d => d.id === datasetId);
    if (dataset) {
      setUploadedData({
        datasetId: dataset.id,
        fileName: dataset.filename,
        rowCount: dataset.rowCount,
      });
      setActiveScreen('analysis');
    }
  }, [recentDatasets]);

  /**
   * Handle clear history
   */
  const handleClearHistory = useCallback(() => {
    setRecentDatasets([]);
  }, []);

  const renderScreen = () => {
    switch (activeScreen) {
      case 'upload':
        return (
          <CSVUpload
            onUploadComplete={handleUploadComplete}
            onClear={handleUploadClear}
            onError={handleUploadError}
          />
        );
      case 'summary':
        return (
          <SummaryScreen
            uploadData={uploadedData}
            onGenerateAnalysis={handleGenerateAnalysis}
            onUploadDifferent={handleUploadDifferent}
          />
        );
      case 'analysis':
        return (
          <AnalysisCharts 
            datasetId={uploadedData?.datasetId}
            equipmentData={uploadedData}
          />
        );
      case 'history':
        return (
          <HistoryScreen 
            datasets={recentDatasets}
            onReanalyze={handleReanalyze}
            onClearHistory={handleClearHistory}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="app">
      <Header />
      <div className="app__body">
        <Sidebar 
          activeItem={activeScreen} 
          onNavigate={handleNavigate}
          datasets={recentDatasets}
          selectedDatasetId={uploadedData?.datasetId}
          onSelectDataset={handleSelectDataset}
          onReanalyze={handleReanalyze}
          onClearHistory={handleClearHistory}
          isAuthenticated={isAuthenticated}
        />
        <MainContent title={PAGE_TITLES[activeScreen]}>
          {renderScreen()}
        </MainContent>
      </div>
    </div>
  );
}

/**
 * History Screen - Full-page dataset history view
 */
function HistoryScreen({ datasets, onReanalyze, onClearHistory }) {
  if (!datasets || datasets.length === 0) {
    return (
      <div className="history-screen history-screen--empty">
        <div className="history-screen__empty-icon">📋</div>
        <h3 className="history-screen__empty-title">No datasets yet</h3>
        <p className="history-screen__empty-text">
          Upload a CSV file to start tracking your dataset history.
        </p>
      </div>
    );
  }

  return (
    <div className="history-screen">
      <div className="history-screen__header">
        <p className="history-screen__count">{datasets.length} dataset{datasets.length !== 1 ? 's' : ''} in history</p>
        {onClearHistory && (
          <button className="btn btn--secondary btn--sm" onClick={onClearHistory}>
            Clear All
          </button>
        )}
      </div>
      <div className="history-screen__list">
        {datasets.map((dataset) => (
          <div key={dataset.id} className="history-screen__item">
            <div className="history-screen__item-info">
              <span className="history-screen__item-icon">📄</span>
              <div className="history-screen__item-details">
                <span className="history-screen__item-name">{dataset.filename}</span>
                <span className="history-screen__item-meta">
                  {dataset.rowCount} rows • {formatRelativeTime(dataset.timestamp)}
                </span>
              </div>
            </div>
            <button 
              className="btn btn--primary btn--sm"
              onClick={() => onReanalyze?.(dataset.id)}
            >
              Analyze
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

/**
 * Format timestamp as relative time
 */
function formatRelativeTime(timestamp) {
  if (!timestamp) return '';
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

export default App;
