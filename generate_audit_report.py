#!/usr/bin/env python3
"""
Turn harness JSON (results_*.json) into MD + HTML audit report for the data room.

Usage:
  python generate_audit_report.py results_real.json
  python generate_audit_report.py results_real.json --out audit_report
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Dict, List


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def md_escape(s: str) -> str:
    return s.replace("|", "\\|").replace("\n", " ")


def build_md(data: dict) -> str:
    summary = data.get("summary") or {}
    rows = data.get("rows") or []
    modes = set()
    for r in rows:
        modes.add(r.get("generator_mode", "?"))
    is_mock = modes == {"mock"} or (len(modes) == 1 and "mock" in modes)

    lines: List[str] = []
    lines.append("# Cranium Core — Behavioral Receipts Audit")
    lines.append("")
    lines.append(f"- **Corpus:** `{data.get('corpus_id', '?')}`")
    lines.append(f"- **Methodology:** `{data.get('methodology', '?')}`")
    lines.append(f"- **Generated:** `{data.get('timestamp', time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))}`")
    lines.append(f"- **Real run requested:** `{data.get('real_requested', False)}`")
    lines.append(f"- **Generator modes observed:** `{sorted(modes)}`")
    lines.append("")
    if is_mock:
        lines.append("> **NOT ACQUISITION EVIDENCE.** Generator mode is mock only. Re-run with `--real` and a live API key.")
        lines.append("")
    else:
        lines.append("> Live model outputs present. Still subject to human spot-check before publication.")
        lines.append("")

    lines.append("## Summary by condition")
    lines.append("")
    lines.append("| Condition | N | Canon acc. | Identity block OK | Dup pair rate | Modes |")
    lines.append("|-----------|---|------------|-------------------|---------------|-------|")
    for cond, s in summary.items():
        lines.append(
            f"| {cond} | {s.get('n')} | {s.get('canon_accuracy')} | "
            f"{s.get('identity_block_ok_rate')} | {s.get('duplicate_pair_rate')} | "
            f"{s.get('generator_modes')} |"
        )
    lines.append("")

    # Honest canon flag
    canons = {
        c: summary[c]["canon_accuracy"]
        for c in summary
        if summary[c].get("canon_accuracy") is not None
    }
    if canons:
        best = max(canons.values())
        cran = canons.get("cranium")
        if cran is not None and cran < best:
            lines.append("## Honest flag")
            lines.append("")
            lines.append(
                f"**Cranium canon_accuracy ({cran}) is below best baseline ({best}).** "
                "Do not market canon superiority. Treat as known gap + fix path."
            )
            lines.append("")

    lines.append("## Sample rows (anonymized outputs)")
    lines.append("")
    lines.append("| Condition | Prompt | Type | Mode | Canon hit | Block OK | Output (truncated) |")
    lines.append("|-----------|--------|------|------|-----------|----------|------------------|")
    for r in rows[:40]:
        out = md_escape((r.get("output") or "")[:160])
        lines.append(
            f"| {r.get('condition')} | {r.get('prompt_id')} | {r.get('prompt_type')} | "
            f"{r.get('generator_mode')} | {r.get('canon_hit')} | {r.get('blocked_ok')} | {out} |"
        )
    if len(rows) > 40:
        lines.append("")
        lines.append(f"_… {len(rows) - 40} more rows in raw JSON._")
    lines.append("")
    lines.append("## Methodology notes")
    lines.append("")
    lines.append("- Lexical canon scoring is a **fallback**; prefer NLI/LLM-judge + human blind review for publication.")
    lines.append("- Identity block OK uses refusal/protect heuristics on adversarial prompts.")
    lines.append("- Duplicate rate is pairwise lexical Jaccard on outputs within a condition.")
    lines.append("")
    return "\n".join(lines)


def build_html(md_body: str, title: str = "Cranium Receipts Audit") -> str:
    # Minimal HTML wrapper — no external deps
    escaped = (
        md_body.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>{title}</title>
<style>
  body {{ font-family: system-ui, sans-serif; max-width: 960px; margin: 2rem auto; padding: 0 1rem; line-height: 1.45; }}
  pre {{ white-space: pre-wrap; background: #f6f8fa; padding: 1rem; border-radius: 8px; }}
  .banner {{ background: #fff3cd; border: 1px solid #ffecb5; padding: 0.75rem 1rem; border-radius: 8px; }}
</style>
</head>
<body>
<h1>{title}</h1>
<p class="banner">Raw markdown report embedded below. Prefer the .md file for editing; use this HTML for quick browser review.</p>
<pre>{escaped}</pre>
</body>
</html>
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("results_json", type=str)
    ap.add_argument("--out", type=str, default="audit_report")
    args = ap.parse_args()
    data = load(Path(args.results_json))
    md = build_md(data)
    out_base = Path(args.out)
    md_path = out_base.with_suffix(".md") if out_base.suffix == "" else out_base
    if md_path.suffix != ".md":
        md_path = Path(str(out_base) + ".md")
    html_path = md_path.with_suffix(".html")
    md_path.write_text(md, encoding="utf-8")
    html_path.write_text(build_html(md), encoding="utf-8")
    print(f"Wrote {md_path}")
    print(f"Wrote {html_path}")


if __name__ == "__main__":
    main()
