# CHEM•VIZ Backend - Testing Guide

## 🔴 PROMPT 9 — TEST BACKEND LOCALLY

### Step 1: Start the Django Backend

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment (if using one)
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies (if not already installed)
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start the server on localhost:8000
python manage.py runserver 8000
```

The server will be available at: **http://localhost:8000**

---

### Step 2: Test All APIs

#### 2.1 API Root
```bash
curl http://localhost:8000/api/
```

**Expected Response:**
```json
{
  "message": "Welcome to CHEM•VIZ API - Chemical Equipment Parameter Visualizer",
  "version": "1.0.0",
  "endpoints": {...}
}
```

---

#### 2.2 Authentication APIs

**Register a new user:**
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'
```

**Expected Response:**
```json
{
  "token": "your_auth_token_here",
  "user_id": 1,
  "username": "testuser",
  "message": "User registered successfully"
}
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}'
```

**Expected Response:**
```json
{
  "token": "your_auth_token_here",
  "user_id": 1,
  "username": "testuser",
  "message": "Login successful"
}
```

**Get User Info (Protected):**
```bash
curl http://localhost:8000/api/auth/user/ \
  -H "Authorization: Token your_auth_token_here"
```

**Logout (Protected):**
```bash
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Token your_auth_token_here"
```

---

#### 2.3 CSV Upload API

**Create a test CSV file (test_equipment.csv):**
```csv
Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-001,Centrifugal,150.5,3.2,45.0
Reactor-A,CSTR,200.0,5.5,120.0
Heat-Ex-01,Shell-Tube,180.0,2.8,85.0
Compressor-C,Reciprocating,95.0,8.0,65.0
Tank-T1,Storage,0,1.0,25.0
```

**Upload the CSV:**
```bash
curl -X POST http://localhost:8000/api/upload/ \
  -F "file=@test_equipment.csv"
```

**Expected Response:**
```json
{
  "dataset_id": "uuid-here",
  "row_count": 5,
  "column_count": 5,
  "validation": {
    "is_valid": true,
    "required_columns": ["Equipment Name", "Type", "Flowrate", "Pressure", "Temperature"],
    "found_columns": ["Equipment Name", "Type", "Flowrate", "Pressure", "Temperature"],
    "missing_columns": [],
    "extra_columns": []
  },
  "message": "CSV file uploaded and validated successfully",
  "name": "test_equipment",
  "uploaded_at": "2026-02-03T..."
}
```

---

#### 2.4 Summary Statistics API

```bash
# Replace <dataset_id> with actual UUID from upload response
curl http://localhost:8000/api/summary/<dataset_id>/
```

**Expected Response:**
```json
{
  "dataset_id": "uuid-here",
  "dataset_name": "test_equipment",
  "total_equipment": 5,
  "average_flowrate": 125.1,
  "average_temperature": 68.0,
  "dominant_equipment_type": "Centrifugal"
}
```

---

#### 2.5 Analysis API (Charts)

```bash
curl http://localhost:8000/api/analysis/<dataset_id>/
```

**Expected Response:**
```json
{
  "dataset_id": "uuid-here",
  "dataset_name": "test_equipment",
  "equipment_type_distribution": {
    "labels": ["Centrifugal", "CSTR", "Shell-Tube", "Reciprocating", "Storage"],
    "data": [1, 1, 1, 1, 1],
    "backgroundColor": ["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6"]
  },
  "temperature_by_equipment": {
    "labels": ["Compressor-C", "Heat-Ex-01", "Pump-001", "Reactor-A", "Tank-T1"],
    "data": [65.0, 85.0, 45.0, 120.0, 25.0]
  },
  "pressure_distribution": {
    "labels": ["1.0-2.4", "2.4-3.8", ...],
    "data": [2, 1, ...],
    "buckets": [...]
  }
}
```

---

#### 2.6 Dataset History API

```bash
curl http://localhost:8000/api/history/
```

**Expected Response:**
```json
{
  "count": 1,
  "datasets": [
    {
      "id": "uuid-here",
      "filename": "test_equipment.csv",
      "upload_time": "2026-02-03T...",
      "row_count": 5
    }
  ]
}
```

---

### Step 3: Verify Complete Workflow

```bash
# 1. Upload a CSV
curl -X POST http://localhost:8000/api/upload/ -F "file=@test_equipment.csv"

# 2. Get history to find dataset_id
curl http://localhost:8000/api/history/

# 3. Get summary statistics
curl http://localhost:8000/api/summary/<dataset_id>/

# 4. Get analysis data for charts
curl http://localhost:8000/api/analysis/<dataset_id>/
```

---

### Postman Collection

Import these endpoints into Postman:

| Method | URL | Description |
|--------|-----|-------------|
| GET | `http://localhost:8000/api/` | API Root |
| POST | `http://localhost:8000/api/auth/register/` | Register user |
| POST | `http://localhost:8000/api/auth/login/` | Login |
| POST | `http://localhost:8000/api/auth/logout/` | Logout |
| GET | `http://localhost:8000/api/auth/user/` | Get user info |
| POST | `http://localhost:8000/api/upload/` | Upload CSV |
| GET | `http://localhost:8000/api/summary/{id}/` | Get summary |
| GET | `http://localhost:8000/api/analysis/{id}/` | Get analysis |
| GET | `http://localhost:8000/api/history/` | Get history |

---

### PowerShell Commands (Windows)

```powershell
# Upload CSV
curl.exe -X POST http://localhost:8000/api/upload/ -F "file=@test_equipment.csv"

# Get history
curl.exe http://localhost:8000/api/history/

# Get summary (replace UUID)
curl.exe http://localhost:8000/api/summary/your-uuid-here/

# Get analysis (replace UUID)
curl.exe http://localhost:8000/api/analysis/your-uuid-here/

# Register user
$body = '{"username":"testuser","password":"testpass123"}'
Invoke-RestMethod -Uri "http://localhost:8000/api/auth/register/" -Method POST -Body $body -ContentType "application/json"

# Login
Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login/" -Method POST -Body $body -ContentType "application/json"
```

---

### Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| `No such table` | Run `python manage.py migrate` |
| `Connection refused` | Ensure server is running on port 8000 |
| `CORS error` in browser | Backend CORS is configured for localhost:3000 |
| `Invalid credentials` | Check username/password or register first |
