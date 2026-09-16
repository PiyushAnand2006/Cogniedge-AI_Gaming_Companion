'use client';

import React from 'react';
import Link from 'next/link';

export interface SessionReportRowData {
  id: string;
  title: string;
  type: 'meeting' | 'gaming';
  date: string;
  duration: string;
  keyMetric: string;
  status: 'completed' | 'active' | 'archived';
  reportHref: string;
}

interface SessionReportRowProps {
  session: SessionReportRowData;
  className?: string;
}

export const SessionReportRow: React.FC<SessionReportRowProps> = React.memo(({ session, className = '' }) => {
  const isMeeting = session.type === 'meeting';

  return (
    <div
      role="row"
      aria-label={`Session: ${session.title}`}
      className={`flex flex-col sm:flex-row sm:items-center justify-between gap-space-sm p-space-md bg-surface-container rounded-xl border border-outline-variant/30 hover:border-outline-variant/80 hover:bg-surface-container-high transition-all shadow-sm ${className}`}
    >
      <div className="flex items-center gap-space-md">
        <div
          className={`w-10 h-10 rounded-lg flex items-center justify-center shrink-0 ${
            isMeeting
              ? 'bg-primary/10 text-primary border border-primary/20'
              : 'bg-gaming-red-subtle text-gaming-red border border-gaming-red/30 shadow-[0_0_12px_rgba(255,0,56,0.2)]'
          }`}
        >
          <span className="material-symbols-outlined text-[22px]">
            {isMeeting ? 'groups' : 'sports_esports'}
          </span>
        </div>

        <div className="flex flex-col">
          <div className="flex items-center gap-space-xs">
            <span className="font-headline-sm text-label-lg text-on-surface font-bold">
              {session.title}
            </span>
            <span
              className={`px-1.5 py-0.5 rounded font-label-sm text-label-sm uppercase font-mono font-medium ${
                isMeeting
                  ? 'bg-primary/10 text-primary'
                  : 'bg-gaming-red-subtle text-gaming-red-bright border border-gaming-red/30'
              }`}
            >
              {isMeeting ? 'Meeting Co-pilot' : 'Gaming Companion'}
            </span>
          </div>
          <div className="flex items-center gap-space-sm font-label-sm text-label-sm text-on-surface-variant mt-0.5">
            <span>{session.date}</span>
            <span>•</span>
            <span>{session.duration}</span>
            <span>•</span>
            <span className="text-tertiary">{session.keyMetric}</span>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-space-sm self-end sm:self-center shrink-0">
        <Link
          href={session.reportHref}
          className="inline-flex items-center gap-1 px-space-md py-1.5 bg-surface-container-high hover:bg-surface-container-highest text-primary font-headline-sm text-label-md rounded-lg border border-outline-variant/40 hover:border-primary/40 transition-all shadow-sm"
        >
          <span>View Report</span>
          <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
        </Link>
      </div>
    </div>
  );
});

SessionReportRow.displayName = 'SessionReportRow';
