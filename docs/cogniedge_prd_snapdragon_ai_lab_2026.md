# Product Requirements Document — CogniEdge
**Status:** Draft  
**Prepared for:** Snapdragon AI Lab 2026 (Qualcomm Challenge Submission)  
**Target platform:** Snapdragon-powered HP PCs (Copilot+ PC, on-device NPU)

---

## 1. Overview
CogniEdge is a fully offline, on-device AI companion built around a single shared local AI engine, deployed across two purpose-built modes:
1. **Meeting & Study Co-pilot** — live contextual explanation of jargon/concepts during meetings, lectures, or podcasts, plus a structured post-session report.
2. **NPU Gaming Companion** — real-time strategy tips and enemy pattern detection during gameplay with zero FPS cost, plus a post-game coaching report.

Both modes share the same local LLM and local speech-to-text pipeline, following one design pattern: live, in-the-moment assistance while it's happening, followed by a structured report once the session ends.

---

## 2. Problem Statement
- **2.1 Comprehension gap in meetings and learning:** Transcription tools don't explain terms or extract actionable decisions.
- **2.2 Performance-costly assistance for gamers:** Traditional AI overlays compete with games for CPU/GPU cycles, introducing frame drops and stutter.
- **2.3 Idle NPU compute:** Snapdragon X/X2 Series chips feature dedicated NPUs (40–80 TOPS) that sit mostly idle during games and meetings.
- **2.4 Privacy & connectivity constraints:** Cloud AI leaks private conversations/proprietary strategies and fails without low-latency internet.

---

## 3. Goals and Non-Goals
### 3.1 Goals
- Real-time in-context AI assistance fully on-device (offline).
- 0 FPS impact on games via dedicated Snapdragon NPU execution.
- High-utility structured reports (decisions, action items, recurring gameplay patterns).
- Unified local AI engine (Qwen3-4B via Genie SDK, Whisper ONNX, NPU Vision Detector).

### 3.2 Non-Goals
- Replacing general-purpose OS live captioning.
- Generic multi-genre game vision (scoped to specific HUD/genre for demo).
- In-game memory or network hooking (read-only Windows Graphics Capture overlay).

---

## 4. Technical Architecture
```
[ Microphone Audio ] ──> [ Whisper STT (NPU/ONNX) ] ──┐
                                                        ├──> [ Mode Router ] ──> [ Shared Qwen3-4B (Genie SDK NPU) ] ──> [ Live HUD Overlay / Post-Session Report ]
[ Screen Capture ]   ──> [ NPU Vision Model ]       ──┘
```

---

## 5. Screen Suite Proposal
To deliver a complete, high-fidelity presentation and evaluation interface for the Snapdragon AI Lab 2026 challenge, CogniEdge includes:
1. **Hub & Engine Dashboard**: Mode switcher, live Snapdragon NPU telemetry (TOPS, latency, thermal, zero GPU impact status), and recent session archives.
2. **Meeting & Study Co-pilot (Live Active Session)**: Rolling audio transcription, live on-device jargon & concept explanation cards with deep-dive chips, and one-click session wrap-up.
3. **Meeting Post-Session Structured Report**: Executive summary, key decisions log, timestamped action item tracker, and knowledge graph/glossary.
4. **NPU Gaming Companion (Live HUD & Zero-FPS Overlay)**: In-game HUD overlay mockup showing real-time enemy pattern detection, strategy tips, and side-by-side FPS benchmarking (0 FPS drop vs competitor GPU overhead).
5. **Post-Game Coaching & Pattern Analysis Report**: Mistake pattern analysis, round-by-round timeline, loadout optimization, and coach advice.
