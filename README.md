# Traffic Intelligence & Vehicle Detection System

Production-style computer vision project for detecting and counting vehicles in traffic video streams.

## Client Demo

Run the backend:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Open the client-facing dashboard:

```text
http://127.0.0.1:8000/dashboard/
```

Open the API documentation:

```text
http://127.0.0.1:8000/docs
```

Demo guides:

- `docs/CLIENT_DEMO.md`
- `docs/API_EXAMPLES.md`

## Phase 1 Scope

- Load local traffic video files
- Detect cars, buses, trucks, and motorcycles with YOLO
- Draw bounding boxes, labels, and confidence scores
- Count detected vehicles per frame
- Keep detection logic separate from visualization and orchestration code

## Phase 2 Scope

- Track vehicles across video frames with ByteTrack
- Assign persistent vehicle IDs
- Count unique vehicles instead of counting the same vehicle every frame
- Estimate traffic density and congestion level
- Export frame-level analytics to CSV
- Export a simple traffic summary report

## Phase 3 Scope

- Expose traffic analytics through a FastAPI backend
- Serve dashboard-ready JSON responses
- Detect traffic events from analytics data
- List and generate reports
- Keep API routes, services, schemas, and CV processing separated

## Phase 4 Scope

- Store every processing run in SQLite
- Generate unique `run_id` values
- Save run-specific CSV, text report, JSON report, and optional processed video paths
- Query historical runs through REST APIs
- Fetch analytics, events, and reports for a specific run

## Client-Ready Scope

- Static dashboard served by FastAPI at `/dashboard/`
- Run processing form for demo videos
- Recent run browser
- Summary metrics, event list, timeline table, and report viewer
- AI Intelligence panel with prediction, anomalies, and SHAP explanations
- Swagger docs still available at `/docs`

## Phase 5 Scope

- Queue video processing runs through the API
- Return `run_id` immediately with `status: running`
- Process videos in a FastAPI background task
- Poll run status from the dashboard
- Keep `/runs/process-sync` available for synchronous debugging

## Phase 7 Scope

- Prepare ML datasets from historical traffic analytics CSV files
- Train an XGBoost congestion prediction model
- Predict future congestion from latest traffic features
- Detect ML-based traffic anomalies with IsolationForest
- Explain predictions with SHAP feature contributions
- Expose intelligent analytics through FastAPI endpoints

## Step 1: Project Setup

### Objective

Create the base project structure, configure a Python virtual environment, install dependencies, and run a first YOLO detection smoke test on one video frame.

### Explanation

This first step keeps the project modular from the beginning:

- `src/detector.py` owns YOLO model loading and vehicle filtering.
- `main.py` is only an entry point for the first test.
- `data/videos/` stores local input videos.
- `data/outputs/` will store processed videos later.
- `models/` can hold downloaded YOLO weights.

Separating these responsibilities matters because future phases will add video processing, counting rules, tracking, and analytics. If all logic starts in one script, every new feature becomes harder to test and maintain.

### Folder/File Location

```text
traffic-intelligence-system/
├── data/
│   ├── videos/
│   └── outputs/
├── models/
├── notebooks/
├── src/
│   ├── __init__.py
│   ├── detector.py
│   └── utils.py
├── .gitignore
├── main.py
├── README.md
└── requirements.txt
```

### Setup Commands

From the `traffic-intelligence-system` folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If `python` is not recognized, install Python 3.11 or newer from python.org and enable **Add python.exe to PATH** during installation.

### First YOLO Test

Place a traffic video in:

```text
data/videos/
```

Example:

```powershell
python main.py --video data/videos/sample_traffic.mp4
```

The first run may download `yolov8n.pt` automatically if it is not already in `models/`.

### Common Errors

- `python is not recognized`: Python is not installed or not on PATH.
- `No module named ultralytics`: the virtual environment is not activated or dependencies were not installed.
- `File not found`: the `--video` path is wrong.
- OpenCV window does not appear: remote/headless environments may not support `cv2.imshow`.
- Very slow first run: YOLO weights may be downloading or PyTorch may be using CPU.

### Next Step

After this smoke test works, the next increment is to move frame-by-frame video processing into `src/video_processor.py` and move counting into `src/counter.py`.

## Step 2: Tracking and Analytics Pipeline

### Objective

Process a full traffic video with tracking, unique vehicle counting, congestion scoring, and analytics export.

### Explanation

Phase 1 detected vehicles frame by frame, which is useful but not enough for traffic intelligence. If the same car appears in 100 frames, frame-level detection can count it 100 times. Phase 2 fixes that by using ByteTrack to assign a persistent `track_id` to each vehicle while it moves through the scene.

The architecture now separates responsibilities:

- `src/tracker.py`: runs YOLO + ByteTrack and returns tracked vehicles.
- `src/counter.py`: counts unique track IDs and class totals.
- `src/congestion.py`: estimates congestion from vehicle count, movement speed, and frame occupancy.
- `src/analytics.py`: stores frame metrics and exports CSV/report data.
- `src/visualization.py`: draws boxes, IDs, counters, congestion, and FPS.
- `src/video_processor.py`: coordinates the complete video pipeline.

### Folder/File Location

```text
traffic-intelligence-system/
├── data/
│   ├── videos/
│   ├── outputs/
│   └── analytics/
├── reports/
├── src/
│   ├── tracker.py
│   ├── counter.py
│   ├── analytics.py
│   ├── congestion.py
│   ├── visualization.py
│   └── video_processor.py
└── main.py
```

### Run Phase 2

Display processed video:

```powershell
.\.venv\Scripts\python.exe main.py --mode video --video data\videos\road_city_5s_360p.mp4
```

Process without display and save outputs:

```powershell
.\.venv\Scripts\python.exe main.py --mode video --video data\videos\road_city_5s_360p.mp4 --no-display --save-output
```

Fast test with only 30 frames:

```powershell
.\.venv\Scripts\python.exe main.py --mode video --video data\videos\road_city_5s_360p.mp4 --no-display --save-output --max-frames 30
```

### Outputs

- Processed video: `data/outputs/phase2_processed.mp4`
- Frame analytics CSV: `data/analytics/frame_metrics.csv`
- Summary report: `reports/traffic_summary.txt`

### Common Errors

- `No module named lap`: install requirements again with `pip install -r requirements.txt`.
- IDs flicker or reset: the video may have heavy occlusion, low resolution, or fast camera motion.
- Counts are not perfect: tracking is probabilistic; unique counting depends on stable track IDs.
- Low FPS: YOLO on CPU is expected to be slower, especially on larger videos.

### Performance Considerations

- Use `--max-frames 30` for quick tests.
- Keep early videos short and low resolution while validating logic.
- `yolov8n.pt` is fast but less accurate than larger YOLO models.
- Saving video adds overhead because every processed frame is encoded.

### Next Step

The next increment is to improve traffic analytics quality: define a counting line or region of interest, separate incoming/outgoing traffic directions, and reduce false counts from parked or static vehicles.

## Step 3: FastAPI Backend

### Objective

Expose the traffic intelligence engine through REST APIs that can support dashboards, reports, and future frontend integrations.

### Explanation

The backend is intentionally separated from the computer vision engine:

- `src/` contains detection, tracking, congestion, analytics, and video processing logic.
- `app/routes/` defines HTTP endpoints.
- `app/services/` coordinates business logic for analytics, events, reports, and processing.
- `app/schemas/` defines structured API responses with Pydantic.
- `app/utils/` contains shared backend helpers such as project path resolution.

This keeps the system easier to test and extend. A dashboard should not need to know how YOLO or ByteTrack works; it should call clean API endpoints and receive JSON.

### Folder/File Location

```text
app/
├── main.py
├── routes/
│   ├── analytics.py
│   ├── congestion.py
│   └── reports.py
├── services/
│   ├── analytics_service.py
│   ├── detection_service.py
│   ├── event_service.py
│   ├── processing_service.py
│   ├── report_service.py
│   └── tracking_service.py
├── schemas/
│   ├── analytics_schema.py
│   └── report_schema.py
└── utils/
    └── paths.py
```

### Run the API

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

### Main Endpoints

```text
GET  /health
GET  /analytics
GET  /analytics/timeline?limit=20
POST /analytics/process
GET  /events
GET  /congestion
GET  /reports
GET  /reports/latest
POST /reports/generate-json
```

### Example API Calls

Process a short video through the backend:

```json
POST /analytics/process
{
  "video_path": "data/videos/road_city_5s_360p.mp4",
  "max_frames": 30,
  "save_output": true,
  "display": false
}
```

Get dashboard summary:

```powershell
curl http://127.0.0.1:8000/analytics
```

Get detected events:

```powershell
curl http://127.0.0.1:8000/events
```

Generate dashboard JSON report:

```powershell
curl -X POST http://127.0.0.1:8000/reports/generate-json
```

### API Testing Instructions

A quick non-server smoke test can be run with FastAPI `TestClient`:

```powershell
.\.venv\Scripts\python.exe -c "from fastapi.testclient import TestClient; from app.main import app; c=TestClient(app); print(c.get('/health').json()); print(c.get('/analytics').json())"
```

### Common Backend Errors

- `ModuleNotFoundError: fastapi`: run `pip install -r requirements.txt`.
- `Analytics CSV not found`: run `/analytics/process` or the Phase 2 video command first.
- Slow `/analytics/process`: YOLO runs synchronously and may be CPU-bound.
- OpenCV display problems from API calls: keep `"display": false` for backend usage.

### Performance Considerations

- The processing endpoint is synchronous for clarity and portfolio readability.
- For long videos, use `max_frames` while testing.
- Production systems should move heavy video jobs to background workers.
- API endpoints read CSV analytics quickly; video processing is the expensive part.

### Next Step

The next improvement is to add a lightweight job system or SQLite storage so processed runs can be queried by run ID instead of always reading the latest CSV.

## Step 4: Run Management and Historical Analytics

### Objective

Turn the backend into a more realistic traffic monitoring platform by storing every processing run separately.

### Explanation

Before Phase 4, the API mostly read the latest CSV/report. That works for demos, but real systems need history. Phase 4 adds a SQLite run registry so each video processing job gets a durable `run_id`.

Each run stores:

- source video path
- status: `running`, `completed`, or `failed`
- creation and completion timestamps
- max frame limit
- analytics CSV path
- text report path
- JSON dashboard report path
- optional processed video path
- summary metrics
- detected events
- error message, if processing fails

### Folder/File Location

```text
app/
├── routes/
│   └── runs.py
├── schemas/
│   └── run_schema.py
├── services/
│   └── run_service.py
└── storage/
    ├── database.py
    └── run_repository.py

storage/
└── traffic_intelligence.db
```

Generated per-run artifacts are stored under:

```text
data/analytics/runs/
data/outputs/runs/
reports/runs/
```

### Run the API

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

### Main Run Endpoints

```text
POST /runs/process
GET  /runs
GET  /runs/{run_id}
GET  /runs/{run_id}/analytics
GET  /runs/{run_id}/events
GET  /runs/{run_id}/report
```

### Example: Create a Run

```json
POST /runs/process
{
  "video_path": "data/videos/road_city_5s_360p.mp4",
  "max_frames": 30,
  "save_output": true,
  "display": false
}
```

The response includes a `run_id`:

```json
{
  "message": "Video processed and stored successfully.",
  "run": {
    "run_id": "run_20260519_074208_d5135f72",
    "status": "completed"
  }
}
```

### Example: Query a Run

```powershell
curl http://127.0.0.1:8000/runs
curl http://127.0.0.1:8000/runs/YOUR_RUN_ID
curl http://127.0.0.1:8000/runs/YOUR_RUN_ID/analytics
curl http://127.0.0.1:8000/runs/YOUR_RUN_ID/events
curl http://127.0.0.1:8000/runs/YOUR_RUN_ID/report
```

### API Testing Instructions

Quick backend test without manually opening Swagger:

```powershell
.\.venv\Scripts\python.exe -c "from fastapi.testclient import TestClient; from app.main import app; c=TestClient(app); payload={'video_path':'data/videos/road_city_5s_360p.mp4','max_frames':5,'save_output':False,'display':False}; r=c.post('/runs/process', json=payload); print(r.status_code); print(r.json()['run']['run_id']); print(c.get('/runs').json())"
```

### Common Backend Errors

- `Run not found`: check the exact `run_id` from `GET /runs`.
- `Run is not completed`: the run failed or is still marked running.
- Slow processing: YOLO/ByteTrack is CPU-heavy; use small `max_frames` during tests.
- Missing DB file: it is created automatically when the API starts or a run service is used.

### Performance Considerations

- SQLite is good for this portfolio phase and local backend demos.
- Long video processing is still synchronous.
- Historical reads are fast because summary/events are stored in the database.
- Frame timelines still read CSV files, which is fine for local scale.

### Next Step

The next natural upgrade is a background processing queue so `POST /runs/process` returns immediately with `status: running`, while video processing continues separately.

## Step 5: Background Processing Jobs

### Objective

Make video processing behave more like a real backend job system.

### Explanation

Long-running computer vision jobs should not block an API request until the whole video finishes. Phase 5 changes the main run endpoint:

```text
POST /runs/process
```

It now creates a run record, returns immediately, and processes the video in a FastAPI background task. The dashboard polls:

```text
GET /runs/{run_id}
```

until the run becomes:

```text
completed
```

Then it loads analytics, events, and reports for that run.

### Endpoints

```text
POST /runs/process       Queues a background run
POST /runs/process-sync  Runs synchronously for debugging
GET  /runs/{run_id}      Checks status
GET  /runs/{run_id}/analytics
GET  /runs/{run_id}/events
GET  /runs/{run_id}/report
```

### Dashboard Workflow

1. Open `/dashboard/`.
2. Click `Start Processing`.
3. The run appears as `running`.
4. The dashboard polls for completion.
5. When completed, metrics, timeline, events, and report load automatically.

### Common Backend Errors

- `409 Run is not completed`: wait for status to become `completed`.
- `failed`: inspect `error_message` from `GET /runs/{run_id}`.
- Slow jobs: expected on CPU; lower `max_frames` during demos.

### Performance Considerations

FastAPI background tasks are good for a local portfolio demo. For production, this would move to a real queue such as Celery, RQ, Dramatiq, or a managed worker system.

## Step 7: AI Traffic Intelligence

### Objective

Add predictive and explainable AI capabilities on top of the traffic analytics history.

### Explanation

The AI layer uses the frame-level CSV files generated by previous phases. Each row describes a traffic frame:

- active vehicles
- unique vehicles
- average movement speed
- congestion score
- congestion level
- timestamp

Phase 7 turns those records into ML features such as lagged vehicle count, rolling averages, congestion history, and traffic deltas. The model predicts the next congestion score, while SHAP explains which features pushed the prediction up or down.

### Folder/File Location

```text
ai/
├── training/
│   ├── dataset.py
│   └── train_congestion_model.py
├── prediction/
│   └── congestion_predictor.py
├── anomaly_detection/
│   └── anomaly_detector.py
├── explainability/
│   └── shap_explainer.py
└── models/

app/routes/
├── predictions.py
├── anomalies.py
└── intelligence.py

app/services/
├── prediction_service.py
├── anomaly_service.py
├── explainability_service.py
└── intelligence_service.py
```

### API Endpoints

```text
POST /predictions/train
GET  /predictions
GET  /anomalies
GET  /intelligence/summary
GET  /intelligence/explanations
```

### Train The Congestion Model

Start the backend:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Train from all available analytics CSV files:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/predictions/train" -Method Post
```

The trained model is saved to:

```text
ai/models/congestion_xgb.joblib
```

### Predict Congestion

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/predictions" -Method Get
```

Returns:

- predicted congestion score
- predicted congestion level
- latest input features
- model path

### Detect AI Anomalies

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/anomalies?limit=20" -Method Get
```

The anomaly detector uses IsolationForest to find frames that look unusual compared with historical traffic patterns.

### Explain Predictions

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/intelligence/explanations" -Method Get
```

SHAP explains which features influenced the prediction most. Positive SHAP values push congestion higher; negative values push it lower.

### Intelligent Summary

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/intelligence/summary" -Method Get
```

This returns trend-style insights such as peak traffic, average active vehicles, peak congestion, and dominant congestion pattern.

### Common ML Errors

- `Congestion model not found`: run `POST /predictions/train` first.
- `Not enough analytics history`: process more video frames or more runs.
- Weak model metrics: sample videos are small; better data improves predictions.
- Too many anomalies: small datasets make anomaly detection sensitive; use the `limit` parameter.

### Performance Considerations

- XGBoost training is fast on the small local CSV history.
- SHAP explanations are computed on the latest feature row, not the full dataset.
- This is an applied ML demo layer, not a city-scale training pipeline.
- For production, model training would be scheduled and versioned separately.
