"""
CogniEdge Native PyQt HUD Components
Corner-docked panels for in-game HUD overlay with dynamic state updates.
"""

from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt
from styles import RADAR_PANEL_STYLE, TELEMETRY_PANEL_STYLE, TACTICAL_TIP_STYLE


class TacticalRadarWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("RadarPanel")
        self.setStyleSheet(RADAR_PANEL_STYLE)
        self.setFixedSize(360, 240)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        # Header Row
        header_layout = QHBoxLayout()
        title_label = QLabel("TACTICAL VISION RADAR")
        title_label.setObjectName("RadarTitle")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        self.threat_badge = QLabel("SECTOR CLEAR")
        self.threat_badge.setObjectName("ThreatActive")
        self.threat_badge.setStyleSheet("color: #4ade80; font-size: 10px; font-weight: bold; background: rgba(74,222,128,0.15); padding: 2px 6px; border-radius: 4px;")
        header_layout.addWidget(self.threat_badge)
        layout.addLayout(header_layout)

        # Subtitle
        sub_label = QLabel("Screen-Only Vision Pipeline • Zero Injection")
        sub_label.setObjectName("RadarSubtitle")
        layout.addWidget(sub_label)

        # Vector Box
        self.vector_box = QFrame()
        self.vector_box.setStyleSheet("background-color: rgba(22, 25, 34, 0.85); border: 1px solid rgba(255, 0, 56, 0.3); border-radius: 6px; padding: 6px;")
        v_layout = QVBoxLayout(self.vector_box)
        v_layout.setContentsMargins(8, 6, 8, 6)
        v_layout.setSpacing(4)

        self.t1 = QLabel("▸ Threat Vector: Clear")
        self.t1.setStyleSheet("color: #ff2a55; font-weight: bold; font-size: 11px; font-family: 'JetBrains Mono', monospace;")
        self.t2 = QLabel("▸ Hostiles in Sector: 0")
        self.t2.setStyleSheet("color: #f8fafc; font-size: 11px; font-family: 'JetBrains Mono', monospace;")
        self.t3 = QLabel("▸ Player Health: 100 HP")
        self.t3.setStyleSheet("color: #8a93a8; font-size: 11px; font-family: 'JetBrains Mono', monospace;")

        v_layout.addWidget(self.t1)
        v_layout.addWidget(self.t2)
        v_layout.addWidget(self.t3)
        layout.addWidget(self.vector_box)

    def update_radar(self, hostiles: int, threat_vector: str, player_hp: int):
        if hostiles > 0:
            self.threat_badge.setText(f"HOSTILES: {hostiles}")
            self.threat_badge.setStyleSheet("color: #ff0038; font-size: 10px; font-weight: bold; background: rgba(255,0,56,0.2); padding: 2px 6px; border-radius: 4px;")
            self.t1.setText(f"▸ Threat Vector: {threat_vector}")
            self.t2.setText(f"▸ Hostiles in Sector: {hostiles} Detected")
        else:
            self.threat_badge.setText("SECTOR CLEAR")
            self.threat_badge.setStyleSheet("color: #4ade80; font-size: 10px; font-weight: bold; background: rgba(74,222,128,0.15); padding: 2px 6px; border-radius: 4px;")
            self.t1.setText("▸ Threat Vector: Clear")
            self.t2.setText("▸ Hostiles in Sector: 0")

        self.t3.setText(f"▸ Player Health: {player_hp} HP")
        if player_hp < 30:
            self.t3.setStyleSheet("color: #ff0038; font-weight: bold; font-size: 11px; font-family: 'JetBrains Mono', monospace;")
        else:
            self.t3.setStyleSheet("color: #8a93a8; font-size: 11px; font-family: 'JetBrains Mono', monospace;")


class TelemetryPanelWidget(QFrame):
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
        title = QLabel("PERFORMANCE DOCTOR")
        title.setObjectName("TelemTitle")
        h_layout.addWidget(title)
        h_layout.addStretch()

        self.prov_badge = QLabel("MEASURED")
        self.prov_badge.setStyleSheet("color: #ffffff; font-size: 9px; font-weight: bold; background: #2563eb; padding: 2px 6px; border-radius: 4px; font-family: 'JetBrains Mono', monospace;")
        h_layout.addWidget(self.prov_badge)
        layout.addLayout(h_layout)

        # FPS & 1% Low Row
        stats_layout = QHBoxLayout()

        col1 = QVBoxLayout()
        l1 = QLabel("GAMEPLAY FPS")
        l1.setStyleSheet("color: #8a93a8; font-size: 10px; font-family: 'JetBrains Mono', monospace;")
        self.v1 = QLabel("138.0 FPS")
        self.v1.setObjectName("StatValueZeroDrop")
        self.c1 = QLabel("1% Low: 94.2 FPS")
        self.c1.setStyleSheet("color: #ff2a55; font-size: 9px; font-family: 'JetBrains Mono', monospace;")
        col1.addWidget(l1)
        col1.addWidget(self.v1)
        col1.addWidget(self.c1)
        stats_layout.addLayout(col1)

        col2 = QVBoxLayout()
        l2 = QLabel("GPU LOAD")
        l2.setStyleSheet("color: #8a93a8; font-size: 10px; font-family: 'JetBrains Mono', monospace;")
        self.v2 = QLabel("88.4 %")
        self.v2.setObjectName("StatValueHighlight")
        self.c2 = QLabel("Stutter Risk: Low")
        self.c2.setStyleSheet("color: #4ade80; font-size: 9px; font-family: 'JetBrains Mono', monospace;")
        col2.addWidget(l2)
        col2.addWidget(self.v2)
        col2.addWidget(self.c2)
        stats_layout.addLayout(col2)

        layout.addLayout(stats_layout)

        # Risk Bar
        self.bar_label = QLabel("Predictive Stutter Risk: 12%")
        self.bar_label.setStyleSheet("color: #dfe2ee; font-size: 10px; margin-top: 4px; font-family: 'JetBrains Mono', monospace;")
        layout.addWidget(self.bar_label)

        self.progress = QProgressBar()
        self.progress.setFixedHeight(6)
        self.progress.setValue(12)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar { background-color: #1a1d28; border-radius: 3px; }
            QProgressBar::chunk { background-color: #4ade80; border-radius: 3px; }
        """)
        layout.addWidget(self.progress)

    def update_metrics(self, fps: float, one_pct: float, gpu_usage: float, stutter_risk: float, risk_level: str, provenance: str):
        self.v1.setText(f"{fps:.1f} FPS")
        self.c1.setText(f"1% Low: {one_pct:.1f} FPS")
        self.v2.setText(f"{gpu_usage:.1f} %")
        self.prov_badge.setText(provenance)

        risk_pct = int(stutter_risk * 100)
        self.bar_label.setText(f"Predictive Stutter Risk: {risk_pct}% ({risk_level.upper()})")
        self.progress.setValue(risk_pct)

        if risk_level in ["high", "critical"]:
            self.c2.setText(f"Stutter Risk: {risk_level.upper()}")
            self.c2.setStyleSheet("color: #ff0038; font-weight: bold; font-size: 9px; font-family: 'JetBrains Mono', monospace;")
            self.progress.setStyleSheet("""
                QProgressBar { background-color: #1a1d28; border-radius: 3px; }
                QProgressBar::chunk { background-color: #ff0038; border-radius: 3px; }
            """)
        else:
            self.c2.setText(f"Stutter Risk: {risk_level.upper()}")
            self.c2.setStyleSheet("color: #4ade80; font-size: 9px; font-family: 'JetBrains Mono', monospace;")
            self.progress.setStyleSheet("""
                QProgressBar { background-color: #1a1d28; border-radius: 3px; }
                QProgressBar::chunk { background-color: #4ade80; border-radius: 3px; }
            """)


class TacticalTipWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TacticalTipPanel")
        self.setStyleSheet(TACTICAL_TIP_STYLE)
        self.setFixedSize(380, 180)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        # Header
        h_layout = QHBoxLayout()
        title = QLabel("QWEN3-4B TACTICAL ADVICE")
        title.setObjectName("TipHeader")
        h_layout.addWidget(title)
        h_layout.addStretch()

        live_badge = QLabel("LOCAL AI REASONING")
        live_badge.setStyleSheet("color: #d0bcff; font-size: 9px; font-weight: bold; background: rgba(139,92,246,0.2); padding: 2px 6px; border-radius: 4px;")
        h_layout.addWidget(live_badge)
        layout.addLayout(h_layout)

        # Tip Body
        self.tip_text = QLabel(
            "Hostile squad flanking via East Corridor choke in ~12s.\n"
            "Recommendation: Deploy thermal grenade at corridor doorway, "
            "then fallback 15m to elevated catwalk."
        )
        self.tip_text.setObjectName("TipBody")
        self.tip_text.setWordWrap(True)
        layout.addWidget(self.tip_text)

    def set_tip(self, text: str):
        self.tip_text.setText(text)
