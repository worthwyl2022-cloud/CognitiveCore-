#!/usr/bin/env python3
"""
Package harness results + audit report + methodology into a data-room zip.

Usage:
  python export_receipts.py results_real.json --audit audit_report.md --out receipts_pack.zip
"""

from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("results_json")
    ap.add_argument("--audit", default="audit_report.md")
    ap.add_argument("--methodology", default="methodology.json")
    ap.add_argument("--corpus", default="corpus_frozen_v1.json")
    ap.add_argument("--out", default="receipts_pack.zip")
    args = ap.parse_args()

    root = Path(__file__).resolve().parent
    files = []
    for p in [
        Path(args.results_json),
        Path(args.audit),
        Path(args.audit).with_suffix(".html"),
        root / args.methodology if not Path(args.methodology).is_file() else Path(args.methodology),
        root / args.corpus if not Path(args.corpus).is_file() else Path(args.corpus),
    ]:
        if p.is_file():
            files.append(p)

    # Manifest
    data = json.loads(Path(args.results_json).read_text(encoding="utf-8"))
    modes = sorted({r.get("generator_mode") for r in data.get("rows") or []})
    manifest = {
        "corpus_id": data.get("corpus_id"),
        "timestamp": data.get("timestamp"),
        "real_requested": data.get("real_requested"),
        "generator_modes": modes,
        "warning": (
            "MOCK ONLY — not acquisition evidence"
            if modes == ["mock"]
            else "Contains live model outputs; human review recommended before external share"
        ),
        "files": [f.name for f in files],
    }
    manifest_path = root / "_receipts_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    files.append(manifest_path)

    out = Path(args.out)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            z.write(f, arcname=f.name)
    print(f"Wrote {out} ({len(files)} files)")
    print("Manifest warning:", manifest["warning"])


if __name__ == "__main__":
    main()
