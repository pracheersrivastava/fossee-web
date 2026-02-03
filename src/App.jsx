/**
 * App Component
 * FOSSEE Scientific Analytics UI - CHEM•VIZ
 * 
 * Main application shell with Header, Sidebar, and MainContent.
 * Follows design.md specifications exactly.
 */

import React, { useState, useCallback } from 'react';
import { Header, Sidebar, MainContent } from './components/Layout';
import { CSVUpload } from './components/CSVUpload';
import './App.css';

const PAGE_TITLES = {
  upload: 'Upload Equipment Data',
  summary: 'Data Summary',
  analysis: 'Parameter Analysis',
  history: 'Analysis History',
};

function App() {
  const [activeScreen, setActiveScreen] = useState('upload');
  const [uploadedData, setUploadedData] = useState(null);

  const handleNavigate = useCallback((screenId) => {
    setActiveScreen(screenId);
  }, []);

  const handleUploadComplete = useCallback((data) => {
    setUploadedData(data);
  }, []);

  const handleUploadClear = useCallback(() => {
    setUploadedData(null);
  }, []);

  const renderScreen = () => {
    switch (activeScreen) {
      case 'upload':
        return (
          <CSVUpload
            onUploadComplete={handleUploadComplete}
            onClear={handleUploadClear}
          />
        );
      case 'summary':
        return <ScreenPlaceholder message="Data summary and KPIs will appear here." />;
      case 'analysis':
        return <ScreenPlaceholder message="Charts and analysis will appear here." />;
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
