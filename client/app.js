const state = {
  selectedRunId: null,
  activeVideoPath: null,
};

const elements = {
  apiStatus: document.querySelector("#apiStatus"),
  processForm: document.querySelector("#processForm"),
  processButton: document.querySelector("#processButton"),
  videoPath: document.querySelector("#videoPath"),
  videoMeta: document.querySelector("#videoMeta"),
  maxFrames: document.querySelector("#maxFrames"),
  saveOutput: document.querySelector("#saveOutput"),
  runBadge: document.querySelector("#runBadge"),
  totalVehicles: document.querySelector("#totalVehicles"),
  incomingVehicles: document.querySelector("#incomingVehicles"),
  outgoingVehicles: document.querySelector("#outgoingVehicles"),
  averageActive: document.querySelector("#averageActive"),
  peakActive: document.querySelector("#peakActive"),
  congestionLevel: document.querySelector("#congestionLevel"),
  runsList: document.querySelector("#runsList"),
  refreshRuns: document.querySelector("#refreshRuns"),
  eventsList: document.querySelector("#eventsList"),
  eventCount: document.querySelector("#eventCount"),
  timelineRun: document.querySelector("#timelineRun"),
  timelineBody: document.querySelector("#timelineBody"),
  activeChart: document.querySelector("#activeChart"),
  congestionChart: document.querySelector("#congestionChart"),
  reportPath: document.querySelector("#reportPath"),
  reportContent: document.querySelector("#reportContent"),
  refreshAi: document.querySelector("#refreshAi"),
  trainAi: document.querySelector("#trainAi"),
  predictedScore: document.querySelector("#predictedScore"),
  predictedLevel: document.querySelector("#predictedLevel"),
  modelMae: document.querySelector("#modelMae"),
  aiAnomalyCount: document.querySelector("#aiAnomalyCount"),
  intelligenceList: document.querySelector("#intelligenceList"),
  shapList: document.querySelector("#shapList"),
  aiAnomaliesList: document.querySelector("#aiAnomaliesList"),
  aiStatus: document.querySelector("#aiStatus"),
  
  // New Interactive Video player elements
  streamStatus: document.querySelector("#streamStatus"),
  streamPlayer: document.querySelector("#streamPlayer"),
  videoSource: document.querySelector("#videoSource"),
  videoPlaceholder: document.querySelector("#videoPlaceholder"),
  activeVideoName: document.querySelector("#activeVideoName"),
  downloadVideoBtn: document.querySelector("#downloadVideoBtn"),
};

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `Request failed: ${response.status}`);
  }

  return response.json();
}

async function checkHealth() {
  try {
    await api("/health");
    elements.apiStatus.textContent = "API online";
    elements.apiStatus.parentElement.className = "status-badge";
  } catch (error) {
    elements.apiStatus.textContent = "API offline";
    elements.apiStatus.parentElement.className = "status-badge error";
  }
}

async function loadVideoLibrary() {
  const data = await api("/videos");
  elements.videoPath.innerHTML = "";

  if (!data.videos.length) {
    const option = document.createElement("option");
    option.value = "";
    option.textContent = "No videos found";
    elements.videoPath.appendChild(option);
    elements.videoMeta.textContent = "Add MP4 files to data/videos.";
    return;
  }

  data.videos.forEach((video) => {
    const option = document.createElement("option");
    option.value = video.path;
    option.textContent = video.name;
    option.dataset.name = video.name;
    option.dataset.frames = video.frame_count;
    option.dataset.fps = video.fps;
    option.dataset.width = video.width;
    option.dataset.height = video.height;
    option.dataset.size = video.size_bytes;
    elements.videoPath.appendChild(option);
  });

  const preferred = [...elements.videoPath.options].find((option) =>
    option.value.includes("traffic_flow_20s_720p.mp4")
  );
  if (preferred) {
    elements.videoPath.value = preferred.value;
  }
  updateVideoMeta();
}

function updateVideoMeta() {
  const selected = elements.videoPath.selectedOptions[0];
  if (!selected || !selected.value) {
    elements.videoMeta.textContent = "No video selected.";
    return;
  }

  const sizeMb = Number(selected.dataset.size || 0) / (1024 * 1024);
  elements.videoMeta.textContent =
    `${selected.dataset.frames} frames - ${selected.dataset.fps} FPS - ` +
    `${selected.dataset.width}x${selected.dataset.height} - ${sizeMb.toFixed(1)} MB`;

  // Preview original video if no run is currently selected
  if (!state.selectedRunId) {
    loadOriginalVideoPreview(selected.dataset.name);
  }
}

function loadOriginalVideoPreview(videoName) {
  state.activeVideoPath = `/videos/${videoName}/stream`;
  elements.activeVideoName.textContent = `Preview: ${videoName}`;
  elements.streamStatus.textContent = "Previewing Raw";
  elements.streamStatus.className = "status-pill status-offline";
  elements.downloadVideoBtn.style.display = "none";
  
  // Update video element source
  elements.videoSource.src = state.activeVideoPath;
  elements.streamPlayer.load();
  elements.streamPlayer.parentElement.classList.add("active");
}

async function trainAiModel() {
  elements.trainAi.disabled = true;
  elements.trainAi.textContent = "Training Model...";
  elements.aiStatus.textContent = "Training congestion model in background...";

  try {
    const metrics = await api("/predictions/train", { method: "POST" });
    elements.modelMae.textContent = metrics.mae.toFixed(3);
    elements.aiStatus.textContent = `XGBoost trained on ${metrics.training_rows} frames. R2: ${metrics.r2.toFixed(3)}`;
    await loadAiInsights();
  } catch (error) {
    elements.aiStatus.textContent = `Training failed: ${error.message}`;
  } finally {
    elements.trainAi.disabled = false;
    elements.trainAi.textContent = "Retrain XGBoost Model";
  }
}

async function loadAiInsights() {
  elements.aiStatus.textContent = "Fetching AI Insights...";

  const results = await Promise.allSettled([
    api("/intelligence/summary"),
    api("/predictions"),
    api("/anomalies?limit=5"),
    api("/intelligence/explanations"),
  ]);

  const [summaryResult, predictionResult, anomaliesResult, explanationResult] = results;

  if (summaryResult.status === "fulfilled") {
    renderIntelligenceSummary(summaryResult.value);
  } else {
    elements.intelligenceList.innerHTML = `<p class="insight-row">${summaryResult.reason.message}</p>`;
  }

  if (predictionResult.status === "fulfilled") {
    renderPrediction(predictionResult.value);
  } else {
    elements.predictedScore.textContent = "-";
    elements.predictedLevel.textContent = "Model untrained";
  }

  if (anomaliesResult.status === "fulfilled") {
    renderAiAnomalies(anomaliesResult.value);
  } else {
    elements.aiAnomaliesList.innerHTML = `<p class="event-row">${anomaliesResult.reason.message}</p>`;
  }

  if (explanationResult.status === "fulfilled") {
    renderShapExplanation(explanationResult.value);
  } else {
    elements.shapList.innerHTML = `<p class="feature-row">${explanationResult.reason.message}</p>`;
  }

  if (elements.aiStatus.textContent.includes("Fetching")) {
    elements.aiStatus.textContent = "AI insights loaded successfully";
  }
}

function renderPrediction(prediction) {
  elements.predictedScore.textContent = prediction.predicted_congestion_score.toFixed(1);
  elements.predictedLevel.textContent = prediction.predicted_congestion_level;
}

function renderIntelligenceSummary(summary) {
  elements.intelligenceList.innerHTML = "";
  if (!summary.insight_summary || !summary.insight_summary.length) {
    elements.intelligenceList.innerHTML = `<p class="insight-row">No patterns detected yet.</p>`;
    return;
  }
  summary.insight_summary.forEach((insight) => {
    const item = document.createElement("div");
    item.className = "insight-row";
    item.textContent = insight;
    elements.intelligenceList.appendChild(item);
  });
}

function renderShapExplanation(explanation) {
  elements.shapList.innerHTML = "";
  const intro = document.createElement("p");
  intro.className = "insight-row";
  intro.textContent = explanation.interpretation;
  elements.shapList.appendChild(intro);

  explanation.top_features.forEach((feature) => {
    const row = document.createElement("div");
    row.className = "feature-row";
    const magnitude = Math.min(Math.abs(feature.shap_value) * 10, 100);
    const directionClass = feature.shap_value >= 0 ? "positive" : "negative";
    row.innerHTML = `
      <span class="feature-name">${feature.feature}</span>
      <strong class="feature-val ${directionClass}">${feature.shap_value >= 0 ? "+" : ""}${feature.shap_value.toFixed(3)}</strong>
      <span class="feature-bar ${directionClass}" style="--bar-width: ${magnitude}%"></span>
    `;
    elements.shapList.appendChild(row);
  });
}

function renderAiAnomalies(anomalies) {
  elements.aiAnomalyCount.textContent = anomalies.length;
  elements.aiAnomaliesList.innerHTML = "";

  if (!anomalies.length) {
    elements.aiAnomaliesList.innerHTML = "<p class='event-row'>No ML anomalies detected in timeline.</p>";
    return;
  }

  anomalies.forEach((event) => {
    const row = document.createElement("div");
    row.className = "event-row";
    row.innerHTML = `
      <div class="event-top">
        <span class="event-type-badge">${event.event_type}</span>
        <span class="severity-pill ${event.severity}">${event.severity}</span>
      </div>
      <p class="event-details">${event.summary}</p>
      <div class="event-meta">
        <span>Frame ${event.frame_index}</span>
        <span>Time: ${event.timestamp_seconds.toFixed(2)}s</span>
      </div>
    `;
    elements.aiAnomaliesList.appendChild(row);
  });
}

function setMetrics(summary = {}) {
  elements.totalVehicles.textContent = summary.total_unique_vehicles ?? "-";
  elements.incomingVehicles.textContent = summary.incoming_vehicles ?? "-";
  elements.outgoingVehicles.textContent = summary.outgoing_vehicles ?? "-";
  elements.averageActive.textContent = summary.average_active_vehicles ?? "-";
  elements.peakActive.textContent = summary.peak_active_vehicles ?? "-";
  elements.congestionLevel.textContent = summary.dominant_congestion_level ?? "-";
}

async function loadRuns() {
  const data = await api("/runs?limit=10");
  elements.runsList.innerHTML = "";

  if (!data.runs.length) {
    elements.runsList.innerHTML = "<p class='run-row'>No processing runs registered yet.</p>";
    return;
  }

  data.runs.forEach((run) => {
    const row = document.createElement("button");
    row.type = "button";
    row.className = `run-row ${state.selectedRunId === run.run_id ? "active" : ""}`;
    
    // Format timestamp
    const dateStr = new Date(run.created_at).toLocaleString();

    row.innerHTML = `
      <span class="run-meta">
        <strong>${run.run_id.substring(0, 16)}...</strong>
        <span>${run.video_path.split('/').pop()}</span>
        <span style="font-size: 10px; color: var(--text-muted);">${dateStr}</span>
      </span>
      <span class="status-pill-small ${run.status}">${run.status}</span>
    `;
    row.addEventListener("click", () => {
      // Toggle active states
      document.querySelectorAll(".run-row").forEach(r => r.classList.remove("active"));
      row.classList.add("active");
      selectRun(run.run_id);
    });
    elements.runsList.appendChild(row);
  });

  if (!state.selectedRunId && data.runs[0]) {
    await selectRun(data.runs[0].run_id);
    const firstRow = elements.runsList.querySelector(".run-row");
    if (firstRow) firstRow.classList.add("active");
  }
}

async function selectRun(runId) {
  state.selectedRunId = runId;
  elements.runBadge.textContent = runId.substring(0, 16) + "...";
  elements.timelineRun.textContent = runId.substring(0, 16) + "...";

  const run = await api(`/runs/${runId}`);
  
  if (run.status !== "completed") {
    setMetrics({});
    elements.eventsList.innerHTML = `<p class="event-row">Run status: ${run.status}</p>`;
    elements.eventCount.textContent = "0 events";
    elements.timelineBody.innerHTML = "";
    elements.activeChart.innerHTML = "";
    elements.congestionChart.innerHTML = "";
    elements.reportPath.textContent = "Processing active/failed";
    elements.reportContent.textContent = run.error_message || "Video processing is currently in progress. Stream overlays will load shortly.";
    
    // Update Video stream status
    elements.streamStatus.textContent = run.status.toUpperCase();
    elements.streamStatus.className = `status-pill status-${run.status}`;
    elements.activeVideoName.textContent = `Pending: ${run.video_path.split('/').pop()}`;
    elements.downloadVideoBtn.style.display = "none";
    elements.streamPlayer.parentElement.classList.remove("active");
    return;
  }

  // Load Completed Run Details
  elements.streamStatus.textContent = "Stream Ready";
  elements.streamStatus.className = "status-pill status-completed";
  
  const videoName = run.video_path.split('/').pop();
  elements.activeVideoName.textContent = `Stream: ${videoName} (Run ID: ${runId.substring(0, 8)})`;
  
  // Set video source to new processed stream endpoint
  state.activeVideoPath = `/runs/${runId}/video`;
  elements.videoSource.src = state.activeVideoPath;
  elements.streamPlayer.load();
  elements.streamPlayer.parentElement.classList.add("active");
  
  // Set download link
  elements.downloadVideoBtn.href = state.activeVideoPath;
  elements.downloadVideoBtn.style.display = "inline-flex";

  const [analytics, events, report] = await Promise.all([
    api(`/runs/${runId}/analytics?limit=25`),
    api(`/runs/${runId}/events`),
    api(`/runs/${runId}/report`),
  ]);

  setMetrics(analytics.summary);
  renderTimeline(analytics.timeline);
  renderCharts(analytics.timeline);
  renderEvents(events.events);
  elements.reportPath.textContent = report.report_path.split('\\').pop().split('/').pop();
  elements.reportContent.textContent = report.content;
}

function renderTimeline(timeline) {
  elements.timelineBody.innerHTML = "";
  timeline.forEach((point) => {
    const row = document.createElement("tr");
    
    // Class names based on congestion
    const cLevel = point.congestion_level.toLowerCase().includes("high") ? "text-danger" 
                 : point.congestion_level.toLowerCase().includes("medium") ? "text-warning" : "text-success";
                 
    row.innerHTML = `
      <td><strong>${point.timestamp_seconds.toFixed(2)}s</strong></td>
      <td>${point.active_vehicles}</td>
      <td>${point.unique_vehicles}</td>
      <td>${point.incoming_vehicles ?? 0}</td>
      <td>${point.outgoing_vehicles ?? 0}</td>
      <td>${point.average_speed_pixels_per_frame.toFixed(1)} px/f</td>
      <td><span class="${cLevel}">${point.congestion_level} (${point.congestion_score.toFixed(1)})</span></td>
    `;
    elements.timelineBody.appendChild(row);
  });
}

function renderCharts(timeline) {
  renderBarChart({
    container: elements.activeChart,
    data: timeline.map((point) => ({
      label: `${point.timestamp_seconds.toFixed(1)}s`,
      value: point.active_vehicles,
    })),
    maxValue: Math.max(...timeline.map((point) => point.active_vehicles), 1),
    suffix: " vehicles",
  });

  renderLineChart({
    container: elements.congestionChart,
    data: timeline.map((point) => ({
      label: `${point.timestamp_seconds.toFixed(1)}s`,
      value: point.congestion_score,
      level: point.congestion_level,
    })),
    maxValue: 100,
  });
}

function renderBarChart({ container, data, maxValue, suffix }) {
  container.innerHTML = "";
  if (!data.length) {
    container.innerHTML = "<p>No analytics metrics gathered yet.</p>";
    return;
  }

  const bars = document.createElement("div");
  bars.className = "bar-chart";

  data.slice(0, 25).forEach((item) => {
    const height = Math.max((item.value / maxValue) * 100, 4);
    const bar = document.createElement("div");
    bar.className = "bar";
    bar.style.height = `${height}%`;
    bar.title = `${item.label}: ${item.value}${suffix}`;
    bars.appendChild(bar);
  });

  container.appendChild(bars);
}

function renderLineChart({ container, data, maxValue }) {
  container.innerHTML = "";
  if (!data.length) {
    container.innerHTML = "<p>No analytics metrics gathered yet.</p>";
    return;
  }

  const width = 640;
  const height = 185;
  const padding = 18;
  const points = data.slice(0, 25).map((item, index, items) => {
    const x = padding + (index / Math.max(items.length - 1, 1)) * (width - padding * 2);
    const y = height - padding - (item.value / maxValue) * (height - padding * 2);
    return { x, y, ...item };
  });
  const polyline = points.map((point) => `${point.x},${point.y}`).join(" ");
  const markers = points
    .map((point) => {
      const color = point.value >= 65 ? "hsl(355, 100%, 60%)" 
                  : point.value >= 35 ? "hsl(40, 100%, 50%)" 
                  : "hsl(150, 100%, 45%)";
      return `<circle cx="${point.x}" cy="${point.y}" r="4" fill="${color}" stroke="rgba(0,0,0,0.4)" stroke-width="1">
        <title>${point.label}: ${point.value.toFixed(1)} (${point.level})</title>
      </circle>`;
    })
    .join("");

  container.innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Congestion timeline line chart">
      <line x1="${padding}" y1="${height - padding}" x2="${width - padding}" y2="${height - padding}"></line>
      <line x1="${padding}" y1="${padding}" x2="${padding}" y2="${height - padding}"></line>
      <polyline points="${polyline}" fill="none" stroke="hsl(180, 100%, 50%)" stroke-width="2.5"></polyline>
      ${markers}
    </svg>
  `;
}

function renderEvents(events) {
  elements.eventsList.innerHTML = "";
  elements.eventCount.textContent = `${events.length} events`;

  if (!events.length) {
    elements.eventsList.innerHTML = "<p class='event-row'>No rule-based anomalies or events captured.</p>";
    return;
  }

  events.forEach((event) => {
    const row = document.createElement("div");
    row.className = "event-row";
    row.innerHTML = `
      <div class="event-top">
        <span class="event-type-badge">${event.event_type.replace('_', ' ')}</span>
        <span class="severity-pill ${event.severity}">${event.severity}</span>
      </div>
      <p class="event-details">${event.summary}</p>
      <div class="event-meta">
        <span>Frame ${event.frame_index}</span>
        <span>Time: ${event.timestamp_seconds.toFixed(2)}s</span>
      </div>
    `;
    elements.eventsList.appendChild(row);
  });
}

async function processRun(event) {
  event.preventDefault();
  elements.processButton.disabled = true;
  elements.processButton.textContent = "Deploying Model...";

  try {
    const payload = {
      video_path: elements.videoPath.value,
      max_frames: Number(elements.maxFrames.value),
      save_output: elements.saveOutput.checked,
      display: false,
    };
    const response = await api("/runs/process", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    
    state.selectedRunId = response.run.run_id;
    elements.runBadge.textContent = `${response.run.run_id.substring(0, 12)}... (queued)`;
    
    // Update visualizer state
    elements.streamStatus.textContent = "RUNNING";
    elements.streamStatus.className = "status-pill status-running";
    elements.activeVideoName.textContent = `Processing: ${payload.video_path.split('/').pop()}`;
    elements.downloadVideoBtn.style.display = "none";
    elements.streamPlayer.parentElement.classList.remove("active");

    await loadRuns();
    await pollRunUntilComplete(response.run.run_id);
  } catch (error) {
    alert(`Processing enqueuing failed: ${error.message}`);
  } finally {
    elements.processButton.disabled = false;
    elements.processButton.textContent = "Start Processing Run";
  }
}

async function pollRunUntilComplete(runId) {
  const maxAttempts = 240;

  for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
    const run = await api(`/runs/${runId}`);
    elements.runBadge.textContent = `${runId.substring(0, 8)}... (${run.status})`;
    elements.streamStatus.textContent = run.status.toUpperCase();
    elements.streamStatus.className = `status-pill status-${run.status}`;

    if (run.status === "completed") {
      await loadRuns();
      await selectRun(runId);
      return;
    }

    if (run.status === "failed") {
      await selectRun(runId);
      throw new Error(run.error_message || "Video analytics extraction failed.");
    }

    await sleep(1500);
  }

  throw new Error("Job timed out in background. Refresh historical runs to check status.");
}

function sleep(milliseconds) {
  return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

elements.processForm.addEventListener("submit", processRun);
elements.refreshRuns.addEventListener("click", loadRuns);
elements.videoPath.addEventListener("change", updateVideoMeta);
elements.refreshAi.addEventListener("click", () => loadAiInsights().catch((error) => {
  elements.aiStatus.textContent = `Refresh failed: ${error.message}`;
}));
elements.trainAi.addEventListener("click", trainAiModel);

// Bootstrap Dashboard
checkHealth();
loadVideoLibrary().catch((error) => {
  elements.videoMeta.textContent = `Library error: ${error.message}`;
});
loadRuns().catch((error) => {
  elements.runsList.innerHTML = `<p class="run-row">${error.message}</p>`;
});
loadAiInsights().catch((error) => {
  elements.aiStatus.textContent = `AI boot error: ${error.message}`;
});
