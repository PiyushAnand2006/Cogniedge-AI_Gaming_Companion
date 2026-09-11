'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export const AppHeader: React.FC = () => {
  const pathname = usePathname();
  const [npuTops, setNpuTops] = useState<number>(45.2);
  const [maxTops] = useState<number>(80.0);
  const [serviceStatus, setServiceStatus] = useState<{ genie: string; whisper: string; serviceOnline: boolean }>({
    genie: 'Active',
    whisper: 'Ready',
    serviceOnline: true,
  });

  useEffect(() => {
    const fetchTelemetry = async () => {
      try {
        const res = await fetch('http://127.0.0.1:8088/telemetry');
        if (res.ok) {
          const data = await res.json();
          if (data.npu_tops) setNpuTops(data.npu_tops);
          if (data.genie_status) {
            setServiceStatus({
              genie: data.genie_status || 'Active',
              whisper: data.whisper_status || 'Ready',
              serviceOnline: true,
            });
          }
        }
      } catch {
        // Backend fallback
      }
    };
    fetchTelemetry();
    const interval = setInterval(fetchTelemetry, 4000);
    return () => clearInterval(interval);
  }, []);

  if (pathname === '/' || pathname === '/login') return null;

  const navLinks = [
    { name: 'Dashboard', href: '/dashboard', icon: 'dashboard' },
    { name: 'Live Session', href: '/live', icon: 'sensors' },
    { name: 'Performance Doctor', href: '/performance', icon: 'medical_services' },
    { name: 'Game Coaching', href: '/gaming-coaching', icon: 'sports_esports' },
    { name: 'Player Memory', href: '/memory', icon: 'psychology' },
    { name: 'FPS Benchmark', href: '/benchmark', icon: 'speed' },
    { name: 'Settings', href: '/settings', icon: 'settings' },
  ];

  const isActive = (href: string) => {
    if (href === '/' && pathname === '/') return true;
    if (href !== '/' && pathname.startsWith(href)) return true;
    return false;
  };

  const launchNativeOverlay = async () => {
    try {
      await fetch('http://127.0.0.1:8088/overlay/launch', { method: 'POST' });
    } catch {
      if (typeof window !== 'undefined' && (window as unknown as { electronAPI?: { launchOverlay: () => void } }).electronAPI) {
        (window as unknown as { electronAPI: { launchOverlay: () => void } }).electronAPI.launchOverlay();
      }
    }
  };

  return (
    <header className="fixed top-0 left-0 right-0 w-full z-50 bg-gaming-panel/95 backdrop-blur-xl shadow-[0_4px_24px_rgba(0,0,0,0.8)] border-b border-gaming-border">
      <div className="h-16 w-full px-gutter-desktop flex items-center justify-between gap-space-md max-w-[1760px] mx-auto">
        {/* Brand & Platform Identity */}
        <div className="flex items-center gap-space-md shrink-0">
          <Link href="/" className="flex items-center gap-2 group">
            <img
              src="/cogniedge_logo.png"
              alt="CogniEdge Brand Logo"
              className="h-8 w-auto object-contain transition-transform group-hover:scale-105"
              onError={(e) => {
                (e.target as HTMLImageElement).src =
                  'https://lh3.googleusercontent.com/aida-public/AB6AXuAZQOQZaKpjFpi9Y46Vpa4fZwluFFElAyBcfKpB9SGgAZy9JtZ5pO-YZlnimXPKvJEAAdHJdSumxIsnpXLxX3jMi2cT6vOq6Rq6YfyqO5KPGoXZdzMCG8COlvSUUCimdU3bIZBLFl5K74QjLNb1OREVbPgfAPv4VeCAqsMMvjhOy9ygRVQXig2hszqViJKEpmU8hH60XoVpLRAKYvWBsAC8-8S2Vv6Z6JpnlTaKdL4v7Wu8YNKoxzgL';
              }}
            />
            <div className="flex items-center gap-space-sm">
              <span className="font-headline-sm text-headline-sm tracking-tight text-gaming-white font-bold">
                CogniEdge
              </span>
              <span className="font-label-sm text-label-sm uppercase px-space-xs py-0.5 bg-gaming-panel-high text-gaming-red-bright border border-gaming-red/30 rounded font-mono">
                Snapdragon X Elite NPU
              </span>
            </div>
          </Link>

          <div className="hidden 2xl:flex items-center gap-space-xs px-space-sm py-1 bg-gaming-carbon text-gaming-slate border border-gaming-border rounded-full font-label-sm text-label-sm">
            <span className="w-1.5 h-1.5 rounded-full bg-gaming-red animate-ping" />
            <span className="text-gaming-white font-medium">100% On-Device</span>
            <span className="text-gaming-border">•</span>
            <span>0 FPS Contention</span>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav
          className="hidden lg:flex items-center gap-1 px-1.5 py-1 bg-gaming-carbon border border-gaming-border rounded-xl shadow-inner"
          aria-label="Main Navigation"
        >
          {navLinks.map((link) => {
            const active = isActive(link.href);
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`font-headline-sm text-label-md px-3 py-1.5 transition-all whitespace-nowrap rounded-lg flex items-center gap-1.5 ${
                  active
                    ? 'bg-gaming-red text-white font-bold shadow-[0_0_14px_rgba(255,0,56,0.5)]'
                    : 'text-gaming-slate hover:text-gaming-white hover:bg-gaming-panel-high'
                }`}
              >
                <span className="material-symbols-outlined text-[15px]">{link.icon}</span>
                <span>{link.name}</span>
              </Link>
            );
          })}

          <button
            type="button"
            onClick={launchNativeOverlay}
            title="Spawns transparent, zero-FPS PyQt Gaming HUD overlay process"
            className="font-headline-sm text-label-md px-space-sm py-1.5 text-gaming-red-bright hover:bg-gaming-red hover:text-white transition-all whitespace-nowrap rounded-lg border border-gaming-red/40 flex items-center gap-1 font-bold shadow-[0_0_10px_rgba(255,0,56,0.2)] ml-1"
          >
            <span className="material-symbols-outlined text-[16px]">sports_esports</span>
            <span>Launch HUD</span>
          </button>
        </nav>

        {/* Real-Time Telemetry Stat Cluster */}
        <div className="flex items-center gap-space-md shrink-0">
          <div className="hidden xl:flex items-center gap-space-sm bg-gaming-carbon px-space-sm py-1 rounded-xl border border-gaming-border">
            <div className="flex flex-col">
              <div className="flex items-center justify-between gap-space-sm font-label-sm text-label-sm font-mono">
                <span className="text-gaming-slate">NPU TOPS</span>
                <span className="text-gaming-red-bright font-bold">
                  {npuTops.toFixed(1)} / {maxTops}
                </span>
              </div>
              <div className="w-24 h-1.5 bg-gaming-panel-highest rounded-full overflow-hidden mt-0.5 border border-gaming-border/40">
                <div
                  className="h-full bg-gaming-red rounded-full shadow-[0_0_8px_rgba(255,0,56,0.8)]"
                  style={{ width: `${(npuTops / maxTops) * 100}%` }}
                />
              </div>
            </div>
          </div>

          <div className="hidden md:flex items-center gap-space-xs font-label-sm text-label-sm font-mono">
            <span className="px-space-xs py-0.5 bg-gaming-panel-high text-gaming-slate border border-gaming-border rounded">
              Genie: <span className="text-gaming-white font-bold">{serviceStatus.genie}</span>
            </span>
            <span className="px-space-xs py-0.5 bg-gaming-panel-high text-gaming-slate border border-gaming-border rounded">
              Whisper: <span className="text-gaming-red-bright font-bold">{serviceStatus.whisper}</span>
            </span>
          </div>

          <Link
            href="/settings"
            aria-label="Settings"
            className="p-1.5 text-gaming-slate hover:text-gaming-white hover:bg-gaming-panel-high rounded-lg transition-colors border border-transparent hover:border-gaming-border"
          >
            <span className="material-symbols-outlined text-[20px]">settings</span>
          </Link>

          <Link
            href="/login"
            className="w-8 h-8 rounded-full bg-gaming-red text-white flex items-center justify-center shadow-[0_0_12px_rgba(255,0,56,0.5)] font-bold cursor-pointer transition-transform hover:scale-105"
            title="Operator Login / Enclave"
          >
            <span className="material-symbols-outlined text-[18px]">person</span>
          </Link>
        </div>
      </div>
    </header>
  );
};
