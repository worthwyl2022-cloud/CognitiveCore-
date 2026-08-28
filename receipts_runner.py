#!/usr/bin/env python3
"""
Alias entrypoint for real behavioral receipts.

  export CRANIUM_LLM=gemini
  export GEMINI_API_KEY=your_key_here
  python receipts_runner.py

This wraps run_harness.py --real and writes results_real.json.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> int:
    if not os.environ.get("GEMINI_API_KEY") and not os.environ.get("GOOGLE_API_KEY"):
        print("ERROR: Set GEMINI_API_KEY (or GOOGLE_API_KEY) before running real receipts.")
        print("Get a key: https://aistudio.google.com/apikey")
        print("")
        print("Example:")
        print("  export CRANIUM_LLM=gemini")
        print("  export GEMINI_API_KEY=...")
        print("  python receipts_runner.py")
        return 2

    os.environ.setdefault("CRANIUM_LLM", "gemini")
    # Accept GOOGLE_API_KEY as alias
    if not os.environ.get("GEMINI_API_KEY") and os.environ.get("GOOGLE_API_KEY"):
        os.environ["GEMINI_API_KEY"] = os.environ["GOOGLE_API_KEY"]

    out = ROOT / "results_real.json"
    cmd = [
        sys.executable,
        str(ROOT / "run_harness.py"),
        "--real",
        "--out",
        str(out),
    ]
    print("Running:", " ".join(cmd))
    print("CRANIUM_LLM=", os.environ.get("CRANIUM_LLM"))
    rc = subprocess.call(cmd, cwd=str(ROOT))
    if rc != 0:
        return rc
    print("")
    print("Next:")
    print("  python generate_audit_report.py results_real.json --out audit_report")
    print("  python export_receipts.py results_real.json --audit audit_report.md --out receipts_pack.zip")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
