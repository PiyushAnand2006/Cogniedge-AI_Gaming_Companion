# CogniEdge AI Service API Specification

Base URL: `http://127.0.0.1:8088`

---

## Endpoints

### 1. Health & Hardware
- `GET /health`: Checks system health, active AI provider capabilities, and detected hardware.
- `GET /system/telemetry`: Returns raw GPU, CPU, RAM, Disk, and NPU hardware metrics with data provenance.

### 2. AI Performance Doctor
- `GET /performance/live`: Returns rolling frame-time statistics, bottleneck diagnoses, and stutter risk forecasts.
- `POST /performance/analyze`: Triggers Qwen3-4B diagnostic evaluation on current telemetry.
- `POST /performance/optimizer/preview`: Previews the outcome of an AI Compute Guard action.
- `POST /performance/optimizer/apply`: Safely applies an optimization action.
- `POST /performance/optimizer/revert`: Rolls back an applied optimization.

### 3. Game Sessions & Player Memory
- `POST /session/start`: Starts a new tracked game session.
  - Body: `{"game_title": "Cyberpunk 2077"}`
- `POST /session/stop`: Concludes session and generates a Qwen coaching debrief.
- `GET /sessions`: Returns all past session history.
- `GET /memory/profile`: Returns recurring player mistake patterns and advice effectiveness metrics.
- `POST /memory/feedback`: Records player compliance and outcome for AI advice.

### 4. Vision & Voice
- `POST /vision/detect`: Runs screen HUD detection on latest captured frame.
- `POST /voice/query`: Processes push-to-talk queries using Whisper STT + Qwen reasoning.
  - Body: `{"query_text": "Why am I losing duels in East Corridor?"}`

### 5. Live Streaming & HUD Overlay
- `GET /events/live`: Server-Sent Events stream delivering continuous telemetry heartbeats and asynchronous alert events.
- `GET /overlay/state`: Polled by PyQt HUD overlay for real-time corner widgets.
- `POST /overlay/launch`: Spawns native transparent click-through overlay.
- `POST /overlay/stop`: Terminates overlay subprocess.

### 6. Settings & Benchmarking
- `GET /settings` / `POST /settings`: Manages local AI preferences, capture FPS, and demo mode.
- `GET /benchmark/run`: Returns measured A/B AI preset comparisons vs external reference data.
