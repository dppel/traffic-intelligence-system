from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
VIDEOS_DIR = DATA_DIR / "videos"
OUTPUTS_DIR = DATA_DIR / "outputs"
ANALYTICS_DIR = DATA_DIR / "analytics"
REPORTS_DIR = PROJECT_ROOT / "reports"
STORAGE_DIR = PROJECT_ROOT / "storage"
DATABASE_PATH = STORAGE_DIR / "traffic_intelligence.db"


def resolve_project_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return PROJECT_ROOT / candidate


def latest_file(directory: Path, pattern: str) -> Path | None:
    files = sorted(directory.glob(pattern), key=lambda file: file.stat().st_mtime, reverse=True)
    return files[0] if files else None
