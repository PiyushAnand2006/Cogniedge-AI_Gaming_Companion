import React from 'react';
import { clsx } from 'clsx';

interface RiskIndicatorProps {
  probability: number;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  windowMs?: number;
  factors?: string[];
}

export const RiskIndicator: React.FC<RiskIndicatorProps> = ({
  probability,
  riskLevel,
  windowMs = 1500,
  factors = [],
}) => {
  const getRiskStyle = () => {
    switch (riskLevel) {
      case 'critical':
        return {
          barColor: 'bg-gaming-red',
          textColor: 'text-gaming-red-bright',
          bgColor: 'bg-gaming-red/20',
          borderColor: 'border-gaming-red',
          label: 'CRITICAL STUTTER RISK',
        };
      case 'high':
        return {
          barColor: 'bg-gaming-red',
          textColor: 'text-gaming-red-bright',
          bgColor: 'bg-gaming-red/15',
          borderColor: 'border-gaming-red/50',
          label: 'HIGH STUTTER RISK',
        };
      case 'medium':
        return {
          barColor: 'bg-amber-500',
          textColor: 'text-amber-400',
          bgColor: 'bg-amber-500/10',
          borderColor: 'border-amber-500/40',
          label: 'MODERATE RISK',
        };
      default:
        return {
          barColor: 'bg-emerald-500',
          textColor: 'text-emerald-400',
          bgColor: 'bg-emerald-500/10',
          borderColor: 'border-emerald-500/30',
          label: 'LOW RISK / SMOOTH',
        };
    }
  };

  const style = getRiskStyle();

  return (
    <div className={clsx('p-4 rounded-xl border bg-gaming-panel space-y-3 clip-chamfer-sm', style.borderColor)}>
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-mono tracking-wider uppercase text-gaming-slate flex items-center gap-1.5">
          <span className="material-symbols-outlined text-gaming-red text-[16px]">radar</span>
          Predictive Stutter Risk (Next {windowMs}ms)
        </span>
        <span className={clsx('text-[10px] font-mono font-bold px-2 py-0.5 rounded', style.bgColor, style.textColor)}>
          {style.label}
        </span>
      </div>

      <div className="flex items-baseline justify-between font-mono">
        <span className="text-3xl font-bold text-gaming-white tracking-tight">
          {(probability * 100).toFixed(0)}%
        </span>
        <span className="text-xs text-gaming-slate">
          Stutter probability window
        </span>
      </div>

      <div className="w-full h-2 bg-gaming-panel-highest rounded-full overflow-hidden border border-gaming-border/40">
        <div
          className={clsx('h-full rounded-full transition-all duration-300', style.barColor)}
          style={{ width: `${Math.min(probability * 100, 100)}%` }}
        />
      </div>

      {factors.length > 0 && (
        <div className="pt-2 border-t border-gaming-border space-y-1">
          <span className="text-[10px] font-mono uppercase text-gaming-slate block">Contributing Risk Factors:</span>
          <div className="flex flex-wrap gap-1">
            {factors.map((f, i) => (
              <span key={i} className="text-[10px] font-mono px-2 py-0.5 rounded bg-gaming-carbon text-gaming-slate border border-gaming-border">
                {f}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
