"""
CogniEdge Gaming HUD Overlay - QSS Stylesheets
Derived from CogniEdge Snapdragon Tactical Armor Palette:
- Primary Crimson: #ff0038 / #ff2a55
- Stealth Graphite & Carbon: #08090c / #12141c / #1a1d28
- Border Accents: rgba(255, 0, 56, 0.5) / rgba(255, 255, 255, 0.12)
- High-Vis Cyber White: #f8fafc / #dfe2ee
"""

RADAR_PANEL_STYLE = """
QFrame#RadarPanel {
    background-color: rgba(12, 14, 20, 0.94);
    border: 2px solid rgba(255, 0, 56, 0.6);
    border-radius: 12px;
}
QLabel {
    color: #f8fafc;
    font-family: 'Space Grotesk', 'Segoe UI', sans-serif;
}
QLabel#RadarTitle {
    color: #ff0038;
    font-size: 15px;
    font-weight: bold;
    letter-spacing: 0.5px;
}
QLabel#RadarSubtitle {
    color: #8a93a8;
    font-size: 11px;
    font-family: 'JetBrains Mono', monospace;
}
QLabel#ThreatActive {
    color: #ffffff;
    background-color: #ff0038;
    border: 1px solid #ff2a55;
    border-radius: 4px;
    padding: 3px 8px;
    font-weight: bold;
    font-size: 10px;
    font-family: 'JetBrains Mono', monospace;
}
"""

TELEMETRY_PANEL_STYLE = """
QFrame#TelemetryPanel {
    background-color: rgba(12, 14, 20, 0.88);
    border: 1px solid rgba(255, 0, 56, 0.35);
    border-radius: 12px;
}
QLabel {
    color: #f8fafc;
    font-family: 'JetBrains Mono', 'Consolas', monospace;
}
QLabel#TelemTitle {
    color: #ff0038;
    font-size: 13px;
    font-weight: bold;
}
QLabel#StatValueHighlight {
    color: #ffffff;
    font-size: 20px;
    font-weight: bold;
}
QLabel#StatValueZeroDrop {
    color: #ff2a55;
    font-size: 20px;
    font-weight: bold;
}
"""

TACTICAL_TIP_STYLE = """
QFrame#TacticalTipPanel {
    background-color: rgba(12, 14, 20, 0.92);
    border: 2px solid rgba(255, 0, 56, 0.55);
    border-radius: 12px;
}
QLabel {
    color: #f8fafc;
    font-family: 'Inter', 'Segoe UI', sans-serif;
}
QLabel#TipHeader {
    color: #ff0038;
    font-size: 14px;
    font-weight: bold;
    letter-spacing: 0.5px;
}
QLabel#TipBody {
    color: #dfe2ee;
    font-size: 12px;
    line-height: 1.4;
}
QLabel#SynergyBadge {
    color: #ff2a55;
    background-color: rgba(255, 0, 56, 0.15);
    border: 1px solid rgba(255, 0, 56, 0.4);
    border-radius: 4px;
    padding: 3px 8px;
    font-size: 11px;
    font-family: 'JetBrains Mono', monospace;
    font-weight: bold;
}
"""
