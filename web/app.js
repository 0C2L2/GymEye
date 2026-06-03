import { BrowserPoseController } from "./modules/browserAI.js";
import { createDemoAnalysis } from "./modules/mockAnalysis.js";
import { normalizeAnalysisPayload } from "./modules/normalizeAnalysis.js";
import {
  buildSessionSummary,
  loadSessionHistory,
  saveSessionHistory,
} from "./modules/sessionHistory.js";

const el = {
  topbar: document.getElementById("topbar"),
  toolbar: document.getElementById("toolbar"),
  controlBar: document.getElementById("controlBar"),
  mobileControlsMount: document.getElementById("mobileControlsMount"),
  modeSelect: document.getElementById("modeSelect"),
  startBrowserBtn: document.getElementById("startBrowserBtn"),
  stopBrowserBtn: document.getElementById("stopBrowserBtn"),
  saveSessionBtn: document.getElementById("saveSessionBtn"),
  connectBtn: document.getElementById("connectBtn"),
  wsUrl: document.getElementById("wsUrl"),
  httpUrl: document.getElementById("httpUrl"),
  browserVideo: document.getElementById("browserVideo"),
  overlayCanvas: document.getElementById("overlayCanvas"),
  backendFrame: document.getElementById("backendFrame"),
  framePlaceholder: document.getElementById("framePlaceholder"),
  cameraSourceChip: document.getElementById("cameraSourceChip"),
  modeChip: document.getElementById("modeChip"),
  repCountHero: document.getElementById("repCountHero"),
  repCorrect: document.getElementById("repCorrect"),
  repIncorrect: document.getElementById("repIncorrect"),
  repRemaining: document.getElementById("repRemaining"),
  activeFeedback: document.getElementById("activeFeedback"),
  repBreakdown: document.getElementById("repBreakdown"),
  repBreakdownCount: document.getElementById("repBreakdownCount"),
  historyList: document.getElementById("historyList"),
  backendStatusPill: document.getElementById("backendStatusPill"),
  connectionGrid: document.getElementById("connectionGrid"),
  exerciseName: document.getElementById("exerciseName"),
  confidencePill: document.getElementById("confidencePill"),
  exerciseMeta: document.getElementById("exerciseMeta"),
  statsGrid: document.getElementById("statsGrid"),
  formScoreHeading: document.getElementById("formScoreHeading"),
  formScoreStatus: document.getElementById("formScoreStatus"),
  scoreBars: document.getElementById("scoreBars"),
  mistakeList: document.getElementById("mistakeList"),
  summaryGrid: document.getElementById("summaryGrid"),
  recommendations: document.getElementById("recommendations"),
  connectionDebug: document.getElementById("connectionDebug"),
  rawPayloadDebug: document.getElementById("rawPayloadDebug"),
  normalizedPayloadDebug: document.getElementById("normalizedPayloadDebug"),
};

const savedMode = localStorage.getItem("gym-eye-selected-mode") || "auto";
const savedWsUrl = localStorage.getItem("gym-eye-ws-url") || "ws://localhost:8000/ws";
const savedHttpUrl = localStorage.getItem("gym-eye-http-url") || "http://localhost:8000";

el.modeSelect.value = savedMode;
el.wsUrl.value = savedWsUrl;
el.httpUrl.value = savedHttpUrl;

const state = {
  selectedMode: savedMode,
  resolvedMode: "demo",
  demoAnalysis: createDemoAnalysis(),
  backendAnalysis: null,
  browserAnalysis: null,
  lastRawPayload: null,
  connection: {
    backend: "disconnected",
    raspberryPi: "not connected",
    latencyMs: null,
    fps: null,
    lastUpdate: null,
    errors: [],
    currentSource: "demo",
    websocketConnected: false,
    polling: false,
  },
  frame: {
    backendAvailable: false,
    cameraSourceLabel: "Demo",
  },
  history: loadSessionHistory(),
  browserStatusMessage: null,
};

let ws = null;
let pollTimer = null;
let frameTimer = null;
let browserController = null;
let lastSavedSessionFingerprint = null;
let mobileControlsInline = false;

function formatDuration(seconds = 0) {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
}

function formatPercent(value) {
  return value === null || value === undefined ? "—" : `${Math.round(value)}%`;
}

function relativeTime(timestamp) {
  if (!timestamp) return "Never";
  const diff = Date.now() - new Date(timestamp).getTime();
  if (diff < 1500) return "Just now";
  return `${Math.max(1, Math.round(diff / 1000))}s ago`;
}

function scoreLabel(score) {
  if (score === null || score === undefined) return "Waiting";
  if (score >= 90) return "Excellent";
  if (score >= 75) return "Good";
  if (score >= 50) return "Needs work";
  return "Poor";
}

function syncResponsiveLayout() {
  const shouldUseMobileControls = window.matchMedia("(max-width: 820px)").matches;
  if (shouldUseMobileControls === mobileControlsInline) return;

  if (shouldUseMobileControls) {
    el.mobileControlsMount.appendChild(el.toolbar);
    el.mobileControlsMount.appendChild(el.controlBar);
  } else {
    el.topbar.appendChild(el.toolbar);
    el.topbar.insertAdjacentElement("afterend", el.controlBar);
  }

  mobileControlsInline = shouldUseMobileControls;
}

function backendHttpUrl() {
  return el.httpUrl.value.trim().replace(/\/$/, "");
}

function backendWsUrl() {
  return el.wsUrl.value.trim();
}

function updateConnectionError(message) {
  state.connection.errors = [message, ...state.connection.errors].slice(0, 5);
}

function applyBackendPayload(rawPayload) {
  const rawAnalysis = rawPayload?.analysis || rawPayload || {};
  state.lastRawPayload = rawPayload;
  state.backendAnalysis = normalizeAnalysisPayload(rawAnalysis, rawAnalysis.source || "backend", state.backendAnalysis);
  const status = rawPayload?.status || {};
  state.connection.websocketConnected = true;
  state.connection.backend = "connected";
  state.connection.polling = false;
  state.connection.currentSource = state.backendAnalysis.source;
  state.connection.raspberryPi =
    state.backendAnalysis.source === "raspberry_pi"
      ? "connected"
      : status.backendConnected
        ? "waiting"
        : "not connected";
  state.connection.latencyMs = state.backendAnalysis.rawPayload?.latencyMs ?? status.latencyMs ?? null;
  state.connection.fps = state.backendAnalysis.rawPayload?.fps ?? status.fps ?? null;
  state.connection.lastUpdate = state.backendAnalysis.timestamp;
  state.frame.backendAvailable = Boolean(status.hasFrame);
  updateResolvedMode();
  render();
}

function updateResolvedMode() {
  const backendAvailable = state.connection.backend === "connected" || state.connection.polling;
  if (state.selectedMode === "demo") {
    state.resolvedMode = "demo";
  } else if (state.selectedMode === "browser_ai") {
    state.resolvedMode = state.browserAnalysis ? "browser_ai" : "demo";
  } else if (state.selectedMode === "live") {
    state.resolvedMode = backendAvailable ? "live" : "demo";
  } else if (backendAvailable) {
    state.resolvedMode = "live";
  } else if (state.browserAnalysis) {
    state.resolvedMode = "browser_ai";
  } else {
    state.resolvedMode = "demo";
  }

  if (state.resolvedMode === "live") {
    state.frame.cameraSourceLabel =
      state.backendAnalysis?.source === "raspberry_pi"
        ? "Raspberry Pi / Pipeline"
        : state.backendAnalysis?.source === "gazebo"
          ? "Gazebo / Backend"
          : "Backend Frame";
  } else if (state.resolvedMode === "browser_ai") {
    state.frame.cameraSourceLabel = "Browser Camera";
  } else {
    state.frame.cameraSourceLabel = "Demo";
  }
}

function activeAnalysis() {
  if (state.resolvedMode === "live" && state.backendAnalysis) return state.backendAnalysis;
  if (state.resolvedMode === "browser_ai" && state.browserAnalysis) return state.browserAnalysis;
  return state.demoAnalysis;
}

async function fetchState() {
  try {
    const startedAt = performance.now();
    const response = await fetch(`${backendHttpUrl()}/state`, { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const payload = await response.json();
    state.connection.polling = true;
    state.connection.backend = "polling";
    state.connection.latencyMs = Math.round(performance.now() - startedAt);
    state.lastRawPayload = payload;
    state.backendAnalysis = normalizeAnalysisPayload(payload.analysis || payload, "backend", state.backendAnalysis);
    state.connection.currentSource = state.backendAnalysis.source;
    state.connection.raspberryPi =
      state.backendAnalysis.source === "raspberry_pi" ? "connected" : "waiting";
    state.connection.lastUpdate = state.backendAnalysis.timestamp;
    state.frame.backendAvailable = Boolean(payload.status?.hasFrame);
  } catch (error) {
    state.connection.backend = "disconnected";
    state.connection.websocketConnected = false;
    state.connection.polling = false;
    updateConnectionError(`REST fallback failed: ${error.message}`);
  }
  updateResolvedMode();
  render();
}

function startPolling() {
  if (pollTimer) clearInterval(pollTimer);
  pollTimer = setInterval(() => {
    if (state.selectedMode === "demo") return;
    fetchState();
  }, 3000);
}

function startFramePolling() {
  if (frameTimer) clearInterval(frameTimer);
  frameTimer = setInterval(() => {
    if (state.resolvedMode !== "live" || !state.frame.backendAvailable) {
      el.backendFrame.removeAttribute("src");
      return;
    }
    el.backendFrame.src = `${backendHttpUrl()}/frame?ts=${Date.now()}`;
  }, 700);
}

function connectBackend() {
  localStorage.setItem("gym-eye-ws-url", backendWsUrl());
  localStorage.setItem("gym-eye-http-url", backendHttpUrl());

  if (ws) {
    ws.close();
    ws = null;
  }

  state.connection.backend = "connecting";
  render();

  try {
    ws = new WebSocket(backendWsUrl());
  } catch (error) {
    state.connection.backend = "disconnected";
    updateConnectionError(`WebSocket setup failed: ${error.message}`);
    startPolling();
    fetchState();
    return;
  }

  ws.addEventListener("open", () => {
    state.connection.backend = "connected";
    state.connection.websocketConnected = true;
    render();
    startFramePolling();
  });

  ws.addEventListener("message", (event) => {
    try {
      const payload = JSON.parse(event.data);
      if (payload.error) {
        updateConnectionError(payload.error);
        return;
      }
      applyBackendPayload(payload);
    } catch (error) {
      updateConnectionError(`Invalid WebSocket payload: ${error.message}`);
    }
  });

  ws.addEventListener("close", () => {
    state.connection.backend = "disconnected";
    state.connection.websocketConnected = false;
    updateResolvedMode();
    render();
    startPolling();
    fetchState();
  });

  ws.addEventListener("error", () => {
    state.connection.backend = "disconnected";
    state.connection.websocketConnected = false;
    updateConnectionError("WebSocket connection failed.");
    render();
  });
}

async function startBrowserAI() {
  if (browserController) return;
  try {
    browserController = new BrowserPoseController({
      videoEl: el.browserVideo,
      canvasEl: el.overlayCanvas,
      onAnalysis: (analysis) => {
        state.browserAnalysis = normalizeAnalysisPayload(analysis, "browser_ai", state.browserAnalysis);
        state.lastRawPayload = analysis;
        updateResolvedMode();
        render();
      },
    });
    await browserController.start();
    state.browserStatusMessage = "Browser AI camera is active.";
    updateResolvedMode();
    render();
  } catch (error) {
    browserController = null;
    state.browserStatusMessage =
      "Browser AI camera is available, but full pose verification is not completed yet.";
    updateConnectionError(`Browser AI failed to start: ${error.message}`);
    render();
  }
}

function stopBrowserAI() {
  if (!browserController) return;
  browserController.stop();
  browserController = null;
  state.browserAnalysis = null;
  state.browserStatusMessage = "Browser AI stopped. You can continue with Demo or Live Backend mode.";
  updateResolvedMode();
  render();
}

function maybeAutoSaveSession(analysis) {
  const fingerprint = `${analysis.exercise}-${analysis.completedReps}-${analysis.durationSeconds}`;
  if (
    analysis.completedReps > 0 &&
    analysis.completedReps >= analysis.targetReps &&
    lastSavedSessionFingerprint !== fingerprint
  ) {
    lastSavedSessionFingerprint = fingerprint;
    saveCurrentSession();
  }
}

function saveCurrentSession() {
  const summary = buildSessionSummary(activeAnalysis());
  state.history = [summary, ...state.history].slice(0, 20);
  saveSessionHistory(state.history);
  render();
}

function setPanelVisibility() {
  if (state.resolvedMode === "browser_ai") {
    el.browserVideo.style.display = "block";
    el.overlayCanvas.style.display = "block";
    el.backendFrame.style.display = "none";
    el.framePlaceholder.style.display = "none";
  } else if (state.resolvedMode === "live" && state.frame.backendAvailable) {
    el.browserVideo.style.display = "none";
    el.overlayCanvas.style.display = "none";
    el.backendFrame.style.display = "block";
    el.framePlaceholder.style.display = "none";
  } else {
    el.browserVideo.style.display = "none";
    el.overlayCanvas.style.display = "none";
    el.backendFrame.style.display = "none";
    el.framePlaceholder.style.display = "flex";
  }
}

function renderKeyValueCards(container, cards) {
  container.innerHTML = cards
    .map(
      (card) => `
        <article class="mini-card">
          <span class="mini-label">${card.label}</span>
          <strong class="mini-value">${card.value}</strong>
        </article>
      `,
    )
    .join("");
}

function renderRepBreakdown(repResults) {
  el.repBreakdownCount.textContent = `${repResults.length} reps`;
  if (!repResults.length) {
    el.repBreakdown.innerHTML = `<div class="empty-state">Rep-by-rep analysis will appear once movement is detected.</div>`;
    return;
  }

  el.repBreakdown.innerHTML = repResults
    .map(
      (rep) => `
        <article class="rep-item rep-${rep.status}">
          <div>
            <strong>Rep ${rep.repNumber}</strong>
            <span>${rep.mistake || "Clean rep"}</span>
          </div>
          <div class="rep-pill-group">
            <span class="rep-pill">${rep.score}%</span>
            <span class="rep-pill">${rep.status.replace("_", " ")}</span>
            <span class="rep-pill">${rep.durationSeconds ? rep.durationSeconds.toFixed(1) + "s" : "—"}</span>
          </div>
        </article>
      `,
    )
    .join("");
}

function renderHistory() {
  if (!state.history.length) {
    el.historyList.innerHTML = `<div class="empty-state">No saved sessions yet. Finish a set or press Save Session.</div>`;
    return;
  }
  el.historyList.innerHTML = state.history
    .map(
      (session) => `
        <article class="history-item">
          <div class="history-head">
            <strong>${session.exercise}</strong>
            <span>${new Date(session.date).toLocaleString()}</span>
          </div>
          <div class="history-grid">
            <span>${session.totalReps} reps</span>
            <span>${formatPercent(session.averageFormScore)}</span>
            <span>${session.mostCommonMistake || "No major mistake"}</span>
            <span>${formatDuration(session.durationSeconds)}</span>
          </div>
        </article>
      `,
    )
    .join("");
}

function render() {
  const analysis = activeAnalysis();
  updateResolvedMode();
  maybeAutoSaveSession(analysis);
  setPanelVisibility();

  const backendLabel =
    state.connection.websocketConnected || state.connection.backend === "connected"
      ? "Connected"
      : state.connection.polling
        ? "Polling"
        : "Disconnected";

  const resolvedModeLabel =
    state.resolvedMode === "live"
      ? "Live Backend"
      : state.resolvedMode === "browser_ai"
        ? "Browser AI"
        : "Demo";

  el.cameraSourceChip.textContent = `Camera Source: ${state.frame.cameraSourceLabel}`;
  el.modeChip.textContent = `Mode: ${resolvedModeLabel}`;
  el.backendStatusPill.textContent = backendLabel;
  el.repCountHero.textContent = `${analysis.completedReps} / ${analysis.targetReps}`;
  el.repCorrect.textContent = `Correct: ${analysis.correctReps}`;
  el.repIncorrect.textContent = `Incorrect: ${analysis.incorrectReps}`;
  el.repRemaining.textContent = `Remaining: ${Math.max(0, analysis.targetReps - analysis.completedReps)}`;
  const feedbackMessage =
    state.selectedMode === "browser_ai" &&
    !state.browserAnalysis &&
    state.browserStatusMessage
      ? state.browserStatusMessage
      : analysis.activeSuggestion || "No major mistake detected. Keep going.";
  el.activeFeedback.textContent = feedbackMessage;
  el.exerciseName.textContent = analysis.exercise || "Waiting for movement";
  el.confidencePill.textContent =
    analysis.confidence !== null ? `${Math.round(analysis.confidence * 100)}% confidence` : "Confidence —";

  renderKeyValueCards(el.connectionGrid, [
    { label: "Mode", value: resolvedModeLabel },
    { label: "Backend", value: backendLabel },
    { label: "Raspberry Pi", value: state.connection.raspberryPi },
    { label: "Latency", value: state.connection.latencyMs ? `${state.connection.latencyMs}ms` : "—" },
    { label: "FPS", value: state.connection.fps ?? "—" },
    { label: "Last update", value: relativeTime(state.connection.lastUpdate) },
  ]);

  renderKeyValueCards(el.exerciseMeta, [
    { label: "Body visible", value: analysis.bodyVisible },
    { label: "Source", value: analysis.source },
    { label: "Person detected", value: analysis.personDetected ? "Yes" : "No" },
    { label: "Face detected", value: analysis.faceDetected ? "Yes" : "No" },
  ]);

  renderKeyValueCards(el.statsGrid, [
    { label: "Current set", value: String(analysis.set) },
    { label: "Workout duration", value: formatDuration(analysis.durationSeconds) },
    { label: "Avg rep time", value: analysis.averageRepTimeSeconds ? `${analysis.averageRepTimeSeconds.toFixed(1)}s` : "—" },
    { label: "Calories", value: analysis.caloriesEstimate ? `${analysis.caloriesEstimate} kcal` : "—" },
    { label: "Form accuracy", value: formatPercent(analysis.formScore) },
    { label: "Confidence", value: analysis.confidence !== null ? `${Math.round(analysis.confidence * 100)}%` : "—" },
  ]);

  el.formScoreHeading.textContent = formatPercent(analysis.formScore);
  el.formScoreStatus.textContent = scoreLabel(analysis.formScore);
  el.scoreBars.innerHTML = [
    ["Balance", analysis.scores.balance],
    ["Range of motion", analysis.scores.rangeOfMotion],
    ["Speed control", analysis.scores.speedControl],
    ["Posture", analysis.scores.posture],
  ]
    .map(
      ([label, value]) => `
        <div class="score-row">
          <div class="score-top">
            <span>${label}</span>
            <span>${formatPercent(value)}</span>
          </div>
          <div class="score-track">
            <div class="score-fill" style="width:${Math.max(0, Math.min(100, value || 0))}%"></div>
          </div>
        </div>
      `,
    )
    .join("");

  if (!analysis.mistakes.length) {
    el.mistakeList.innerHTML = `<div class="empty-state">No major mistake detected. Keep going.</div>`;
  } else {
    el.mistakeList.innerHTML = analysis.mistakes
      .map(
        (mistake) => `
          <article class="mistake-item">
            <div class="mistake-head">
              <strong>${mistake.label}</strong>
              <span class="mistake-severity severity-${mistake.severity}">${mistake.severity}</span>
            </div>
            <p>${mistake.suggestion || "Correction suggestion pending."}</p>
            <span class="subtle">${mistake.count} times</span>
          </article>
        `,
      )
      .join("");
  }

  const latestSummary = state.history[0] || buildSessionSummary(analysis);
  renderKeyValueCards(el.summaryGrid, [
    { label: "Exercise", value: latestSummary.exercise },
    { label: "Total reps", value: String(latestSummary.totalReps) },
    { label: "Correct reps", value: String(latestSummary.correctReps) },
    { label: "Incorrect reps", value: String(latestSummary.incorrectReps) },
    { label: "Avg form", value: formatPercent(latestSummary.averageFormScore) },
    { label: "Most common mistake", value: latestSummary.mostCommonMistake || "None" },
  ]);

  const recommendations = analysis.mistakes.length
    ? analysis.mistakes.slice(0, 3).map((item) => item.suggestion || item.label)
    : ["No major mistake detected. Keep going."];
  el.recommendations.innerHTML = recommendations
    .map((item) => `<div class="recommendation-item">${item}</div>`)
    .join("");

  renderRepBreakdown(analysis.repResults || []);
  renderHistory();

  el.connectionDebug.textContent = JSON.stringify(
    {
      selectedMode: state.selectedMode,
      resolvedMode: state.resolvedMode,
      wsUrl: backendWsUrl(),
      httpUrl: backendHttpUrl(),
      connection: state.connection,
    },
    null,
    2,
  );
  el.rawPayloadDebug.textContent = JSON.stringify(state.lastRawPayload, null, 2);
  el.normalizedPayloadDebug.textContent = JSON.stringify(analysis, null, 2);
}

el.modeSelect.addEventListener("change", () => {
  state.selectedMode = el.modeSelect.value;
  localStorage.setItem("gym-eye-selected-mode", state.selectedMode);
  updateResolvedMode();
  render();
  if (state.selectedMode === "live" || state.selectedMode === "auto") {
    connectBackend();
    fetchState();
  }
});

el.connectBtn.addEventListener("click", () => {
  connectBackend();
  fetchState();
});
el.startBrowserBtn.addEventListener("click", startBrowserAI);
el.stopBrowserBtn.addEventListener("click", stopBrowserAI);
el.saveSessionBtn.addEventListener("click", saveCurrentSession);
window.addEventListener("resize", syncResponsiveLayout);

connectBackend();
startPolling();
startFramePolling();
fetchState();
syncResponsiveLayout();
render();
