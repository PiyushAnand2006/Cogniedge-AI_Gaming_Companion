import React from 'react';
import { clsx } from 'clsx';

interface DiagnosisCardProps {
  likelyIssue: string;
  confidence: number;
  evidence: string[];
  severity: 'low' | 'medium' | 'high' | 'critical';
  diagnosisText: string;
  recommendationText: string;
  expectedEffect?: string;
  provenance?: 'MEASURED' | 'ESTIMATED' | 'REFERENCE' | 'DEMO';
  onApplyFix?: () => void;
}

export const DiagnosisCard: React.FC<DiagnosisCardProps> = React.memo(({
  likelyIssue,
  confidence,
  evidence,
  severity,
  diagnosisText,
  recommendationText,
  expectedEffect,
  provenance = 'MEASURED',
  onApplyFix,
}) => {
  const getSeverityBadge = () => {
    switch (severity) {
      case 'critical':
        return <span className="text-[10px] font-mono font-medium px-2 py-0.5 rounded bg-gaming-red text-white uppercase shadow-[0_0_10px_rgba(255,0,56,0.6)]">CRITICAL BOTTLENECK</span>;
      case 'high':
        return <span className="text-[10px] font-mono font-medium px-2 py-0.5 rounded bg-gaming-red/40 text-gaming-red-bright uppercase border border-gaming-red/60">HIGH SEVERITY</span>;
      case 'medium':
        return <span className="text-[10px] font-mono font-medium px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 uppercase border border-amber-500/30">MODERATE ISSUE</span>;
      default:
        return <span className="text-[10px] font-mono font-medium px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 uppercase border border-emerald-500/30">OPTIMAL PERFORMANCE</span>;
    }
  };

  return (
    <div className="p-5 rounded-2xl bg-gaming-panel border border-gaming-border shadow-xl clip-chamfer-tl-br space-y-4 laser-border-left">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-gaming-border">
        <div className="flex items-center gap-2">
          <div className="hazard-slashes">
            <span />
            <span />
            <span />
          </div>
          <span className="text-sm font-headline-sm font-bold text-gaming-white tracking-wide uppercase">
            AI Performance Doctor Diagnosis
          </span>
        </div>
        <div className="flex items-center gap-2">
          {getSeverityBadge()}
          <span className="text-[10px] font-mono font-medium px-2 py-0.5 rounded bg-gaming-carbon text-gaming-slate border border-gaming-border">
            Confidence: {(confidence * 100).toFixed(0)}%
          </span>
        </div>
      </div>

      {/* Likely Issue & Narrative */}
      <div className="space-y-2">
        <div className="text-lg font-bold font-mono text-gaming-white flex items-center gap-2">
          <span className="material-symbols-outlined text-gaming-red text-[20px]">troubleshoot</span>
          <span>{likelyIssue.replace(/_/g, ' ')}</span>
        </div>
        <p className="text-xs text-gaming-slate leading-relaxed font-normal">
          {diagnosisText}
        </p>
      </div>

      {/* Evidence Pill Tags */}
      {evidence && evidence.length > 0 && (
        <div className="space-y-1.5">
          <span className="text-[10px] font-mono uppercase tracking-wider text-gaming-slate font-medium">
            Observed Hardware Evidence:
          </span>
          <div className="flex flex-wrap gap-1.5">
            {evidence.map((ev, idx) => (
              <span
                key={idx}
                className="text-[11px] font-mono font-normal px-2 py-1 rounded bg-gaming-carbon border border-gaming-border text-gaming-white flex items-center gap-1"
              >
                <span className="material-symbols-outlined text-[13px] text-gaming-red">check_circle</span>
                {ev}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Recommendation Action Block */}
      <div className="p-3.5 rounded-xl bg-gaming-carbon border border-gaming-border space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-mono font-medium text-gaming-red-bright uppercase flex items-center gap-1.5">
            <span className="material-symbols-outlined text-[16px]">psychology</span> Prescribed Action
          </span>
          {expectedEffect && (
            <span className="text-[10px] font-mono text-emerald-400 font-normal">
              Expected: {expectedEffect}
            </span>
          )}
        </div>
        <p className="text-xs text-gaming-slate leading-relaxed font-normal">
          {recommendationText}
        </p>
        {onApplyFix && (
          <button
            type="button"
            onClick={onApplyFix}
            className="mt-2 w-full py-2 px-3 rounded-lg bg-gaming-red hover:bg-gaming-red-bright text-white font-headline-sm text-xs font-medium transition-all shadow-[0_0_12px_rgba(255,0,56,0.4)] flex items-center justify-center gap-1.5 cursor-pointer"
          >
            <span className="material-symbols-outlined text-[15px]">bolt</span>
            <span>Apply Recommended Optimization</span>
          </button>
        )}
      </div>
    </div>
  );
});

DiagnosisCard.displayName = 'DiagnosisCard';
