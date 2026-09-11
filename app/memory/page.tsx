'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { MemoryPatternCard } from '@/components/common/MemoryPatternCard';
import { MetricCard } from '@/components/common/MetricCard';

export default function PlayerMemoryPage() {
  const [profileData, setProfileData] = useState<any>(null);
  const [selectedGame, setSelectedGame] = useState<string>('Cyberpunk 2077');

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await fetch(`http://127.0.0.1:8088/memory/profile?game_title=${encodeURIComponent(selectedGame)}`);
        if (res.ok) {
          const data = await res.json();
          setProfileData(data);
        }
      } catch (e) {
        console.error(e);
      }
    };
    fetchProfile();
  }, [selectedGame]);

  const patterns = profileData?.patterns || [
    {
      pattern_name: 'Low HP (<30%) Over-Engagement',
      category: 'TACTICAL',
      description: 'Tendency to push duels when health is under 30% rather than securing cover or healing.',
      occurrences: 14,
      successful_corrections: 7,
      current_confidence: 0.88,
      game_title: 'Cyberpunk 2077',
      recommendation: 'Enforce 2-second retreat behind kinetic barrier when shield capacitor drops below 30%.',
    },
    {
      pattern_name: 'Delayed Defensive Rotation',
      category: 'POSITIONING',
      description: 'Remaining anchored in exposed choke points >8 seconds after radar flank warnings.',
      occurrences: 9,
      successful_corrections: 5,
      current_confidence: 0.82,
      game_title: 'Cyberpunk 2077',
      recommendation: 'Rotate to secondary high-ground walkway within 4s of hostile radar blip detection.',
    },
    {
      pattern_name: 'Left-Flank Sector Blindspot',
      category: 'POSITIONING',
      description: 'Elevated death rate from blind spot entries on asymmetric left corridors.',
      occurrences: 6,
      successful_corrections: 1,
      current_confidence: 0.74,
      game_title: 'Cyberpunk 2077',
      recommendation: 'Pre-aim corner angle at 45° elevation before crossing threshold of Sector B-9.',
    },
  ];

  const effectiveness = profileData?.effectiveness || {
    total_advice_given: 26,
    total_followed: 21,
    total_successful_outcomes: 17,
    overall_success_rate_pct: 81.0,
  };

  return (
    <div className="min-h-screen bg-gaming-bg text-gaming-white pt-20 pb-16 px-gutter-desktop max-w-[1760px] mx-auto flex flex-col gap-space-lg font-sans">
      {/* Header */}
      <div className="p-space-lg rounded-2xl bg-gaming-panel border border-gaming-border shadow-2xl flex flex-col md:flex-row md:items-center justify-between gap-space-md clip-chamfer-tl-br laser-border-left">
        <div>
          <div className="flex items-center gap-space-xs mb-1 font-mono text-xs">
            <span className="px-2 py-0.5 rounded bg-gaming-red/20 text-gaming-red-bright border border-gaming-red/40 uppercase font-bold">
              SOVEREIGN SQLITE MEMORY
            </span>
            <span className="text-gaming-slate">
              Cross-Session Habit Pattern Mining &amp; Strategic Effectiveness
            </span>
          </div>
          <h1 className="font-headline-lg text-headline-lg text-gaming-white font-bold tracking-tight">
            PLAYER HABIT &amp; MEMORY ENGINE
          </h1>
          <p className="font-body-md text-body-md text-gaming-slate mt-0.5">
            Encrypted on-device SQLite database correlating combat decisions, position vulnerabilities, and AI advice outcome tracking.
          </p>
        </div>

        <div className="flex items-center gap-space-sm font-mono text-xs shrink-0">
          <button
            type="button"
            onClick={() => setSelectedGame('Cyberpunk 2077')}
            className={`px-3 py-1.5 rounded-lg border font-bold transition-colors ${
              selectedGame === 'Cyberpunk 2077'
                ? 'bg-gaming-red text-white border-gaming-red'
                : 'bg-gaming-carbon text-gaming-slate border-gaming-border hover:text-gaming-white'
            }`}
          >
            Cyberpunk 2077
          </button>
          <button
            type="button"
            onClick={() => setSelectedGame('Apex Legends')}
            className={`px-3 py-1.5 rounded-lg border font-bold transition-colors ${
              selectedGame === 'Apex Legends'
                ? 'bg-gaming-red text-white border-gaming-red'
                : 'bg-gaming-carbon text-gaming-slate border-gaming-border hover:text-gaming-white'
            }`}
          >
            Apex Legends
          </button>
        </div>
      </div>

      {/* KPI Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-space-md">
        <MetricCard
          label="Tracked Behavioral Patterns"
          value={patterns.length}
          subValue="Across 18 Sessions"
          subColor="text-gaming-slate"
          icon={<span className="material-symbols-outlined text-[18px]">psychology</span>}
        />
        <MetricCard
          label="Coach Advice Followed"
          value={`${effectiveness.total_followed} / ${effectiveness.total_advice_given}`}
          subValue={`${((effectiveness.total_followed / (effectiveness.total_advice_given || 1)) * 100).toFixed(0)}% Compliance`}
          subColor="text-emerald-400"
          icon={<span className="material-symbols-outlined text-[18px]">check_circle</span>}
        />
        <MetricCard
          label="Advice Success Rate"
          value={`${effectiveness.overall_success_rate_pct.toFixed(1)}%`}
          subValue="Positive Combat Outcomes"
          subColor="text-emerald-400"
          icon={<span className="material-symbols-outlined text-[18px]">trending_up</span>}
        />
        <MetricCard
          label="Enclave Sovereign DB"
          value="cogniedge.db"
          subValue="Zero Cloud Ingress / Egress"
          subColor="text-gaming-red-bright"
          icon={<span className="material-symbols-outlined text-[18px]">security</span>}
        />
      </div>

      {/* Pattern Grid */}
      <section className="bg-gaming-panel rounded-2xl p-space-lg shadow-2xl border border-gaming-border flex flex-col gap-space-md clip-chamfer-tl-br laser-border-left">
        <div className="flex items-center justify-between pb-3 border-b border-gaming-border">
          <div className="flex items-center gap-space-xs">
            <span className="material-symbols-outlined text-gaming-red text-[20px]">troubleshoot</span>
            <h2 className="font-headline-sm text-headline-sm text-gaming-white font-bold">
              Detected Combat Habits &amp; Correction Tracking
            </h2>
          </div>
          <span className="text-[10px] font-mono text-gaming-slate">
            SQLite Database: Real-time Pattern Mining Engine
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-space-md">
          {patterns.map((p: any, idx: number) => (
            <MemoryPatternCard
              key={idx}
              id={`pat_${idx}`}
              patternType="tactical_habit"
              name={p.pattern_name}
              description={p.description}
              occurrences={p.occurrences}
              confidence={p.current_confidence}
              impactScore={8.2}
              recommendation={p.recommendation || 'Maintain discipline behind primary cover and avoid re-peeking identical angles.'}
            />
          ))}
        </div>
      </section>
    </div>
  );
}
