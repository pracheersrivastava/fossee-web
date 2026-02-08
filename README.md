# CHEM•VIZ

**Chemical Equipment Parameter Visualizer**

A full-stack scientific data analytics application for uploading, analyzing, and visualizing chemical equipment parameters. Built as a hybrid **Web (React) + Desktop (PyQt5)** system backed by a **Django REST API**, following the FOSSEE Scientific Analytics UI design system.

![FOSSEE](https://img.shields.io/badge/FOSSEE-IIT%20Bombay-blue)
![Django](https://img.shields.io/badge/Django-4.2+-092E20)
![React](https://img.shields.io/badge/React-18.x-61dafb)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-41cd52)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB)

---

## Features

- **CSV Upload** — Drag-and-drop file upload with validation (type, size, structure)
- **Data Summary** — KPI cards: Total Equipment, Avg Flowrate, Avg Temperature, Dominant Type
- **Interactive Charts** — Equipment distribution (Bar), Temperature profile (Line), Pressure analysis (Bar) with smooth Bézier curves and rounded bar caps
- **Data Tables** — Sortable equipment data with status badges (Active / Inactive / Maintenance)
- **Dataset History** — Full history screen + sidebar list with sparkline previews and re-analyze actions
- **PDF Reports** — Formatted A4 reports with charts, KPIs, and data tables (ReportLab on Desktop, jsPDF on Web)
- **Authentication** — Token-based login/register/logout with dataset ownership
- **Cross-Platform** — Consistent visual experience across Web and Desktop, powered by a shared backend API

---

## Architecture

```
┌──────────────────┐     HTTP/REST     ┌──────────────────┐
│   React Web App  │ ◄───────────────► │   Django Backend  │
│   (Vite, :5173)  │                   │   (DRF, :8000)    │
└──────────────────┘                   └──────────────────┘
                                              ▲
┌──────────────────┐     HTTP/REST            │
│  PyQt5 Desktop   │ ◄───────────────────────►│
│   (Standalone)   │
└──────────────────┘
```

---

## Quick Start

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

### 2. Start the Backend (required for both Web & Desktop)

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8000
```

The API is now live at **http://localhost:8000/api/**

> **Optional:** Create a superuser for the Django admin panel:
> ```bash
> python manage.py createsuperuser
> ```

### 3a. Start the Web Frontend

```bash
# From the project root
npm install
npm run dev
```

Open **http://localhost:5173**

### 3b. Run the Desktop Application

```bash
cd desktop
pip install -r requirements.txt
python app.py
```

---

## Project Structure

```
CHEM•VIZ Design System/
├── README.md                        # This file
├── design.md                        # Design system specification (v1.0)
├── task.md                          # Development task tracker
├── package.json                     # React/Vite dependencies
├── vite.config.js                   # Vite configuration
├── index.html                       # Web entry HTML
├── .env                             # Environment variables
│
├── backend/                         # Django REST API
│   ├── manage.py
│   ├── requirements.txt
│   ├── db.sqlite3                   # SQLite database
│   ├── chemviz_api/                 # Django project settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── datasets/                    # Dataset CRUD + upload
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── analytics/                   # KPI / chart / summary computation
│   │   ├── services.py             # Pandas analytics engine
│   │   ├── views.py
│   │   └── urls.py
│   └── media/datasets/             # Uploaded CSV storage
│
├── src/                             # React Web Application
│   ├── App.jsx
│   ├── index.jsx
│   ├── styles/
│   │   ├── tokens.css               # Design tokens
│   │   └── global.css               # Global styles
│   ├── services/
│   │   ├── api.js                   # Axios/fetch wrapper
│   │   ├── authService.js           # Login/register/logout
│   │   └── pdfGenerator.js          # jsPDF report generation
│   ├── config/
│   │   └── pdfReportConfig.js       # PDF layout specification
│   └── components/
│       ├── Auth/                    # Login/Register dialogs
│       ├── Layout/                  # Header, Sidebar, MainContent
│       ├── CSVUpload/               # File upload with validation
│       ├── KPICards/                # Summary metric cards
│       ├── SummaryScreen/           # Data summary view
│       ├── Charts/                  # Chart.js visualizations
│       ├── DataTable/               # Equipment data table
│       └── DatasetHistory/          # Sidebar history list
│
├── desktop/                         # PyQt5 Desktop Application
│   ├── app.py                       # Entry point
│   ├── main_window.py               # Main window + navigation
│   ├── requirements.txt
│   ├── core/
│   │   └── tokens.py                # Design tokens
│   ├── styles/
│   │   └── theme.qss                # QSS stylesheet
│   ├── widgets/
│   │   ├── header.py                # App header bar
│   │   ├── sidebar.py               # Navigation sidebar
│   │   ├── main_content.py          # Scrollable content area
│   │   ├── csv_upload.py            # Drag-and-drop upload
│   │   ├── kpi_cards.py             # KPI metric cards
│   │   ├── summary_screen.py        # Data summary view
│   │   ├── data_table.py            # QTableView equipment table
│   │   ├── dataset_history.py       # Sidebar history widget
│   │   ├── history_screen.py        # Full-page history view
│   │   └── auth_dialog.py           # Login/register dialog
│   ├── charts/
│   │   ├── chart_config.py          # Matplotlib config (smooth, rounded)
│   │   └── charts.py                # Matplotlib chart widgets
│   └── config/
│       ├── pdf_report_config.py     # PDF layout specification
│       └── pdf_generator.py         # ReportLab PDF generation
```

---

## API Endpoints

The backend serves all data at **http://localhost:8000/api/**. Full API documentation is in [backend/README.md](backend/README.md).

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/datasets/upload/` | Upload a CSV file |
| GET | `/api/datasets/` | List all datasets (last 5) |
| GET | `/api/datasets/active/` | Get the currently active dataset |
| GET | `/api/analytics/summary/` | Summary stats for active dataset |
| GET | `/api/analytics/kpis/` | KPI metrics for dashboard |
| GET | `/api/analytics/charts/` | All chart data (distribution, temperature, pressure) |
| GET | `/api/analytics/charts/{id}/{type}/` | Specific chart type |
| GET | `/api/history/` | Dataset upload history |

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register a new account |
| POST | `/api/auth/login/` | Login (returns auth token) |
| POST | `/api/auth/logout/` | Logout (invalidates token) |

---

## Design System

The UI follows **design.md v1.0 — FOSSEE Scientific Analytics UI**. Key tokens:

### Colors

| Purpose | Color | Hex |
|---------|-------|-----|
| Primary Text | Deep Indigo | `#1E2A38` |
| Primary Action | Academic Blue | `#2F80ED` |
| Surface Background | Off-White | `#F8FAFC` |
| Secondary Text | Slate Gray | `#6B7280` |
| Flowrate (chart) | Teal | `#14B8A6` |
| Temperature (chart) | Amber | `#F59E0B` |
| Pressure (chart) | Crimson | `#EF4444` |
| Equipment (chart) | Violet | `#8B5CF6` |

### Typography

| Platform | Font | Weights |
|----------|------|---------|
| Web | Inter | 400, 500, 600, 700 |
| Desktop | Source Sans 3 | 400, 600, 700 |

### Spacing

Base unit: **8px** — xs: 4px · sm: 8px · md: 16px · lg: 24px · xl: 32px · xxl: 48px

---

## PDF Report Layout

Generated reports (A4, 1″ margins) follow a structured hierarchy:

1. **Header** — Logo, report title, FOSSEE badge
2. **Metadata** — Generation timestamp, dataset info, record count
3. **Summary KPIs** — Total Equipment, Avg Flowrate, Avg Temperature, Dominant Type
4. **Charts** — Equipment Distribution, Temperature Profile, Pressure Analysis
5. **Data Table** — Equipment records with status badges, zebra striping
6. **Footer** — Page numbers, FOSSEE credit

---

## Dependencies

### Backend (Python)

| Package | Version | Purpose |
|---------|---------|---------|
| Django | ≥ 4.2 | Web framework |
| djangorestframework | ≥ 3.14 | REST API |
| django-cors-headers | ≥ 4.3 | CORS support |
| pandas | ≥ 2.0 | Data analytics |
| numpy | ≥ 1.24 | Numerical computing |
| openpyxl | ≥ 3.1 | Excel file support |
| python-dotenv | ≥ 1.0 | Environment variables |

### Web Frontend (JavaScript)

| Package | Version | Purpose |
|---------|---------|---------|
| react | ^18.2 | UI library |
| react-dom | ^18.2 | DOM rendering |
| chart.js | ^4.4 | Chart rendering |
| react-chartjs-2 | ^5.2 | Chart.js React wrapper |
| jspdf | ^2.5 | PDF generation |
| vite | ^5.0 | Build tool |

### Desktop (Python)

| Package | Version | Purpose |
|---------|---------|---------|
| PyQt5 | ≥ 5.15 | GUI framework |
| matplotlib | ≥ 3.7 | Chart rendering |
| numpy | ≥ 1.24 | Numerical computing |
| requests | ≥ 2.28 | HTTP client for API |
| reportlab | ≥ 4.0 | PDF generation |
| scipy | ≥ 1.10 | Smooth Bézier curve interpolation |

---

## Deployment & Hosting

> See the **Hosting Guide** section below for FOSSEE-specific deployment instructions.

### Production Build — Web Frontend

```bash
npm run build      # outputs to dist/
npm run preview    # preview locally
```

### Production — Django Backend

```bash
pip install gunicorn
gunicorn chemviz_api.wsgi:application --bind 0.0.0.0:8000
```

Key production settings in `chemviz_api/settings.py`:

```python
DEBUG = False
ALLOWED_HOSTS = ['your-domain.fossee.in', 'localhost']
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

Then collect static files:

```bash
python manage.py collectstatic
```

---

## FOSSEE Hosting Guide

### Recommended Stack

| Layer | Technology |
|-------|------------|
| Web Server | Nginx |
| App Server | Gunicorn |
| Backend | Django (WSGI) |
| Frontend | Static files (Vite build → Nginx) |
| Database | PostgreSQL (production) / SQLite (dev) |
| Process Manager | systemd |

### Step-by-Step Deployment

#### 1. Server Setup

```bash
# On your FOSSEE server / VM (Ubuntu/Debian)
sudo apt update
sudo apt install python3 python3-venv python3-pip nginx postgresql postgresql-contrib nodejs npm
```

#### 2. Clone & Configure

```bash
git clone https://github.com/pracheersrivastava/fossee-web.git /opt/chemviz
cd /opt/chemviz
```

Create a production `.env`:

```env
DJANGO_SECRET_KEY=<generate-a-strong-key>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-domain.fossee.in,localhost
DATABASE_URL=postgres://chemviz_user:password@localhost:5432/chemviz_db
CORS_ALLOWED_ORIGINS=https://your-domain.fossee.in
```

#### 3. Database (PostgreSQL)

```bash
sudo -u postgres psql
CREATE DATABASE chemviz_db;
CREATE USER chemviz_user WITH PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE chemviz_db TO chemviz_user;
\q
```

> Update `settings.py` to read from `DATABASE_URL` or switch the `DATABASES` config to PostgreSQL.

#### 4. Backend Setup

```bash
cd /opt/chemviz/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

#### 5. Gunicorn systemd Service

Create `/etc/systemd/system/chemviz.service`:

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
sudo systemctl enable chemviz
sudo systemctl start chemviz
```

#### 6. Build the Web Frontend

```bash
cd /opt/chemviz
npm install
npm run build    # produces dist/
```

#### 7. Nginx Configuration

Create `/etc/nginx/sites-available/chemviz`:

```nginx
server {
    listen 80;
    server_name your-domain.fossee.in;

    # Serve React frontend
    location / {
        root /opt/chemviz/dist;
        try_files $uri $uri/ /index.html;
    }

    # Proxy API requests to Django
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Django admin
    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
    }

    # Django static files
    location /static/ {
        alias /opt/chemviz/backend/staticfiles/;
    }

    # Uploaded media files
    location /media/ {
        alias /opt/chemviz/backend/media/;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/chemviz /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 8. HTTPS (Optional but Recommended)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.fossee.in
```

### Alternative: PythonAnywhere (Free Tier)

If FOSSEE provides a PythonAnywhere account:

1. Upload code via Git
2. Set up a virtualenv with backend dependencies
3. Configure the WSGI file to point to `chemviz_api.wsgi`
4. Set static file mappings: `/static/` → `/home/user/chemviz/backend/staticfiles/`
5. Build the React frontend locally, upload `dist/` as static files

### Alternative: Docker

```bash
# (future) docker-compose up -d
```

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/my-feature`
3. Commit changes: `git commit -m "feat: add my feature"`
4. Push: `git push origin feat/my-feature`
5. Open a Pull Request

---

## License

**FOSSEE Project, IIT Bombay**

Built as part of the [FOSSEE](https://fossee.in/) initiative at the Indian Institute of Technology Bombay.
