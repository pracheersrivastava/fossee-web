# CHEM•VIZ — Chemical Equipment Parameter Visualizer

**Hybrid Web + Desktop Application** | FOSSEE Intern Screening Task

A hybrid application that allows users to upload a CSV file containing chemical equipment parameters (Equipment Name, Type, Flowrate, Pressure, Temperature), parses and analyzes the data via a Django REST backend, and displays data tables, charts, and summaries on both a **React Web frontend** and a **PyQt5 Desktop frontend**.

![FOSSEE](https://img.shields.io/badge/FOSSEE-IIT%20Bombay-blue)
![Django](https://img.shields.io/badge/Django-4.2+-092E20)
![React](https://img.shields.io/badge/React-18.x-61dafb)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-41cd52)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57)

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend (Web) | React.js + Chart.js | Data table + chart visualization |
| Frontend (Desktop) | PyQt5 + Matplotlib | Same visualization in desktop |
| Backend | Python Django + Django REST Framework | Common backend API |
| Data Handling | Pandas | Reading CSV & analytics |
| Database | SQLite | Store last 5 uploaded datasets |
| PDF Generation | jsPDF (Web) + ReportLab (Desktop) | Export analysis reports |
| Authentication | Token-based (DRF Tokens) | Login, Register, Logout |
| Version Control | Git & GitHub | Collaboration & submission |
| Sample Data | `sample_equipment_data.csv` | Provided for testing & demo |

---

## Features Implemented

| # | Feature | Web | Desktop | Details |
|---|---------|-----|---------|---------|
| 1 | **CSV Upload** | ✅ | ✅ | Drag-and-drop + file dialog upload to Django backend |
| 2 | **Data Summary API** | ✅ | ✅ | Total count, averages (flowrate, temperature, pressure), equipment type distribution |
| 3 | **Visualization** | ✅ Chart.js | ✅ Matplotlib | Equipment Distribution (Bar), Temperature Profile (Line), Pressure Analysis (Bar) |
| 4 | **History Management** | ✅ | ✅ | Stores last 5 uploaded datasets with summary; sidebar + full history screen |
| 5 | **PDF Report** | ✅ jsPDF | ✅ ReportLab | A4 formatted report with KPIs, charts, data table, FOSSEE branding |
| 6 | **Authentication** | ✅ | ✅ | Token-based login/register/logout with dataset ownership |
| 7 | **Data Tables** | ✅ | ✅ | Sortable equipment table with status badges, zebra striping |
| 8 | **Sample CSV** | ✅ | ✅ | `sample_equipment_data.csv` included in repo root (25 records, 7 equipment types) |

---

## Architecture

```
┌──────────────────┐     HTTP/REST     ┌──────────────────┐
│   React Web App  │ ◄───────────────► │  Django Backend   │
│   (Vite, :5173)  │                   │  (DRF, :8000)     │
└──────────────────┘                   │  SQLite + Pandas  │
                                       └──────────────────┘
┌──────────────────┐     HTTP/REST            ▲
│  PyQt5 Desktop   │ ◄───────────────────────►│
│   (Standalone)   │
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
├── design.md                        # UI design system specification
├── task.md                          # Development task tracker
├── package.json                     # React/Vite dependencies
├── vite.config.js                   # Vite configuration
├── index.html                       # Web entry point
├── .env                             # Environment variables
│
├── backend/                         # Django REST API Backend
│   ├── manage.py
│   ├── requirements.txt
│   ├── db.sqlite3                   # SQLite database (auto-created)
│   ├── chemviz_api/                 # Django project config
│   │   ├── settings.py              # DB, CORS, REST, auth settings
│   │   ├── urls.py                  # Root URL routing
│   │   ├── wsgi.py                  # WSGI entry point
│   │   └── asgi.py
│   ├── datasets/                    # Dataset management app
│   │   ├── models.py               # Dataset model (CSV metadata + storage)
│   │   ├── serializers.py           # DRF serializers
│   │   ├── views.py                 # Upload, list, summary, analysis endpoints
│   │   ├── auth_views.py            # Login, register, logout endpoints
│   │   ├── authentication.py        # Lenient token auth (anonymous fallback)
│   │   └── urls.py
│   ├── analytics/                   # Analytics & charting app
│   │   ├── services.py              # Pandas analytics engine
│   │   ├── views.py                 # Summary, KPIs, chart data endpoints
│   │   └── urls.py
│   └── media/datasets/              # Uploaded CSV file storage
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

Base URL: **http://localhost:8000/api/**

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

## Deployment (Optional)

### Quick Deploy — PythonAnywhere (Free)

1. Sign up at [pythonanywhere.com](https://www.pythonanywhere.com)
2. Open a Bash console and clone:
   ```bash
   git clone https://github.com/pracheersrivastava/fossee-web.git
   ```
3. Create a virtualenv (Python 3.9+) and install dependencies:
   ```bash
   cd fossee-web/backend
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```
4. In the **Web** tab → Add new web app → Manual config → Python 3.9
5. Edit the WSGI file:
   ```python
   import sys, os
   path = '/home/yourusername/fossee-web/backend'
   if path not in sys.path:
       sys.path.append(path)
   os.environ['DJANGO_SETTINGS_MODULE'] = 'chemviz_api.settings'
   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```
6. Add static file mappings in the Web tab:
   - `/static/` → `/home/yourusername/fossee-web/backend/staticfiles/`
   - `/media/` → `/home/yourusername/fossee-web/backend/media/`
7. For the React frontend: build locally with `npm run build`, then upload `dist/` contents as static files
8. Reload the web app

### Production Deploy — VPS (Nginx + Gunicorn)

For a full-scale deployment on a FOSSEE server or VM:

#### 1. Install dependencies on server

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip nginx postgresql postgresql-contrib nodejs npm
```

#### 2. Clone and set up backend

```bash
git clone https://github.com/pracheersrivastava/fossee-web.git /opt/chemviz
cd /opt/chemviz/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt gunicorn psycopg2-binary
python manage.py migrate
python manage.py collectstatic --noinput
```

#### 3. Create Gunicorn systemd service

`/etc/systemd/system/chemviz.service`:

```ini
[Unit]
Description=CHEM•VIZ Django Backend
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/chemviz/backend
Environment="PATH=/opt/chemviz/backend/venv/bin"
ExecStart=/opt/chemviz/backend/venv/bin/gunicorn chemviz_api.wsgi:application --bind 127.0.0.1:8000 --workers 3

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now chemviz
```

#### 4. Build React frontend

```bash
cd /opt/chemviz
npm install
npm run build
```

#### 5. Configure Nginx

`/etc/nginx/sites-available/chemviz`:

```nginx
server {
    listen 80;
    server_name your-domain.fossee.in;

    location / {
        root /opt/chemviz/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        client_max_body_size 10M;
    }

    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }

    location /static/ {
        alias /opt/chemviz/backend/staticfiles/;
    }

    location /media/ {
        alias /opt/chemviz/backend/media/;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/chemviz /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx
```

#### 6. HTTPS (recommended)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.fossee.in
```

### Production Settings Checklist

| Setting | Value |
|---------|-------|
| `DEBUG` | `False` |
| `SECRET_KEY` | Generate a new one |
| `ALLOWED_HOSTS` | `['your-domain.fossee.in']` |
| `CORS_ALLOWED_ORIGINS` | `['https://your-domain.fossee.in']` |
| Database | PostgreSQL (optional, SQLite works for small scale) |
| Static files | `python manage.py collectstatic` |

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
