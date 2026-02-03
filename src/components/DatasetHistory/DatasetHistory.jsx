/**
 * Dataset History Component
 * FOSSEE Scientific Analytics UI
 * 
 * Displays last 5 uploads in sidebar with:
 * - Filename and timestamp
 * - Small sparkline preview
 * - Hover actions: Re-analyze / Compare
 */

import React, { useState } from 'react';
import './DatasetHistory.css';

/**
 * Mini sparkline SVG component
 * Renders a small line chart from data points
 */
function Sparkline({ data = [], color = 'var(--color-academic-blue)', width = 48, height = 16 }) {
  if (!data || data.length < 2) {
    return <span className="sparkline sparkline--empty" style={{ width, height }} />;
  }

  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;

  const points = data.map((value, index) => {
    const x = (index / (data.length - 1)) * width;
    const y = height - ((value - min) / range) * height;
    return `${x},${y}`;
  }).join(' ');

  return (
    <svg 
      className="sparkline" 
      width={width} 
      height={height} 
      viewBox={`0 0 ${width} ${height}`}
      aria-hidden="true"
    >
      <polyline
        points={points}
        fill="none"
        stroke={color}
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

/**
 * Single history item with hover actions
 */
function HistoryItem({ 
  id,
  filename, 
  timestamp, 
  rowCount,
  sparklineData,
  isSelected,
  onReanalyze, 
  onCompare 
}) {
  const [isHovered, setIsHovered] = useState(false);

  // Format timestamp relative or absolute
  const formatTimestamp = (ts) => {
    const date = new Date(ts);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric' 
    });
  };

  // Truncate filename if too long
  const truncateFilename = (name, maxLength = 18) => {
    if (name.length <= maxLength) return name;
    const ext = name.slice(name.lastIndexOf('.'));
    const base = name.slice(0, name.lastIndexOf('.'));
    const truncated = base.slice(0, maxLength - ext.length - 3);
    return `${truncated}...${ext}`;
  };

  return (
    <li 
      className={`history-item ${isSelected ? 'history-item--selected' : ''}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="history-item__content">
        <div className="history-item__info">
          <span className="history-item__filename" title={filename}>
            {truncateFilename(filename)}
          </span>
          <span className="history-item__meta">
            <span className="history-item__timestamp">{formatTimestamp(timestamp)}</span>
            {rowCount && (
              <span className="history-item__rows">{rowCount} rows</span>
            )}
          </span>
        </div>
        
        {sparklineData && sparklineData.length > 0 && (
          <div className="history-item__sparkline">
            <Sparkline data={sparklineData} />
          </div>
        )}
      </div>

      {/* Hover actions */}
      <div className={`history-item__actions ${isHovered ? 'history-item__actions--visible' : ''}`}>
        <button 
          className="history-item__action"
          onClick={() => onReanalyze?.(id)}
          title="Re-analyze this dataset"
        >
          ↻
        </button>
        <button 
          className="history-item__action"
          onClick={() => onCompare?.(id)}
          title="Compare with current"
        >
          ⇋
        </button>
      </div>
    </li>
  );
}

/**
 * Dataset History List
 * Shows last 5 uploads with actions
 */
export function DatasetHistory({ 
  datasets = [], 
  selectedId,
  maxItems = 5,
  onReanalyze,
  onCompare,
  onClearHistory
}) {
  const displayedDatasets = datasets.slice(0, maxItems);
  const hasDatasets = displayedDatasets.length > 0;

  return (
    <div className="dataset-history">
      <div className="dataset-history__header">
        <h3 className="dataset-history__title">Recent Datasets</h3>
        {hasDatasets && onClearHistory && (
          <button 
            className="dataset-history__clear"
            onClick={onClearHistory}
            title="Clear history"
          >
            Clear
          </button>
        )}
      </div>

      {hasDatasets ? (
        <ul className="dataset-history__list">
          {displayedDatasets.map((dataset) => (
            <HistoryItem
              key={dataset.id}
              id={dataset.id}
              filename={dataset.filename}
              timestamp={dataset.timestamp}
              rowCount={dataset.rowCount}
              sparklineData={dataset.sparklineData}
              isSelected={dataset.id === selectedId}
              onReanalyze={onReanalyze}
              onCompare={onCompare}
            />
          ))}
        </ul>
      ) : (
        <p className="dataset-history__empty">No recent datasets</p>
      )}

      {datasets.length > maxItems && (
        <span className="dataset-history__more">
          +{datasets.length - maxItems} more
        </span>
      )}
    </div>
  );
}

export { Sparkline, HistoryItem };
export default DatasetHistory;
