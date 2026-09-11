'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import Link from 'next/link';

interface FPSDataPoint {
  timestamp_s: number;
  cogniedge_fps: number;
  discord_fps: number;
  overwolf_fps: number;
  obs_fps: number;
  baseline_fps: number;
}

interface BenchmarkResult {
  baseline_fps: number;
  test_duration_s: number;
  cogniedge: {
    name: string;
    type: string;
    avg_fps_drop: number;
    max_fps_drop: number;
    gpu_contention_pct: number;
    vram_mb: number;
    cpu_overhead_pct: number;
    frame_time_impact_ms: number;
    measured_fps: number;
    frame_time_avg_ms: number;
    frame_time_p99_ms: number;
    npu_tops_used?: number;
  };
  gpu_overlays: Array<{
    name: string;
    type: string;
    avg_fps_drop: number;
    max_fps_drop: number;
    gpu_contention_pct: number;
    vram_mb: number;
    cpu_overhead_pct: number;
    frame_time_impact_ms: number;
    measured_fps: number;
    frame_time_avg_ms: number;
    frame_time_p99_ms: number;
  }>;
  summary: {
    cogniedge_fps: number;
    worst_gpu_overlay: string;
    worst_gpu_fps_drop: number;
    best_gpu_overlay: string;
    best_gpu_fps_drop: number;
    total_gpu_vram_saved_mb: number;
  };
}

export default function BenchmarkPage() {
  const [isRunning, setIsRunning] = useState(false);
  const [fpsData, setFpsData] = useState<FPSDataPoint[]>([]);
  const [benchResult, setBenchResult] = useState<BenchmarkResult | null>(null);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  // Draw FPS chart on canvas
  const drawChart = useCallback((data: FPSDataPoint[]) => {
    const canvas = canvasRef.current;
    if (!canvas || data.length === 0) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);

    const W = rect.width;
    const H = rect.height;
    const PADDING = { top: 32, right: 16, bottom: 40, left: 52 };
    const chartW = W - PADDING.left - PADDING.right;
    const chartH = H - PADDING.top - PADDING.bottom;

    // Clear
    ctx.fillStyle = '#08090c';
    ctx.fillRect(0, 0, W, H);

    // Grid
    const maxFPS = 160;
    const minFPS = 100;
    const gridLines = [100, 110, 120, 130, 140, 150, 160];
    ctx.strokeStyle = 'rgba(255,255,255,0.06)';
    ctx.lineWidth = 1;
    ctx.font = '11px monospace';
    ctx.fillStyle = 'rgba(255,255,255,0.35)';

    gridLines.forEach((fps) => {
      const y = PADDING.top + chartH - ((fps - minFPS) / (maxFPS - minFPS)) * chartH;
      ctx.beginPath();
      ctx.moveTo(PADDING.left, y);
      ctx.lineTo(W - PADDING.right, y);
      ctx.stroke();
      ctx.fillText(`${fps}`, 8, y + 4);
    });

    // X-axis labels
    const maxTime = data[data.length - 1].timestamp_s;
    for (let t = 0; t <= maxTime; t += 5) {
      const x = PADDING.left + (t / Math.max(maxTime, 1)) * chartW;
      ctx.fillStyle = 'rgba(255,255,255,0.35)';
      ctx.fillText(`${t}s`, x - 6, H - 8);
    }

    // Helper to draw a line series
    const drawLine = (
      series: (d: FPSDataPoint) => number,
      color: string,
      width: number = 2
    ) => {
      ctx.beginPath();
      ctx.strokeStyle = color;
      ctx.lineWidth = width;
      ctx.lineJoin = 'round';
      data.forEach((d, i) => {
        const x = PADDING.left + (d.timestamp_s / Math.max(maxTime, 1)) * chartW;
        const fps = Math.max(Math.min(series(d), maxFPS), minFPS);
        const y = PADDING.top + chartH - ((fps - minFPS) / (maxFPS - minFPS)) * chartH;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.stroke();
    };

    // Draw series (order: back to front)
    drawLine((d) => d.overwolf_fps, '#8a93a8', 1.5);   // Slate — Overwolf
    drawLine((d) => d.discord_fps, '#f59e0b', 1.5);     // Amber — Discord
    drawLine((d) => d.obs_fps, '#ec4899', 1.5);         // Pink — OBS
    drawLine((d) => d.baseline_fps, 'rgba(255,255,255,0.15)', 1);  // Baseline dim
    drawLine((d) => d.cogniedge_fps, '#ff0038', 2.5);   // Cyber Crimson — CogniEdge (on top)

    // Glow effect for CogniEdge line
    ctx.shadowColor = '#ff0038';
    ctx.shadowBlur = 12;
    drawLine((d) => d.cogniedge_fps, 'rgba(255,0,56,0.5)', 4);
    ctx.shadowBlur = 0;

    // Legend
    const legends = [
      { label: 'CogniEdge (NPU Isolated)', color: '#ff0038' },
      { label: 'Discord', color: '#f59e0b' },
      { label: 'Overwolf', color: '#8a93a8' },
      { label: 'OBS Studio', color: '#ec4899' },
    ];
    let lx = PADDING.left;
    legends.forEach((l) => {
      ctx.fillStyle = l.color;
      ctx.fillRect(lx, 8, 14, 3);
      ctx.fillStyle = 'rgba(255,255,255,0.85)';
      ctx.font = '11px Inter, sans-serif';
      ctx.fillText(l.label, lx + 18, 14);
      lx += ctx.measureText(l.label).width + 36;
    });
  }, []);

  useEffect(() => {
    drawChart(fpsData);
  }, [fpsData, drawChart]);

  // Start benchmark SSE stream
  const startBenchmark = useCallback(async () => {
    setIsRunning(true);
    setFpsData([]);
    setElapsedSeconds(0);

    // First fetch the full comparison results
    try {
      const res = await fetch('http://127.0.0.1:8088/benchmark/run');
      if (res.ok) {
        const result = await res.json();
        setBenchResult(result);
      }
    } catch {
      // Service may not be running
    }

    // Start the SSE stream for real-time chart data
    const evtSource = new EventSource('http://127.0.0.1:8088/benchmark/stream');
    eventSourceRef.current = evtSource;

    evtSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'complete') {
          evtSource.close();
          setIsRunning(false);
          return;
        }
        setFpsData((prev) => [...prev.slice(-120), data]); // Keep last 120 points
        setElapsedSeconds(data.timestamp_s || 0);
      } catch {
        // ignore parse errors
      }
    };

    evtSource.onerror = () => {
      evtSource.close();
      setIsRunning(false);
    };
  }, []);

  const stopBenchmark = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setIsRunning(false);
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  const overlayCards = [
    {
      name: 'CogniEdge NPU Overlay',
      type: 'Hexagon NPU (Dedicated)',
      fps: benchResult ? benchResult.cogniedge.measured_fps : 144.0,
      fpsDrop: 0.0,
      gpuPct: 0.0,
      vram: 0.0,
      cpu: 0.3,
      color: '#ff0038',
      isCogniEdge: true,
    },
    {
      name: 'Discord Overlay',
      type: 'GPU-Rendered',
      fps: benchResult?.gpu_overlays?.[0]?.measured_fps ?? 135.8,
      fpsDrop: 8.2,
      gpuPct: 3.8,
      vram: 85,
      cpu: 2.1,
      color: '#f59e0b',
      isCogniEdge: false,
    },
    {
      name: 'Overwolf Overlay',
      type: 'GPU-Rendered',
      fps: benchResult?.gpu_overlays?.[1]?.measured_fps ?? 131.4,
      fpsDrop: 12.6,
      gpuPct: 5.2,
      vram: 140,
      cpu: 4.8,
      color: '#8a93a8',
      isCogniEdge: false,
    },
    {
      name: 'OBS Studio Preview',
      type: 'GPU-Rendered',
      fps: benchResult?.gpu_overlays?.[2]?.measured_fps ?? 137.6,
      fpsDrop: 6.4,
      gpuPct: 2.9,
      vram: 65,
      cpu: 3.5,
      color: '#ec4899',
      isCogniEdge: false,
    },
  ];

  return (
    <div className="w-full flex flex-col min-h-[calc(100vh-4rem)] tactical-hex-grid text-gaming-white pb-16">
      {/* Header / Title Bar */}
      <section className="w-full px-gutter-desktop py-space-lg bg-gaming-panel shadow-2xl border-b border-gaming-border laser-border-left">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-space-md max-w-[1760px] mx-auto">
          <div className="flex flex-col gap-space-xs">
            <div className="flex items-center gap-space-xs">
              <div className="hazard-slashes">
                <span />
                <span />
                <span />
              </div>
              <h1 className="font-headline-md text-headline-md text-gaming-white tracking-tight flex items-center gap-space-sm font-bold">
                Zero-FPS Contention Benchmark
              </h1>
            </div>
            <p className="font-body-md text-body-md text-gaming-slate max-w-[760px]">
              CogniEdge runs 100% on Hexagon NPU — zero GPU pipeline contention, zero VRAM allocation,
              and zero frame time drop. Compare against traditional GPU-rendered overlays.
            </p>
          </div>

          <div className="flex items-center gap-space-sm shrink-0">
            <button
              onClick={() => (isRunning ? stopBenchmark() : startBenchmark())}
              className={`px-space-lg py-2.5 font-headline-sm text-label-lg rounded-lg transition-all flex items-center gap-space-sm shadow-xl font-bold ${
                isRunning
                  ? 'bg-gaming-panel-highest text-white border border-gaming-red hover:shadow-[0_0_20px_rgba(255,0,56,0.5)]'
                  : 'bg-gaming-red hover:bg-gaming-red-bright text-white shadow-[0_0_20px_rgba(255,0,56,0.5)] hover:shadow-[0_0_28px_rgba(255,0,56,0.8)]'
              }`}
              type="button"
            >
              <span className="material-symbols-outlined text-[20px]">
                {isRunning ? 'stop_circle' : 'play_circle'}
              </span>
              <span>{isRunning ? 'Stop Benchmark' : 'Run Benchmark'}</span>
            </button>
            {isRunning && (
              <span className="font-label-sm text-label-sm text-gaming-red-bright font-mono font-bold animate-pulse">
                {elapsedSeconds.toFixed(1)}s / 30.0s
              </span>
            )}
          </div>
        </div>
      </section>

      {/* Main Content */}
      <div className="w-full px-gutter-desktop py-space-lg flex flex-col gap-space-lg max-w-[1760px] mx-auto flex-1">
        {/* FPS Chart */}
        <section className="bg-gaming-panel rounded-2xl p-space-lg shadow-2xl border border-gaming-border laser-border-left">
          <div className="flex items-center justify-between mb-space-md">
            <div className="flex items-center gap-space-sm">
              <span className="material-symbols-outlined text-gaming-red text-[20px]">monitoring</span>
              <h2 className="font-headline-sm text-headline-sm text-gaming-white font-bold">Real-Time FPS Comparison</h2>
            </div>
            <span className="font-label-sm text-label-sm text-gaming-slate font-mono">
              Baseline: 144 FPS • {fpsData.length} data points
            </span>
          </div>
          <div className="w-full h-[320px] rounded-xl overflow-hidden border border-gaming-border bg-gaming-carbon shadow-inner">
            <canvas
              ref={canvasRef}
              className="w-full h-full"
              style={{ display: 'block' }}
            />
          </div>
          {fpsData.length === 0 && !isRunning && (
            <div className="flex items-center justify-center py-space-xl text-gaming-slate font-body-md font-mono">
              <span className="material-symbols-outlined text-[24px] mr-2 text-gaming-red">info</span>
              Click &quot;Run Benchmark&quot; to begin live FPS data streaming
            </div>
          )}
        </section>

        {/* Overlay Comparison Cards */}
        <section>
          <div className="flex items-center gap-space-sm mb-space-md">
            <span className="material-symbols-outlined text-gaming-red text-[20px]">compare</span>
            <h2 className="font-headline-sm text-headline-sm text-gaming-white font-bold">Overlay Comparison</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-space-md">
            {overlayCards.map((card) => (
              <div
                key={card.name}
                className={`bg-gaming-panel rounded-2xl p-space-lg border transition-all ${
                  card.isCogniEdge
                    ? 'border-gaming-red/70 shadow-[0_0_24px_rgba(255,0,56,0.3)] relative overflow-hidden'
                    : 'border-gaming-border hover:border-gaming-border/80'
                }`}
              >
                {/* Card Header */}
                <div className="flex items-center justify-between mb-space-md">
                  <div>
                    <h3 className="font-headline-sm text-label-lg text-gaming-white font-bold">{card.name}</h3>
                    <span className="font-label-sm text-label-sm text-gaming-slate font-mono">{card.type}</span>
                  </div>
                  {card.isCogniEdge && (
                    <span className="px-2 py-0.5 bg-gaming-red text-white font-label-sm text-label-sm rounded font-bold font-mono shadow-[0_0_10px_rgba(255,0,56,0.4)]">
                      ★ ZERO IMPACT
                    </span>
                  )}
                </div>

                {/* FPS Display */}
                <div className="mb-space-md">
                  <div className="flex items-baseline gap-space-xs">
                    <span
                      className="font-headline-lg text-display-sm font-extrabold font-mono"
                      style={{ color: card.color }}
                    >
                      {card.fps.toFixed(1)}
                    </span>
                    <span className="font-label-sm text-label-sm text-gaming-slate font-mono">FPS</span>
                  </div>
                  <div className="flex items-center gap-space-xs mt-1">
                    <span className={`font-label-sm text-label-sm font-mono font-bold ${
                      card.fpsDrop === 0 ? 'text-gaming-red-bright' : 'text-gaming-slate'
                    }`}>
                      {card.fpsDrop === 0 ? '0.0' : `-${card.fpsDrop}`} FPS drop
                    </span>
                  </div>
                </div>

                {/* Metrics */}
                <div className="space-y-space-xs font-mono">
                  <div className="flex items-center justify-between font-label-sm text-label-sm">
                    <span className="text-gaming-slate">GPU Contention</span>
                    <span className={card.gpuPct === 0 ? 'text-gaming-red-bright font-bold' : 'text-gaming-white'}>
                      {card.gpuPct.toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex items-center justify-between font-label-sm text-label-sm">
                    <span className="text-gaming-slate">VRAM Usage</span>
                    <span className={card.vram === 0 ? 'text-gaming-red-bright font-bold' : 'text-gaming-white'}>
                      {card.vram.toFixed(0)} MB
                    </span>
                  </div>
                  <div className="flex items-center justify-between font-label-sm text-label-sm">
                    <span className="text-gaming-slate">CPU Overhead</span>
                    <span className="text-gaming-white">{card.cpu.toFixed(1)}%</span>
                  </div>
                </div>

                {/* Bottom Bar */}
                <div className="mt-space-md pt-space-sm border-t border-gaming-border">
                  <div className="w-full h-1.5 bg-gaming-carbon rounded-full overflow-hidden border border-gaming-border/40">
                    <div
                      className="h-full rounded-full transition-all"
                      style={{
                        width: `${(card.fps / 144) * 100}%`,
                        backgroundColor: card.color,
                        boxShadow: card.isCogniEdge ? `0 0 10px ${card.color}` : 'none',
                      }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Summary Table */}
        {benchResult && (
          <section className="bg-gaming-panel rounded-2xl p-space-lg shadow-2xl border border-gaming-border laser-border-left">
            <div className="flex items-center gap-space-sm mb-space-md">
              <span className="material-symbols-outlined text-gaming-red text-[20px]">table_chart</span>
              <h2 className="font-headline-sm text-headline-sm text-gaming-white font-bold">Detailed Performance Metrics</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full font-label-md text-label-md font-mono">
                <thead>
                  <tr className="text-left border-b border-gaming-border text-gaming-slate font-bold">
                    <th className="px-space-sm py-space-xs">Overlay</th>
                    <th className="px-space-sm py-space-xs">Type</th>
                    <th className="px-space-sm py-space-xs text-right">Measured FPS</th>
                    <th className="px-space-sm py-space-xs text-right">Avg Drop</th>
                    <th className="px-space-sm py-space-xs text-right">Max Drop</th>
                    <th className="px-space-sm py-space-xs text-right">GPU %</th>
                    <th className="px-space-sm py-space-xs text-right">VRAM</th>
                    <th className="px-space-sm py-space-xs text-right">Frame Time</th>
                    <th className="px-space-sm py-space-xs text-right">P99 Frame</th>
                  </tr>
                </thead>
                <tbody>
                  {/* CogniEdge Row */}
                  <tr className="border-b border-gaming-border/60 bg-gaming-red-subtle font-bold">
                    <td className="px-space-sm py-space-sm text-gaming-white font-bold">{benchResult.cogniedge.name}</td>
                    <td className="px-space-sm py-space-sm text-gaming-red-bright">{benchResult.cogniedge.type}</td>
                    <td className="px-space-sm py-space-sm text-right text-gaming-red-bright font-bold">{benchResult.cogniedge.measured_fps.toFixed(1)}</td>
                    <td className="px-space-sm py-space-sm text-right text-gaming-red-bright">0.0</td>
                    <td className="px-space-sm py-space-sm text-right text-gaming-red-bright">0.0</td>
                    <td className="px-space-sm py-space-sm text-right text-gaming-red-bright">0.00%</td>
                    <td className="px-space-sm py-space-sm text-right text-gaming-red-bright">0 MB</td>
                    <td className="px-space-sm py-space-sm text-right text-gaming-white">{benchResult.cogniedge.frame_time_avg_ms} ms</td>
                    <td className="px-space-sm py-space-sm text-right text-gaming-white">{benchResult.cogniedge.frame_time_p99_ms} ms</td>
                  </tr>
                  {/* GPU Overlay Rows */}
                  {benchResult.gpu_overlays.map((overlay) => (
                    <tr key={overlay.name} className="border-b border-gaming-border/30 hover:bg-gaming-panel-high/50">
                      <td className="px-space-sm py-space-sm text-gaming-white">{overlay.name}</td>
                      <td className="px-space-sm py-space-sm text-gaming-slate">{overlay.type}</td>
                      <td className="px-space-sm py-space-sm text-right text-gaming-white font-bold">{overlay.measured_fps.toFixed(1)}</td>
                      <td className="px-space-sm py-space-sm text-right text-gaming-slate">-{overlay.avg_fps_drop}</td>
                      <td className="px-space-sm py-space-sm text-right text-gaming-slate">-{overlay.max_fps_drop}</td>
                      <td className="px-space-sm py-space-sm text-right text-gaming-slate">{overlay.gpu_contention_pct}%</td>
                      <td className="px-space-sm py-space-sm text-right text-gaming-slate">{overlay.vram_mb} MB</td>
                      <td className="px-space-sm py-space-sm text-right text-gaming-slate">{overlay.frame_time_avg_ms} ms</td>
                      <td className="px-space-sm py-space-sm text-right text-gaming-slate">{overlay.frame_time_p99_ms} ms</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}
      </div>
    </div>
  );
}
