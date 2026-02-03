/**
 * KPI Card Components
 * FOSSEE Scientific Analytics UI
 * 
 * Summary KPI cards following design.md Section 5.3:
 * - Background: White
 * - Radius: 8px
 * - Padding: 16px
 * - Shadow: 0px 2px 6px rgba(0,0,0,0.05)
 */

import React from 'react';
import './KPICards.css';

/**
 * Individual KPI Card
 * 
 * @param {string} label - KPI label (e.g., "Total Equipment")
 * @param {string|number} value - KPI value
 * @param {string} unit - Optional unit (e.g., "m³/hr", "°C")
 * @param {string} icon - Optional icon character
 * @param {string} accentColor - Optional accent color for icon background
 */
export function KPICard({ label, value, unit, icon, accentColor }) {
  return (
    <div className="kpi-card">
      {icon && (
        <div 
          className="kpi-card__icon"
          style={accentColor ? { 
            backgroundColor: `${accentColor}15`,
            color: accentColor 
          } : undefined}
          aria-hidden="true"
        >
          {icon}
        </div>
      )}
      <div className="kpi-card__content">
        <span className="kpi-card__value">
          {typeof value === 'number' ? value.toLocaleString() : value}
          {unit && <span className="kpi-card__unit">{unit}</span>}
        </span>
        <span className="kpi-card__label">{label}</span>
      </div>
    </div>
  );
}

/**
 * KPI Grid - Responsive layout for KPI cards
 * 
 * @param {React.ReactNode} children - KPICard components
 */
export function KPIGrid({ children }) {
  return (
    <div className="kpi-grid">
      {children}
    </div>
  );
}

/**
 * Summary KPIs Component
 * Pre-configured KPIs for equipment data summary
 * 
 * @param {object} data - Data object with computed KPI values
 * @param {number} data.totalEquipment - Total equipment count
 * @param {number} data.avgFlowrate - Average flowrate
 * @param {number} data.avgTemperature - Average temperature
 * @param {string} data.dominantType - Most common equipment type
 */
export function SummaryKPIs({ data }) {
  const {
    totalEquipment = 0,
    avgFlowrate = 0,
    avgTemperature = 0,
    dominantType = '—',
  } = data || {};

  return (
    <KPIGrid>
      <KPICard
        icon="⚙"
        label="Total Equipment"
        value={totalEquipment}
        accentColor="#8B5CF6"
      />
      <KPICard
        icon="◎"
        label="Avg. Flowrate"
        value={avgFlowrate.toFixed(1)}
        unit=" m³/hr"
        accentColor="#14B8A6"
      />
      <KPICard
        icon="◐"
        label="Avg. Temperature"
        value={avgTemperature.toFixed(1)}
        unit="°C"
        accentColor="#F59E0B"
      />
      <KPICard
        icon="▣"
        label="Dominant Type"
        value={dominantType}
        accentColor="#8B5CF6"
      />
    </KPIGrid>
  );
}

export default KPICard;
