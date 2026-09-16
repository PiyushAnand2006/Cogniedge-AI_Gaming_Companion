import React from 'react';
import { clsx } from 'clsx';

interface MemoryPatternCardProps {
  id: string;
  patternType: 'tactical_habit' | 'performance_correlation' | 'stutter_trigger' | 'weapon_recoil';
  name: string;
  description: string;
  occurrences: number;
  confidence: number;
  impactScore: number;
  recommendation: string;
}

export const MemoryPatternCard: React.FC<MemoryPatternCardProps> = React.memo(({
  patternType,
  name,
  description,
  occurrences,
  confidence,
  impactScore,
  recommendation,
}) => {
  return (
    <div className="p-4 rounded-xl bg-gaming-panel border border-gaming-border hover:border-gaming-red/40 transition-all clip-chamfer-sm space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-gaming-red text-[18px]">psychology</span>
          <span className="text-sm font-headline-sm font-bold text-gaming-white">{name}</span>
        </div>
        <span className="text-[10px] font-mono font-medium px-2 py-0.5 rounded bg-gaming-carbon text-gaming-slate border border-gaming-border uppercase">
          {patternType.replace(/_/g, ' ')}
        </span>
      </div>

      <p className="text-xs text-gaming-slate leading-relaxed font-normal">
        {description}
      </p>

      <div className="grid grid-cols-3 gap-2 p-2 rounded-lg bg-gaming-carbon border border-gaming-border text-center font-mono">
        <div>
          <span className="text-[9px] uppercase text-gaming-slate block font-medium">Observations</span>
          <span className="text-xs font-bold text-gaming-white">{occurrences}x</span>
        </div>
        <div>
          <span className="text-[9px] uppercase text-gaming-slate block font-medium">Confidence</span>
          <span className="text-xs font-bold text-gaming-red-bright">{(confidence * 100).toFixed(0)}%</span>
        </div>
        <div>
          <span className="text-[9px] uppercase text-gaming-slate block font-medium">Impact</span>
          <span className="text-xs font-bold text-amber-400">{impactScore.toFixed(1)}/10</span>
        </div>
      </div>

      <div className="p-2.5 rounded-lg bg-gaming-carbon/80 border border-gaming-red/20 space-y-1">
        <span className="text-[10px] font-mono font-medium text-emerald-400 uppercase flex items-center gap-1">
          <span className="material-symbols-outlined text-[13px]">lightbulb</span>
          Strategic Counter-Play:
        </span>
        <p className="text-[11px] text-gaming-white leading-relaxed font-normal">
          {recommendation}
        </p>
      </div>
    </div>
  );
});

MemoryPatternCard.displayName = 'MemoryPatternCard';
