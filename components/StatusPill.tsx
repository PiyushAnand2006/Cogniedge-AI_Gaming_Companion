'use client';

import React from 'react';

export type StatusVariant = 'neutral' | 'active' | 'warning' | 'critical' | 'nominal' | 'secondary';

interface StatusPillProps {
  label: string;
  variant?: StatusVariant;
  icon?: string;
  pulsing?: boolean;
  className?: string;
  role?: string;
  ariaLabel?: string;
}

export const StatusPill: React.FC<StatusPillProps> = React.memo(({
  label,
  variant = 'neutral',
  icon,
  pulsing = false,
  className = '',
  role = 'status',
  ariaLabel,
}) => {
  const variantStyles: Record<StatusVariant, { container: string; text: string; dot: string }> = {
    nominal: {
      container: 'bg-surface-container-low border border-tertiary/30 text-tertiary',
      text: 'text-tertiary',
      dot: 'bg-tertiary',
    },
    active: {
      container: 'bg-surface-container-high border border-primary/30 text-primary',
      text: 'text-primary',
      dot: 'bg-primary-container',
    },
    warning: {
      container: 'bg-secondary-container/20 border border-secondary/40 text-secondary',
      text: 'text-secondary',
      dot: 'bg-secondary',
    },
    critical: {
      container: 'bg-error-container/30 border border-error/50 text-error',
      text: 'text-error',
      dot: 'bg-error',
    },
    secondary: {
      container: 'bg-surface-container-high border border-secondary/30 text-secondary',
      text: 'text-secondary',
      dot: 'bg-secondary',
    },
    neutral: {
      container: 'bg-surface-container-high border border-outline-variant/40 text-on-surface-variant',
      text: 'text-on-surface-variant',
      dot: 'bg-outline',
    },
  };

  const style = variantStyles[variant] || variantStyles.neutral;

  return (
    <div
      role={role}
      aria-label={ariaLabel || label}
      className={`inline-flex items-center gap-1.5 px-space-sm py-0.5 rounded-full font-label-sm text-label-sm transition-all ${style.container} ${className}`}
    >
      <span
        aria-hidden="true"
        className={`w-1.5 h-1.5 rounded-full shrink-0 ${style.dot} ${pulsing ? 'animate-pulse' : ''}`}
      />
      {icon && (
        <span className="material-symbols-outlined text-[14px]" aria-hidden="true">
          {icon}
        </span>
      )}
      <span className={`font-medium ${style.text}`}>{label}</span>
    </div>
  );
});

StatusPill.displayName = 'StatusPill';
