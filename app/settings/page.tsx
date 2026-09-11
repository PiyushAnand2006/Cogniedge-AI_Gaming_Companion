'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';

export default function SettingsPage() {
  const [settings, setSettings] = useState<any>({
    overlay_hotkey: 'F10',
    ptt_hotkey: 'Ctrl+Space',
    overlay_opacity: 0.90,
    click_through_hud: true,
    vision_capture_fps: 60,
    predictive_stutter_enabled: true,
    npu_isolation_mode: 'Hexagon_NPU_Turbo',
    session_retention_days: 30,
  });

  const [saved, setSaved] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        const res = await fetch('http://127.0.0.1:8088/settings');
        if (res.ok) {
          const data = await res.json();
          setSettings((prev: any) => ({ ...prev, ...data }));
        }
      } catch (e) {
        // Local defaults
      }
    };
    fetchSettings();
  }, []);

  const handleSave = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://127.0.0.1:8088/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings),
      });
      if (res.ok) {
        setSaved(true);
        setTimeout(() => setSaved(false), 2500);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleClearMemory = async () => {
    if (confirm('Are you sure you want to clear local SQLite session history? This will reset all player habits and coaching correlations.')) {
      try {
        await fetch('http://127.0.0.1:8088/memory/clear', { method: 'POST' });
        alert('Local database history reset successfully.');
      } catch (e) {
        console.error(e);
      }
    }
  };

  return (
    <div className="min-h-screen bg-gaming-bg text-gaming-white pt-20 pb-16 px-gutter-desktop max-w-[1280px] mx-auto flex flex-col gap-space-lg font-sans">
      {/* Header */}
      <div className="p-space-lg rounded-2xl bg-gaming-panel border border-gaming-border shadow-2xl flex flex-col md:flex-row md:items-center justify-between gap-space-md clip-chamfer-tl-br laser-border-left">
        <div>
          <div className="flex items-center gap-space-xs mb-1 font-mono text-xs">
            <span className="px-2 py-0.5 rounded bg-gaming-red/20 text-gaming-red-bright border border-gaming-red/40 uppercase font-bold">
              SOVEREIGN RUNTIME CONFIGURATION
            </span>
            <span className="text-gaming-slate">
              Built-In Qualcomm NPU Hardware Controller • 100% Offline &amp; Air-Gapped
            </span>
          </div>
          <h1 className="font-headline-lg text-headline-lg text-gaming-white font-bold tracking-tight">
            COGNIEGDE SYSTEM &amp; OVERLAY SETTINGS
          </h1>
          <p className="font-body-md text-body-md text-gaming-slate mt-0.5">
            All AI models (Qwen3-4B INT4, YOLO26-N, Whisper ONNX) execute from on-device local storage. Zero cloud dependency.
          </p>
        </div>

        <button
          onClick={handleSave}
          disabled={loading}
          className="px-space-lg py-space-sm bg-gaming-red text-white font-headline-sm text-label-lg rounded-lg shadow-[0_0_18px_rgba(255,0,56,0.5)] hover:shadow-[0_0_26px_rgba(255,0,56,0.75)] hover:bg-gaming-red-bright transition-all font-bold cursor-pointer flex items-center gap-2 self-start md:self-auto"
        >
          <span className="material-symbols-outlined text-[20px]">{saved ? 'check_circle' : 'save'}</span>
          <span>{saved ? 'SETTINGS SAVED!' : 'SAVE SETTINGS'}</span>
        </button>
      </div>

      {/* Embedded Model Engine Manifest */}
      <section className="bg-gaming-panel rounded-2xl p-space-lg shadow-2xl border border-gaming-border flex flex-col gap-space-md clip-chamfer-sm">
        <div className="flex items-center justify-between pb-3 border-b border-gaming-border">
          <div className="flex items-center gap-space-xs">
            <span className="material-symbols-outlined text-gaming-red text-[20px]">developer_board</span>
            <h2 className="font-headline-sm text-headline-sm text-gaming-white font-bold">
              Built-In On-Device AI Model Enclave
            </h2>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-gaming-carbon text-emerald-400 border border-emerald-500/30 font-bold">
            100% AIR-GAPPED // ZERO CLOUD
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-space-md font-mono text-xs">
          <div className="p-3.5 rounded-xl bg-gaming-carbon border border-gaming-border space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-gaming-slate text-[10px] uppercase">Tactical Reasoning</span>
              <span className="text-emerald-400 text-[10px] font-bold">ACTIVE</span>
            </div>
            <span className="text-gaming-white font-bold text-sm block">Qwen3-4B INT4</span>
            <span className="text-[11px] text-gaming-slate">Snapdragon Hexagon NPU</span>
          </div>

          <div className="p-3.5 rounded-xl bg-gaming-carbon border border-gaming-border space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-gaming-slate text-[10px] uppercase">Vision OCR / Bounding</span>
              <span className="text-emerald-400 text-[10px] font-bold">ACTIVE</span>
            </div>
            <span className="text-gaming-white font-bold text-sm block">YOLO26-N Vision</span>
            <span className="text-[11px] text-gaming-slate">60 FPS Direct3D Surface Hook</span>
          </div>

          <div className="p-3.5 rounded-xl bg-gaming-carbon border border-gaming-border space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-gaming-slate text-[10px] uppercase">Voice Recognition</span>
              <span className="text-emerald-400 text-[10px] font-bold">ACTIVE</span>
            </div>
            <span className="text-gaming-white font-bold text-sm block">Whisper ONNX</span>
            <span className="text-[11px] text-gaming-slate">Sub-20ms Beamforming Mic</span>
          </div>

          <div className="p-3.5 rounded-xl bg-gaming-carbon border border-gaming-border space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-gaming-slate text-[10px] uppercase">Player Habit DB</span>
              <span className="text-emerald-400 text-[10px] font-bold">ACTIVE</span>
            </div>
            <span className="text-gaming-white font-bold text-sm block">SQLite Enclave</span>
            <span className="text-[11px] text-gaming-slate">Local File: cogniedge.db</span>
          </div>
        </div>
      </section>

      {/* Settings Options Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-space-lg">
        {/* HUD & Overlay Hotkeys */}
        <section className="bg-gaming-panel rounded-2xl p-space-lg shadow-2xl border border-gaming-border space-y-4 clip-chamfer-sm">
          <div className="flex items-center gap-space-xs pb-3 border-b border-gaming-border">
            <span className="material-symbols-outlined text-gaming-red text-[20px]">sports_esports</span>
            <h2 className="font-headline-sm text-headline-sm text-gaming-white font-bold">
              HUD Overlay &amp; Hotkey Controls
            </h2>
          </div>

          <div className="space-y-3 font-mono text-xs">
            <div>
              <label className="text-gaming-slate uppercase text-[10px] block mb-1">
                Toggle Live HUD Overlay Hotkey
              </label>
              <input
                type="text"
                value={settings.overlay_hotkey}
                onChange={(e) => setSettings({ ...settings, overlay_hotkey: e.target.value })}
                className="w-full py-2 px-3 rounded-lg bg-gaming-carbon border border-gaming-border text-gaming-white font-bold focus:outline-none focus:border-gaming-red"
              />
            </div>

            <div>
              <label className="text-gaming-slate uppercase text-[10px] block mb-1">
                Push-to-Talk Tactical Voice Hotkey
              </label>
              <input
                type="text"
                value={settings.ptt_hotkey}
                onChange={(e) => setSettings({ ...settings, ptt_hotkey: e.target.value })}
                className="w-full py-2 px-3 rounded-lg bg-gaming-carbon border border-gaming-border text-gaming-white font-bold focus:outline-none focus:border-gaming-red"
              />
            </div>

            <div>
              <div className="flex items-center justify-between text-gaming-slate mb-1">
                <span className="uppercase text-[10px]">HUD Transparency Opacity</span>
                <span className="text-gaming-white font-bold">{Math.round(settings.overlay_opacity * 100)}%</span>
              </div>
              <input
                type="range"
                min="0.5"
                max="1.0"
                step="0.05"
                value={settings.overlay_opacity}
                onChange={(e) => setSettings({ ...settings, overlay_opacity: parseFloat(e.target.value) })}
                className="w-full accent-[#ff0038] cursor-pointer"
              />
            </div>

            <div className="flex items-center justify-between pt-2 border-t border-gaming-border">
              <span className="text-gaming-white">Click-Through Zero-Input Interception</span>
              <input
                type="checkbox"
                checked={settings.click_through_hud}
                onChange={(e) => setSettings({ ...settings, click_through_hud: e.target.checked })}
                className="w-4 h-4 accent-[#ff0038] cursor-pointer"
              />
            </div>
          </div>
        </section>

        {/* NPU Telemetry & Frame Guard */}
        <section className="bg-gaming-panel rounded-2xl p-space-lg shadow-2xl border border-gaming-border space-y-4 clip-chamfer-sm">
          <div className="flex items-center gap-space-xs pb-3 border-b border-gaming-border">
            <span className="material-symbols-outlined text-gaming-red text-[20px]">troubleshoot</span>
            <h2 className="font-headline-sm text-headline-sm text-gaming-white font-bold">
              AI Performance Guard &amp; Telemetry
            </h2>
          </div>

          <div className="space-y-3 font-mono text-xs">
            <div>
              <label className="text-gaming-slate uppercase text-[10px] block mb-1">
                Hexagon NPU Execution Power Mode
              </label>
              <select
                value={settings.npu_isolation_mode}
                onChange={(e) => setSettings({ ...settings, npu_isolation_mode: e.target.value })}
                className="w-full py-2 px-3 rounded-lg bg-gaming-carbon border border-gaming-border text-gaming-white font-bold focus:outline-none focus:border-gaming-red"
              >
                <option value="Hexagon_NPU_Turbo">Hexagon NPU Turbo (Zero GPU Drop, 80 TOPS)</option>
                <option value="Hexagon_NPU_Balanced">Hexagon NPU Balanced (Power Efficiency)</option>
              </select>
            </div>

            <div className="flex items-center justify-between pt-2">
              <div>
                <span className="text-gaming-white block font-bold">Predictive Stutter Detection</span>
                <span className="text-[11px] text-gaming-slate font-sans">
                  Forecasts frame time variance spikes 1500ms ahead
                </span>
              </div>
              <input
                type="checkbox"
                checked={settings.predictive_stutter_enabled}
                onChange={(e) => setSettings({ ...settings, predictive_stutter_enabled: e.target.checked })}
                className="w-4 h-4 accent-[#ff0038] cursor-pointer"
              />
            </div>

            <div className="pt-3 border-t border-gaming-border flex items-center justify-between">
              <div>
                <span className="text-gaming-white block font-bold">SQLite Session Database</span>
                <span className="text-[11px] text-gaming-slate font-sans">
                  Reset habit mining cache &amp; advice logs
                </span>
              </div>
              <button
                type="button"
                onClick={handleClearMemory}
                className="px-3 py-1.5 rounded bg-gaming-carbon hover:bg-gaming-red hover:text-white text-gaming-slate border border-gaming-border transition-colors text-[11px] font-bold cursor-pointer"
              >
                Reset DB
              </button>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
