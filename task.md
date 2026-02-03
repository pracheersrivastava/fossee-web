# CHEM•VIZ Development Tasks

**FOSSEE Scientific Analytics UI - Chemical Equipment Parameter Visualizer**

This document tracks implementation progress for both Web (React) and Desktop (PyQt5) platforms.

---

## Project Overview

Building a hybrid Web + Desktop application following `design.md` specifications:
- **Web**: React 18 + Vite + Chart.js
- **Desktop**: PyQt5 with QSS styling
- **Repository**: github.com/pracheersrivastava/fossee-web

---

## ✅ COMPLETED TASKS

### Foundation (Both Platforms)

| Task | Web (React) | Desktop (PyQt5) | Notes |
|------|-------------|-----------------|-------|
| Design tokens | ✅ `tokens.css` | ✅ `tokens.py` | Colors, spacing, typography |
| Global styles | ✅ `global.css` | ✅ `theme.qss` | Reset, base typography |

### Layout Shell

| Task | Web (React) | Desktop (PyQt5) | Notes |
|------|-------------|-----------------|-------|
| Header (56px) | ✅ `Header.jsx` | ✅ `header.py` | Logo, title, FOSSEE badge |
| Sidebar (240px) | ✅ `Sidebar.jsx` | ✅ `sidebar.py` | Navigation, 4 items |
| Main Content | ✅ `MainContent.jsx` | ✅ `main_content.py` | Scrollable area |
| Main Window | ✅ `App.jsx` | ✅ `main_window.py` | Layout integration |

### Screen 1: Upload

| Task | Web (React) | Desktop (PyQt5) | Notes |
|------|-------------|-----------------|-------|
| Drop zone | ✅ | ✅ | Drag/drop, file dialog |
| Upload states | ✅ | ✅ | idle, drag, loading, error, success |
| File validation | ✅ | ✅ | CSV only, size check |
| Summary card | ✅ | ✅ | Post-upload transformation |
| Status badges | ✅ | ✅ | Validated/Issues Found |

### Screen 2: Summary

| Task | Web (React) | Desktop (PyQt5) | Notes |
|------|-------------|-----------------|-------|
| KPI Cards | ✅ | ✅ | Total Equipment, Avg Flowrate, Avg Temp, Dominant Type |
| KPI Grid | ✅ | ✅ | 4-column responsive |
| File Info Card | ✅ | ✅ | Filename, rows, size, columns |
| Action Buttons | ✅ | ✅ | View Charts, Export, Upload New |
| Summary Screen | ✅ `SummaryScreen.jsx` | ✅ `summary_screen.py` | Full integration |

### Screen 3: Charts (React Only - Current Sprint)

| Task | Web (React) | Desktop (PyQt5) | Notes |
|------|-------------|-----------------|-------|
| Chart.js config | ✅ `chartConfig.js` | ❌ | Base options, colors |
| Equipment Distribution (Bar) | ✅ | ❌ | Violet, no borders |
| Temperature vs Equipment (Line) | ✅ | ❌ | Amber with fill |
| Pressure Distribution (Bar) | ✅ | ❌ | Crimson, no borders |
| Charts Grid | ✅ `Charts.jsx` | ❌ | Responsive layout |

---

## 🔄 IN PROGRESS

None currently.

---

## ❌ REMAINING TASKS

### Screen 3: Charts (Desktop)

| Task | Priority | Notes |
|------|----------|-------|
| Matplotlib config | High | Match Chart.js tokens |
| Equipment Distribution (Bar) | High | Use `COLOR_EQUIPMENT` |
| Temperature vs Equipment (Line) | High | Use `COLOR_TEMPERATURE` |
| Pressure Distribution (Bar) | High | Use `COLOR_PRESSURE` |
| Charts layout widget | High | Integrate with MainContent |

### Screen 4: History

| Task | Web (React) | Desktop (PyQt5) | Notes |
|------|-------------|-----------------|-------|
| History table | ❌ | ❌ | Per design.md Section 5.4 |
| Zebra striping | ❌ | ❌ | `#FAFAFA` alt rows |
| Sticky header | ❌ | ❌ | `#F1F5F9` background |
| Row actions | ❌ | ❌ | View, Export, Delete |
| Pagination | ❌ | ❌ | Optional |

### Data Flow & State

| Task | Platform | Notes |
|------|----------|-------|
| CSV parsing | Both | Parse to structured data |
| Data context/store | React | Share data between screens |
| Signal/slot wiring | PyQt5 | Connect upload → summary → charts |
| Actual KPI calculation | Both | From real CSV data |

### Export Features

| Task | Platform | Notes |
|------|----------|-------|
| Export to CSV | Both | Filtered data |
| Export to PDF | Both | Report layout per design.md |
| Chart image export | Both | PNG/SVG |

### Polish & Accessibility

| Task | Platform | Notes |
|------|----------|-------|
| Keyboard navigation | Both | Tab, Enter, Escape |
| Focus indicators | Both | Per design.md Section 8 |
| Error boundaries | React | Graceful error handling |
| Loading states | Both | Spinners, progress bars |
| Empty states | Both | No data placeholders |

---

## File Structure

```
CHEM•VIZ Design System/
├── design.md                    # Design specifications
├── task.md                      # This file
├── package.json                 # React dependencies
├── vite.config.js              # Vite configuration
├── index.html                  # Entry HTML
│
├── src/                        # React Web App
│   ├── index.jsx
│   ├── App.jsx
│   ├── App.css
│   ├── styles/
│   │   ├── tokens.css          # Design tokens
│   │   └── global.css          # Global styles
│   └── components/
│       ├── Layout/
│       │   ├── Header.jsx/.css
│       │   ├── Sidebar.jsx/.css
│       │   ├── MainContent.jsx/.css
│       │   └── index.js
│       ├── CSVUpload/
│       │   ├── CSVUpload.jsx/.css
│       │   └── index.js
│       ├── KPICards/
│       │   ├── KPICards.jsx/.css
│       │   └── index.js
│       ├── SummaryScreen/
│       │   ├── SummaryScreen.jsx/.css
│       │   └── index.js
│       └── Charts/
│           ├── chartConfig.js   # Chart.js configurations
│           ├── Charts.jsx/.css  # Chart components
│           └── index.js
│
├── desktop/                    # PyQt5 Desktop App
│   ├── __init__.py
│   ├── app.py                  # Entry point
│   ├── main_window.py          # Main window
│   ├── requirements.txt
│   ├── core/
│   │   ├── __init__.py
│   │   └── tokens.py           # Design tokens
│   ├── styles/
│   │   └── theme.qss           # QSS stylesheet
│   └── widgets/
│       ├── __init__.py
│       ├── header.py
│       ├── sidebar.py
│       ├── main_content.py
│       ├── csv_upload.py
│       ├── kpi_cards.py
│       └── summary_screen.py
```

---

## Design Reference

All implementations MUST follow `design.md`:

### Colors (data visualization)
- Flowrate: `#14B8A6` (Teal)
- Temperature: `#F59E0B` (Amber)
- Pressure: `#EF4444` (Crimson)
- Equipment: `#8B5CF6` (Muted Violet)

### Chart Rules
- No borders
- Gridlines: `#E5E7EB`
- Tooltip: Dark Indigo @ 90% opacity
- Max 4 colors per chart
- No gradients

### Spacing
- Base unit: 8px
- xs: 4px, sm: 8px, md: 16px, lg: 24px, xl: 32px, xxl: 48px

---

## Git History

| Commit | Description |
|--------|-------------|
| Initial | React + PyQt5 shell, Layout components |
| feat: CSV upload PyQt5 | Desktop upload matching React |
| feat: KPI cards React | Summary KPIs + SummaryScreen |
| feat: add PyQt5 summary KPI cards and summary screen | Desktop KPIs |
| feat: add Chart.js charts | React charts (current) |

---

## Next Steps for AI Dev

1. **Integrate Charts into App.jsx** - Wire AnalysisCharts to analysis screen
2. **PyQt5 Charts** - Matplotlib implementation matching React
3. **History Screen** - Table component with data persistence
4. **Data Flow** - Connect CSV parsing to real chart data
5. **Export Features** - PDF report generation

---

*Last updated: February 3, 2026*
