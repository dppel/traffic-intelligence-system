# Client Demo Guide

This guide shows how to present the Traffic Intelligence system as a client-facing demo.

## Start The Backend

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

## Open The Dashboard

```text
http://127.0.0.1:8000/dashboard/
```

The dashboard lets you:

- create a video processing run
- inspect unique vehicle count
- view congestion summary
- train and refresh the AI model
- inspect congestion predictions
- review ML anomalies
- view SHAP feature explanations
- review recent runs
- inspect event detection output
- read the generated traffic report

## Open The API Docs

```text
http://127.0.0.1:8000/docs
```

Useful endpoints:

```text
POST /runs/process
GET  /runs
GET  /runs/{run_id}/analytics
GET  /runs/{run_id}/events
GET  /runs/{run_id}/report
```

## Demo Script

1. Open `/dashboard/`.
2. Keep the default video path: `data/videos/road_city_5s_360p.mp4`.
3. Set `max_frames` to `30`.
4. Click `Start Processing`.
5. Watch the run status move from `running` to `completed`.
6. Select the newest run from `Recent Runs`.
7. Walk through:
   - total unique vehicles
   - average active vehicles
   - peak active vehicles
   - congestion level
   - AI predicted congestion score
   - AI anomaly list
   - SHAP feature explanation
   - events
   - timeline
   - report

## Talking Points

- YOLO detects vehicles in each frame.
- ByteTrack gives vehicles persistent IDs across frames.
- Unique vehicle counting avoids duplicate per-frame counting.
- The backend stores every processing run in SQLite.
- Processing runs are queued as background jobs.
- XGBoost predicts congestion from historical frame analytics.
- SHAP explains which traffic features influenced the prediction.
- IsolationForest highlights unusual traffic patterns.
- The dashboard consumes REST APIs and is ready for a future richer frontend.
