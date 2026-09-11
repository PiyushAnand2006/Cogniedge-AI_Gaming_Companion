"""
CogniEdge Native PyQt Gaming HUD Overlay
Transparent, Click-Through, Always-On-Top In-Game Companion.
Zero-game-injection HUD overlay connecting to local CogniEdge AI Service.
"""

import sys
import ctypes
import urllib.request
import json
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor

from hud_components import TacticalRadarWidget, TelemetryPanelWidget, TacticalTipWidget


class GamingHudOverlay(QMainWindow):
    def __init__(self):
        super().__init__()

        # Frameless, Always on Top, Translucent
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.SubWindow
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)

        # Full Screen Overlay
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)

        # Central Widget & 3x3 Grid Layout (Preserving Center Third Clearance for crosshairs)
        central_widget = QWidget(self)
        central_widget.setStyleSheet("background: transparent;")
        self.setCentralWidget(central_widget)

        grid = QGridLayout(central_widget)
        grid.setContentsMargins(24, 24, 24, 24)

        # 1. Top-Left: Tactical Radar Panel
        self.radar_panel = TacticalRadarWidget()
        grid.addWidget(self.radar_panel, 0, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        # Top Center: Blank
        grid.addWidget(QWidget(), 0, 1)

        # 2. Top-Right: Telemetry Panel
        self.telemetry_panel = TelemetryPanelWidget()
        grid.addWidget(self.telemetry_panel, 0, 2, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

        # Middle Row: Completely Empty (Center gameplay area kept clear)
        grid.addWidget(QWidget(), 1, 0)
        grid.addWidget(QWidget(), 1, 1)
        grid.addWidget(QWidget(), 1, 2)

        # Bottom-Left: Blank
        grid.addWidget(QWidget(), 2, 0)

        # Bottom Center: Blank
        grid.addWidget(QWidget(), 2, 1)

        # 3. Bottom-Right: Tactical Tip Card
        self.tip_panel = TacticalTipWidget()
        grid.addWidget(self.tip_panel, 2, 2, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)

        # Stretches
        grid.setRowStretch(0, 0)
        grid.setRowStretch(1, 1)
        grid.setRowStretch(2, 0)
        grid.setColumnStretch(0, 0)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 0)

        # Polling Timer for live telemetry & game updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.poll_overlay_state)
        self.timer.start(500)  # 500ms refresh

    def showEvent(self, event):
        super().showEvent(event)
        self.apply_win32_clickthrough()

    def apply_win32_clickthrough(self):
        """Apply Win32 WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOPMOST for true click-through"""
        if sys.platform == "win32":
            try:
                hwnd = int(self.winId())
                GWL_EXSTYLE = -20
                WS_EX_LAYERED = 0x00080000
                WS_EX_TRANSPARENT = 0x00000020
                WS_EX_TOPMOST = 0x00000008

                style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                ctypes.windll.user32.SetWindowLongW(
                    hwnd, GWL_EXSTYLE, style | WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOPMOST
                )
            except Exception as e:
                print(f"[CogniEdge HUD] Win32 click-through note: {e}")

    def poll_overlay_state(self):
        try:
            req = urllib.request.Request("http://127.0.0.1:8088/overlay/state")
            with urllib.request.urlopen(req, timeout=0.8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                self.telemetry_panel.update_metrics(
                    fps=data.get("game_fps", 144.0),
                    one_pct=data.get("one_pct_low", 95.0),
                    gpu_usage=data.get("gpu_usage", 85.0),
                    stutter_risk=data.get("stutter_risk", 0.12),
                    risk_level=data.get("risk_level", "low"),
                    provenance=data.get("provenance", "MEASURED")
                )
                self.radar_panel.update_radar(
                    hostiles=data.get("hostiles_count", 0),
                    threat_vector=data.get("threat_vector", "Clear"),
                    player_hp=data.get("player_hp", 100)
                )
        except Exception:
            pass  # Backend not ready or offline


def main():
    app = QApplication(sys.argv)
    overlay = GamingHudOverlay()
    overlay.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
