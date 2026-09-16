'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const router = useRouter();
  const [isSignUp, setIsSignUp] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [rememberMe, setRememberMe] = useState(true);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    setTimeout(() => {
      setIsLoading(false);
      router.push('/dashboard');
    }, 600);
  };

  const handleGoogleLogin = () => {
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      router.push('/dashboard');
    }, 600);
  };

  return (
    <div className="fixed inset-0 z-50 w-screen h-screen bg-[#07090e] text-white flex items-center justify-center p-4 sm:p-6 md:p-8 overflow-hidden font-sans select-none">
      {/* Subtle modern ambient background glow (Indigo / Cyan - independent of red/black app theme) */}
      <div className="absolute top-1/3 left-1/4 -translate-x-1/2 -translate-y-1/2 w-[550px] h-[550px] bg-indigo-600/15 rounded-full blur-[140px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 translate-x-1/2 translate-y-1/2 w-[550px] h-[550px] bg-blue-600/10 rounded-full blur-[160px] pointer-events-none" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_40%,rgba(15,23,42,0.4),rgba(7,9,14,0.95))] pointer-events-none" />

      {/* Main Glass Split Card */}
      <div className="relative z-10 w-full max-w-5xl rounded-3xl bg-[#0f1422]/70 backdrop-blur-2xl border border-white/10 shadow-[0_24px_80px_rgba(0,0,0,0.8)] overflow-hidden grid grid-cols-1 lg:grid-cols-2">
        
        {/* =========================================================================
            LEFT HALF: 21st.dev Auth Box (Clean Underline Inputs, Minimalist & Focused)
           ========================================================================= */}
        <div className="p-8 sm:p-12 lg:p-14 flex flex-col justify-between bg-gradient-to-b from-white/[0.03] to-transparent">
          <div>
            {/* Header / Title */}
            <div className="mb-8">
              <h1 className="text-3xl font-bold tracking-tight text-white mb-2 font-headline">
                {isSignUp ? 'Create an account' : 'Welcome back'}
              </h1>
              <p className="text-gray-400 text-sm font-normal">
                {isSignUp
                  ? 'Enter your details to create your account'
                  : 'Please enter your details to sign in'}
              </p>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-6">
              {isSignUp && (
                <div className="relative group">
                  <div className="flex items-center border-b border-white/20 group-focus-within:border-indigo-400 transition-colors py-2">
                    <span className="material-symbols-outlined text-gray-400 group-focus-within:text-indigo-400 text-[20px] mr-3 transition-colors">
                      person
                    </span>
                    <input
                      type="text"
                      required
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      placeholder="Full Name"
                      className="w-full bg-transparent text-white placeholder:text-gray-500 text-sm focus:outline-none font-normal"
                    />
                  </div>
                </div>
              )}

              {/* Email Underline Input */}
              <div className="relative group">
                <div className="flex items-center border-b border-white/20 group-focus-within:border-indigo-400 transition-colors py-2">
                  <span className="material-symbols-outlined text-gray-400 group-focus-within:text-indigo-400 text-[20px] mr-3 transition-colors">
                    mail
                  </span>
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Email address"
                    className="w-full bg-transparent text-white placeholder:text-gray-500 text-sm focus:outline-none font-normal"
                  />
                </div>
              </div>

              {/* Password Underline Input with Visibility Toggle */}
              <div className="relative group">
                <div className="flex items-center border-b border-white/20 group-focus-within:border-indigo-400 transition-colors py-2">
                  <span className="material-symbols-outlined text-gray-400 group-focus-within:text-indigo-400 text-[20px] mr-3 transition-colors">
                    lock
                  </span>
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Password"
                    className="w-full bg-transparent text-white placeholder:text-gray-500 text-sm focus:outline-none font-normal"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="text-gray-400 hover:text-white transition-colors focus:outline-none p-1"
                    title={showPassword ? 'Hide password' : 'Show password'}
                  >
                    <span className="material-symbols-outlined text-[18px]">
                      {showPassword ? 'visibility_off' : 'visibility'}
                    </span>
                  </button>
                </div>
              </div>

              {/* Options: Remember Me & Forgot Password */}
              <div className="flex items-center justify-between text-xs pt-1">
                <label className="flex items-center gap-2 cursor-pointer text-gray-400 hover:text-gray-300 font-normal">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="w-4 h-4 rounded bg-white/10 border-white/20 text-indigo-500 focus:ring-0 accent-indigo-500 cursor-pointer"
                  />
                  <span>Remember me</span>
                </label>
                <button
                  type="button"
                  onClick={() => alert('Password reset instructions will be sent to your email.')}
                  className="text-indigo-400 hover:text-indigo-300 transition-colors font-medium"
                >
                  Forgot password?
                </button>
              </div>

              {/* Primary Sign In / Sign Up Button */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-3 px-6 rounded-xl bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-500 hover:to-blue-500 text-white font-medium text-sm tracking-wide transition-all duration-200 shadow-[0_4px_20px_rgba(79,70,229,0.35)] hover:shadow-[0_6px_28px_rgba(79,70,229,0.5)] flex items-center justify-center gap-2 group disabled:opacity-60 cursor-pointer"
              >
                <span>{isLoading ? 'Please wait...' : isSignUp ? 'Sign Up' : 'Sign In'}</span>
                <span className="material-symbols-outlined text-[18px] transition-transform group-hover:translate-x-1">
                  arrow_forward
                </span>
              </button>
            </form>

            {/* Divider */}
            <div className="relative my-7">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-white/10" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-[#0f1422] px-3 text-gray-500 font-mono tracking-wider font-medium">
                  OR CONTINUE WITH
                </span>
              </div>
            </div>

            {/* Google Social Login */}
            <button
              type="button"
              onClick={handleGoogleLogin}
              className="w-full py-2.5 px-4 rounded-xl bg-white/[0.06] hover:bg-white/[0.1] border border-white/10 hover:border-white/20 text-white text-sm font-medium transition-all flex items-center justify-center gap-3 cursor-pointer"
            >
              <svg className="w-4 h-4 shrink-0" viewBox="0 0 24 24">
                <path
                  fill="#4285F4"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="#34A853"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="#FBBC05"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
                />
                <path
                  fill="#EA4335"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
                />
              </svg>
              <span>Sign in with Google</span>
            </button>
          </div>

          {/* Footer: Switch between Sign In / Sign Up */}
          <div className="mt-8 pt-6 border-t border-white/10 text-center text-xs text-gray-400">
            {isSignUp ? (
              <p>
                Already have an account?{' '}
                <button
                  type="button"
                  onClick={() => setIsSignUp(false)}
                  className="text-indigo-400 hover:text-indigo-300 font-medium ml-1 cursor-pointer"
                >
                  Sign in
                </button>
              </p>
            ) : (
              <p>
                Don&apos;t have an account?{' '}
                <button
                  type="button"
                  onClick={() => setIsSignUp(true)}
                  className="text-indigo-400 hover:text-indigo-300 font-medium ml-1 cursor-pointer"
                >
                  Sign up
                </button>
              </p>
            )}
          </div>
        </div>

        {/* =========================================================================
            RIGHT HALF: Simple & Elegant Brand Showcase (Logo + Project Name Only)
           ========================================================================= */}
        <div className="hidden lg:flex flex-col items-center justify-center p-12 lg:p-16 bg-gradient-to-br from-indigo-950/40 via-[#0d1220] to-[#0a0d18] border-l border-white/10 relative text-center">
          {/* Subtle central glow */}
          <div className="absolute w-72 h-72 bg-indigo-500/10 rounded-full blur-[80px] pointer-events-none" />

          <div className="relative z-10 flex flex-col items-center max-w-sm">
            {/* Clean Logo Container */}
            <div className="w-24 h-24 mb-6 rounded-3xl bg-white/[0.05] border border-white/10 p-4 shadow-2xl flex items-center justify-center backdrop-blur-md">
              <img
                src="/cogniedge_logo.png"
                alt="CogniEdge Logo"
                className="w-full h-full object-contain"
                onError={(e) => {
                  (e.target as HTMLImageElement).src =
                    'https://lh3.googleusercontent.com/aida-public/AB6AXuAZQOQZaKpjFpi9Y46Vpa4fZwluFFElAyBcfKpB9SGgAZy9JtZ5pO-YZlnimXPKvJEAAdHJdSumxIsnpXLxX3jMi2cT6vOq6Rq6YfyqO5KPGoXZdzMCG8COlvSUUCimdU3bIZBLFl5K74QjLNb1OREVbPgfAPv4VeCAqsMMvjhOy9ygRVQXig2hszqViJKEpmU8hH60XoVpLRAKYvWBsAC8-8S2Vv6Z6JpnlTaKdL4v7Wu8YNKoxzgL';
                }}
              />
            </div>

            {/* Project Name */}
            <h2 className="text-3xl font-bold tracking-tight text-white mb-3 font-headline">
              CogniEdge
            </h2>

            {/* Minimalist Subtitle */}
            <p className="text-sm text-gray-400 leading-relaxed font-normal mb-8">
              On-Device Neural Intelligence Platform
            </p>

            {/* Return to App Button */}
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-2 px-5 py-2 rounded-full bg-white/[0.05] hover:bg-white/[0.1] border border-white/10 text-xs text-gray-300 hover:text-white transition-all font-medium"
            >
              <span>Explore Platform</span>
              <span className="material-symbols-outlined text-[14px]">arrow_forward</span>
            </Link>
          </div>
        </div>

      </div>
    </div>
  );
}
