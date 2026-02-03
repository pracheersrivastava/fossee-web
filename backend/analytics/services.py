"""
Analytics Services - Core analytics computations using Pandas
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional


class AnalyticsService:
    """
    Service class for computing analytics on chemical equipment datasets.
    Uses Pandas for efficient data processing and statistical computations.
    """
    
    def __init__(self, data: List[Dict[str, Any]], columns: List[str], column_types: Dict[str, str]):
        """
        Initialize analytics service with dataset.
        
        Args:
            data: List of dictionaries representing dataset rows
            columns: List of column names
            column_types: Dictionary mapping column names to their types
        """
        self.df = pd.DataFrame(data)
        self.columns = columns
        self.column_types = column_types
        self._prepare_data()
    
    def _prepare_data(self):
        """Prepare and clean the dataframe for analysis."""
        # Convert numeric columns
        for col, dtype in self.column_types.items():
            if col in self.df.columns:
                if dtype in ['integer', 'float']:
                    self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                elif dtype == 'datetime':
                    self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
    
    def get_numeric_columns(self) -> List[str]:
        """Get list of numeric column names."""
        return [col for col, dtype in self.column_types.items() 
                if dtype in ['integer', 'float']]
    
    def get_categorical_columns(self) -> List[str]:
        """Get list of categorical (string) column names."""
        return [col for col, dtype in self.column_types.items() 
                if dtype == 'string']
    
    def compute_summary_statistics(self) -> Dict[str, Any]:
        """
        Compute comprehensive summary statistics for the dataset.
        
        Returns:
            Dictionary containing:
            - overview: Basic dataset info
            - numeric_summary: Statistics for numeric columns
            - categorical_summary: Value counts for categorical columns
            - kpi_metrics: Key performance indicators
        """
        numeric_cols = self.get_numeric_columns()
        categorical_cols = self.get_categorical_columns()
        
        result = {
            'overview': {
                'total_rows': len(self.df),
                'total_columns': len(self.columns),
                'numeric_columns': len(numeric_cols),
                'categorical_columns': len(categorical_cols),
                'missing_values': int(self.df.isnull().sum().sum()),
                'memory_usage': float(self.df.memory_usage(deep=True).sum()) / 1024,  # KB
            },
            'numeric_summary': {},
            'categorical_summary': {},
            'kpi_metrics': {},
        }
        
        # Compute numeric statistics
        for col in numeric_cols:
            if col in self.df.columns:
                series = self.df[col].dropna()
                if len(series) > 0:
                    result['numeric_summary'][col] = {
                        'count': int(series.count()),
                        'mean': float(series.mean()) if not np.isnan(series.mean()) else None,
                        'std': float(series.std()) if not np.isnan(series.std()) else None,
                        'min': float(series.min()) if not np.isnan(series.min()) else None,
                        'max': float(series.max()) if not np.isnan(series.max()) else None,
                        'median': float(series.median()) if not np.isnan(series.median()) else None,
                        'q1': float(series.quantile(0.25)) if not np.isnan(series.quantile(0.25)) else None,
                        'q3': float(series.quantile(0.75)) if not np.isnan(series.quantile(0.75)) else None,
                        'missing': int(self.df[col].isnull().sum()),
                    }
        
        # Compute categorical statistics
        for col in categorical_cols:
            if col in self.df.columns:
                value_counts = self.df[col].value_counts().head(10)
                result['categorical_summary'][col] = {
                    'unique_values': int(self.df[col].nunique()),
                    'top_values': value_counts.to_dict(),
                    'missing': int(self.df[col].isnull().sum()),
                }
        
        # Compute KPI metrics (using first few numeric columns)
        result['kpi_metrics'] = self._compute_kpi_metrics(numeric_cols[:4])
        
        return result
    
    def _compute_kpi_metrics(self, columns: List[str]) -> List[Dict[str, Any]]:
        """
        Compute KPI metrics for dashboard cards.
        
        Args:
            columns: List of column names to generate KPIs for
            
        Returns:
            List of KPI metric dictionaries
        """
        kpis = []
        
        for col in columns:
            if col not in self.df.columns:
                continue
                
            series = self.df[col].dropna()
            if len(series) == 0:
                continue
            
            mean_val = series.mean()
            
            # Calculate trend (comparing first half vs second half)
            mid = len(series) // 2
            if mid > 0:
                first_half_mean = series.iloc[:mid].mean()
                second_half_mean = series.iloc[mid:].mean()
                if first_half_mean != 0:
                    trend_pct = ((second_half_mean - first_half_mean) / first_half_mean) * 100
                else:
                    trend_pct = 0
            else:
                trend_pct = 0
            
            kpis.append({
                'id': col.lower().replace(' ', '_'),
                'label': col,
                'value': round(mean_val, 2) if not np.isnan(mean_val) else 0,
                'unit': self._infer_unit(col),
                'trend': round(trend_pct, 1),
                'trend_direction': 'up' if trend_pct > 0 else 'down' if trend_pct < 0 else 'stable',
            })
        
        return kpis
    
    def _infer_unit(self, column_name: str) -> str:
        """Infer the unit of measurement from column name."""
        name_lower = column_name.lower()
        
        if 'temperature' in name_lower or 'temp' in name_lower:
            return '°C'
        elif 'pressure' in name_lower:
            return 'bar'
        elif 'flow' in name_lower:
            return 'L/min'
        elif 'concentration' in name_lower or 'conc' in name_lower:
            return 'mol/L'
        elif 'ph' in name_lower:
            return ''
        elif 'voltage' in name_lower:
            return 'V'
        elif 'current' in name_lower:
            return 'A'
        elif 'power' in name_lower:
            return 'kW'
        elif 'time' in name_lower:
            return 's'
        elif 'weight' in name_lower or 'mass' in name_lower:
            return 'kg'
        elif 'volume' in name_lower:
            return 'L'
        elif 'speed' in name_lower or 'rpm' in name_lower:
            return 'RPM'
        elif 'percent' in name_lower or '%' in name_lower:
            return '%'
        else:
            return ''
    
    def get_chart_data(self, chart_type: str, x_column: Optional[str] = None, 
                       y_column: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Generate data formatted for different chart types.
        
        Args:
            chart_type: Type of chart ('line', 'bar', 'pie', 'scatter', 'histogram', 'heatmap')
            x_column: Column to use for X axis
            y_column: Column to use for Y axis
            **kwargs: Additional chart-specific parameters
            
        Returns:
            Dictionary with chart-formatted data
        """
        if chart_type == 'line':
            return self._get_line_chart_data(x_column, y_column)
        elif chart_type == 'bar':
            return self._get_bar_chart_data(x_column, y_column)
        elif chart_type == 'pie':
            return self._get_pie_chart_data(x_column or y_column)
        elif chart_type == 'scatter':
            return self._get_scatter_chart_data(x_column, y_column)
        elif chart_type == 'histogram':
            return self._get_histogram_data(x_column or y_column, kwargs.get('bins', 20))
        elif chart_type == 'heatmap':
            return self._get_heatmap_data()
        elif chart_type == 'combined':
            return self._get_combined_chart_data()
        else:
            return {'error': f'Unknown chart type: {chart_type}'}
    
    def _get_line_chart_data(self, x_column: Optional[str], y_column: Optional[str]) -> Dict[str, Any]:
        """Generate line chart data."""
        numeric_cols = self.get_numeric_columns()
        
        if not numeric_cols:
            return {'error': 'No numeric columns available for line chart'}
        
        # Use index as X if no x_column specified
        if x_column and x_column in self.df.columns:
            x_data = self.df[x_column].tolist()
            x_label = x_column
        else:
            x_data = list(range(len(self.df)))
            x_label = 'Index'
        
        # Use first numeric column if no y_column specified
        y_cols = [y_column] if y_column and y_column in numeric_cols else numeric_cols[:3]
        
        datasets = []
        for col in y_cols:
            datasets.append({
                'label': col,
                'data': [
                    None if pd.isna(v) else float(v) 
                    for v in self.df[col].tolist()
                ]
            })
        
        return {
            'type': 'line',
            'labels': [str(x) for x in x_data],
            'datasets': datasets,
            'xAxisLabel': x_label,
            'yAxisLabel': 'Value',
        }
    
    def _get_bar_chart_data(self, x_column: Optional[str], y_column: Optional[str]) -> Dict[str, Any]:
        """Generate bar chart data."""
        categorical_cols = self.get_categorical_columns()
        numeric_cols = self.get_numeric_columns()
        
        # Determine X column (categorical)
        if x_column and x_column in self.df.columns:
            x_col = x_column
        elif categorical_cols:
            x_col = categorical_cols[0]
        else:
            # Use first column as category
            x_col = self.columns[0] if self.columns else None
        
        # Determine Y column (numeric for aggregation)
        if y_column and y_column in numeric_cols:
            y_col = y_column
        elif numeric_cols:
            y_col = numeric_cols[0]
        else:
            # Just count occurrences
            y_col = None
        
        if x_col is None:
            return {'error': 'No suitable columns for bar chart'}
        
        # Aggregate data
        if y_col:
            aggregated = self.df.groupby(x_col)[y_col].mean().reset_index()
            labels = aggregated[x_col].astype(str).tolist()[:20]  # Limit to 20 categories
            values = [float(v) if not pd.isna(v) else 0 for v in aggregated[y_col].tolist()[:20]]
            y_label = f'Average {y_col}'
        else:
            value_counts = self.df[x_col].value_counts().head(20)
            labels = value_counts.index.astype(str).tolist()
            values = value_counts.values.tolist()
            y_label = 'Count'
        
        return {
            'type': 'bar',
            'labels': labels,
            'datasets': [{
                'label': y_label,
                'data': values,
            }],
            'xAxisLabel': x_col,
            'yAxisLabel': y_label,
        }
    
    def _get_pie_chart_data(self, column: Optional[str]) -> Dict[str, Any]:
        """Generate pie chart data."""
        categorical_cols = self.get_categorical_columns()
        
        # Determine column to use
        if column and column in self.df.columns:
            col = column
        elif categorical_cols:
            col = categorical_cols[0]
        else:
            col = self.columns[0] if self.columns else None
        
        if col is None:
            return {'error': 'No suitable column for pie chart'}
        
        value_counts = self.df[col].value_counts().head(8)  # Limit to 8 slices
        
        return {
            'type': 'pie',
            'labels': value_counts.index.astype(str).tolist(),
            'datasets': [{
                'label': col,
                'data': value_counts.values.tolist(),
            }],
        }
    
    def _get_scatter_chart_data(self, x_column: Optional[str], y_column: Optional[str]) -> Dict[str, Any]:
        """Generate scatter plot data."""
        numeric_cols = self.get_numeric_columns()
        
        if len(numeric_cols) < 2:
            return {'error': 'Need at least 2 numeric columns for scatter plot'}
        
        x_col = x_column if x_column in numeric_cols else numeric_cols[0]
        y_col = y_column if y_column in numeric_cols else numeric_cols[1]
        
        # Create scatter data points
        scatter_data = []
        for _, row in self.df.iterrows():
            x_val = row.get(x_col)
            y_val = row.get(y_col)
            if pd.notna(x_val) and pd.notna(y_val):
                scatter_data.append({
                    'x': float(x_val),
                    'y': float(y_val),
                })
        
        # Limit to 500 points for performance
        if len(scatter_data) > 500:
            step = len(scatter_data) // 500
            scatter_data = scatter_data[::step]
        
        return {
            'type': 'scatter',
            'datasets': [{
                'label': f'{x_col} vs {y_col}',
                'data': scatter_data,
            }],
            'xAxisLabel': x_col,
            'yAxisLabel': y_col,
        }
    
    def _get_histogram_data(self, column: Optional[str], bins: int = 20) -> Dict[str, Any]:
        """Generate histogram data."""
        numeric_cols = self.get_numeric_columns()
        
        if not numeric_cols:
            return {'error': 'No numeric columns available for histogram'}
        
        col = column if column in numeric_cols else numeric_cols[0]
        
        # Compute histogram
        data = self.df[col].dropna()
        counts, bin_edges = np.histogram(data, bins=bins)
        
        # Create bin labels
        labels = [f'{bin_edges[i]:.2f}-{bin_edges[i+1]:.2f}' for i in range(len(counts))]
        
        return {
            'type': 'histogram',
            'labels': labels,
            'datasets': [{
                'label': col,
                'data': counts.tolist(),
            }],
            'xAxisLabel': col,
            'yAxisLabel': 'Frequency',
        }
    
    def _get_heatmap_data(self) -> Dict[str, Any]:
        """Generate correlation heatmap data."""
        numeric_cols = self.get_numeric_columns()
        
        if len(numeric_cols) < 2:
            return {'error': 'Need at least 2 numeric columns for heatmap'}
        
        # Limit to 10 columns for readability
        cols = numeric_cols[:10]
        
        # Compute correlation matrix
        corr_matrix = self.df[cols].corr()
        
        # Convert to heatmap format
        data = []
        for i, row_col in enumerate(cols):
            for j, col_col in enumerate(cols):
                val = corr_matrix.loc[row_col, col_col]
                data.append({
                    'x': j,
                    'y': i,
                    'v': round(float(val), 3) if not pd.isna(val) else 0,
                })
        
        return {
            'type': 'heatmap',
            'labels': cols,
            'data': data,
            'min': -1,
            'max': 1,
        }
    
    def _get_combined_chart_data(self) -> Dict[str, Any]:
        """Generate combined multi-chart data for dashboard."""
        numeric_cols = self.get_numeric_columns()
        categorical_cols = self.get_categorical_columns()
        
        result = {
            'line': self._get_line_chart_data(None, numeric_cols[0] if numeric_cols else None),
            'available_charts': ['line'],
        }
        
        if categorical_cols:
            result['bar'] = self._get_bar_chart_data(categorical_cols[0], 
                                                      numeric_cols[0] if numeric_cols else None)
            result['pie'] = self._get_pie_chart_data(categorical_cols[0])
            result['available_charts'].extend(['bar', 'pie'])
        
        if len(numeric_cols) >= 2:
            result['scatter'] = self._get_scatter_chart_data(numeric_cols[0], numeric_cols[1])
            result['heatmap'] = self._get_heatmap_data()
            result['available_charts'].extend(['scatter', 'heatmap'])
        
        if numeric_cols:
            result['histogram'] = self._get_histogram_data(numeric_cols[0])
            result['available_charts'].append('histogram')
        
        return result
    
    def get_all_charts(self) -> Dict[str, Any]:
        """Get data for all available chart types."""
        return self._get_combined_chart_data()
