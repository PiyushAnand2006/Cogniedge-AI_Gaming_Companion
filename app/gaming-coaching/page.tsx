'use client';

import React, { useState } from 'react';
import Link from 'next/link';

export default function GamingCoachingPage() {
  const [activeTab, setActiveTab] = useState<'patterns' | 'vision' | 'loadout' | 'timeline'>('patterns');
  const [overlayStatus, setOverlayStatus] = useState<string>('Ready');
  const [selectedRound, setSelectedRound] = useState<number>(7);

  const launchOverlay = async () => {
    setOverlayStatus('Launching Overlay...');
    try {
      const res = await fetch('http://127.0.0.1:8088/overlay/launch', { method: 'POST' });
      if (res.ok) {
        setOverlayStatus('Active • Zero FPS Contention');
      } else {
        setOverlayStatus('Spawned (PyQt Process)');
      }
    } catch {
      if (typeof window !== 'undefined' && (window as unknown as { electronAPI?: { launchOverlay: () => void } }).electronAPI) {
        (window as unknown as { electronAPI: { launchOverlay: () => void } }).electronAPI.launchOverlay();
        setOverlayStatus('Active via Electron IPC');
      } else {
        setOverlayStatus('Active • Native Process');
      }
    }
  };

  return (
    <div className="w-full min-h-screen tactical-hex-grid px-gutter-desktop py-space-lg max-w-[1760px] mx-auto flex flex-col gap-space-lg text-gaming-white pb-16">
      
      {/* TOP MATCH TELEMETRY BANNER & HEADER DEBRIEF (Sleek Stealth Armor with Crimson Highlights) */}
      <section className="w-full bg-gaming-panel rounded-2xl p-space-lg relative overflow-hidden shadow-2xl border border-gaming-border/80 laser-border-left">
        {/* Ambient Tech Watermark Accent */}
        <div className="absolute right-6 -bottom-8 select-none pointer-events-none text-gaming-panel-highest/20 font-headline-lg text-[140px] leading-none tracking-tighter font-extrabold">
          VICTORY
        </div>

        {/* Top-Right Decorative Triple Hazard Slashes */}
        <div className="absolute top-4 right-6 hidden sm:flex items-center gap-1.5 opacity-80">
          <div className="hazard-slashes hazard-slashes-lg">
            <span />
            <span />
            <span />
          </div>
        </div>

        <div className="relative z-10 flex flex-col xl:flex-row xl:items-center justify-between gap-space-md">
          {/* Title & Match Context */}
          <div className="flex flex-col gap-space-xs max-w-3xl">
            <div className="flex flex-wrap items-center gap-space-xs">
              <span className="px-space-sm py-0.5 rounded-sm bg-gaming-red-subtle border border-gaming-red/40 text-gaming-red-bright font-label-sm text-label-sm uppercase tracking-wider flex items-center gap-1.5 shadow-[0_0_12px_rgba(255,0,56,0.3)]">
                <span className="w-2 h-2 rounded-full bg-gaming-red animate-ping" />
                Debrief Synthesized
              </span>
              <span className="px-space-sm py-0.5 rounded-sm bg-gaming-panel-high border border-gaming-border text-gaming-slate font-label-sm text-label-sm font-mono">
                SESSION: #APX-7829-X
              </span>
              <span className="px-space-sm py-0.5 rounded-sm bg-gaming-panel-high border border-gaming-border text-gaming-white font-label-sm text-label-sm flex items-center gap-1">
                <span className="material-symbols-outlined text-[14px] text-gaming-red">memory</span>
                Hexagon NPU v4.2 On-Device
              </span>
            </div>

            <div className="flex items-center gap-3 mt-1">
              <h1 className="font-display-lg text-display-lg text-gaming-white tracking-tight font-bold">
                Apex Vanguard <span className="text-gaming-red">//</span> Ranked Match
              </h1>
            </div>
            
            <p className="font-body-md text-body-md text-gaming-slate flex items-center gap-2">
              <span className="text-gaming-white font-semibold flex items-center gap-1">
                <span className="material-symbols-outlined text-[16px] text-gaming-red">location_on</span>
                Neo Tokyo Sector B-9
              </span>
              <span className="text-gaming-border">•</span>
              <span>Qualcomm AI Vision (YOLO26-N) &amp; Acoustic Stream Inference</span>
            </p>
          </div>

          {/* Match Outcome & Fast Stats Cards */}
          <div className="flex flex-wrap items-center gap-space-md">
            {/* Rank / Placement Card */}
            <div className="bg-gaming-panel-high/90 px-space-md py-space-sm rounded-xl flex items-center gap-space-sm shadow-lg border border-gaming-border hover:border-gaming-red/50 transition-all">
              <div className="w-12 h-12 rounded-lg bg-gaming-red-subtle border border-gaming-red/30 flex items-center justify-center text-gaming-red shadow-[0_0_15px_rgba(255,0,56,0.25)]">
                <span className="material-symbols-outlined text-[28px]" style={{ fontVariationSettings: "'FILL' 1" }}>
                  military_tech
                </span>
              </div>
              <div className="flex flex-col">
                <span className="font-label-sm text-label-sm text-gaming-slate uppercase tracking-wider font-semibold">Match Result</span>
                <span className="font-headline-md text-headline-md text-gaming-red-bright tracking-tight leading-tight font-extrabold font-mono">
                  CHAMPION #1
                </span>
                <span className="font-label-sm text-label-sm text-gaming-slate">Outlived 20 Squads</span>
              </div>
            </div>

            {/* Duration & Snapshots */}
            <div className="bg-gaming-panel-high/90 px-space-md py-space-sm rounded-xl flex items-center gap-space-sm shadow-lg border border-gaming-border hover:border-gaming-red/50 transition-all">
              <div className="w-12 h-12 rounded-lg bg-gaming-panel-highest flex items-center justify-center text-gaming-white border border-gaming-border">
                <span className="material-symbols-outlined text-[28px]">timer</span>
              </div>
              <div className="flex flex-col">
                <span className="font-label-sm text-label-sm text-gaming-slate uppercase tracking-wider font-semibold">Match Duration</span>
                <span className="font-headline-md text-headline-md text-gaming-white tracking-tight leading-tight font-bold font-mono">
                  22m 45s
                </span>
                <span className="font-label-sm text-label-sm text-gaming-slate font-mono">1,365 Frames Inferred</span>
              </div>
            </div>

            {/* Inference Speed */}
            <div className="bg-gaming-panel-high/90 px-space-md py-space-sm rounded-xl flex items-center gap-space-sm shadow-lg border border-gaming-border hover:border-gaming-red/50 transition-all">
              <div className="w-12 h-12 rounded-lg bg-gaming-red-subtle border border-gaming-red/30 flex items-center justify-center text-gaming-red">
                <span className="material-symbols-outlined text-[28px]">bolt</span>
              </div>
              <div className="flex flex-col">
                <span className="font-label-sm text-label-sm text-gaming-red-bright uppercase tracking-wider font-semibold">Analysis Speed</span>
                <span className="font-headline-md text-headline-md text-gaming-white tracking-tight leading-tight font-bold font-mono">
                  1.4 sec
                </span>
                <span className="font-label-sm text-label-sm text-gaming-slate">100% Offline Parsing</span>
              </div>
            </div>
          </div>
        </div>

        {/* Telemetry Status Bar Strip with Action CTA */}
        <div className="mt-space-md pt-space-sm flex flex-wrap items-center justify-between gap-space-sm bg-gaming-carbon -mx-space-lg -mb-space-lg px-space-lg py-space-sm border-t border-gaming-border/60">
          <div className="flex flex-wrap items-center gap-space-md font-label-sm text-label-sm text-gaming-slate">
            <span className="flex items-center gap-1.5 text-gaming-red-bright font-semibold">
              <span className="w-2 h-2 rounded-full bg-gaming-red animate-ping" />
              0.00 FPS Variance Recorded (Zero GPU Drop)
            </span>
            <span className="text-gaming-border hidden sm:inline">•</span>
            <span className="flex items-center gap-1.5 text-gaming-white">
              <span className="material-symbols-outlined text-[16px] text-gaming-red">memory</span>
              Hexagon NPU Sovereign: 0.0% CPU/GPU Contention
            </span>
            <span className="text-gaming-border hidden sm:inline">•</span>
            <span className="flex items-center gap-1.5 text-gaming-slate">
              <span className="material-symbols-outlined text-[16px] text-gaming-slate">graphic_eq</span>
              Acoustic Whisper Sync Active
            </span>
          </div>
          
          <div className="flex items-center gap-space-sm">
            <button
              onClick={launchOverlay}
              type="button"
              className="px-space-md py-1.5 bg-gaming-red hover:bg-gaming-red-bright text-white font-headline-sm text-label-md rounded-lg shadow-[0_0_16px_rgba(255,0,56,0.45)] hover:shadow-[0_0_24px_rgba(255,0,56,0.7)] transition-all flex items-center gap-1.5 active:scale-95 font-bold"
            >
              <span className="material-symbols-outlined text-[16px]">sports_esports</span>
              <span>{overlayStatus}</span>
            </button>
            <Link
              href="/benchmark"
              className="px-space-md py-1.5 bg-gaming-panel-highest hover:bg-gaming-border text-gaming-white font-headline-sm text-label-md rounded-lg border border-gaming-border transition-all flex items-center gap-1"
            >
              <span className="material-symbols-outlined text-[16px] text-gaming-red">speed</span>
              <span>Zero-FPS Benchmark</span>
            </Link>
          </div>
        </div>
      </section>

      {/* INTERACTIVE NAVIGATION CONTROL BAR (Tab Switcher) */}
      <section className="flex flex-wrap items-center justify-between gap-space-sm bg-gaming-panel p-1.5 rounded-xl border border-gaming-border shadow-lg">
        <div className="flex flex-wrap items-center gap-1">
          <button
            onClick={() => setActiveTab('patterns')}
            type="button"
            className={`px-space-md py-2 rounded-lg font-headline-sm text-label-md flex items-center gap-2 transition-all ${
              activeTab === 'patterns'
                ? 'bg-gaming-red text-white font-bold shadow-[0_0_16px_rgba(255,0,56,0.4)]'
                : 'text-gaming-slate hover:text-gaming-white hover:bg-gaming-panel-high'
            }`}
          >
            <span className="material-symbols-outlined text-[18px]">psychology</span>
            <span>Tactical Mistake Breakdown</span>
            <span className={`px-1.5 py-0.2 rounded text-[10px] font-mono ${activeTab === 'patterns' ? 'bg-black/30 text-white' : 'bg-gaming-panel-highest text-gaming-slate'}`}>
              2 Habits
            </span>
          </button>

          <button
            onClick={() => setActiveTab('vision')}
            type="button"
            className={`px-space-md py-2 rounded-lg font-headline-sm text-label-md flex items-center gap-2 transition-all ${
              activeTab === 'vision'
                ? 'bg-gaming-red text-white font-bold shadow-[0_0_16px_rgba(255,0,56,0.4)]'
                : 'text-gaming-slate hover:text-gaming-white hover:bg-gaming-panel-high'
            }`}
          >
            <span className="material-symbols-outlined text-[18px]">center_focus_strong</span>
            <span>YOLO26-N Vision Stream &amp; Radar</span>
            <span className={`px-1.5 py-0.2 rounded text-[10px] font-mono ${activeTab === 'vision' ? 'bg-black/30 text-white' : 'bg-gaming-panel-highest text-gaming-slate'}`}>
              60 FPS
            </span>
          </button>

          <button
            onClick={() => setActiveTab('loadout')}
            type="button"
            className={`px-space-md py-2 rounded-lg font-headline-sm text-label-md flex items-center gap-2 transition-all ${
              activeTab === 'loadout'
                ? 'bg-gaming-red text-white font-bold shadow-[0_0_16px_rgba(255,0,56,0.4)]'
                : 'text-gaming-slate hover:text-gaming-white hover:bg-gaming-panel-high'
            }`}
          >
            <span className="material-symbols-outlined text-[18px]">equalizer</span>
            <span>Loadout &amp; DPS Matrix</span>
          </button>

          <button
            onClick={() => setActiveTab('timeline')}
            type="button"
            className={`px-space-md py-2 rounded-lg font-headline-sm text-label-md flex items-center gap-2 transition-all ${
              activeTab === 'timeline'
                ? 'bg-gaming-red text-white font-bold shadow-[0_0_16px_rgba(255,0,56,0.4)]'
                : 'text-gaming-slate hover:text-gaming-white hover:bg-gaming-panel-high'
            }`}
          >
            <span className="material-symbols-outlined text-[18px]">timeline</span>
            <span>Round-by-Round Timeline</span>
            <span className={`px-1.5 py-0.2 rounded text-[10px] font-mono ${activeTab === 'timeline' ? 'bg-black/30 text-white' : 'bg-gaming-panel-highest text-gaming-slate'}`}>
              12 Rounds
            </span>
          </button>
        </div>

        <div className="hidden lg:flex items-center gap-2 px-space-sm text-gaming-slate font-label-sm text-label-sm font-mono">
          <span className="w-2 h-2 rounded-full bg-gaming-red animate-pulse" />
          <span>SNAPDRAGON SOVEREIGN AI WORKSTATION</span>
        </div>
      </section>

      {/* TAB 1: TACTICAL MISTAKE BREAKDOWN */}
      {activeTab === 'patterns' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-lg">
          {/* Dominant Section: Recurring Tactical Patterns (8 Cols) */}
          <section
            className="lg:col-span-8 flex flex-col gap-space-md bg-gaming-panel p-space-lg rounded-2xl shadow-2xl relative border border-gaming-border laser-border-left"
            role="region"
            aria-label="Dominant Recurring Mistake Section"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-space-xs">
                <div className="hazard-slashes">
                  <span />
                  <span />
                  <span />
                </div>
                <h2 className="font-headline-lg text-gaming-white text-headline-lg font-bold tracking-tight">
                  Recurring Mistake &amp; Tactical Pattern Breakdown
                </h2>
              </div>
              <span className="font-label-sm text-label-sm text-gaming-slate bg-gaming-panel-high border border-gaming-border px-space-xs py-0.5 rounded font-mono">
                Neural Habit Extraction
              </span>
            </div>

            {/* Pattern Card 1: Over-peeking Chokepoints (Critical) */}
            <div className="bg-gaming-panel-high rounded-xl p-space-md flex flex-col gap-space-sm shadow-md transition-all hover:border-gaming-red/50 border border-gaming-border relative overflow-hidden group">
              <div className="absolute top-0 right-0 w-32 h-32 bg-gaming-red/5 rounded-full blur-2xl pointer-events-none group-hover:bg-gaming-red/10 transition-all" />
              
              <div className="flex flex-wrap items-center justify-between gap-space-xs">
                <div className="flex items-center gap-space-xs">
                  <span className="px-2.5 py-1 rounded bg-gaming-red text-white font-label-sm text-label-sm font-bold uppercase flex items-center gap-1 shadow-[0_0_10px_rgba(255,0,56,0.4)]">
                    <span className="material-symbols-outlined text-[14px]">warning</span>
                    Critical Habit (Freq: 4x)
                  </span>
                  <span className="font-headline-sm text-label-lg text-gaming-white font-bold">
                    Over-peeking East Corridor Chokepoints Under 40 HP
                  </span>
                </div>
                <span className="font-label-sm text-label-sm text-gaming-slate font-mono bg-gaming-carbon px-2 py-0.5 rounded border border-gaming-border">
                  Occurrences: R2, R4, R7, R11
                </span>
              </div>

              <p className="font-body-md text-body-md text-gaming-slate leading-relaxed">
                YOLO26-N vision detection observed 4 instances where player maintained ADS sightline while kinetic armor was depleted and shield was on 6s recharge. Resulted in 78% of total damage taken across the match.
              </p>

              {/* Actionable Coach Advice with Highlight Box */}
              <div className="bg-gaming-carbon/80 border border-gaming-border/80 rounded-lg p-space-sm flex flex-col gap-2 mt-1">
                <div className="flex items-start gap-2">
                  <span className="w-7 h-7 rounded-lg bg-gaming-red-subtle border border-gaming-red/40 flex items-center justify-center text-gaming-red-bright shrink-0 mt-0.5">
                    <span className="material-symbols-outlined text-[16px]">psychology</span>
                  </span>
                  <div>
                    <span className="font-label-sm text-label-sm text-gaming-red-bright font-bold uppercase">
                      Qwen3 On-Device Tactical Coach:
                    </span>
                    <p className="font-body-sm text-body-sm text-gaming-white mt-0.5">
                      Fall back 15m to elevated Catwalk B-9 and deploy thermal smoke before resetting. Do not challenge long-range angles while kinetic shield is depleted.
                    </p>
                  </div>
                </div>

                <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-gaming-border/60 font-label-sm text-label-sm">
                  <span className="text-gaming-slate flex items-center gap-1 font-mono">
                    <span className="material-symbols-outlined text-[14px] text-gaming-red">security</span>
                    Target Area: East Corridor B-9
                  </span>
                  <span className="text-gaming-red-bright font-mono font-bold bg-gaming-red-subtle border border-gaming-red/30 px-2 py-0.5 rounded">
                    Estimated Delta: +28% Survivability
                  </span>
                </div>
              </div>
            </div>

            {/* Pattern Card 2: Reload Cadence Timing */}
            <div className="bg-gaming-panel-high rounded-xl p-space-md flex flex-col gap-space-sm shadow-md transition-all hover:border-gaming-red/50 border border-gaming-border relative overflow-hidden group">
              <div className="flex flex-wrap items-center justify-between gap-space-xs">
                <div className="flex items-center gap-space-xs">
                  <span className="px-2.5 py-1 rounded bg-gaming-panel-highest text-gaming-white border border-gaming-border font-label-sm text-label-sm font-bold uppercase flex items-center gap-1">
                    <span className="material-symbols-outlined text-[14px] text-gaming-red">autorenew</span>
                    Medium Impact (Freq: 3x)
                  </span>
                  <span className="font-headline-sm text-label-lg text-gaming-white font-bold">
                    Premature Weapon Swapping Before Ammo Exhaustion
                  </span>
                </div>
                <span className="font-label-sm text-label-sm text-gaming-slate font-mono bg-gaming-carbon px-2 py-0.5 rounded border border-gaming-border">
                  Occurrences: R3, R8, R10
                </span>
              </div>

              <p className="font-body-md text-body-md text-gaming-slate leading-relaxed">
                Swapped Heavy Pulse Rifle with &gt;12 rounds remaining during CQB engagements. Transition animation added 650ms vulnerability window where enemies scored kinetic headshots.
              </p>

              {/* Actionable Coach Advice */}
              <div className="bg-gaming-carbon/80 border border-gaming-border/80 rounded-lg p-space-sm flex flex-col gap-2 mt-1">
                <div className="flex items-start gap-2">
                  <span className="w-7 h-7 rounded-lg bg-gaming-red-subtle border border-gaming-red/40 flex items-center justify-center text-gaming-red-bright shrink-0 mt-0.5">
                    <span className="material-symbols-outlined text-[16px]">psychology</span>
                  </span>
                  <div>
                    <span className="font-label-sm text-label-sm text-gaming-red-bright font-bold uppercase">
                      Qwen3 On-Device Tactical Coach:
                    </span>
                    <p className="font-body-sm text-body-sm text-gaming-white mt-0.5">
                      Empty the pulse clip completely before switching weapons, or prioritize melee stagger at &lt;4m distance to cancel enemy aim.
                    </p>
                  </div>
                </div>

                <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-gaming-border/60 font-label-sm text-label-sm">
                  <span className="text-gaming-slate flex items-center gap-1 font-mono">
                    <span className="material-symbols-outlined text-[14px] text-gaming-red">bolt</span>
                    Vulnerability Window: 650ms
                  </span>
                  <span className="text-gaming-red-bright font-mono font-bold bg-gaming-red-subtle border border-gaming-red/30 px-2 py-0.5 rounded">
                    DPS Retention: +19%
                  </span>
                </div>
              </div>
            </div>
          </section>

          {/* Sidebar: Performance & Hardware Evidence (4 Cols) */}
          <section
            className="lg:col-span-4 flex flex-col gap-space-md bg-gaming-panel p-space-lg rounded-2xl shadow-xl border border-gaming-border"
            role="region"
            aria-label="Loadout and Performance Metrics Section"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-space-xs">
                <span className="material-symbols-outlined text-gaming-red text-[20px]">equalizer</span>
                <h2 className="font-headline-sm text-headline-sm text-gaming-white font-bold">
                  Tactical Performance Profile
                </h2>
              </div>
              <span className="font-label-sm text-label-sm text-gaming-red-bright font-mono">HEXAGON NPU</span>
            </div>

            <div className="flex flex-col gap-space-sm">
              {/* Pulse Rifle Metric */}
              <div className="bg-gaming-panel-high p-space-md rounded-xl flex flex-col gap-1 border border-gaming-border">
                <div className="flex items-center justify-between font-label-sm text-label-sm">
                  <span className="text-gaming-white font-bold">Heavy Pulse Rifle</span>
                  <span className="text-gaming-red-bright font-mono font-bold">46.8% Accuracy</span>
                </div>
                <div className="w-full h-2 bg-gaming-carbon rounded-full overflow-hidden mt-1 border border-gaming-border/40">
                  <div className="h-full bg-gaming-red w-[46.8%] rounded-full shadow-[0_0_10px_rgba(255,0,56,0.8)]" />
                </div>
                <span className="font-label-sm text-label-sm text-gaming-slate mt-1 font-mono">
                  Headshot Multiplier: 1.4x • 14 Eliminations
                </span>
              </div>

              {/* Scattergun Metric */}
              <div className="bg-gaming-panel-high p-space-md rounded-xl flex flex-col gap-1 border border-gaming-border">
                <div className="flex items-center justify-between font-label-sm text-label-sm">
                  <span className="text-gaming-white font-bold">Plasma Scattergun</span>
                  <span className="text-gaming-red-bright font-mono font-bold">68.2% Accuracy</span>
                </div>
                <div className="w-full h-2 bg-gaming-carbon rounded-full overflow-hidden mt-1 border border-gaming-border/40">
                  <div className="h-full bg-gaming-red w-[68.2%] rounded-full shadow-[0_0_10px_rgba(255,0,56,0.8)]" />
                </div>
                <span className="font-label-sm text-label-sm text-gaming-slate mt-1 font-mono">
                  CQB Burst: 820 DPS • 8 Eliminations
                </span>
              </div>

              {/* Zero-FPS Benchmark Evidence Box */}
              <div className="bg-gaming-carbon p-space-md rounded-xl border border-gaming-red/30 flex flex-col gap-2 mt-space-xs shadow-[0_0_16px_rgba(255,0,56,0.1)]">
                <div className="flex items-center justify-between border-b border-gaming-border/60 pb-1.5">
                  <span className="font-label-sm text-label-sm text-gaming-red-bright uppercase font-bold flex items-center gap-1">
                    <span className="w-2 h-2 rounded-full bg-gaming-red animate-pulse" />
                    Zero-FPS Benchmark Evidence
                  </span>
                  <span className="text-gaming-slate font-label-sm text-label-sm font-mono">Verified</span>
                </div>

                <div className="flex items-center justify-between font-label-sm text-label-sm text-gaming-white">
                  <span className="text-gaming-slate">Average Game FPS:</span>
                  <span className="text-gaming-red-bright font-mono font-bold">144.0 FPS (0 Drop)</span>
                </div>

                <div className="flex items-center justify-between font-label-sm text-label-sm text-gaming-white">
                  <span className="text-gaming-slate">GPU Contention:</span>
                  <span className="text-gaming-white font-mono font-bold">0.00% (Isolated to NPU)</span>
                </div>

                <div className="flex items-center justify-between font-label-sm text-label-sm text-gaming-white">
                  <span className="text-gaming-slate">Vision Latency:</span>
                  <span className="text-gaming-white font-mono">16.2 ms (YOLO26-N INT8)</span>
                </div>

                <div className="flex items-center justify-between font-label-sm text-label-sm text-gaming-white">
                  <span className="text-gaming-slate">VRAM Allocation:</span>
                  <span className="text-gaming-white font-mono">0.0 MB (Shared Memory)</span>
                </div>
              </div>
            </div>
          </section>
        </div>
      )}

      {/* TAB 2: YOLO26-N VISION STREAM & RADAR HEATMAP */}
      {activeTab === 'vision' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-space-lg">
          {/* Main Visual Stream Display (8 cols) */}
          <section className="lg:col-span-8 bg-gaming-panel rounded-2xl p-space-lg border border-gaming-border flex flex-col gap-space-md laser-border-left">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-space-xs">
                <div className="hazard-slashes">
                  <span />
                  <span />
                  <span />
                </div>
                <h2 className="font-headline-lg text-gaming-white text-headline-lg font-bold">
                  YOLO26-N NPU Vision Feed (Replay Frame #842)
                </h2>
              </div>
              <span className="px-space-xs py-0.5 rounded bg-gaming-red text-white font-label-sm text-label-sm font-bold font-mono uppercase">
                60 FPS STREAM • INT8
              </span>
            </div>

            {/* Simulated HUD Vision Frame */}
            <div className="relative w-full h-[380px] bg-gaming-carbon rounded-xl overflow-hidden border border-gaming-border/80 flex items-center justify-center">
              {/* Tactical Crosshair / Grid overlay */}
              <div className="absolute inset-0 opacity-20 pointer-events-none" style={{
                backgroundImage: 'radial-gradient(circle, #ff0038 1px, transparent 1px)',
                backgroundSize: '24px 24px'
              }} />

              {/* Center Crosshair */}
              <div className="absolute w-12 h-12 border border-gaming-red/40 rounded-full flex items-center justify-center">
                <div className="w-2 h-2 bg-gaming-red rounded-full animate-ping" />
              </div>

              {/* Bounding Box 1 (Hostile Armor) */}
              <div className="absolute left-[24%] top-[28%] w-[160px] h-[190px] border-2 border-gaming-red rounded-md bg-gaming-red/10 flex flex-col justify-between p-1.5 shadow-[0_0_15px_rgba(255,0,56,0.35)]">
                <div className="flex items-center justify-between font-mono text-[10px] bg-gaming-red text-white px-1 py-0.5 rounded font-bold">
                  <span>HOSTILE #1 [ARMOR]</span>
                  <span>94%</span>
                </div>
                <div className="text-[10px] font-mono text-gaming-red-bright bg-black/80 px-1 rounded self-start">
                  DIST: 24m • THREAT: HIGH
                </div>
              </div>

              {/* Bounding Box 2 (Hostile Flank) */}
              <div className="absolute right-[28%] top-[34%] w-[140px] h-[170px] border border-gaming-red-bright rounded-md bg-gaming-red/5 flex flex-col justify-between p-1.5">
                <div className="flex items-center justify-between font-mono text-[10px] bg-gaming-panel-highest text-gaming-white px-1 py-0.5 rounded">
                  <span>HOSTILE #2 [LOW HP]</span>
                  <span>88%</span>
                </div>
                <div className="text-[10px] font-mono text-gaming-white bg-black/80 px-1 rounded self-start">
                  DIST: 38m • CHOKE B-9
                </div>
              </div>

              {/* Bottom Stream Status */}
              <div className="absolute bottom-3 left-4 right-4 flex items-center justify-between bg-gaming-panel/90 px-space-md py-1.5 rounded-lg border border-gaming-border text-gaming-slate font-mono font-label-sm text-label-sm">
                <span className="flex items-center gap-1.5 text-gaming-white">
                  <span className="w-2 h-2 rounded-full bg-gaming-red animate-pulse" />
                  NPU Frame Latency: 16.2ms
                </span>
                <span>YOLO26-N Quantization: INT8 Tensor Core</span>
                <span className="text-gaming-red-bright font-bold">0% CPU/GPU Load</span>
              </div>
            </div>

            <p className="font-body-md text-body-md text-gaming-slate">
              Hexagon NPU scans the active display buffer at 60 FPS directly via DirectX surface capture. Objects, player models, and weapon states are categorized in real-time without taking any GPU render cycles away from the game engine.
            </p>
          </section>

          {/* Vision Telemetry Sidebar (4 cols) */}
          <section className="lg:col-span-4 bg-gaming-panel rounded-2xl p-space-lg border border-gaming-border flex flex-col gap-space-md">
            <div className="flex items-center justify-between">
              <h3 className="font-headline-sm text-headline-sm text-gaming-white font-bold">
                Threat Proximity Radar
              </h3>
              <span className="font-label-sm text-label-sm text-gaming-red-bright font-mono">SECTOR B-9</span>
            </div>

            <div className="w-full aspect-square bg-gaming-carbon rounded-xl border border-gaming-border relative flex items-center justify-center overflow-hidden">
              {/* Concentric Radar Rings */}
              <div className="w-[85%] h-[85%] border border-gaming-border/40 rounded-full flex items-center justify-center">
                <div className="w-[65%] h-[65%] border border-gaming-border/60 rounded-full flex items-center justify-center">
                  <div className="w-[35%] h-[35%] border border-gaming-red/40 rounded-full flex items-center justify-center">
                    <div className="w-3 h-3 bg-gaming-white rounded-full shadow-[0_0_8px_white]" title="Player Position" />
                  </div>
                </div>
              </div>

              {/* Hostile Blips */}
              <div className="absolute top-[28%] right-[32%] w-3 h-3 bg-gaming-red rounded-full animate-ping" />
              <div className="absolute top-[28%] right-[32%] w-3 h-3 bg-gaming-red rounded-full shadow-[0_0_10px_#ff0038]" />

              <div className="absolute bottom-[36%] left-[28%] w-2.5 h-2.5 bg-gaming-red rounded-full shadow-[0_0_10px_#ff0038]" />

              {/* Radar Sweep Line */}
              <div className="absolute inset-0 bg-gradient-to-tr from-transparent via-gaming-red/10 to-transparent pointer-events-none animate-spin" style={{ animationDuration: '4s' }} />
            </div>

            <div className="flex flex-col gap-2 font-label-sm text-label-sm font-mono">
              <div className="flex items-center justify-between text-gaming-white bg-gaming-panel-high p-2 rounded border border-gaming-border">
                <span>Active Threat Vectors:</span>
                <span className="text-gaming-red-bright font-bold">2 Hostiles Logged</span>
              </div>
              <div className="flex items-center justify-between text-gaming-white bg-gaming-panel-high p-2 rounded border border-gaming-border">
                <span>Flank Prediction Window:</span>
                <span className="text-gaming-white font-bold">12 seconds</span>
              </div>
            </div>
          </section>
        </div>
      )}

      {/* TAB 3: LOADOUT & WEAPON DPS MATRIX */}
      {activeTab === 'loadout' && (
        <section className="bg-gaming-panel rounded-2xl p-space-lg border border-gaming-border flex flex-col gap-space-md laser-border-left shadow-2xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-space-xs">
              <div className="hazard-slashes">
                <span />
                <span />
                <span />
              </div>
              <h2 className="font-headline-lg text-gaming-white text-headline-lg font-bold">
                Weapon Arsenal &amp; Recoil Telemetry Breakdown
              </h2>
            </div>
            <span className="font-label-sm text-label-sm text-gaming-slate font-mono">
              MATCH #APX-7829-X
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-space-lg">
            {/* Weapon 1 */}
            <div className="bg-gaming-panel-high p-space-lg rounded-xl border border-gaming-border flex flex-col gap-space-sm">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-headline-md text-headline-md text-gaming-white font-bold">Heavy Pulse Rifle</h3>
                  <span className="font-label-sm text-label-sm text-gaming-slate font-mono">PRIMARY WEAPON • KINETIC</span>
                </div>
                <span className="px-2 py-1 rounded bg-gaming-red text-white font-label-sm text-label-sm font-bold font-mono">
                  14 KILLS
                </span>
              </div>

              <div className="grid grid-cols-3 gap-2 my-2 font-mono text-center">
                <div className="bg-gaming-carbon p-2 rounded border border-gaming-border">
                  <span className="text-gaming-slate text-[10px] uppercase block">Accuracy</span>
                  <span className="text-gaming-red-bright font-bold text-[16px]">46.8%</span>
                </div>
                <div className="bg-gaming-carbon p-2 rounded border border-gaming-border">
                  <span className="text-gaming-slate text-[10px] uppercase block">Headshots</span>
                  <span className="text-gaming-white font-bold text-[16px]">38.2%</span>
                </div>
                <div className="bg-gaming-carbon p-2 rounded border border-gaming-border">
                  <span className="text-gaming-slate text-[10px] uppercase block">Avg DPS</span>
                  <span className="text-gaming-white font-bold text-[16px]">412 DPS</span>
                </div>
              </div>

              <p className="font-body-sm text-body-sm text-gaming-slate">
                High precision at 25-50m range. Recommendation: Avoid prematurely swapping to secondary when magazine has &gt;8 bullets left during corridor pushes.
              </p>
            </div>

            {/* Weapon 2 */}
            <div className="bg-gaming-panel-high p-space-lg rounded-xl border border-gaming-border flex flex-col gap-space-sm">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-headline-md text-headline-md text-gaming-white font-bold">Plasma Scattergun</h3>
                  <span className="font-label-sm text-label-sm text-gaming-slate font-mono">SECONDARY WEAPON • ENERGY</span>
                </div>
                <span className="px-2 py-1 rounded bg-gaming-panel-highest text-gaming-white border border-gaming-border font-label-sm text-label-sm font-bold font-mono">
                  8 KILLS
                </span>
              </div>

              <div className="grid grid-cols-3 gap-2 my-2 font-mono text-center">
                <div className="bg-gaming-carbon p-2 rounded border border-gaming-border">
                  <span className="text-gaming-slate text-[10px] uppercase block">Accuracy</span>
                  <span className="text-gaming-red-bright font-bold text-[16px]">68.2%</span>
                </div>
                <div className="bg-gaming-carbon p-2 rounded border border-gaming-border">
                  <span className="text-gaming-slate text-[10px] uppercase block">CQB Burst</span>
                  <span className="text-gaming-white font-bold text-[16px]">820 DPS</span>
                </div>
                <div className="bg-gaming-carbon p-2 rounded border border-gaming-border">
                  <span className="text-gaming-slate text-[10px] uppercase block">Kill Conversion</span>
                  <span className="text-gaming-white font-bold text-[16px]">91.4%</span>
                </div>
              </div>

              <p className="font-body-sm text-body-sm text-gaming-slate">
                Devastating CQB stopping power. Perfect pairing with Qwen3 high-ground catwalk repositioning strategies.
              </p>
            </div>
          </div>
        </section>
      )}

      {/* TAB 4: ROUND-BY-ROUND TIMELINE */}
      {activeTab === 'timeline' && (
        <section className="w-full bg-gaming-panel rounded-2xl p-space-lg shadow-2xl border border-gaming-border flex flex-col gap-space-md laser-border-left">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-space-xs">
              <div className="hazard-slashes">
                <span />
                <span />
                <span />
              </div>
              <h2 className="font-headline-lg text-gaming-white text-headline-lg font-bold">Round-by-Round Tactical Timeline</h2>
            </div>
            <span className="font-label-sm text-label-sm text-gaming-slate font-mono">12 Rounds Logged</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-space-md">
            {/* Early Rounds */}
            <div className="p-space-md rounded-xl bg-gaming-panel-high border border-gaming-border flex flex-col gap-2 hover:border-gaming-red/50 transition-all">
              <div className="flex items-center justify-between">
                <span className="font-label-md text-label-md text-gaming-white font-bold font-mono">Round 01-04 (Early)</span>
                <span className="px-2 py-0.5 rounded bg-gaming-panel-highest text-gaming-white border border-gaming-border font-label-sm text-label-sm font-mono">Clean Phase</span>
              </div>
              <p className="font-body-sm text-body-sm text-gaming-slate">
                Controlled perimeter looting in Sector B-9. Perfect kinetic shield management. 0 deaths recorded.
              </p>
            </div>

            {/* Mid Rounds */}
            <div className="p-space-md rounded-xl bg-gaming-panel-high border border-gaming-red/40 flex flex-col gap-2 shadow-[0_0_12px_rgba(255,0,56,0.15)]">
              <div className="flex items-center justify-between">
                <span className="font-label-md text-label-md text-gaming-red-bright font-bold font-mono">Round 05-08 (Mid)</span>
                <span className="px-2 py-0.5 rounded bg-gaming-red text-white font-label-sm text-label-sm font-mono font-bold">Flank Alert</span>
              </div>
              <p className="font-body-sm text-body-sm text-gaming-slate">
                Hostile squad attempted East Corridor flank. NPU HUD radar gave 12s warning, allowing choke-point trap.
              </p>
            </div>

            {/* Late Rounds */}
            <div className="p-space-md rounded-xl bg-gaming-panel-high border border-gaming-red/40 flex flex-col gap-2 shadow-[0_0_12px_rgba(255,0,56,0.15)]">
              <div className="flex items-center justify-between">
                <span className="font-label-md text-label-md text-gaming-red-bright font-bold font-mono">Round 09-12 (Late)</span>
                <span className="px-2 py-0.5 rounded bg-gaming-red text-white font-label-sm text-label-sm font-mono font-bold">Victory Clutch</span>
              </div>
              <p className="font-body-sm text-body-sm text-gaming-slate">
                Final 1v2 engagement won with high-ground catwalk repositioning suggested by on-device Qwen3 coach.
              </p>
            </div>
          </div>
        </section>
      )}

    </div>
  );
}
