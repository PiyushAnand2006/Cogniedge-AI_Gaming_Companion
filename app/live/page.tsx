'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { MetricCard } from '@/components/common/MetricCard';
import { RiskIndicator } from '@/components/common/RiskIndicator';

export default function LiveSessionPage() {
  const [liveData, setLiveData] = useState<any>(null);
  const [voiceQuery, setVoiceQuery] = useState('');
  const [voiceLogs, setVoiceLogs] = useState<Array<{ query: string; response: string; latency_ms: number }>>([
    {
      query: 'Why am I losing duels in East Corridor?',
      response: "You're pushing into combat below 30% HP. In the last 4 similar engagements, 3 ended in deaths. Rotate to B-Connector to reset shields.",
      latency_ms: 18.4,
    },
  ]);
  const [isQuerying, setIsQuerying] = useState(false);

  useEffect(() => {
    const eventSource = new EventSource('http://127.0.0.1:8088/events/live');
    eventSource.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.type === 'telemetry_tick') {
          setLiveData(payload.data);
        }
      } catch (err) {
        console.error(err);
      }
    };
    return () => eventSource.close();
  }, []);

  const handleSendVoiceQuery = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!voiceQuery.trim() || isQuerying) return;

    setIsQuerying(true);
    const q = voiceQuery;
    setVoiceQuery('');

    try {
      const res = await fetch('http://127.0.0.1:8088/voice/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query_text: q }),
      });
      if (res.ok) {
        const data = await res.json();
        setVoiceLogs((prev) => [
          { query: q, response: data.response, latency_ms: data.latency_ms || 19.2 },
          ...prev,
        ]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsQuerying(false);
    }
  };

  const frames = liveData?.frames || { fps: 138.4, one_percent_low: 94.6, frame_time_ms: 7.22 };
  const prediction = liveData?.stutter_prediction || { stutter_probability: 0.08, risk_level: 'low', predicted_window_ms: 1500 };

  return (
    <div className="min-h-screen bg-gaming-bg text-gaming-white pt-20 pb-16 px-gutter-desktop max-w-[1760px] mx-auto flex flex-col gap-space-lg font-sans">
      {/* Live Header */}
      <div className="p-space-lg rounded-2xl bg-gaming-panel border border-gaming-border shadow-2xl flex flex-col md:flex-row md:items-center justify-between gap-space-md clip-chamfer-tl-br laser-border-left">
        <div>
          <div className="flex items-center gap-space-xs mb-1 font-mono text-xs">
            <span className="px-2 py-0.5 rounded bg-gaming-red/20 text-gaming-red-bright border border-gaming-red/40 uppercase font-bold flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-gaming-red animate-ping" /> LIVE SESSION ACTIVE
            </span>
            <span className="text-gaming-slate">Cyberpunk 2077 • Sector B-9 Tactical Stream</span>
          </div>
          <h1 className="font-headline-lg text-headline-lg text-gaming-white font-bold tracking-tight">
            IN-GAME AI COMPANION // LIVE HUD CONSOLE
          </h1>
          <p className="font-body-md text-body-md text-gaming-slate mt-0.5">
            Real-time screen understanding via YOLO26-N, push-to-talk Qwen3-4B tactical queries, and sub-20ms frame synchronization.
          </p>
        </div>

        <div className="flex items-center gap-3 font-mono text-xs shrink-0">
          <div className="p-3 rounded-xl bg-gaming-carbon border border-gaming-border flex items-center gap-3">
            <div>
              <span className="text-gaming-slate text-[10px] block">LIVE FPS</span>
              <span className="text-xl font-bold text-gaming-red-bright">{frames.fps.toFixed(1)}</span>
            </div>
            <div className="border-l border-gaming-border pl-3">
              <span className="text-gaming-slate text-[10px] block">1% LOW</span>
              <span className="text-xl font-bold text-emerald-400">{frames.one_percent_low.toFixed(1)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Primary KPI Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-space-md">
        <MetricCard
          label="Vision Bounding Boxes"
          value="4 Hostiles"
          subValue="YOLO26-N NPU Stream (60 FPS)"
          subColor="text-gaming-red-bright"
          icon={<span className="material-symbols-outlined text-[18px]">center_focus_strong</span>}
        />
        <MetricCard
          label="Host Frame-Time"
          value={`${frames.frame_time_ms.toFixed(2)} ms`}
          subValue="Zero DirectX Hook Delay"
          subColor="text-emerald-400"
          icon={<span className="material-symbols-outlined text-[18px]">speed</span>}
        />
        <MetricCard
          label="Voice Reasoning Latency"
          value="~18.4 ms"
          subValue="Whisper + Qwen3-4B INT4"
          subColor="text-emerald-400"
          icon={<span className="material-symbols-outlined text-[18px]">mic</span>}
        />
        <MetricCard
          label="Memory Enclave"
          value="Air-Gapped"
          subValue="Zero Cloud Ingress / Egress"
          subColor="text-gaming-slate"
          icon={<span className="material-symbols-outlined text-[18px]">security</span>}
        />
      </div>

      {/* Main Console Split */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-space-lg">
        {/* Left: Tactical Radar & Vision Feeds */}
        <div className="lg:col-span-2 bg-gaming-panel rounded-2xl p-space-lg shadow-2xl border border-gaming-border flex flex-col gap-space-md clip-chamfer-tl-br laser-border-left">
          <div className="flex items-center justify-between pb-3 border-b border-gaming-border">
            <div className="flex items-center gap-space-xs">
              <span className="material-symbols-outlined text-gaming-red text-[20px]">radar</span>
              <h2 className="font-headline-sm text-headline-sm text-gaming-white font-bold">
                Live Spatial Radar &amp; Vision State
              </h2>
            </div>
            <span className="text-[10px] font-mono text-emerald-400 flex items-center gap-1 font-bold">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
              DIRECTX SURFACE HOOK ACTIVE
            </span>
          </div>

          <div className="relative h-64 rounded-xl bg-gaming-carbon border border-gaming-border overflow-hidden flex items-center justify-center tactical-hex-grid">
            {/* Radar Circular Grid */}
            <div className="absolute w-52 h-52 rounded-full border border-gaming-border/60" />
            <div className="absolute w-36 h-36 rounded-full border border-dashed border-gaming-border/40" />
            <div className="absolute w-20 h-20 rounded-full border border-gaming-red/30" />
            <div className="absolute w-2.5 h-2.5 rounded-full bg-gaming-red shadow-[0_0_12px_rgba(255,0,56,0.9)] animate-ping" />

            {/* Target Blips */}
            <div className="absolute top-12 right-20 px-2 py-0.5 rounded bg-gaming-red/80 text-white font-mono text-[10px] font-bold shadow-[0_0_10px_rgba(255,0,56,0.8)]">
              HOSTILE [18m East]
            </div>
            <div className="absolute bottom-16 left-24 px-2 py-0.5 rounded bg-gaming-panel-highest border border-gaming-border text-gaming-slate font-mono text-[10px]">
              PATROL SQUAD [42m]
            </div>

            <span className="absolute bottom-3 left-4 font-mono text-[10px] text-gaming-slate">
              FOV: 110° • Detection Confidence: 96.4%
            </span>
          </div>

          <div className="p-3.5 rounded-xl bg-gaming-carbon border border-gaming-border flex items-center justify-between text-xs font-mono">
            <div className="flex items-center gap-2 text-gaming-slate">
              <span className="material-symbols-outlined text-gaming-red text-[16px]">psychology</span>
              <span>Live Coach Advice: <strong className="text-gaming-white">Maintain catwalk high ground</strong></span>
            </div>
            <span className="text-emerald-400 font-bold">0% GPU DROP</span>
          </div>
        </div>

        {/* Right: Push-to-Talk Voice & Reasoning Console */}
        <div className="bg-gaming-panel rounded-2xl p-space-lg shadow-2xl border border-gaming-border flex flex-col justify-between gap-space-md clip-chamfer-sm">
          <div className="space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-gaming-border">
              <div className="flex items-center gap-2">
                <span className="material-symbols-outlined text-gaming-red text-[20px]">mic</span>
                <span className="font-headline-sm text-sm font-bold text-gaming-white uppercase">
                  Voice Co-pilot Console
                </span>
              </div>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-gaming-carbon text-gaming-red-bright border border-gaming-red/30">
                WHISPER ON-DEVICE
              </span>
            </div>

            <div className="space-y-3 max-h-72 overflow-y-auto pr-1">
              {voiceLogs.map((log, idx) => (
                <div key={idx} className="p-3 rounded-xl bg-gaming-carbon border border-gaming-border space-y-1.5 font-mono text-xs">
                  <div className="flex items-center justify-between text-gaming-slate">
                    <span className="text-[10px] text-gaming-red-bright font-bold">PLAYER QUERY:</span>
                    <span className="text-[10px]">{log.latency_ms.toFixed(1)} ms</span>
                  </div>
                  <p className="text-gaming-white font-sans">{log.query}</p>
                  <div className="pt-1.5 border-t border-gaming-border/60 text-gaming-slate text-[11px] font-sans">
                    <strong className="text-emerald-400 font-mono block text-[10px] mb-0.5">COGNIAI RESPONSE:</strong>
                    {log.response}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <form onSubmit={handleSendVoiceQuery} className="pt-3 border-t border-gaming-border space-y-2">
            <div className="relative">
              <input
                type="text"
                value={voiceQuery}
                onChange={(e) => setVoiceQuery(e.target.value)}
                placeholder="Ask tactical coach (e.g., 'How do I counter this sniper?')"
                className="w-full py-2.5 pl-3 pr-10 rounded-lg bg-gaming-carbon border border-gaming-border text-xs text-gaming-white placeholder-gaming-slate focus:outline-none focus:border-gaming-red"
              />
              <button
                type="submit"
                disabled={isQuerying}
                className="absolute right-1.5 top-1.5 p-1.5 rounded bg-gaming-red text-white hover:bg-gaming-red-bright transition-colors cursor-pointer"
              >
                <span className="material-symbols-outlined text-[15px]">send</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
