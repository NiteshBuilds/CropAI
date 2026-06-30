# AI-Driven Automated Crop Type, Moisture Stress Detection and Irrigation Advisory

> Across Growth Stages Using Multi-source Satellite Data

---

## Project Overview

This system uses multi-temporal satellite imagery (Sentinel-1 SAR + Sentinel-2 Optical) combined with weather data to automatically:

- **Classify crop types** at the field level across growth stages
- **Detect moisture stress** using spectral indices (NDWI, NDMI, EVI)
- **Generate irrigation advisories** tailored to each growth stage

The backend is a production-grade FastAPI service. The frontend is a React (Vite) single-page application. Machine learning inference is handled server-side and exposed through a clean REST API.

---

## Folder Structure

```
CropAI/
├── backend/
│   ├── app/
│   │   ├── api/          # Route handlers (FastAPI routers)
│   │   ├── core/         # Config, settings, shared infrastructure
│   │   ├── models/       # Domain / ORM data models
│   │   ├── schemas/      # Pydantic request & response schemas
│   │   ├── services/     # Business logic & orchestration layer
│   │   ├── utils/        # Shared utility functions
│   │   └── advisory/     # Irrigation & growth-stage advisory engine
│   ├── main.py           # FastAPI application factory & entry point
│   ├── requirements.txt  # Python dependencies
│   └── .env.example      # Environment variable template
│
├── frontend/
│   └── src/
│       ├── components/   # Reusable UI components
│       ├── pages/        # Top-level page components
│       ├── services/     # Axios API client modules
│       ├── hooks/        # Custom React hooks
│       ├── assets/       # Static files (images, icons)
│       └── styles/       # Global and module CSS files
│
├── data/
│   ├── raw/              # Raw satellite imagery (untracked by Git)
│   ├── processed/        # Processed rasters & features (untracked)
│   ├── labels/           # Ground-truth labels for model training
│   └── sample_fields/    # GeoJSON field polygons for demos & tests
│
├── docs/                 # Architecture diagrams, API references
├── scripts/              # Data download & preprocessing utilities
├── .gitignore
└── README.md
```

---

## Setup Instructions

### Prerequisites

| Tool | Minimum Version |
|------|----------------|
| Python | 3.12 |
| Node.js | 20 LTS |
| npm | 10 |

---

### Run the Backend

```bash
# 1. Navigate to backend
cd backend

# 2. Create and activate virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy and fill environment variables
copy .env.example .env   # Windows
# cp .env.example .env   # macOS / Linux

# 5. Start the development server
uvicorn main:application --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **Health check** → `http://localhost:8000/`
- **Swagger UI** → `http://localhost:8000/docs`
- **ReDoc** → `http://localhost:8000/redoc`

---

### Run the Frontend

```bash
# 1. Navigate to frontend
cd frontend

# 2. Install dependencies
npm install

# 3. Start the Vite dev server
npm run dev
```

The frontend will be available at `http://localhost:5173`.
The Vite proxy automatically forwards `/api/*` requests to the FastAPI backend.

---

## Environment Variables

Copy `backend/.env.example` to `backend/.env` and fill in the values.

| Variable | Description |
|----------|-------------|
| `COPERNICUS_USERNAME` | Copernicus Data Space Ecosystem account username |
| `COPERNICUS_PASSWORD` | Copernicus Data Space Ecosystem account password |
| `SENTINEL_CLIENT_ID` | Sentinel Hub OAuth2 client ID |
| `SENTINEL_CLIENT_SECRET` | Sentinel Hub OAuth2 client secret |
| `OPEN_METEO_BASE_URL` | Base URL for the Open-Meteo weather API |
| `APP_ENV` | Runtime environment: `development` or `production` |
| `DEBUG` | Set to `true` to enable debug mode (default: `false`) |
| `DEFAULT_LATITUDE` | Default AOI centre latitude (decimal degrees) |
| `DEFAULT_LONGITUDE` | Default AOI centre longitude (decimal degrees) |
| `DEFAULT_AOI_RADIUS_KM` | Radius in km around the default AOI centre (default: `5`) |
| `ALLOWED_ORIGINS` | Comma-separated list of allowed CORS origins |

> **Never commit your `.env` file.** It is excluded by `.gitignore`.

---

## External Accounts Required

Before running data ingestion or ML pipelines, register for the following
third-party platforms and populate your `.env` file accordingly.

### 1. Copernicus Data Space Ecosystem

| Field | Detail |
|-------|--------|
| **Portal** | [dataspace.copernicus.eu](https://dataspace.copernicus.eu) |
| **Registration** | Free account — self-service sign-up |
| **Credentials** | Username + Password (OpenID Connect) |
| **Env vars** | `COPERNICUS_USERNAME`, `COPERNICUS_PASSWORD` |
| **Purpose** | Sentinel-1 SAR and Sentinel-2 optical product search and download |

**Configuration check:**
```bash
curl http://localhost:8000/api/health/services
# "copernicus": "configured"  ← only when both vars are set
```

### 2. Sentinel Hub

| Field | Detail |
|-------|--------|
| **Portal** | [apps.sentinel-hub.com](https://apps.sentinel-hub.com) |
| **Registration** | Free trial available; commercial plans for production use |
| **Credentials** | OAuth2 Client ID + Client Secret |
| **Env vars** | `SENTINEL_CLIENT_ID`, `SENTINEL_CLIENT_SECRET` |
| **Purpose** | Evalscript-based band processing (NDVI, NDWI, NDMI, EVI, SAR backscatter) |

**Configuration check:**
```bash
curl http://localhost:8000/api/health/services
# "sentinel": "configured"  ← only when both vars are set
```

### 3. Open-Meteo

| Field | Detail |
|-------|--------|
| **Portal** | [open-meteo.com](https://open-meteo.com) |
| **Registration** | **No account required** — free and open API |
| **Credentials** | None — only a base URL is needed |
| **Env var** | `OPEN_METEO_BASE_URL=https://api.open-meteo.com/v1` |
| **Purpose** | Hourly/daily weather forecasts and ERA5 reanalysis for ET₀ computation |

**Configuration check:**
```bash
curl http://localhost:8000/api/health/services
# "weather": "configured"  ← when OPEN_METEO_BASE_URL is set
```

### Verification — All Services

Once all variables are set, the combined status endpoint should return:

```json
{
  "copernicus": "configured",
  "sentinel": "configured",
  "weather": "configured"
}
```

> If any service shows `"not_configured"`, check the corresponding `.env`
> entries and restart the backend server.

---

## Copernicus Authentication

The backend provides a dedicated service to handle secure authentication against the Copernicus Data Space Ecosystem. The service automatically retrieves access tokens, manages expiry, and can refresh tokens.

### Environment Variables Required
The authentication service requires the following credentials to be present in your `.env` file:
- `COPERNICUS_USERNAME`
- `COPERNICUS_PASSWORD`

### Authentication Endpoints

The API provides two endpoints for managing authentication:

1. **Check Status**  
   `GET /api/copernicus/status`  
   Returns the current configuration and authentication status.
   ```json
   {
       "configured": true,
       "authenticated": false
   }
   ```

2. **Authenticate**  
   `POST /api/copernicus/authenticate`  
   Attempts login and retrieves an access token.
   ```json
   {
       "authenticated": true,
       "expires_in": 600
   }
   ```

---

## Future Roadmap

### Phase 1 — Data Ingestion
- Sentinel-2 optical band acquisition via SentinelHub API
- Sentinel-1 SAR backscatter preprocessing
- Open-Meteo weather data integration
- GeoJSON field polygon management

### Phase 2 — Feature Engineering
- Spectral index computation: NDVI, NDWI, NDMI, EVI, SAVI
- SAR-derived soil moisture proxies
- Time-series feature extraction across growth stages

### Phase 3 — ML Model Training
- Crop type classification (XGBoost / Random Forest)
- Moisture stress detection (multi-class)
- Growth stage estimation

### Phase 4 — Irrigation Advisory Engine
- Rule-based + ML-hybrid advisory generation
- Field-level irrigation scheduling
- Alert and threshold management

### Phase 5 — Frontend Dashboard
- Interactive Leaflet map with field overlays
- NDVI / moisture stress visualisation layers
- Advisory report panels per field

### Phase 6 — Production Hardening
- Authentication (OAuth2 / JWT)
- PostgreSQL + PostGIS backend
- Celery task queue for async ML inference
- Docker + CI/CD pipeline
