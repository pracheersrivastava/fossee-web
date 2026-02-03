# CHEM•VIZ

**Chemical Equipment Parameter Visualizer**

A scientific data analytics application for visualizing chemical equipment parameters. Built with React (Web) and PyQt5 (Desktop) following FOSSEE design guidelines.

![FOSSEE](https://img.shields.io/badge/FOSSEE-IIT%20Bombay-blue)
![React](https://img.shields.io/badge/React-18.x-61dafb)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-41cd52)

---

## Features

- **CSV Upload** - Drag-and-drop CSV file upload with validation
- **Data Summary** - KPI cards showing equipment metrics at a glance
- **Interactive Charts** - Equipment distribution, temperature profiles, pressure analysis
- **Data Tables** - Sortable equipment data with status indicators
- **Dataset History** - Quick access to recent uploads with sparkline previews
- **PDF Reports** - Export analysis as formatted PDF documents
- **Cross-Platform** - Consistent experience on Web and Desktop

---

## Quick Start

### Web (React)

```bash
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173)

### Desktop (PyQt5)

```bash
cd desktop
pip install -r requirements.txt
python app.py
```

---

## Project Structure

```
├── src/                        # React Web Application
│   ├── components/
│   │   ├── Layout/             # Header, Sidebar, MainContent
│   │   ├── CSVUpload/          # File upload with validation
│   │   ├── KPICards/           # Summary metric cards
│   │   ├── SummaryScreen/      # Data summary view
│   │   ├── Charts/             # Chart.js visualizations
│   │   ├── DataTable/          # Equipment data table
│   │   └── DatasetHistory/     # Sidebar history list
│   ├── config/
│   │   └── pdfReportConfig.js  # PDF export configuration
│   ├── styles/
│   │   ├── tokens.css          # Design tokens
│   │   └── global.css          # Global styles
│   ├── App.jsx
│   └── index.jsx
│
├── desktop/                    # PyQt5 Desktop Application
│   ├── widgets/
│   │   ├── header.py
│   │   ├── sidebar.py
│   │   ├── main_content.py
│   │   ├── csv_upload.py
│   │   ├── kpi_cards.py
│   │   ├── summary_screen.py
│   │   ├── data_table.py
│   │   └── dataset_history.py
│   ├── charts/
│   │   ├── chart_config.py     # Matplotlib configuration
│   │   └── charts.py           # Chart widgets
│   ├── config/
│   │   └── pdf_report_config.py
│   ├── core/
│   │   └── tokens.py           # Design tokens
│   ├── styles/
│   │   └── theme.qss           # QSS stylesheet
│   ├── main_window.py
│   └── app.py
```

---

## Design System

### Colors

| Purpose | Color | Hex |
|---------|-------|-----|
| Primary Text | Deep Indigo | `#1E2A38` |
| Primary Action | Academic Blue | `#2F80ED` |
| Flowrate | Teal | `#14B8A6` |
| Temperature | Amber | `#F59E0B` |
| Pressure | Crimson | `#EF4444` |
| Equipment | Violet | `#8B5CF6` |

### Typography

| Platform | Font |
|----------|------|
| Web | Inter |
| Desktop | Source Sans 3 |

### Spacing

Base unit: **8px**

- xs: 4px
- sm: 8px
- md: 16px
- lg: 24px
- xl: 32px

---

## PDF Report Layout

Generated reports follow a structured layout:

1. **Header** - Logo, report title, FOSSEE badge
2. **Metadata** - Generation timestamp, dataset info, record count
3. **Summary KPIs** - Total equipment, avg flowrate, avg temperature, dominant type
4. **Charts** - Equipment distribution, temperature profile, pressure analysis
5. **Data Table** - Equipment records with status badges
6. **Footer** - Page numbers, credits

See `src/config/pdfReportConfig.js` or `desktop/config/pdf_report_config.py` for full specifications.

---

## Scripts

### Web

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run preview` | Preview production build |

### Desktop

| Command | Description |
|---------|-------------|
| `python app.py` | Run application |
| `pip install -r requirements.txt` | Install dependencies |

---

## Requirements

### Web
- Node.js 18+
- npm 9+

### Desktop
- Python 3.9+
- PyQt5 >= 5.15.0
- Matplotlib >= 3.7.0
- NumPy >= 1.24.0

---

## License

FOSSEE Project, IIT Bombay
