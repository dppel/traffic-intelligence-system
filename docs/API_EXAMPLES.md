# API Examples

## Health Check

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method Get
```

## Create A Processing Run

```powershell
$body = @{
    video_path = "data/videos/road_city_5s_360p.mp4"
    max_frames = 30
    save_output = $true
    display = $false
} | ConvertTo-Json

$response = Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/runs/process" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body

$response
```

`POST /runs/process` queues the run and returns a `run_id`. The run may still be `running`.

## Save The Run ID

```powershell
$runId = $response.run.run_id
$runId
```

## Query Run Analytics

Wait until the run status is `completed`:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/runs/$runId" -Method Get
```

Then query analytics:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/runs/$runId/analytics" -Method Get
```

## Query Run Events

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/runs/$runId/events" -Method Get
```

## Query Run Report

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/runs/$runId/report" -Method Get
```
