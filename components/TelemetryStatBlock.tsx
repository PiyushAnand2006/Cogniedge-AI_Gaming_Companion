'use client';

import React from 'react';

interface TelemetryStatBlockProps {
  label: string;
  value: string | number;
  unit?: string;
  contextLine?: string;
  icon?: string;
  accentColor?: 'primary' | 'tertiary' | 'secondary' | 'error';
  progressPercent?: number;
  className?: string;
  role?: string;
  ariaLabel?: string;
}

const colorMap = {
  primary: {
    text: 'text-gaming-red-bright',
    bgBar: 'bg-gaming-red',
    glow: 'shadow-[0_0_8px_rgba(255,0,56,0.8)]',
    iconText: 'text-gaming-red',
  },
  tertiary: {
    text: 'text-gaming-white',
    bgBar: 'bg-gaming-red',
    glow: 'shadow-[0_0_8px_rgba(255,0,56,0.6)]',
    iconText: 'text-gaming-red-bright',
  },
  secondary: {
    text: 'text-gaming-white',
    bgBar: 'bg-gaming-red',
    glow: 'shadow-[0_0_8px_rgba(255,0,56,0.6)]',
    iconText: 'text-gaming-red',
  },
  error: {
    text: 'text-gaming-red',
    bgBar: 'bg-gaming-red',
    glow: 'shadow-[0_0_8px_rgba(255,0,56,0.8)]',
    iconText: 'text-gaming-red',
  },
};

export const TelemetryStatBlock: React.FC<TelemetryStatBlockProps> = React.memo(({
  label,
  value,
  unit,
  contextLine,
  icon,
  accentColor = 'primary',
  progressPercent,
  className = '',
  role = 'region',
  ariaLabel,
}) => {
  const style = colorMap[accentColor] || colorMap.primary;

  return (
    <div
      role={role}
      aria-label={ariaLabel || `${label}: ${value} ${unit || ''}`}
      className={`bg-gaming-panel border border-gaming-border p-space-md rounded-2xl flex flex-col justify-between shadow-xl transition-all hover:border-gaming-red/50 relative overflow-hidden group ${className}`}
    >
      <div className="absolute top-0 right-0 w-24 h-24 bg-gaming-red/5 rounded-full blur-xl pointer-events-none group-hover:bg-gaming-red/10 transition-all" />
      
      <div className="flex items-center justify-between gap-space-sm mb-space-xs relative z-10">
        <span className="font-label-sm text-label-sm text-gaming-slate uppercase tracking-wider flex items-center gap-1.5 font-medium">
          {icon && (
            <span className={`material-symbols-outlined text-[16px] ${style.iconText}`} aria-hidden="true">
              {icon}
            </span>
          )}
          {label}
        </span>
      </div>

      <div className="flex items-baseline gap-1 my-1 relative z-10">
        <span className={`font-display-lg text-headline-lg font-bold tracking-tight font-mono ${style.text}`}>
          {value}
        </span>
        {unit && (
          <span className="font-label-md text-label-md text-gaming-slate ml-1 font-mono">
            {unit}
          </span>
        )}
      </div>

      {progressPercent !== undefined && (
        <div className="w-full h-1.5 bg-gaming-carbon rounded-full overflow-hidden my-1.5 border border-gaming-border/40 relative z-10">
          <div
            className={`h-full ${style.bgBar} ${style.glow} rounded-full transition-all duration-500`}
            style={{ width: `${Math.min(100, Math.max(0, progressPercent))}%` }}
          />
        </div>
      )}

      {contextLine && (
        <span className="font-label-sm text-label-sm text-gaming-slate mt-1 flex items-center gap-1 relative z-10 font-mono">
          {contextLine}
        </span>
      )}
    </div>
  );
});

TelemetryStatBlock.displayName = 'TelemetryStatBlock';
