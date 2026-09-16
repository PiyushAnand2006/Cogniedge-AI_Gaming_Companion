'use client';

import React, { useEffect, useRef } from 'react';
import Link from 'next/link';

/* ─────────────────────────────────────────────────────────────────────────────
   CogniEdge — Cinematic Hero Landing Page
   Netflix-style dark cinematic hero with scroll-reveal feature cards.
   ────────────────────────────────────────────────────────────────────────── */

export default function HeroPage() {
  const featuresRef = useRef<HTMLDivElement>(null);
  const howRef = useRef<HTMLDivElement>(null);
  const techRef = useRef<HTMLDivElement>(null);

  // Intersection Observer for scroll-reveal animations
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('reveal-visible');
          }
        });
      },
      { threshold: 0.15 }
    );

    const revealElements = document.querySelectorAll('.reveal-on-scroll');
    revealElements.forEach((el) => observer.observe(el));

    return () => observer.disconnect();
  }, []);

  const launchOverlay = async () => {
    try {
      await fetch('http://127.0.0.1:8088/overlay/launch', { method: 'POST' });
    } catch {
      // fallback
    }
  };

  return (
    <div className="w-full bg-gaming-carbon text-gaming-white overflow-x-hidden">
      {/* ═══════════════════════════════════════════════════════════════════════
          HERO NAV — Minimal, clean, no heavy AppHeader on the landing page
         ═══════════════════════════════════════════════════════════════════════ */}
      <nav className="fixed top-0 left-0 right-0 z-50 w-full px-6 lg:px-12">
        <div className="max-w-7xl mx-auto h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2.5 group">
            <img
              src="/cogniedge_logo.png"
              alt="CogniEdge Logo"
              className="h-7 w-auto object-contain"
              onError={(e) => {
                (e.target as HTMLImageElement).src =
                  'https://lh3.googleusercontent.com/aida-public/AB6AXuAZQOQZaKpjFpi9Y46Vpa4fZwluFFElAyBcfKpB9SGgAZy9JtZ5pO-YZlnimXPKvJEAAdHJdSumxIsnpXLxX3jMi2cT6vOq6Rq6YfyqO5KPGoXZdzMCG8COlvSUUCimdU3bIZBLFl5K74QjLNb1OREVbPgfAPv4VeCAqsMMvjhOy9ygRVQXig2hszqViJKEpmU8hH60XoVpLRAKYvWBsAC8-8S2Vv6Z6JpnlTaKdL4v7Wu8YNKoxzgL';
              }}
            />
            <span className="text-lg font-bold tracking-wider text-gaming-white font-headline">
              Cogni<span className="text-gaming-red">Edge</span>
            </span>
          </Link>

          <div className="flex items-center gap-6">
            <Link href="/dashboard" className="hidden sm:inline text-sm text-gaming-slate hover:text-gaming-white transition-colors font-normal">
              Dashboard
            </Link>
            <Link href="/gaming-coaching" className="hidden sm:inline text-sm text-gaming-slate hover:text-gaming-white transition-colors font-normal">
              Coaching
            </Link>
            <Link href="/benchmark" className="hidden sm:inline text-sm text-gaming-slate hover:text-gaming-white transition-colors font-normal">
              Benchmark
            </Link>
            <Link
              href="/login"
              className="px-4 py-1.5 rounded-lg bg-gaming-red hover:bg-gaming-red-bright text-white text-sm font-medium transition-all shadow-[0_0_12px_rgba(255,0,56,0.3)]"
            >
              Sign In
            </Link>
          </div>
        </div>
      </nav>

      {/* ═══════════════════════════════════════════════════════════════════════
          HERO SECTION — Full viewport, cinematic, Netflix-style bold text
         ═══════════════════════════════════════════════════════════════════════ */}
      <section className="relative w-full min-h-screen flex items-center overflow-hidden">
        {/* Background layers */}
        <div className="absolute inset-0 bg-gaming-carbon" />
        <div
          className="absolute inset-0 bg-cover bg-center bg-no-repeat opacity-30"
          style={{ backgroundImage: "url('/hero_gaming.jpg')" }}
        />
        <div className="absolute inset-0 bg-gradient-to-r from-gaming-carbon via-gaming-carbon/80 to-transparent" />
        <div className="absolute inset-0 bg-gradient-to-t from-gaming-carbon via-transparent to-gaming-carbon/60" />

        {/* Ambient glow */}
        <div className="absolute top-1/3 right-1/4 w-[600px] h-[600px] bg-gaming-red/8 rounded-full blur-[150px] pointer-events-none hero-glow" />

        {/* Content */}
        <div className="relative z-10 w-full max-w-7xl mx-auto px-6 lg:px-12 pt-32 pb-20">
          <div className="max-w-2xl">
            {/* Badge */}
            <div className="hero-stagger-1 flex items-center gap-2 mb-6">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-gaming-red/15 border border-gaming-red/30 text-gaming-red-bright text-xs font-mono font-medium uppercase tracking-wider">
                <span className="w-1.5 h-1.5 rounded-full bg-gaming-red animate-pulse" />
                Snapdragon X Elite
              </span>
              <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-gaming-panel-high/80 border border-gaming-border text-gaming-slate text-xs font-mono font-normal">
                100% On-Device
              </span>
            </div>

            {/* Headline */}
            <h1 className="hero-stagger-2 font-display text-5xl sm:text-6xl lg:text-7xl font-bold tracking-tighter leading-[0.9] mb-6">
              YOUR AI
              <br />
              <span className="text-gaming-red">GAMING EDGE</span>
            </h1>

            {/* Subtitle */}
            <p className="hero-stagger-3 text-lg sm:text-xl text-gaming-slate leading-relaxed max-w-lg mb-10 font-normal">
              On-device NPU copilot that coaches you in real-time — zero FPS drop, zero cloud, zero compromise.
            </p>

            {/* CTA Buttons */}
            <div className="hero-stagger-4 flex flex-wrap items-center gap-4">
              <button
                type="button"
                onClick={launchOverlay}
                className="group inline-flex items-center gap-2.5 px-7 py-3.5 rounded-xl bg-gaming-red hover:bg-gaming-red-bright text-white font-medium text-sm tracking-wide transition-all shadow-[0_4px_24px_rgba(255,0,56,0.4)] hover:shadow-[0_8px_36px_rgba(255,0,56,0.6)] cursor-pointer"
              >
                <span className="material-symbols-outlined text-[20px]">sports_esports</span>
                <span>Launch Overlay</span>
                <span className="material-symbols-outlined text-[18px] transition-transform group-hover:translate-x-1">arrow_forward</span>
              </button>

              <Link
                href="/dashboard"
                className="inline-flex items-center gap-2 px-6 py-3.5 rounded-xl bg-transparent border border-gaming-border hover:border-gaming-slate text-gaming-white font-medium text-sm transition-all hover:bg-gaming-panel-high/50"
              >
                <span className="material-symbols-outlined text-[18px] text-gaming-slate">dashboard</span>
                <span>View Dashboard</span>
              </Link>
            </div>
          </div>
        </div>

        {/* Scroll indicator */}
        <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 text-gaming-slate/50 animate-bounce">
          <span className="text-xs font-mono uppercase tracking-widest font-normal">Scroll</span>
          <span className="material-symbols-outlined text-[20px]">expand_more</span>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════════════
          HOW IT WORKS — 3-step pipeline, concise and visual
         ═══════════════════════════════════════════════════════════════════════ */}
      <section ref={howRef} className="relative w-full py-24 lg:py-32 border-t border-gaming-border/50">
        <div className="max-w-7xl mx-auto px-6 lg:px-12">
          <div className="reveal-on-scroll text-center mb-16">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-gaming-panel-high border border-gaming-border text-gaming-slate text-xs font-mono uppercase tracking-wider mb-4 font-medium">
              How It Works
            </span>
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-gaming-white font-display">
              Three steps. Zero latency.
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 lg:gap-12">
            {/* Step 1 */}
            <div className="reveal-on-scroll stagger-1 text-center group">
              <div className="w-16 h-16 mx-auto mb-5 rounded-2xl bg-gaming-panel-high border border-gaming-border flex items-center justify-center group-hover:border-gaming-red/50 group-hover:shadow-[0_0_20px_rgba(255,0,56,0.15)] transition-all">
                <span className="material-symbols-outlined text-[28px] text-gaming-red" style={{ fontVariationSettings: "'FILL' 1" }}>
                  center_focus_strong
                </span>
              </div>
              <div className="flex items-center justify-center gap-2 mb-2">
                <span className="text-xs font-mono text-gaming-red font-medium">01</span>
                <h3 className="text-lg font-bold text-gaming-white">Vision Detection</h3>
              </div>
              <p className="text-sm text-gaming-slate leading-relaxed max-w-xs mx-auto font-normal">
                YOLO26-N reads your screen at 60 FPS via NPU — detecting enemies, map state, and weapon info with zero GPU overhead.
              </p>
            </div>

            {/* Step 2 */}
            <div className="reveal-on-scroll stagger-2 text-center group">
              <div className="w-16 h-16 mx-auto mb-5 rounded-2xl bg-gaming-panel-high border border-gaming-border flex items-center justify-center group-hover:border-gaming-red/50 group-hover:shadow-[0_0_20px_rgba(255,0,56,0.15)] transition-all">
                <span className="material-symbols-outlined text-[28px] text-gaming-red" style={{ fontVariationSettings: "'FILL' 1" }}>
                  psychology
                </span>
              </div>
              <div className="flex items-center justify-center gap-2 mb-2">
                <span className="text-xs font-mono text-gaming-red font-medium">02</span>
                <h3 className="text-lg font-bold text-gaming-white">On-Device AI Analysis</h3>
              </div>
              <p className="text-sm text-gaming-slate leading-relaxed max-w-xs mx-auto font-normal">
                Qwen3-4B runs locally on Hexagon NPU, analyzing game state and generating tactical coaching in under 20ms.
              </p>
            </div>

            {/* Step 3 */}
            <div className="reveal-on-scroll stagger-3 text-center group">
              <div className="w-16 h-16 mx-auto mb-5 rounded-2xl bg-gaming-panel-high border border-gaming-border flex items-center justify-center group-hover:border-gaming-red/50 group-hover:shadow-[0_0_20px_rgba(255,0,56,0.15)] transition-all">
                <span className="material-symbols-outlined text-[28px] text-gaming-red" style={{ fontVariationSettings: "'FILL' 1" }}>
                  sports_esports
                </span>
              </div>
              <div className="flex items-center justify-center gap-2 mb-2">
                <span className="text-xs font-mono text-gaming-red font-medium">03</span>
                <h3 className="text-lg font-bold text-gaming-white">Real-Time Coaching</h3>
              </div>
              <p className="text-sm text-gaming-slate leading-relaxed max-w-xs mx-auto font-normal">
                Transparent HUD overlay delivers tips, warnings, and post-match debrief — all air-gapped, nothing leaves your machine.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════════════
          FEATURES — 3 core gaming features, card layout
         ═══════════════════════════════════════════════════════════════════════ */}
      <section ref={featuresRef} className="relative w-full py-24 lg:py-32 bg-gaming-panel/30 border-t border-gaming-border/50">
        <div className="absolute top-0 right-0 w-96 h-96 bg-gaming-red/5 rounded-full blur-[120px] pointer-events-none" />

        <div className="max-w-7xl mx-auto px-6 lg:px-12">
          <div className="reveal-on-scroll text-center mb-16">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-gaming-panel-high border border-gaming-border text-gaming-slate text-xs font-mono uppercase tracking-wider mb-4 font-medium">
              Core Features
            </span>
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-gaming-white font-display">
              Built for competitive gamers.
            </h2>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Feature 1: Push-to-Talk Q&A */}
            <div className="reveal-on-scroll stagger-1 group relative rounded-2xl bg-gaming-panel border border-gaming-border p-8 hover:border-gaming-red/40 transition-all duration-300 hover:shadow-[0_0_30px_rgba(255,0,56,0.1)] overflow-hidden">
              <div className="absolute -top-8 -right-8 w-32 h-32 bg-gaming-red/5 rounded-full blur-2xl group-hover:bg-gaming-red/10 transition-all" />
              <div className="relative z-10">
                <div className="w-12 h-12 rounded-xl bg-gaming-red/10 border border-gaming-red/30 flex items-center justify-center mb-5">
                  <span className="material-symbols-outlined text-[24px] text-gaming-red" style={{ fontVariationSettings: "'FILL' 1" }}>
                    mic
                  </span>
                </div>
                <h3 className="text-xl font-bold text-gaming-white mb-3">Push-to-Talk Q&A</h3>
                <p className="text-sm text-gaming-slate leading-relaxed mb-5 font-normal">
                  Hold a hotkey, ask anything about your current game state. Whisper STT transcribes, Qwen3-4B answers using the last N game-state snapshots as context — grounded, not hallucinated.
                </p>
                <div className="flex items-center gap-2 text-xs font-mono text-gaming-red-bright font-medium">
                  <span className="material-symbols-outlined text-[14px]">bolt</span>
                  <span>Sub-4s end-to-end latency</span>
                </div>
              </div>
            </div>

            {/* Feature 2: Cross-Session Coaching Memory */}
            <div className="reveal-on-scroll stagger-2 group relative rounded-2xl bg-gaming-panel border border-gaming-border p-8 hover:border-gaming-red/40 transition-all duration-300 hover:shadow-[0_0_30px_rgba(255,0,56,0.1)] overflow-hidden">
              <div className="absolute -top-8 -right-8 w-32 h-32 bg-gaming-red/5 rounded-full blur-2xl group-hover:bg-gaming-red/10 transition-all" />
              <div className="relative z-10">
                <div className="w-12 h-12 rounded-xl bg-gaming-red/10 border border-gaming-red/30 flex items-center justify-center mb-5">
                  <span className="material-symbols-outlined text-[24px] text-gaming-red" style={{ fontVariationSettings: "'FILL' 1" }}>
                    psychology_alt
                  </span>
                </div>
                <h3 className="text-xl font-bold text-gaming-white mb-3">Cross-Session Memory</h3>
                <p className="text-sm text-gaming-slate leading-relaxed mb-5 font-normal">
                  Persistent local SQLite tracks your patterns across sessions. &ldquo;Over-extended after kill: 6 of last 8 sessions&rdquo; — the AI remembers what you forget.
                </p>
                <div className="flex items-center gap-2 text-xs font-mono text-gaming-red-bright font-medium">
                  <span className="material-symbols-outlined text-[14px]">trending_up</span>
                  <span>Trend lines across sessions</span>
                </div>
              </div>
            </div>

            {/* Feature 3: Live Compute Dashboard */}
            <div className="reveal-on-scroll stagger-3 group relative rounded-2xl bg-gaming-panel border border-gaming-border p-8 hover:border-gaming-red/40 transition-all duration-300 hover:shadow-[0_0_30px_rgba(255,0,56,0.1)] overflow-hidden">
              <div className="absolute -top-8 -right-8 w-32 h-32 bg-gaming-red/5 rounded-full blur-2xl group-hover:bg-gaming-red/10 transition-all" />
              <div className="relative z-10">
                <div className="w-12 h-12 rounded-xl bg-gaming-red/10 border border-gaming-red/30 flex items-center justify-center mb-5">
                  <span className="material-symbols-outlined text-[24px] text-gaming-red" style={{ fontVariationSettings: "'FILL' 1" }}>
                    monitoring
                  </span>
                </div>
                <h3 className="text-xl font-bold text-gaming-white mb-3">Live Compute Dashboard</h3>
                <p className="text-sm text-gaming-slate leading-relaxed mb-5 font-normal">
                  Real-time NPU/GPU/CPU telemetry overlay proving zero FPS impact. Watch NPU climb while GPU stays flat — your strongest demo moment.
                </p>
                <div className="flex items-center gap-2 text-xs font-mono text-gaming-red-bright font-medium">
                  <span className="material-symbols-outlined text-[14px]">speed</span>
                  <span>0.0 FPS contention verified</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════════════
          DEMO SCREENSHOT — Cinematic overlay preview
         ═══════════════════════════════════════════════════════════════════════ */}
      <section className="relative w-full py-24 lg:py-32 border-t border-gaming-border/50">
        <div className="max-w-7xl mx-auto px-6 lg:px-12">
          <div className="reveal-on-scroll text-center mb-12">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-gaming-panel-high border border-gaming-border text-gaming-slate text-xs font-mono uppercase tracking-wider mb-4 font-medium">
              In Action
            </span>
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-gaming-white font-display">
              See the overlay in-game.
            </h2>
          </div>

          <div className="reveal-on-scroll relative rounded-2xl overflow-hidden border border-gaming-border shadow-[0_20px_60px_rgba(0,0,0,0.6)] group">
            <img
              src="/hero_gaming.jpg"
              alt="CogniEdge AI overlay in a tactical shooter — showing tactical advisor HUD, enemy radar, and weapon status"
              className="w-full h-auto object-cover group-hover:scale-[1.02] transition-transform duration-700"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-gaming-carbon/80 via-transparent to-transparent" />
            <div className="absolute bottom-6 left-6 flex items-center gap-3">
              <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gaming-panel/90 backdrop-blur-sm border border-gaming-border text-xs text-gaming-white font-mono font-medium">
                <span className="w-2 h-2 rounded-full bg-gaming-red animate-pulse" />
                Live AI Overlay • 0% GPU Impact
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════════════
          TECH STACK STRIP
         ═══════════════════════════════════════════════════════════════════════ */}
      <section ref={techRef} className="w-full py-16 border-t border-gaming-border/50 bg-gaming-panel/20">
        <div className="max-w-7xl mx-auto px-6 lg:px-12">
          <div className="reveal-on-scroll flex flex-wrap items-center justify-center gap-x-8 gap-y-4 text-gaming-slate text-sm font-mono font-normal">
            <span className="flex items-center gap-2">
              <span className="material-symbols-outlined text-[16px] text-gaming-red">developer_board</span>
              Snapdragon X Elite
            </span>
            <span className="text-gaming-border">•</span>
            <span className="flex items-center gap-2">
              <span className="material-symbols-outlined text-[16px] text-gaming-red">memory</span>
              Hexagon NPU (45 TOPS)
            </span>
            <span className="text-gaming-border">•</span>
            <span>Qwen3-4B INT4</span>
            <span className="text-gaming-border">•</span>
            <span>Whisper ONNX STT</span>
            <span className="text-gaming-border">•</span>
            <span>YOLO26-N Vision</span>
            <span className="text-gaming-border">•</span>
            <span>Genie SDK</span>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════════════════════════════════════
          FOOTER
         ═══════════════════════════════════════════════════════════════════════ */}
      <footer className="w-full py-10 border-t border-gaming-border/50 text-center">
        <div className="max-w-7xl mx-auto px-6 lg:px-12">
          <div className="flex flex-col items-center gap-3">
            <Link href="/" className="flex items-center gap-2">
              <img
                src="/cogniedge_logo.png"
                alt="CogniEdge"
                className="h-6 w-auto object-contain"
                onError={(e) => {
                  (e.target as HTMLImageElement).src =
                    'https://lh3.googleusercontent.com/aida-public/AB6AXuAZQOQZaKpjFpi9Y46Vpa4fZwluFFElAyBcfKpB9SGgAZy9JtZ5pO-YZlnimXPKvJEAAdHJdSumxIsnpXLxX3jMi2cT6vOq6Rq6YfyqO5KPGoXZdzMCG8COlvSUUCimdU3bIZBLFl5K74QjLNb1OREVbPgfAPv4VeCAqsMMvjhOy9ygRVQXig2hszqViJKEpmU8hH60XoVpLRAKYvWBsAC8-8S2Vv6Z6JpnlTaKdL4v7Wu8YNKoxzgL';
                }}
              />
              <span className="text-sm font-bold text-gaming-white font-headline">
                Cogni<span className="text-gaming-red">Edge</span>
              </span>
            </Link>
            <p className="text-xs text-gaming-slate font-mono font-normal">
              Built for Snapdragon 2026 Hackathon • 100% On-Device • Air-Gapped Sovereign AI
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
