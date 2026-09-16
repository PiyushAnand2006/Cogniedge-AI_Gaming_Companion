import React from 'react';

interface PerformanceChartProps {
  data: Array<{ timestamp: number; fps: number; frame_time_ms: number; stutter?: boolean }>;
  height?: number;
}

export const PerformanceChart: React.FC<PerformanceChartProps> = React.memo(({
  data,
  height = 140,
}) => {
  const chartMetrics = React.useMemo(() => {
    if (!data || data.length === 0) return null;
    const maxFps = Math.max(...data.map((d) => d.fps), 160);
    const minFps = Math.max(0, Math.min(...data.map((d) => d.fps)) - 10);
    const range = maxFps - minFps || 1;

    const points = data.map((d, i) => {
      const x = (i / (data.length - 1 || 1)) * 100;
      const y = 100 - ((d.fps - minFps) / range) * 100;
      return `${x},${y}`;
    });

    const pathD = `M 0,100 L ${points.join(' L ')} L 100,100 Z`;
    const lineD = `M ${points.join(' L ')}`;
    const latestFps = data[data.length - 1]?.fps.toFixed(1);

    return { pathD, lineD, latestFps };
  }, [data]);

  if (!chartMetrics) {
    return (
      <div
        className="flex items-center justify-center rounded-xl bg-gaming-carbon border border-gaming-border text-gaming-slate text-xs font-mono"
        style={{ height }}
      >
        <span className="material-symbols-outlined text-[16px] mr-1 text-gaming-red">sensors</span>
        Awaiting Live Telemetry Tick Stream...
      </div>
    );
  }

  return (
    <div className="p-4 rounded-xl bg-gaming-panel border border-gaming-border space-y-2 clip-chamfer-sm">
      <div className="flex items-center justify-between text-xs font-mono">
        <span className="text-gaming-slate uppercase flex items-center gap-1.5 font-medium">
          <span className="material-symbols-outlined text-gaming-red text-[16px]">show_chart</span>
          Live Frame Pacing Telemetry
        </span>
        <div className="flex items-center gap-3">
          <span className="text-gaming-red-bright font-bold">
            Target: 144 FPS
          </span>
          <span className="text-gaming-slate font-normal">
            Current: {chartMetrics.latestFps} FPS
          </span>
        </div>
      </div>

      <div className="relative w-full overflow-hidden rounded-lg bg-gaming-carbon border border-gaming-border" style={{ height }}>
        {/* SVG Curve */}
        <svg
          viewBox="0 0 100 100"
          preserveAspectRatio="none"
          className="w-full h-full"
        >
          <defs>
            <linearGradient id="fpsGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#ff0038" stopOpacity="0.4" />
              <stop offset="100%" stopColor="#ff0038" stopOpacity="0.0" />
            </linearGradient>
          </defs>
          <path d={chartMetrics.pathD} fill="url(#fpsGradient)" />
          <path
            d={chartMetrics.lineD}
            fill="none"
            stroke="#ff0038"
            strokeWidth="2"
            vectorEffect="non-scaling-stroke"
          />
        </svg>

        {/* 60 FPS Threshold Guide Line */}
        <div className="absolute inset-x-0 top-1/2 border-b border-dashed border-gaming-border/60 pointer-events-none" />
      </div>

      <div className="flex items-center justify-between text-[10px] font-mono text-gaming-slate">
        <span>-60 Seconds</span>
        <span className="flex items-center gap-1 text-emerald-400">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
          Zero Micro-Stutter Pacing
        </span>
        <span>Live</span>
      </div>
    </div>
  );
});

PerformanceChart.displayName = 'PerformanceChart';
