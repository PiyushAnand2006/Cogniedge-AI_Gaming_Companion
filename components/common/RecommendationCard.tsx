import React from 'react';
import { clsx } from 'clsx';

interface RecommendationCardProps {
  id: string;
  category: 'graphics' | 'cpu' | 'display' | 'system';
  settingName: string;
  currentValue: string;
  recommendedValue: string;
  expectedFpsGain: number;
  expectedStabilityGain: string;
  riskLevel: 'safe' | 'moderate' | 'advanced';
  applied?: boolean;
  onApply?: (id: string) => void;
}

export const RecommendationCard: React.FC<RecommendationCardProps> = React.memo(({
  id,
  category,
  settingName,
  currentValue,
  recommendedValue,
  expectedFpsGain,
  expectedStabilityGain,
  riskLevel,
  applied = false,
  onApply,
}) => {
  return (
    <div
      className={clsx(
        'p-4 rounded-xl border bg-gaming-panel transition-all clip-chamfer-sm space-y-3',
        applied ? 'border-emerald-500/50 bg-emerald-950/10' : 'border-gaming-border hover:border-gaming-red/50'
      )}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-mono font-medium uppercase px-2 py-0.5 rounded bg-gaming-carbon text-gaming-red-bright border border-gaming-red/30">
            {category}
          </span>
          <span className="text-sm font-headline-sm font-bold text-gaming-white">{settingName}</span>
        </div>
        <span
          className={clsx(
            'text-[10px] font-mono px-2 py-0.5 rounded font-medium uppercase',
            riskLevel === 'safe'
              ? 'bg-emerald-500/20 text-emerald-400'
              : riskLevel === 'moderate'
              ? 'bg-amber-500/20 text-amber-400'
              : 'bg-gaming-red/20 text-gaming-red-bright'
          )}
        >
          {riskLevel} fix
        </span>
      </div>

      <div className="grid grid-cols-2 gap-3 p-2.5 rounded-lg bg-gaming-carbon border border-gaming-border text-xs font-mono">
        <div>
          <span className="text-gaming-slate text-[10px] uppercase block font-medium">Current Value</span>
          <span className="text-gaming-slate line-through font-normal">{currentValue}</span>
        </div>
        <div>
          <span className="text-gaming-red-bright text-[10px] uppercase block font-medium">Recommended</span>
          <span className="text-gaming-white font-bold">{recommendedValue}</span>
        </div>
      </div>

      <div className="flex items-center justify-between pt-1">
        <div className="flex items-center gap-2 text-xs font-mono">
          <span className="text-emerald-400 font-bold">+{expectedFpsGain.toFixed(1)} FPS</span>
          <span className="text-gaming-border">•</span>
          <span className="text-gaming-slate font-normal">{expectedStabilityGain}</span>
        </div>

        {onApply && (
          <button
            type="button"
            disabled={applied}
            onClick={() => onApply(id)}
            className={clsx(
              'px-3 py-1.5 rounded-lg text-xs font-headline-sm font-medium transition-all cursor-pointer flex items-center gap-1',
              applied
                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                : 'bg-gaming-red hover:bg-gaming-red-bright text-white shadow-[0_0_10px_rgba(255,0,56,0.4)]'
            )}
          >
            <span className="material-symbols-outlined text-[14px]">
              {applied ? 'check' : 'flash_on'}
            </span>
            <span>{applied ? 'Applied' : 'Apply Fix'}</span>
          </button>
        )}
      </div>
    </div>
  );
});

RecommendationCard.displayName = 'RecommendationCard';
