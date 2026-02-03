# CHEM•VIZ Django Backend

Chemical Equipment Parameter Visualizer - Django REST API Backend

## Project Structure

```
backend/
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
├── db.sqlite3                   # SQLite database (auto-created)
│
├── chemviz_api/                 # Main Django project
│   ├── __init__.py
│   ├── settings.py              # Project settings (CORS, REST, DB)
│   ├── urls.py                  # Root URL configuration
│   ├── wsgi.py                  # WSGI application
│   └── asgi.py                  # ASGI application
│
├── datasets/                    # Dataset management app
│   ├── __init__.py
│   ├── admin.py                 # Admin configuration
│   ├── apps.py                  # App configuration
│   ├── models.py                # Dataset model (CSV storage)
│   ├── serializers.py           # DRF serializers
│   ├── signals.py               # Post-save signals
│   ├── urls.py                  # Dataset API routes
│   └── views.py                 # Dataset ViewSet
│
├── analytics/                   # Analytics & charts app
│   ├── __init__.py
│   ├── apps.py                  # App configuration
│   ├── services.py              # Pandas analytics service
│   ├── urls.py                  # Analytics API routes
│   └── views.py                 # Analytics endpoints
│
└── media/                       # Uploaded files (auto-created)
    └── datasets/                # CSV files storage
```

## Setup Instructions

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Migrations

```bash
python manage.py migrate
```

### 4. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 5. Run Development Server

```bash
python manage.py runserver 8000
```

The API will be available at: http://localhost:8000/api/

## API Endpoints

### Root

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/` | API welcome & endpoints list |

### Datasets

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/datasets/` | List all datasets (last 5) |
| POST | `/api/datasets/upload/` | Upload new CSV file |
| GET | `/api/datasets/{id}/` | Get dataset details |
| GET | `/api/datasets/{id}/data/` | Get full dataset data |
| POST | `/api/datasets/{id}/activate/` | Set as active dataset |
| DELETE | `/api/datasets/{id}/` | Delete a dataset |
| GET | `/api/datasets/active/` | Get currently active dataset |

### Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analytics/` | Analytics API info |
| GET | `/api/analytics/summary/` | Summary stats for active dataset |
| GET | `/api/analytics/summary/{id}/` | Summary stats for specific dataset |
| GET | `/api/analytics/kpis/` | KPI metrics for dashboard |
| GET | `/api/analytics/charts/` | All charts data |
| GET | `/api/analytics/charts/{id}/` | Charts for specific dataset |
| GET | `/api/analytics/charts/{id}/{type}/` | Specific chart type |
| GET | `/api/analytics/columns/` | Column information |

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/auth/login/` | DRF login page |
| POST | `/api/auth/logout/` | Logout |

### Admin

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/` | Django admin interface |

## Chart Types

Available chart types for `/api/analytics/charts/{id}/{type}/`:

- `line` - Line chart for time series
- `bar` - Bar chart for categorical data
- `pie` - Pie chart for distributions
- `scatter` - Scatter plot for correlations
- `histogram` - Histogram for value distribution
- `heatmap` - Correlation heatmap

Query parameters for chart endpoints:
- `x_column` - Column for X axis
- `y_column` - Column for Y axis
- `bins` - Number of bins (histogram only)

## Configuration

### CORS Settings (settings.py)

CORS is enabled for:
- http://localhost:3000 (React)
- http://localhost:5173 (Vite)

### Database

SQLite database at `backend/db.sqlite3`

### File Upload

- Max file size: 10MB
- Allowed extensions: .csv
- Storage: `backend/media/datasets/`

### Dataset History

Maximum 5 datasets kept in history (configurable in settings.py)

## App Descriptions

### `chemviz_api` (Main Project)

The core Django project configuration containing:
- Global settings (database, CORS, REST framework)
- Root URL routing
- WSGI/ASGI configuration

### `datasets` App

Handles CSV file management:
- File upload with validation
- CSV parsing using Pandas
- Dataset metadata extraction
- History management (keeps last 5)
- Active dataset tracking

### `analytics` App

Provides data analysis capabilities:
- Summary statistics computation
- KPI metrics generation
- Chart data formatting for:
  - Line, Bar, Pie charts
  - Scatter plots
  - Histograms
  - Correlation heatmaps

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| Django | 4.2+ | Web framework |
| djangorestframework | 3.14+ | REST API |
| django-cors-headers | 4.3+ | CORS support |
| pandas | 2.0+ | Data analysis |
| numpy | 1.24+ | Numerical computing |
| openpyxl | 3.1+ | Excel support |
| python-dotenv | 1.0+ | Environment variables |

## Usage Example

### Upload a CSV file:

```bash
curl -X POST http://localhost:8000/api/datasets/upload/ \
  -F "file=@equipment_data.csv" \
  -F "name=Equipment Parameters"
```

### Get summary statistics:

```bash
curl http://localhost:8000/api/analytics/summary/
```

### Get chart data:

```bash
curl http://localhost:8000/api/analytics/charts/
```

### Get specific chart:

```bash
curl "http://localhost:8000/api/analytics/charts/{dataset_id}/scatter/?x_column=Temperature&y_column=Pressure"
```
