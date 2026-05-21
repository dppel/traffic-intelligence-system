from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.routes import analytics, anomalies, congestion, intelligence, predictions, reports, runs, videos
from app.storage.database import initialize_database
from app.utils.paths import PROJECT_ROOT


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="Traffic Intelligence API",
    description="Backend API for traffic analytics, events, and dashboard-ready reports.",
    version="0.3.0",
    lifespan=lifespan,
)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "traffic-intelligence-api"}


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse(url="/dashboard/")


app.include_router(analytics.router)
app.include_router(predictions.router)
app.include_router(anomalies.router)
app.include_router(intelligence.router)
app.include_router(congestion.router)
app.include_router(reports.router)
app.include_router(runs.router)
app.include_router(videos.router)

client_dir = PROJECT_ROOT / "client"
if client_dir.exists():
    app.mount("/dashboard", StaticFiles(directory=client_dir, html=True), name="dashboard")
