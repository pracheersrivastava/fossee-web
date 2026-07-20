# CHEM•VIZ — Chemical Equipment Parameter Visualizer

**Hybrid Web + Desktop Application** | FOSSEE Intern Screening Task

A hybrid application that allows users to upload a CSV file containing chemical equipment parameters (Equipment Name, Type, Flowrate, Pressure, Temperature), parses and analyzes the data via a Django REST backend, and displays data tables, charts, and summaries on both a **React Web frontend** and a **PyQt5 Desktop frontend**.

![FOSSEE](https://img.shields.io/badge/FOSSEE-IIT%20Bombay-blue)
![Django](https://img.shields.io/badge/Django-4.2+-092E20)
![React](https://img.shields.io/badge/React-18.x-61dafb)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-41cd52)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Production-4169E1)

---

## Live Demo & Downloads

| Platform | Link |
|----------|------|
| **Web App** | [https://fossee-web.vercel.app](https://fossee-web.vercel.app) |
| **Backend API** | [https://fossee-api.onrender.com/api/](https://fossee-api.onrender.com/api/) |
| **Desktop App** | [Download ChemViz.exe (Windows)](https://github.com/pracheersrivastava/fossee-web/releases/latest) |

> **Quick Start:** Visit the web app, register an account, upload `sample_equipment_data.csv`, and explore the charts, summaries, and PDF export.

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend (Web) | React.js + Chart.js | Data table + chart visualization |
| Frontend (Desktop) | PyQt5 + Matplotlib | Same visualization in desktop |
| Backend | Python Django + Django REST Framework | Common backend API |
| Data Handling | Pandas | Reading CSV & analytics |
| Database | PostgreSQL (Render) / SQLite (local) | Store datasets, users, and upload history |
| PDF Generation | jsPDF (Web) + ReportLab (Desktop) | Export analysis reports |
| Authentication | Token-based (DRF Tokens) | Login, Register, Logout |
| Version Control | Git & GitHub | Collaboration & submission |
| Sample Data | `sample_equipment_data.csv` | Provided for testing & demo |

---

## Features Implemented

| # | Feature | Web | Desktop | Details |
|---|---------|-----|---------|---------|
| 1 | **CSV Upload** | Yes | Yes | Drag-and-drop + file dialog upload to Django backend |
| 2 | **Data Summary API** | Yes | Yes | Total count, averages (flowrate, temperature, pressure), equipment type distribution |
| 3 | **Visualization** | Yes (Chart.js) | Yes (Matplotlib) | Equipment Distribution (Bar), Temperature Profile (Line), Pressure Analysis (Bar) |
| 4 | **History Management** | Yes | Yes | Stores last 5 uploaded datasets with summary; sidebar + full history screen |
| 5 | **PDF Report** | Yes (jsPDF) | Yes (ReportLab) | A4 formatted report with KPIs, charts, data table, FOSSEE branding |
| 6 | **Authentication** | Yes | Yes | Token-based login/register/logout with dataset ownership |
| 7 | **Data Tables** | Yes | Yes | Sortable equipment table with status badges, zebra striping |
| 8 | **Sample CSV** | Yes | Yes | `sample_equipment_data.csv` included in repo root (25 records, 7 equipment types) |

---

## Architecture

```
┌──────────────────┐     HTTP/REST     ┌──────────────────┐
│   React Web App  │ ◄───────────────► │  Django Backend   │
│   (Vercel)       │                   │  (Render)         │
└──────────────────┘                   │  PostgreSQL +     │
                                       │  Pandas           │
                                       └──────────────────┘
┌──────────────────┐     HTTP/REST            ▲
│  PyQt5 Desktop   │ ◄───────────────────────►│
│   (.exe release) │
└──────────────────┘
```

Both frontends connect to the **same Django backend API**.

---

## Setup Instructions

### Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.9+ |
| Node.js | 18+ |
| npm | 9+ |
| Git | 2.x |

### 1. Clone the Repository

```bash
git clone https://github.com/pracheersrivastava/fossee-web.git
cd fossee-web
```

### 2. Start the Backend (required first)

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Linux / Mac
source venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8000
```

API is now live at **http://localhost:8000/api/**

> **Optional:** Create a superuser for the Django admin panel:
> ```bash
> python manage.py createsuperuser
> ```
> Then visit http://localhost:8000/admin/

### 3a. Start the Web Frontend (React)

```bash
# From the project root (not backend/)
npm install
npm run dev
```

Open **http://localhost:5173**

### 3b. Run the Desktop Application (PyQt5)

```bash
cd desktop
pip install -r requirements.txt
python app.py
```

### 4. Test with Sample Data

Upload the included `sample_equipment_data.csv` from the repo root through either the Web or Desktop interface to see charts, KPIs, and data tables.

---

## Project Structure

```
fossee-web/
├── README.md                        # This file
├── sample_equipment_data.csv        # Sample CSV for testing & demo
├── package.json                     # React/Vite dependencies
├── vite.config.js                   # Vite configuration
├── index.html                       # Web entry point
│
├── backend/                         # Django REST API Backend
│   ├── manage.py
│   ├── requirements.txt
│   ├── chemviz_api/                 # Django project config
│   │   ├── settings.py              # DB, CORS, REST, auth settings
│   │   ├── urls.py                  # Root URL routing
│   │   └── wsgi.py                  # WSGI entry point
│   ├── datasets/                    # Dataset management app
│   │   ├── models.py               # Dataset model (CSV metadata + storage)
│   │   ├── serializers.py           # DRF serializers
│   │   ├── views.py                 # Upload, list, summary, analysis endpoints
│   │   ├── auth_views.py            # Login, register, logout endpoints
│   │   ├── authentication.py        # Lenient token auth (anonymous fallback)
│   │   └── urls.py
│   └── analytics/                   # Analytics & charting app
│       ├── services.py              # Pandas analytics engine
│       ├── views.py                 # Summary, KPIs, chart data endpoints
│       └── urls.py
│
├── src/                             # React Web Frontend
│   ├── App.jsx                      # Main app with routing
│   ├── index.jsx                    # Entry point
│   ├── styles/
│   │   ├── tokens.css               # Design tokens (colors, spacing)
│   │   └── global.css               # Global base styles
│   ├── services/
│   │   ├── api.js                   # API client (fetch wrapper)
│   │   ├── authService.js           # Auth token management
│   │   └── pdfGenerator.js          # jsPDF report generation
│   ├── config/
│   │   └── pdfReportConfig.js       # PDF layout specification
│   └── components/
│       ├── Auth/                    # Login/Register modal
│       ├── Layout/                  # Header, Sidebar, MainContent
│       ├── CSVUpload/               # File upload with drag-and-drop
│       ├── KPICards/                # Summary metric cards
│       ├── SummaryScreen/           # Data summary view
│       ├── Charts/                  # Chart.js bar/line charts
│       ├── DataTable/               # Equipment data table
│       └── DatasetHistory/          # Sidebar history list
│
├── desktop/                         # PyQt5 Desktop Frontend
│   ├── app.py                       # Entry point
│   ├── main_window.py               # Main window + screen navigation
│   ├── requirements.txt
│   ├── core/
│   │   ├── tokens.py                # Design tokens
│   │   └── api_client.py            # HTTP client for Django API
│   ├── styles/
│   │   └── theme.qss                # QSS stylesheet
│   ├── widgets/
│   │   ├── header.py                # App header bar
│   │   ├── sidebar.py               # Navigation sidebar
│   │   ├── main_content.py          # Scrollable content area
│   │   ├── csv_upload.py            # Drag-and-drop CSV upload
│   │   ├── kpi_cards.py             # KPI metric cards
│   │   ├── summary_screen.py        # Data summary view
│   │   ├── data_table.py            # QTableView equipment table
│   │   ├── dataset_history.py       # Sidebar history widget
│   │   ├── history_screen.py        # Full-page history view
│   │   └── auth_dialog.py           # Login/Register dialog
│   ├── charts/
│   │   ├── chart_config.py          # Matplotlib chart config
│   │   └── charts.py                # Matplotlib chart widgets
│   └── config/
│       ├── pdf_report_config.py     # PDF layout specification
│       └── pdf_generator.py         # ReportLab PDF generation
```

---

## API Endpoints

Base URL: **https://fossee-api.onrender.com/api/** (hosted) or **http://localhost:8000/api/** (local)

### Datasets

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/datasets/upload/` | Upload a CSV file |
| GET | `/api/datasets/` | List datasets (last 5) |
| GET | `/api/datasets/{id}/` | Get dataset details |
| GET | `/api/datasets/active/` | Get currently active dataset |
| POST | `/api/datasets/{id}/activate/` | Set a dataset as active |
| DELETE | `/api/datasets/{id}/` | Delete a dataset |

### Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/summary/{id}/` | Summary stats (total count, averages, type distribution) |
| GET | `/api/analysis/{id}/` | Chart data (equipment distribution, temperature, pressure) |
| GET | `/api/analytics/summary/` | Summary for active dataset |
| GET | `/api/analytics/kpis/` | KPI metrics for dashboard |
| GET | `/api/analytics/charts/` | All chart data |
| GET | `/api/history/` | Dataset upload history (last 5) |

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Create new account |
| POST | `/api/auth/login/` | Login → returns auth token |
| POST | `/api/auth/logout/` | Logout → invalidates token |
| GET | `/api/auth/user/` | Get current user info |

Full API documentation: [backend/README.md](backend/README.md)

---

## Sample Data

The repository includes `sample_equipment_data.csv` with 25 records across 7 equipment types:

| Column | Description | Example Values |
|--------|-------------|----------------|
| Equipment Name | Unique equipment identifier | Heat Exchanger A1, Reactor C2 |
| Type | Equipment category | Heat Exchanger, Reactor, Pump, Compressor, Distillation Column, Boiler, Condenser, Storage Tank |
| Flowrate | Flow rate value | 0.0 – 420.0 |
| Pressure | Operating pressure | 1.0 – 10.5 |
| Temperature | Operating temperature | 25.0 – 260.0 |

---

## Dependencies

### Backend

| Package | Version | Purpose |
|---------|---------|---------|
| Django | ≥ 4.2 | Web framework |
| djangorestframework | ≥ 3.14 | REST API |
| django-cors-headers | ≥ 4.3 | CORS support |
| pandas | ≥ 2.0 | CSV parsing & analytics |
| numpy | ≥ 1.24 | Numerical computing |
| openpyxl | ≥ 3.1 | Excel file support |
| python-dotenv | ≥ 1.0 | Environment variables |
| gunicorn | ≥ 21.2 | Production WSGI server |
| whitenoise | ≥ 6.6 | Static file serving |
| dj-database-url | ≥ 2.1 | Database URL parsing |
| psycopg2-binary | ≥ 2.9 | PostgreSQL driver (Render) |

### Web Frontend

| Package | Version | Purpose |
|---------|---------|---------|
| react | ^18.2 | UI library |
| react-dom | ^18.2 | DOM rendering |
| chart.js | ^4.4 | Chart visualization |
| react-chartjs-2 | ^5.2 | Chart.js React bindings |
| jspdf | ^2.5 | PDF report generation |
| vite | ^5.0 | Build tool & dev server |

### Desktop

| Package | Version | Purpose |
|---------|---------|---------|
| PyQt5 | ≥ 5.15 | GUI framework |
| matplotlib | ≥ 3.7 | Chart visualization |
| numpy | ≥ 1.24 | Numerical computing |
| requests | ≥ 2.28 | HTTP client for Django API |
| reportlab | ≥ 4.0 | PDF report generation |
| scipy | ≥ 1.10 | Smooth curve interpolation |

---

## Scripts Reference

### Web

| Command | Description |
|---------|-------------|
| `npm install` | Install dependencies |
| `npm run dev` | Start dev server (port 5173) |
| `npm run build` | Production build → `dist/` |
| `npm run preview` | Preview production build |

### Backend

| Command | Description |
|---------|-------------|
| `python manage.py runserver 8000` | Start dev server |
| `python manage.py migrate` | Apply database migrations |
| `python manage.py createsuperuser` | Create admin user |
| `python manage.py collectstatic` | Collect static files for production |

### Desktop

| Command | Description |
|---------|-------------|
| `pip install -r requirements.txt` | Install dependencies |
| `python app.py` | Run the desktop application |

---

## License

**FOSSEE Project, IIT Bombay**

Built as part of the [FOSSEE](https://fossee.in/) initiative at the Indian Institute of Technology Bombay.

---

## Deployment

### Web Frontend — Vercel
- Auto-deploys from `main` on push.
- Live at [https://fossee-web.vercel.app](https://fossee-web.vercel.app).
- Set `VITE_API_BASE_URL=https://fossee-api.onrender.com/api` in Vercel project env.

### Backend — Render (PostgreSQL)
- Django API at [https://fossee-api.onrender.com](https://fossee-api.onrender.com).
- **PostgreSQL** database (`fossee-db`) for persistent users, datasets, and upload history.
- Gunicorn + WhiteNoise; CORS allows the Vercel frontend and desktop app.
- One-click deploy from `render.yaml`:

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/pracheersrivastava/fossee-web)

Or connect the repo in [Render Dashboard](https://dashboard.render.com/) → **New** → **Blueprint** → select `pracheersrivastava/fossee-web`.

**Render services created:**
| Service | Type | Purpose |
|---------|------|---------|
| `fossee-api` | Web (Python) | Django REST API |
| `fossee-db` | PostgreSQL | Production database |

**Note:** Free-tier Render services spin down after ~15 min idle; first request after sleep may take 30–60s.

### Backend — Vercel (fallback)
- Serverless deploy at [https://fossee-api.vercel.app](https://fossee-api.vercel.app) (ephemeral SQLite in `/tmp`).
- Use Render for production; Vercel config remains in `backend/vercel.json` for quick demos.

### Desktop — GitHub Releases
- Built with **PyInstaller** (`--onefile --windowed`).
- Download the latest `.exe` from [Releases](https://github.com/pracheersrivastava/fossee-web/releases/latest).
- Points at `https://fossee-api.onrender.com/api` by default.
- Override with env var `CHEMVIZ_API_BASE_URL` if needed.
