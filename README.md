# Configuration Drift Detection System
Detects differences between expected and observed configs. JSON/YAML, missing, unexpected, changed, severity, history, remediation.
## Severity
- Critical: missing password/secret/replicas/image OR type change
- High: changed replicas/port/cpu/memory/image
- Medium: any other changed value
- Low: unexpected / extra property
## Run Backend
cd backend; uvicorn app.main:app --port 8014 --reload
## Run Frontend
cd frontend; npm run dev
# http://localhost:5173/
## Test
cd backend; python -m pytest tests -v
## Endpoints
- POST /api/configs {name, expected_text, format}
- POST /api/snapshots {name, observed_text, format}
- GET /api/compare?name=&snapshot_id=
- POST /api/seed
- GET /api/dashboard
