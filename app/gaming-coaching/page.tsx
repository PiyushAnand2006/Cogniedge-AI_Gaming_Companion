'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { MetricCard } from '@/components/common/MetricCard';

export default function GamingCoachingPage() {
  const [activeTab, setActiveTab] = useState<'summary' | 'mistakes' | 'weapons' | 'timeline'>('summary');
  const [sessions, setSessions] = useState<any[]>([]);
  const [selectedSession, setSelectedSession] = useState<any>(null);

  useEffect(() => {
    const fetchSessions = async () => {
      try {
        const res = await fetch('http://127.0.0.1:8088/sessions');
        if (res.ok) {
          const data = await res.json();
          setSessions(data);
          if (data.length > 0) setSelectedSession(data[0]);
        }
      } catch {
        // Fallback session
      }
    };
    fetchSessions();
  }, []);

  const fallbackSession = {
    id: 'sess_live_cyberpunk',
    game_title: 'Cyberpunk 2077',
    start_time: Date.now() / 1000 - 1800,
    duration_s: 1800,
    avg_fps: 138.4,
    one_pct_low: 94.6,
    stutter_count: 2,
    kills: 24,
    deaths: 5,
    coach_rating: 'A-',
    summary: 'Strong engagement pacing in mid-range combat. Critical vulnerability detected in sub-30% HP duels in East Corridor.',
  };

  const active = selectedSession || fallbackSession;

  return (
    <div className="min-h-screen bg-gaming-bg text-gaming-white pt-20 pb-16 px-gutter-desktop max-w-[1760px] mx-auto flex flex-col gap-space-lg font-sans">
      {/* Top Banner & Debrief Identity */}
      <div className="p-space-lg rounded-2xl bg-gaming-panel border border-gaming-border shadow-2xl flex flex-col md:flex-row md:items-center justify-between gap-space-md clip-chamfer-tl-br laser-border-left">
        <div>
          <div className="flex items-center gap-space-xs mb-1 font-mono text-xs">
            <span className="px-2 py-0.5 rounded bg-gaming-red/20 text-gaming-red-bright border border-gaming-red/40 uppercase font-bold">
              POST-GAME ANALYSIS
            </span>
            <span className="text-gaming-slate">
              Cross-Domain Intelligence (Player Behavior + Machine Performance)
            </span>
          </div>
          <h1 className="font-headline-lg text-headline-lg text-gaming-white font-bold tracking-tight">
            SESSION COACHING DEBRIEF // MATCH #APX-7829-X
          </h1>
          <p className="font-body-md text-body-md text-gaming-slate mt-0.5">
            Qwen3-4B post-session evaluation correlating combat deaths with real-time frame pacing.
          </p>
        </div>

        <div className="flex items-center gap-space-md font-mono shrink-0">
          <div className="p-space-sm rounded-xl bg-gaming-carbon border border-gaming-border flex items-center gap-3">
            <span className="text-gaming-slate text-xs uppercase">Overall Rating:</span>
            <span className="text-2xl font-bold text-gaming-red-bright">{active.coach_rating || 'A-'}</span>
          </div>
          <button
            type="button"
            onClick={() => window.print()}
            className="px-4 py-2 rounded-lg bg-gaming-panel-highest hover:bg-gaming-border text-gaming-white font-headline-sm text-xs font-bold border border-gaming-border transition-colors flex items-center gap-1.5"
          >
            <span className="material-symbols-outlined text-[16px]">download</span>
            <span>Export Intel</span>
          </button>
        </div>
      </div>

      {/* Primary KPI Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-space-md">
        <MetricCard
          label="Combat Score (K/D)"
          value={`${active.kills || 24} / ${active.deaths || 5}`}
          subValue="4.8 K/D Ratio"
          subColor="text-emerald-400"
          icon={<span className="material-symbols-outlined text-[18px]">crosshair</span>}
        />
        <MetricCard
          label="Session Average FPS"
          value={`${(active.avg_fps || 138.4).toFixed(1)}`}
          subValue={`1% Low: ${(active.one_pct_low || 94.6).toFixed(1)} FPS`}
          subColor="text-emerald-400"
          icon={<span className="material-symbols-outlined text-[18px]">speed</span>}
        />
        <MetricCard
          label="Micro-Stutter Events"
          value={`${active.stutter_count || 2}`}
          subValue="0 Deaths from Stutter"
          subColor="text-gaming-slate"
          icon={<span className="material-symbols-outlined text-[18px]">bolt</span>}
        />
        <MetricCard
          label="Combat Precision Rating"
          value="88.2%"
          subValue="+14% vs Regional Avg"
          subColor="text-emerald-400"
          icon={<span className="material-symbols-outlined text-[18px]">award_star</span>}
        />
      </div>

      {/* Tactical Tab Navigation */}
      <div className="flex items-center gap-2 p-1.5 rounded-xl bg-gaming-panel border border-gaming-border shadow-inner font-mono text-xs">
        <button
          type="button"
          onClick={() => setActiveTab('summary')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg font-headline-sm text-xs font-bold transition-all cursor-pointer ${
            activeTab === 'summary'
              ? 'bg-gaming-red text-white shadow-[0_0_14px_rgba(255,0,56,0.5)]'
              : 'text-gaming-slate hover:text-gaming-white hover:bg-gaming-carbon'
          }`}
        >
          <span className="material-symbols-outlined text-[16px]">summarize</span>
          <span>Match Summary &amp; Radar</span>
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('mistakes')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg font-headline-sm text-xs font-bold transition-all cursor-pointer ${
            activeTab === 'mistakes'
              ? 'bg-gaming-red text-white shadow-[0_0_14px_rgba(255,0,56,0.5)]'
              : 'text-gaming-slate hover:text-gaming-white hover:bg-gaming-carbon'
          }`}
        >
          <span className="material-symbols-outlined text-[16px]">troubleshoot</span>
          <span>Tactical Mistakes &amp; Habit Engine</span>
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('weapons')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg font-headline-sm text-xs font-bold transition-all cursor-pointer ${
            activeTab === 'weapons'
              ? 'bg-gaming-red text-white shadow-[0_0_14px_rgba(255,0,56,0.5)]'
              : 'text-gaming-slate hover:text-gaming-white hover:bg-gaming-carbon'
          }`}
        >
          <span className="material-symbols-outlined text-[16px]">sports_martial_arts</span>
          <span>Weapon Arsenal Breakdown</span>
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('timeline')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg font-headline-sm text-xs font-bold transition-all cursor-pointer ${
            activeTab === 'timeline'
              ? 'bg-gaming-red text-white shadow-[0_0_14px_rgba(255,0,56,0.5)]'
              : 'text-gaming-slate hover:text-gaming-white hover:bg-gaming-carbon'
          }`}
        >
          <span className="material-symbols-outlined text-[16px]">timeline</span>
          <span>Round-by-Round Timeline</span>
        </button>
      </div>

      {/* TAB 1: MATCH SUMMARY & RADAR */}
      {activeTab === 'summary' && (
        <section className="grid grid-cols-1 lg:grid-cols-3 gap-space-lg">
          {/* Tactical Overview */}
          <div className="lg:col-span-2 bg-gaming-panel rounded-2xl p-space-lg shadow-2xl border border-gaming-border flex flex-col gap-space-md clip-chamfer-tl-br laser-border-left">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-space-xs">
                <div className="hazard-slashes">
                  <span />
                  <span />
                  <span />
                </div>
                <h2 className="font-headline-lg text-gaming-white text-headline-lg font-bold">
                  Tactical Debrief Analysis
                </h2>
              </div>
              <span className="font-label-sm text-label-sm text-gaming-red-bright font-mono px-2 py-0.5 bg-gaming-carbon border border-gaming-red/30 rounded">
                GENIE QWEN3-4B INT4
              </span>
            </div>

            <div className="p-4 rounded-xl bg-gaming-carbon border border-gaming-border space-y-2">
              <span className="font-label-sm text-label-sm text-gaming-red-bright uppercase font-mono font-bold flex items-center gap-1.5">
                <span className="material-symbols-outlined text-[16px]">psychology</span>
                Coach Summary &amp; Key Findings
              </span>
              <p className="font-body-md text-body-md text-gaming-slate leading-relaxed">
                {active.summary || 'Player exhibited exceptional aim stability (46.8% accuracy) during opening phase. Micro-stutters occurred 2 times in East Corridor during volumetric smoke rendering, but zero frame drops were caused by local NPU AI background telemetry.'}
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-space-sm font-mono text-center">
              <div className="p-space-sm bg-gaming-carbon rounded-xl border border-gaming-border">
                <span className="text-gaming-slate text-[10px] uppercase block">Engagement Winrate</span>
                <span className="text-gaming-white font-bold text-lg">78.4%</span>
              </div>
              <div className="p-space-sm bg-gaming-carbon rounded-xl border border-gaming-border">
                <span className="text-gaming-slate text-[10px] uppercase block">First Blood Rate</span>
                <span className="text-gaming-red-bright font-bold text-lg">62.5%</span>
              </div>
              <div className="p-space-sm bg-gaming-carbon rounded-xl border border-gaming-border">
                <span className="text-gaming-slate text-[10px] uppercase block">Clutch Conversions</span>
                <span className="text-emerald-400 font-bold text-lg">3 / 4 (75%)</span>
              </div>
            </div>
          </div>

          {/* Radar Dimension Block */}
          <div className="bg-gaming-panel rounded-2xl p-space-lg shadow-2xl border border-gaming-border flex flex-col justify-between gap-space-md clip-chamfer-sm">
            <div>
              <div className="flex items-center justify-between mb-4">
                <span className="font-headline-sm text-headline-sm text-gaming-white font-bold">
                  Tactical Radar Attributes
                </span>
                <span className="text-[10px] font-mono text-gaming-slate">Normalized 0-100</span>
              </div>

              <div className="space-y-3 font-mono text-xs">
                <div>
                  <div className="flex items-center justify-between text-gaming-slate mb-1">
                    <span>Aim Accuracy</span>
                    <span className="text-gaming-white font-bold">92 / 100</span>
                  </div>
                  <div className="w-full h-1.5 bg-gaming-carbon rounded-full overflow-hidden">
                    <div className="h-full bg-gaming-red rounded-full" style={{ width: '92%' }} />
                  </div>
                </div>

                <div>
                  <div className="flex items-center justify-between text-gaming-slate mb-1">
                    <span>Positioning &amp; Cover</span>
                    <span className="text-gaming-white font-bold">78 / 100</span>
                  </div>
                  <div className="w-full h-1.5 bg-gaming-carbon rounded-full overflow-hidden">
                    <div className="h-full bg-gaming-red rounded-full" style={{ width: '78%' }} />
                  </div>
                </div>

                <div>
                  <div className="flex items-center justify-between text-gaming-slate mb-1">
                    <span>Retreat Discipline</span>
                    <span className="text-gaming-red-bright font-bold">44 / 100</span>
                  </div>
                  <div className="w-full h-1.5 bg-gaming-carbon rounded-full overflow-hidden">
                    <div className="h-full bg-amber-500 rounded-full" style={{ width: '44%' }} />
                  </div>
                </div>

                <div>
                  <div className="flex items-center justify-between text-gaming-slate mb-1">
                    <span>Resource Management</span>
                    <span className="text-gaming-white font-bold">85 / 100</span>
                  </div>
                  <div className="w-full h-1.5 bg-gaming-carbon rounded-full overflow-hidden">
                    <div className="h-full bg-emerald-500 rounded-full" style={{ width: '85%' }} />
                  </div>
                </div>
              </div>
            </div>

            <div className="p-3 rounded-lg bg-gaming-carbon border border-gaming-red/30 text-xs font-mono text-gaming-slate">
              <strong className="text-gaming-red-bright uppercase block mb-1">Key Growth Vector:</strong>
              Increase retreat discipline when health dips below 30% HP.
            </div>
          </div>
        </section>
      )}

      {/* TAB 2: TACTICAL MISTAKES */}
      {activeTab === 'mistakes' && (
        <section className="w-full bg-gaming-panel rounded-2xl p-space-lg shadow-2xl border border-gaming-border flex flex-col gap-space-md laser-border-left">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-space-xs">
              <div className="hazard-slashes">
                <span />
                <span />
                <span />
              </div>
              <h2 className="font-headline-lg text-gaming-white text-headline-lg font-bold">
                Tactical Mistakes &amp; Critical Death Analysis
              </h2>
            </div>
            <span className="font-label-sm text-label-sm text-gaming-slate font-mono">
              3 Recurring Habits Found
            </span>
          </div>

          <div className="space-y-4">
            <div className="p-4 rounded-xl bg-gaming-carbon border border-gaming-red/40 space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-headline-sm text-sm text-gaming-red-bright font-bold flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-[18px]">warning</span>
                  Over-staying in East Corridor at Low Shield (Round 07)
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-gaming-red text-white font-bold">
                  HIGH SEVERITY
                </span>
              </div>
              <p className="text-xs text-gaming-slate">
                Player took a 1v2 engagement with 28% shield while enemy squad held high ground.
              </p>
              <div className="p-2.5 rounded-lg bg-gaming-panel border border-gaming-border text-xs text-emerald-400 font-mono">
                💡 Qwen Coach Advice: Rotate through B-Connector staircase to reset shield capacitor before re-engaging.
              </div>
            </div>

            <div className="p-4 rounded-xl bg-gaming-carbon border border-gaming-border space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-headline-sm text-sm text-gaming-white font-bold flex items-center gap-1.5">
                  <span className="material-symbols-outlined text-[18px] text-amber-400">info</span>
                  Reload Timing in Open Line of Sight (Round 11)
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-bold">
                  MODERATE SEVERITY
                </span>
              </div>
              <p className="text-xs text-gaming-slate">
                Primary weapon reloaded without taking hard cover in mid-courtyard.
              </p>
              <div className="p-2.5 rounded-lg bg-gaming-panel border border-gaming-border text-xs text-emerald-400 font-mono">
                💡 Qwen Coach Advice: Slide-cancel behind stone barrier before initiating full reload animation.
              </div>
            </div>
          </div>
        </section>
      )}

      {/* TAB 3: WEAPONS */}
      {activeTab === 'weapons' && (
        <section className="w-full bg-gaming-panel rounded-2xl p-space-lg shadow-2xl border border-gaming-border flex flex-col gap-space-md laser-border-left">
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
                High precision at 25-50m range. Recommendation: Avoid prematurely swapping to secondary when magazine has &gt;8 bullets left.
              </p>
            </div>

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

      {/* TAB 4: TIMELINE */}
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
            <div className="p-space-md rounded-xl bg-gaming-panel-high border border-gaming-border flex flex-col gap-2 hover:border-gaming-red/50 transition-all">
              <div className="flex items-center justify-between">
                <span className="font-label-md text-label-md text-gaming-white font-bold font-mono">Round 01-04 (Early)</span>
                <span className="px-2 py-0.5 rounded bg-gaming-panel-highest text-gaming-white border border-gaming-border font-label-sm text-label-sm font-mono">Clean Phase</span>
              </div>
              <p className="font-body-sm text-body-sm text-gaming-slate">
                Controlled perimeter looting in Sector B-9. Perfect kinetic shield management. 0 deaths recorded.
              </p>
            </div>

            <div className="p-space-md rounded-xl bg-gaming-panel-high border border-gaming-red/40 flex flex-col gap-2 shadow-[0_0_12px_rgba(255,0,56,0.15)]">
              <div className="flex items-center justify-between">
                <span className="font-label-md text-label-md text-gaming-red-bright font-bold font-mono">Round 05-08 (Mid)</span>
                <span className="px-2 py-0.5 rounded bg-gaming-red text-white font-label-sm text-label-sm font-mono font-bold">Flank Alert</span>
              </div>
              <p className="font-body-sm text-body-sm text-gaming-slate">
                Hostile squad attempted East Corridor flank. NPU HUD radar gave 12s warning, allowing choke-point trap.
              </p>
            </div>

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
