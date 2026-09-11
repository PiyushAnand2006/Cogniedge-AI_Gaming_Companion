"""
CogniEdge Unified Live Event Bus
Single asynchronous broadcast mechanism for:
- Performance telemetry
- Vision detections
- Voice transcription & PTT
- AI coaching & Performance Doctor alerts
- Memory & Optimization events
Powers both the Next.js desktop frontend and PyQt HUD overlay via SSE (/events/live).
"""

import asyncio
import json
import time
from typing import Dict, Any, List, Set


class LiveEventBus:
    def __init__(self):
        self._subscribers: Set[asyncio.Queue] = set()

    def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        self._subscribers.add(q)
        return q

    def unsubscribe(self, q: asyncio.Queue):
        self._subscribers.discard(q)

    async def broadcast(self, event_type: str, data: Dict[str, Any], severity: str = "info"):
        payload = {
            "type": event_type,
            "timestamp": time.time(),
            "severity": severity,
            "data": data
        }
        for q in list(self._subscribers):
            try:
                await q.put(payload)
            except Exception:
                self._subscribers.discard(q)

    def publish_sync(self, event_type: str, data: Dict[str, Any], severity: str = "info"):
        """Helper to publish from synchronous background worker threads."""
        payload = {
            "type": event_type,
            "timestamp": time.time(),
            "severity": severity,
            "data": data
        }
        for q in list(self._subscribers):
            try:
                q.put_nowait(payload)
            except Exception:
                pass


# Global singleton instance
event_bus = LiveEventBus()
