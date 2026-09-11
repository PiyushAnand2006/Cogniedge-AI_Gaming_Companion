# CogniEdge Codebase Architecture Audit

> **Date**: September 2026  
> **Status**: Comprehensive Baseline Audit & Modernization Map  
> **Target Device**: Windows Gaming PC / Laptop (RTX + NPU & multi-vendor compatible)

---

## 1. Executive Summary

CogniEdge was initially scaffolded with a mix of Next.js frontend routes, a Python FastAPI microservice (`ai_service.py`), a standalone PyQt6 transparent HUD overlay (`overlay/hud_overlay.py`), and an Electron desktop wrapper (`electron/main.js`).

While the conceptual vision of an on-device AI gaming companion is strong, the current codebase contains several hardcoded assumptions (e.g., hardcoded Snapdragon X Elite strings, fabricated 0.0 FPS overhead claims, mock HUD vision detections, and lack of real hardware telemetry). This audit establishes the baseline facts across all subsystems to guide the production-grade architecture overhaul.

---

## 2. Existing Routes & Navigation

| Route | File Path | Current Status | Findings & Issues |
| :--- | :--- | :--- | :--- |
| `/` | `app/page.tsx` | Working | Cinematic landing page showcasing product features, 3-step pipeline, and live HUD preview. |
| `/login` | `app/login/page.tsx` | Working | Minimal split auth interface (Sign In / Sign Up) with CogniEdge branding and independent styling. |
| `/dashboard` | `app/dashboard/page.tsx` | Working (Static Telemetry) | Command center showing NPU telemetry, quick launch buttons, and session history. Contains hardcoded telemetry values. |
| `/gaming-coaching` | `app/gaming-coaching/page.tsx` | Working (Mock Reports) | Post-game coaching analysis with tabs (Summary, Spatial Patterns, AI Vision & Combat, Weapon Efficiency). Uses static mock data. |
| `/benchmark` | `app/benchmark/page.tsx` | Working (Simulated Comparison) | Live FPS benchmark comparison against GPU overlays. Relies on hardcoded delta metrics. |
| `/live` | *(Missing)* | Needs Creation | Live in-game session control, active telemetry stream, real-time tactical advice stream. |
| `/performance` | *(Missing)* | Needs Creation | Performance Doctor page: frame-time distribution, stutter analysis, bottleneck classifier, and safe optimizer. |
| `/memory` | *(Missing)* | Needs Creation | Player Memory page: recurring patterns, advice effectiveness tracker, and per-game profiles. |
| `/settings` | *(Missing)* | Needs Creation | Local AI providers, hardware detection, overlay configuration, demo mode, and privacy controls. |

---

## 3. Existing React Components

- **`components/AppHeader.tsx`**: Navigation header with tabs, hardware status indicators, and live session status. Currently has hardcoded hardware strings ("Snapdragon X Elite 45.2 TOPS"). Needs dynamic hardware provider integration.
- **`components/TelemetryStatBlock.tsx`**: Reusable metric display card with glow effects and trend indicators. High quality, ready for reuse with real telemetry schemas.
- **`components/SessionReportRow.tsx`**: Row component for past session summaries. Ready for reuse with SQLite-backed session models.
- **`components/StatusPill.tsx`**: Status indicator pill with pulse animation. Ready for reuse across UI states.

---

## 4. Existing Python Services (`services/`)

### `services/ai_service.py` (FastAPI backend on port `8088`)
- **Endpoints**:
  - `GET /health`: Returns service health & model availability. Hardcoded device strings.
  - `GET /telemetry`: Returns mock telemetry (`npu_utilization: 56.5`, `gpu_contention_pct: 0.00`).
  - `POST /router/query`: Dispatches LLM tasks through `ModeRouter`.
  - `POST /stt/stream`: Transcribes audio files via `WhisperSTTBridge`.
  - `POST /stt/loopback/start`, `POST /stt/loopback/stop`, `GET /stt/loopback/status`: System audio loopback (WASAPI).
  - `WS /ws/stt`: WebSocket for real-time speech-to-text.
  - `POST /vision/detect`: Calls `HUDVisionDetector` on the latest captured screen frame.
  - `GET /overlay/state`: Polled by PyQt overlay for tactical tips and threat vectors.
  - `POST /overlay/launch`, `POST /overlay/stop`: Subprocess management for `overlay/hud_overlay.py`.
  - `GET /benchmark/run`, `GET /benchmark/stream`: Runs/streams benchmark data from `BenchmarkHarness`.
  - `POST /capture/start`, `POST /capture/stop`: Starts/stops `ScreenCaptureWorker`.

### `services/genie_llm_bridge.py`
- Implements prompt formatting for Qwen3-4B Chat template (`<|im_start|>`).
- Attempts execution via Qualcomm Genie SDK binary (`genie-t2t-run.exe`).
- Falls back to hardcoded regex strings when Genie is not installed on the host.
- **Limitation**: Permanently tied to Genie SDK; lacks an extensible `LocalLLMProvider` abstraction (e.g., local OpenAI-compatible endpoints like Ollama, vLLM, LMStudio, llama.cpp).

### `services/whisper_bridge.py`
- Provides ONNX-based Whisper transcription and PCM chunk handling.
- Gracefully handles missing local model files with fallback test fixtures.
- Usable for push-to-talk voice queries and player observation notes.

### `services/vision_detector.py`
- Configured for YOLO26-N / YOLO11-N detection paths.
- Currently returns static simulated objects (`Enemy_Armored`, `Hostiles: 3`).
- **Limitation**: Needs a clean `GameVisionProvider` interface returning structured JSON state and explicit `DEMO / SIMULATED` provenance tags.

### `services/screen_capture.py`
- Safe screen-only capture using `mss` (zero DLL injection, no game hooking, non-invasive).
- Bounded thread loop with configurable capture FPS (e.g., 3.0 FPS).
- Well structured and ready for direct reuse.

### `services/benchmark_harness.py`
- Returns static comparison table against Discord, Overwolf, OBS.
- Contains hardcoded 0.00 FPS impact numbers. Needs real frame-time measurement pipeline (PresentMon / Windows telemetry).

### `services/mode_router.py`
- Routes prompts to LLM bridge for tactical tips and coaching reports.
- Legacy meeting mode routes should be consolidated into pure gaming workflows.

---

## 5. Overlay Architecture (`overlay/`)

- **Process Model**: Spawned as an independent subprocess by FastAPI (`subprocess.Popen([sys.executable, "overlay/hud_overlay.py"])`).
- **Rendering & Windows Interop**:
  - Uses `PyQt6` with `Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.SubWindow`.
  - Win32 API interop applies `WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOPMOST` for true click-through.
  - 3x3 layout maintains clear center for crosshairs and gameplay focus.
- **Defects Identified**:
  - `handle_state_update(self, data: dict)` in `hud_overlay.py` was a no-op stub (`pass`), meaning polled telemetry was never applied to widget labels.
  - Hardcoded strings in `hud_components.py` ("Snapdragon NPU Allocation: 45.2 / 80 TOPS").
  - Lack of a unified Event Bus (overlay repeatedly polled `GET /overlay/state` via HTTP instead of SSE/WebSocket).

---

## 6. Electron Process Model (`electron/`)

- **`electron/main.js`**:
  - Creates a 1440x900 window with `contextIsolation: true`, `nodeIntegration: false`.
  - Serves local Next.js instance on `http://localhost:3000`.
- **Defects Identified**:
  - Does not manage the lifecycle of the Python FastAPI backend or PyQt overlay (requires manual server launch).
  - Needs a robust `ServiceManager` to start, monitor, auto-restart, and cleanly terminate Python backend processes upon exit.

---

## 7. Data Storage & Persistence

- Currently **no SQLite database exists** in the repository.
- Sessions and reports are ephemeral in-memory objects in the frontend state.
- **Required**: A lightweight SQLite database (`services/memory/database.py`) storing:
  - `sessions`
  - `performance_samples`
  - `stutter_events`
  - `game_events`
  - `player_patterns`
  - `game_profiles`
  - `recommendations` & `recommendation_outcomes` (Advice Effectiveness)
  - `voice_notes`
  - `optimization_experiments`

---

## 8. Hardcoded / Mock Data Inventory

| Location | Mock / Hardcoded Artifact | Action Required |
| :--- | :--- | :--- |
| `services/ai_service.py` | Hardcoded NPU TOPS, device names, 0.00% GPU contention | Replace with dynamic `HardwareProvider` & real telemetry |
| `services/vision_detector.py` | Fake 3 hostiles, fixed threat vectors | Replace with `GameVisionProvider` + labeled DEMO mode |
| `services/genie_llm_bridge.py` | Static regex mock answers | Build generic `LocalLLMProvider` (OpenAI-compatible + Genie) |
| `services/benchmark_harness.py` | Static comparison values vs Discord/OBS | Build real A/B benchmarking + cited external reference data |
| `app/dashboard/page.tsx` | Static 45.2 TOPS, 0.00% GPU overhead | Bind to real `/system/telemetry` & `/performance/live` APIs |
| `app/gaming-coaching/page.tsx` | Hardcoded session stats & match timeline | Bind to SQLite session store & live events |
| `overlay/hud_components.py` | Static text labels in PyQt widgets | Wire dynamic reactive updates from unified event bus |

---

## 9. Modernization & Expansion Blueprint

1. **AI Performance Doctor Subsystem**:
   - `services/performance/collector.py`: Multi-source telemetry collector (PresentMon, Windows PDH, NVIDIA NVML/SMI, NPU).
   - `services/performance/frame_analyzer.py`: Rolling window frame-time analyzer (FPS, 1% low, 0.1% low, P50, P95, P99, variance).
   - `services/performance/bottleneck_detector.py`: Deterministic rule classifier (`GPU_BOUND`, `CPU_BOUND`, `VRAM_PRESSURE`, `THERMAL_LIMIT`, `BACKGROUND_INTERFERENCE`, etc.).
   - `services/performance/stutter_detector.py`: Real-time anomaly & frame-spike detector.
   - `services/performance/predictor.py`: Numerical risk model predicting stutter probability in upcoming windows.
   - `services/performance/optimizer.py`: Safe AI Compute Guard (optimizing CogniEdge's own capture/inference rates before touching system settings).
2. **Local LLM Provider Abstraction**:
   - `services/ai/provider.py`: Generic `LocalLLMProvider` interface.
   - Support for local OpenAI-compatible endpoints (`localhost:11434`, `localhost:1234`, `localhost:8000`), Qualcomm Genie SDK, and high-fidelity fallback.
   - Tool execution registry for Qwen3-4B.
3. **Player Memory & Advice Effectiveness**:
   - SQLite persistent storage with migrations.
   - Cross-session recurring pattern recognition.
   - Advice tracking: Was advice followed? Did survival/performance improve?
4. **Unified Live Event Bus**:
   - Single SSE/WebSocket stream (`/events/live`) connecting FastAPI, Next.js frontend, and PyQt overlay.
5. **UI/UX Production Polish**:
   - Implement new routes: `/live`, `/performance`, `/memory`, `/settings`.
   - Dark graphite/carbon aesthetic with semantic crimson/amber/green/cyan accents.
   - Clear data provenance badges (`MEASURED`, `ESTIMATED`, `REFERENCE`, `DEMO`, `UNAVAILABLE`).
   - Reusable component library (`MetricCard`, `PerformanceChart`, `DiagnosisCard`, `RiskIndicator`, etc.).
6. **Electron & Build Hardening**:
   - Sidecar Python service management.
   - Clean shutdown handlers and health watchdog.
   - Full test suite covering unit & integration paths.
