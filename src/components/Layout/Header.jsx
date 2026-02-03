/**
 * Header Component
 * FOSSEE Scientific Analytics UI
 * 
 * Persistent header with app title and FOSSEE branding.
 * Height: 56px, Background: Deep Indigo (#1E2A38)
 */

import React from 'react';
import './Header.css';

export function Header() {
  return (
    <header className="header">
      <div className="header__brand">
        <span className="header__logo">⬡</span>
        <h1 className="header__title">CHEM•VIZ</h1>
      </div>
      <div className="header__context">
        <span className="header__fossee">FOSSEE</span>
      </div>
    </header>
  );
}

export default Header;
