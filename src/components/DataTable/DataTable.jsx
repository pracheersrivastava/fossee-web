/**
 * Data Table Components
 * FOSSEE Scientific Analytics UI
 *
 * Equipment data table following design.md Section 5.4:
 * - Header background: #F1F5F9
 * - Row height: 44px
 * - Zebra striping: #FAFAFA
 * - Sticky headers: Enabled
 * - No vertical grid lines
 * - Hover highlight only
 */

import React, { useMemo, useState, useCallback } from 'react';
import './DataTable.css';

/**
 * Table Header Cell
 */
const TableHeaderCell = ({ children, sortable, sorted, sortDirection, onSort }) => {
  const handleClick = () => {
    if (sortable && onSort) {
      onSort();
    }
  };

  return (
    <th 
      className={`table-header-cell ${sortable ? 'sortable' : ''} ${sorted ? 'sorted' : ''}`}
      onClick={handleClick}
    >
      <div className="header-content">
        <span>{children}</span>
        {sortable && (
          <span className="sort-indicator">
            {sorted && sortDirection === 'asc' && '↑'}
            {sorted && sortDirection === 'desc' && '↓'}
            {!sorted && '↕'}
          </span>
        )}
      </div>
    </th>
  );
};

/**
 * Table Cell
 */
const TableCell = ({ children, align = 'left', className = '' }) => (
  <td className={`table-cell ${className}`} style={{ textAlign: align }}>
    {children}
  </td>
);

/**
 * Table Row
 */
const TableRow = ({ children, onClick, isEven }) => (
  <tr 
    className={`table-row ${isEven ? 'even' : 'odd'}`}
    onClick={onClick}
  >
    {children}
  </tr>
);

/**
 * Data Table Component
 *
 * @param {Object} props
 * @param {Array} props.columns - Column definitions [{key, label, sortable?, align?, render?}]
 * @param {Array} props.data - Array of row data objects
 * @param {Function} props.onRowClick - Optional row click handler
 * @param {string} props.emptyMessage - Message when no data
 */
export const DataTable = ({
  columns = [],
  data = [],
  onRowClick,
  emptyMessage = 'No data available',
  sortable = true,
}) => {
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });

  const handleSort = useCallback((key) => {
    setSortConfig((prev) => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc',
    }));
  }, []);

  const sortedData = useMemo(() => {
    if (!sortConfig.key) return data;

    return [...data].sort((a, b) => {
      const aVal = a[sortConfig.key];
      const bVal = b[sortConfig.key];

      if (aVal === null || aVal === undefined) return 1;
      if (bVal === null || bVal === undefined) return -1;

      let comparison = 0;
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        comparison = aVal - bVal;
      } else {
        comparison = String(aVal).localeCompare(String(bVal));
      }

      return sortConfig.direction === 'asc' ? comparison : -comparison;
    });
  }, [data, sortConfig]);

  if (!columns.length) {
    return null;
  }

  return (
    <div className="table-container">
      <table className="data-table">
        <thead className="table-header">
          <tr>
            {columns.map((col) => (
              <TableHeaderCell
                key={col.key}
                sortable={sortable && col.sortable !== false}
                sorted={sortConfig.key === col.key}
                sortDirection={sortConfig.direction}
                onSort={() => handleSort(col.key)}
              >
                {col.label}
              </TableHeaderCell>
            ))}
          </tr>
        </thead>
        <tbody className="table-body">
          {sortedData.length === 0 ? (
            <tr className="empty-row">
              <td colSpan={columns.length} className="empty-cell">
                {emptyMessage}
              </td>
            </tr>
          ) : (
            sortedData.map((row, index) => (
              <TableRow
                key={row.id || index}
                isEven={index % 2 === 1}
                onClick={onRowClick ? () => onRowClick(row) : undefined}
              >
                {columns.map((col) => (
                  <TableCell key={col.key} align={col.align}>
                    {col.render ? col.render(row[col.key], row) : row[col.key]}
                  </TableCell>
                ))}
              </TableRow>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
};

/**
 * Equipment Data Table
 *
 * Pre-configured table for equipment data display.
 * Shows: ID, Type, Temperature, Pressure, Flowrate, Status
 */
export const EquipmentDataTable = ({ data = [], onRowClick }) => {
  const columns = useMemo(() => [
    {
      key: 'id',
      label: 'Equipment ID',
      sortable: true,
    },
    {
      key: 'type',
      label: 'Type',
      sortable: true,
    },
    {
      key: 'temperature',
      label: 'Temperature (°C)',
      sortable: true,
      align: 'right',
      render: (value) => value?.toFixed(1) ?? '—',
    },
    {
      key: 'pressure',
      label: 'Pressure (bar)',
      sortable: true,
      align: 'right',
      render: (value) => value?.toFixed(2) ?? '—',
    },
    {
      key: 'flowrate',
      label: 'Flowrate (m³/hr)',
      sortable: true,
      align: 'right',
      render: (value) => value?.toFixed(2) ?? '—',
    },
    {
      key: 'status',
      label: 'Status',
      sortable: true,
      render: (value) => (
        <span className={`status-badge status-${value?.toLowerCase() || 'unknown'}`}>
          {value || 'Unknown'}
        </span>
      ),
    },
  ], []);

  // Transform data to expected format
  const tableData = useMemo(() => {
    return data.map((row, index) => ({
      id: row.id || row.equipment_id || `EQ-${String(index + 1).padStart(3, '0')}`,
      type: row.type || row.equipment_type || 'Unknown',
      temperature: parseFloat(row.temperature) || null,
      pressure: parseFloat(row.pressure) || null,
      flowrate: parseFloat(row.flowrate) || null,
      status: row.status || 'Active',
    }));
  }, [data]);

  return (
    <DataTable
      columns={columns}
      data={tableData}
      onRowClick={onRowClick}
      emptyMessage="No equipment data available. Upload a CSV file to view data."
    />
  );
};

/**
 * Table Card wrapper
 */
export const TableCard = ({ title, children, actions }) => (
  <div className="table-card">
    <div className="table-card-header">
      <h3 className="table-card-title">{title}</h3>
      {actions && <div className="table-card-actions">{actions}</div>}
    </div>
    <div className="table-card-content">
      {children}
    </div>
  </div>
);

export default DataTable;
