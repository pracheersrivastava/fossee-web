/**
 * MainContent Component
 * FOSSEE Scientific Analytics UI
 * 
 * Main content area with proper spacing and max-width.
 * Padding: 24px (lg), Max-width: 1200px - sidebar
 */

import React from 'react';
import './MainContent.css';

export function MainContent({ children, title }) {
  return (
    <main className="main-content">
      <div className="main-content__inner">
        {title && <h1 className="main-content__title">{title}</h1>}
        {children}
      </div>
    </main>
  );
}

export default MainContent;
