/**
 * Sidebar Component
 * FOSSEE Scientific Analytics UI
 * 
 * Navigation sidebar with dataset history.
 * Width: 240px, Background: Pure White (#FFFFFF)
 */

import React from 'react';
import { DatasetHistory } from '../DatasetHistory';
import './Sidebar.css';

const NAV_ITEMS = [
  { id: 'upload', label: 'Upload', icon: '↑' },
  { id: 'summary', label: 'Summary', icon: '▤' },
  { id: 'analysis', label: 'Analysis', icon: '◩' },
  { id: 'history', label: 'History', icon: '◷' },
];

export function Sidebar({ 
  activeItem = 'upload', 
  onNavigate,
  datasets = [],
  selectedDatasetId,
  onReanalyze,
  onCompare,
  onClearHistory
}) {
  return (
    <aside className="sidebar">
      <nav className="sidebar__nav">
        <ul className="sidebar__nav-list">
          {NAV_ITEMS.map((item) => (
            <li key={item.id}>
              <button
                className={`sidebar__nav-item ${activeItem === item.id ? 'sidebar__nav-item--active' : ''}`}
                onClick={() => onNavigate?.(item.id)}
                aria-current={activeItem === item.id ? 'page' : undefined}
              >
                <span className="sidebar__nav-icon" aria-hidden="true">
                  {item.icon}
                </span>
                <span className="sidebar__nav-label">{item.label}</span>
              </button>
            </li>
          ))}
        </ul>
      </nav>

      <div className="sidebar__history">
        <DatasetHistory
          datasets={datasets}
          selectedId={selectedDatasetId}
          maxItems={5}
          onReanalyze={onReanalyze}
          onCompare={onCompare}
          onClearHistory={onClearHistory}
        />
      </div>

      <div className="sidebar__footer">
        <span className="meta">FOSSEE Project</span>
        <span className="meta">IIT Bombay</span>
      </div>
    </aside>
  );
}

export default Sidebar;
