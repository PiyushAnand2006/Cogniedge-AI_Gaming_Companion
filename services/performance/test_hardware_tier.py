"""
Standalone Hardware Tier Detection Test Script
Prints detected RAM, logical/physical CPU core count, GPU presence/backend,
and resulting hardware_tier on the current machine.
"""

import os
import sys
import json

# Ensure services directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from hardware_tier import HardwareTierDetector, get_tier_configuration


def main():
    print("=" * 60)
    print("  COGNIEDGE HARDWARE TIER DETECTION (Stage 1 Standalone Test)")
    print("=" * 60)

    detector = HardwareTierDetector()
    result = detector.detect_hardware_tier()

    print(f"\n[1] Detected System RAM:        {result.total_ram_gb} GB")
    print(f"[2] CPU Core Count:             {result.logical_cpu_cores} Logical ({result.physical_cpu_cores} Physical)")
    print(f"[3] GPU Detected:               {result.gpu_detected}")
    print(f"[4] GPU Name:                   {result.gpu_name or 'None (or Integrated only)'}")
    print(f"[5] GPU Acceleration Backend:   {result.gpu_backend or 'None'}")
    print(f"[6] Resulting hardware_tier:    >> {result.hardware_tier.upper()} <<")
    print(f"[7] Tier Assignment Reason:     {result.reason}")

    print("\n" + "-" * 60)
    print("  Tier-to-Configuration Mapping (Technical Requirements §6.2):")
    print("-" * 60)
    config = get_tier_configuration(result.hardware_tier)
    print(json.dumps(config, indent=2))

    print("\n" + "-" * 60)
    print("  Exact GET /system/telemetry Response (§3.1 Schema):")
    print("-" * 60)
    telemetry = detector.get_telemetry_payload()
    print(json.dumps(telemetry, indent=2))
    print("=" * 60)


if __name__ == "__main__":
    main()
