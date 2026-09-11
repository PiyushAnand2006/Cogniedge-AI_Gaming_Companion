"""
CogniEdge Native PyQt HUD Components
Corner-docked panels for zero-FPS in-game HUD overlay.
"""

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPolygonF
from PyQt6.QtCore import QPointF
import math
from styles import RADAR_PANEL_STYLE, TELEMETRY_PANEL_STYLE, TACTICAL_TIP_STYLE


class TacticalRadarWidget(QFrame):
    """Top-Left Tactical Radar Panel - Full Opacity (100%)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("RadarPanel")
        self.setStyleSheet(RADAR_PANEL_STYLE)
        self.setFixedSize(360, 260)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)

        # Header Row
        header_layout = QHBoxLayout()
        title_label = QLabel("TACTICAL SECTOR B-9")
        title_label.setObjectName("RadarTitle")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        threat_badge = QLabel("HOSTILES: 3 DETECTED")
        threat_badge.setObjectName("ThreatActive")
        header_layout.addWidget(threat_badge)
        layout.addLayout(header_layout)

        # Subtitle
        sub_label = QLabel("YOLO26-N INT8 • Hexagon NPU Stream • 60 FPS")
        sub_label.setObjectName("RadarSubtitle")
        layout.addWidget(sub_label)

        # Threat Vector Metrics
        vector_box = QFrame()
        vector_box.setStyleSheet("background-color: rgba(22, 25, 34, 0.85); border: 1px solid rgba(255, 0, 56, 0.3); border-radius: 6px; padding: 6px;")
        v_layout = QVBoxLayout(vector_box)
        v_layout.setContentsMargins(8, 6, 8, 6)
        v_layout.setSpacing(4)

        t1 = QLabel("▸ Threat Vector: East Corridor (94% Conf)")
        t1.setStyleSheet("color: #ff2a55; font-weight: bold; font-size: 11px; font-family: 'JetBrains Mono', monospace;")
        t2 = QLabel("▸ Flank Risk: High (Predicted in 12s)")
        t2.setStyleSheet("color: #f8fafc; font-size: 11px; font-family: 'JetBrains Mono', monospace;")
        t3 = QLabel("▸ Target Health: 2x Armored / 1x Low HP (<30)")
        t3.setStyleSheet("color: #8a93a8; font-size: 11px; font-family: 'JetBrains Mono', monospace;")

        v_layout.addWidget(t1)
        v_layout.addWidget(t2)
        v_layout.addWidget(t3)
        layout.addWidget(vector_box)

        # Bottom Hardware Badge
        footer_layout = QHBoxLayout()
        foot_label = QLabel("0.0% GPU Impact • Air-Gapped Hexagon NPU")
        foot_label.setStyleSheet("color: #ff0038; font-size: 10px; font-weight: bold; font-family: 'JetBrains Mono', monospace;")
        footer_layout.addWidget(foot_label)
        layout.addLayout(footer_layout)


class TelemetryPanelWidget(QFrame):
    """Top-Right Hardware Benchmark & Telemetry Panel - Reduced Opacity (65%)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TelemetryPanel")
        self.setStyleSheet(TELEMETRY_PANEL_STYLE)
        self.setFixedSize(340, 220)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)

        # Header
        h_layout = QHBoxLayout()
        title = QLabel("NPU ZERO-FPS BENCHMARK")
        title.setObjectName("TelemTitle")
        h_layout.addWidget(title)
        h_layout.addStretch()

        badge = QLabel("VERIFIED 0.00 FPS DROP")
        badge.setStyleSheet("color: #ffffff; font-size: 10px; font-weight: bold; background: #ff0038; padding: 2px 6px; border-radius: 4px; font-family: 'JetBrains Mono', monospace;")
        h_layout.addWidget(badge)
        layout.addLayout(h_layout)

        # FPS & Contention Row
        stats_layout = QHBoxLayout()

        col1 = QVBoxLayout()
        l1 = QLabel("GAMEPLAY FPS")
        l1.setStyleSheet("color: #8a93a8; font-size: 10px; font-family: 'JetBrains Mono', monospace;")
        v1 = QLabel("144 FPS")
        v1.setObjectName("StatValueZeroDrop")
        c1 = QLabel("0.0% Stutter Delta")
        c1.setStyleSheet("color: #ff2a55; font-size: 9px; font-family: 'JetBrains Mono', monospace;")
        col1.addWidget(l1)
        col1.addWidget(v1)
        col1.addWidget(c1)
        stats_layout.addLayout(col1)

        col2 = QVBoxLayout()
        l2 = QLabel("GPU OVERHEAD")
        l2.setStyleSheet("color: #8a93a8; font-size: 10px; font-family: 'JetBrains Mono', monospace;")
        v2 = QLabel("0.00 %")
        v2.setObjectName("StatValueHighlight")
        c2 = QLabel("Hexagon NPU Isolated")
        c2.setStyleSheet("color: #f8fafc; font-size: 9px; font-family: 'JetBrains Mono', monospace;")
        col2.addWidget(l2)
        col2.addWidget(v2)
        col2.addWidget(c2)
        stats_layout.addLayout(col2)

        layout.addLayout(stats_layout)

        # NPU Utilization Bar
        bar_label = QLabel("Snapdragon NPU Allocation: 45.2 / 80 TOPS")
        bar_label.setStyleSheet("color: #dfe2ee; font-size: 10px; margin-top: 4px; font-family: 'JetBrains Mono', monospace;")
        layout.addWidget(bar_label)

        self.progress = QProgressBar()
        self.progress.setFixedHeight(6)
        self.progress.setValue(56)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar { background-color: #1a1d28; border-radius: 3px; }
            QProgressBar::chunk { background-color: #ff0038; border-radius: 3px; }
        """)
        layout.addWidget(self.progress)


class TacticalTipWidget(QFrame):
    """Bottom-Right Tactical Tip Card - Reduced Opacity (70%)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TacticalTipPanel")
        self.setStyleSheet(TACTICAL_TIP_STYLE)
        self.setFixedSize(380, 200)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        # Header
        h_layout = QHBoxLayout()
        title = QLabel("QWEN3-4B TACTICAL ADVICE")
        title.setObjectName("TipHeader")
        h_layout.addWidget(title)
        h_layout.addStretch()

        live_badge = QLabel("LIVE NPU REASONING")
        live_badge.setStyleSheet("color: #d0bcff; font-size: 10px; font-weight: bold; background: rgba(139,92,246,0.2); padding: 2px 6px; border-radius: 4px;")
        h_layout.addWidget(live_badge)
        layout.addLayout(h_layout)

        # Tip Body
        tip_text = QLabel(
            "Hostile squad flanking via East Corridor choke in ~12s.\n"
            "Recommendation: Deploy thermal grenade at corridor doorway, "
            "then fallback 15m to elevated Catwalk B-9 for 1.4x headshot multiplier."
        )
        tip_text.setObjectName("TipBody")
        tip_text.setWordWrap(True)
        layout.addWidget(tip_text)

        # Synergy Badge
        synergy = QLabel("Loadout Synergy: Heavy Pulse Rifle (+14% CQB Multiplier)")
        synergy.setObjectName("SynergyBadge")
        layout.addWidget(synergy)
