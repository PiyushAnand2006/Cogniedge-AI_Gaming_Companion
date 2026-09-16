import React from 'react';
import type { Metadata } from 'next';
import './globals.css';
import { AppHeader } from '@/components/AppHeader';

export const metadata: Metadata = {
  title: 'CogniEdge — On-Device NPU Intelligence Hub',
  description:
    'Sovereign, air-gapped on-device AI companion for Snapdragon Copilot+ hardware powered by Hexagon NPU, Genie SDK Qwen3-4B, Whisper ONNX STT, and YOLO26-N.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&family=JetBrains+Mono:wght@400;500;700&family=Space+Grotesk:wght@500;700&display=swap"
          rel="stylesheet"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200"
          rel="stylesheet"
        />
      </head>
      <body className="tactical-hex-grid font-body text-gaming-white antialiased selection:bg-gaming-red selection:text-white min-h-screen">
        <AppHeader />
        <main className="w-full pt-16 min-h-screen">{children}</main>
      </body>
    </html>
  );
}
