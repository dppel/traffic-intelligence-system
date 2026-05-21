from pydantic import BaseModel


class ReportListItem(BaseModel):
    name: str
    path: str
    size_bytes: int
    modified_timestamp: float


class ReportsResponse(BaseModel):
    reports: list[ReportListItem]
    analytics_exports: list[ReportListItem]


class ReportDetailResponse(BaseModel):
    name: str
    path: str
    content: str

class JsonReportResponse(BaseModel):
    output_path: str
    summary: dict[str, int | float | str]
    events: list[dict[str, int | float | str]]

