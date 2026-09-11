import React from 'react';
import { clsx } from 'clsx';

interface MetricCardProps {
  label: string;
  value: string | number;
  subValue?: string;
  subColor?: string;
  trend?: 'up' | 'down' | 'neutral';
  provenance?: 'MEASURED' | 'ESTIMATED' | 'REFERENCE' | 'DEMO' | 'UNAVAILABLE';
  icon?: React.ReactNode;
  highlight?: boolean;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  subValue,
  subColor = 'text-gaming-slate',
  provenance = 'MEASURED',
  icon,
  highlight = false,
}) => {
  const getProvenanceBadge = () => {
    switch (provenance) {
      case 'MEASURED':
        return <span className="text-[9px] font-mono font-semibold px-1.5 py-0.5 rounded bg-gaming-panel-highest text-gaming-red-bright border border-gaming-red/30">MEASURED</span>;
      case 'DEMO':
        return <span className="text-[9px] font-mono font-semibold px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/30">DEMO</span>;
      case 'ESTIMATED':
        return <span className="text-[9px] font-mono font-semibold px-1.5 py-0.5 rounded bg-purple-500/20 text-purple-400 border border-purple-500/30">ESTIMATED</span>;
      case 'REFERENCE':
        return <span className="text-[9px] font-mono font-semibold px-1.5 py-0.5 rounded bg-slate-500/20 text-slate-400 border border-slate-500/30">REFERENCE</span>;
      default:
        return null;
    }
  };

  return (
    <div
      className={clsx(
        'relative p-4 rounded-xl border transition-all duration-200 clip-chamfer-sm',
        highlight
          ? 'bg-gaming-panel border-gaming-red shadow-[0_0_20px_rgba(255,0,56,0.25)] laser-border-left'
          : 'bg-gaming-panel border-gaming-border hover:border-gaming-red/40'
      )}
    >
      <div className="flex items-center justify-between gap-2 mb-2">
        <span className="text-[11px] font-mono tracking-wider uppercase text-gaming-slate flex items-center gap-1.5">
          {icon && <span className="text-gaming-red">{icon}</span>}
          {label}
        </span>
        {getProvenanceBadge()}
      </div>

      <div className="flex items-baseline gap-2">
        <span className="text-2xl font-bold font-mono text-gaming-white tracking-tight">
          {value}
        </span>
      </div>

      {subValue && (
        <div className={clsx('text-xs mt-1.5 font-mono flex items-center gap-1', subColor)}>
          {subValue}
        </div>
      )}
    </div>
  );
};
