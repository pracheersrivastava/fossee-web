/**
 * App Component
 * FOSSEE Scientific Analytics UI - CHEM•VIZ
 * 
 * Main application shell with Header, Sidebar, and MainContent.
 * Follows design.md specifications exactly.
 * 
 * State Flow:
 * 1. Upload CSV → API returns datasetId + metadata
 * 2. Summary shows KPIs (can call API for analysis preview)
 * 3. Analysis fetches full chart data using datasetId
 */

import React, { useState, useCallback } from 'react';
import { Header, Sidebar, MainContent } from './components/Layout';
import { CSVUpload } from './components/CSVUpload';
import { SummaryScreen } from './components/SummaryScreen';
import { AnalysisCharts } from './components/Charts';
import './App.css';

const PAGE_TITLES = {
  upload: 'Upload Equipment Data',
  summary: 'Data Summary',
  analysis: 'Parameter Analysis',
  history: 'Analysis History',
};

function App() {
  const [activeScreen, setActiveScreen] = useState('upload');
  // Store both metadata and datasetId from upload response
  const [uploadedData, setUploadedData] = useState(null);
  const [uploadError, setUploadError] = useState(null);

  const handleNavigate = useCallback((screenId) => {
    setActiveScreen(screenId);
  }, []);

  /**
   * Handle successful upload
   * Receives full response from API including datasetId
   */
  const handleUploadComplete = useCallback((data) => {
    setUploadedData(data);
    setUploadError(null);
    // Auto-navigate to summary after upload
    setActiveScreen('summary');
  }, []);

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
        return <ScreenPlaceholder message="Analysis history table will appear here." />;
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
          recentDatasets={uploadedData ? [uploadedData] : []}
        />
        <MainContent title={PAGE_TITLES[activeScreen]}>
          {renderScreen()}
        </MainContent>
      </div>
    </div>
  );
}

/**
 * Placeholder component for screen content
 * Will be replaced with actual screen components
 */
function ScreenPlaceholder({ message }) {
  return (
    <div className="screen-placeholder">
      <p className="text-secondary">{message}</p>
    </div>
  );
}

export default App;
