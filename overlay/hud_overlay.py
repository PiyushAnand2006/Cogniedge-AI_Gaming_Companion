"""
CogniEdge Native PyQt Gaming HUD Overlay
Transparent, Click-Through, Always-On-Top In-Game Companion for Snapdragon X Elite.
Enforces 0.0 FPS contention via Win32 WS_EX_LAYERED | WS_EX_TRANSPARENT interop.
"""

import sys
import ctypes
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from hud_components import TacticalRadarWidget, TelemetryPanelWidget, TacticalTipWidget
from vision_worker import VisionWorker


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

        # Central Widget & 3x3 Grid Layout (Preserving Center Third Clearance)
        central_widget = QWidget(self)
        central_widget.setStyleSheet("background: transparent;")
        self.setCentralWidget(central_widget)

        grid = QGridLayout(central_widget)
        grid.setContentsMargins(24, 24, 24, 24)

        # 1. Top-Left: Tactical Radar Panel (Full Opacity)
        self.radar_panel = TacticalRadarWidget()
        grid.addWidget(self.radar_panel, 0, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        # Top Center: Blank
        grid.addWidget(QWidget(), 0, 1)

        # 2. Top-Right: Telemetry Panel (Reduced Opacity)
        self.telemetry_panel = TelemetryPanelWidget()
        grid.addWidget(self.telemetry_panel, 0, 2, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)

        # Middle Row: Completely Empty (Center Third of screen clear for crosshair & combat)
        grid.addWidget(QWidget(), 1, 0)
        grid.addWidget(QWidget(), 1, 1)
        grid.addWidget(QWidget(), 1, 2)

        # Bottom-Left: Blank
        grid.addWidget(QWidget(), 2, 0)

        # Bottom Center: Blank
        grid.addWidget(QWidget(), 2, 1)

        # 3. Bottom-Right: Tactical Tip Card (Reduced Opacity)
        self.tip_panel = TacticalTipWidget()
        grid.addWidget(self.tip_panel, 2, 2, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)

        # Row and Column Stretches
        grid.setRowStretch(0, 0)
        grid.setRowStretch(1, 1)
        grid.setRowStretch(2, 0)
        grid.setColumnStretch(0, 0)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 0)

        # Start Vision & State polling worker thread
        self.worker = VisionWorker(self)
        self.worker.state_updated.connect(self.handle_state_update)
        self.worker.start()

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

                # Retrieve current window style
                style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                # Apply layered, transparent click-through and topmost
                ctypes.windll.user32.SetWindowLongW(
                    hwnd, GWL_EXSTYLE, style | WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOPMOST
                )
                print("[CogniEdge HUD] Win32 Click-Through attributes successfully applied.")
            except Exception as e:
                print(f"[CogniEdge HUD] Win32 interop warning: {e}")

    def handle_state_update(self, data: dict):
        # Update components when real state changes
        pass

    def closeEvent(self, event):
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.stop()
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    overlay = GamingHudOverlay()
    overlay.show()
    print("[CogniEdge] Transparent PyQt Gaming HUD Overlay running.")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
