# Cranium Substrate — Complete (gaps filled)

**Owner path:** drop these packages into an Android/`com.example.core` tree **or** keep as the acquisition core for `CognitiveCore-`.

This is **not** the React/Vite rewrite that overwrote `WorthWyl-game-changer` main.  
This is the **Kotlin governance substrate** with the upgrades from the Aug 2026 build line.

## Layout

```
substrate/     Core field + governance loop
immune/        Adaptive constitutional / immune tier
judge/         LLM-judge contradiction adapter (optional, behind proxy)
product/       Multi-project API (constitution, quarantine, audit)
docs/          Honest acquisition one-pager
benchmark/     Frozen corpus + harness + receipts scripts
```

## Gaps that were filled (vs early v2 lab)

| Gap | Module |
|-----|--------|
| Canon-first factual lane | `CanonLane.kt` |
| NLI-proxy v2 (mention vs endorse, paraphrase, sabotage) | `ContradictionEngine.kt` |
| Evaluation-gated write-back | `OutputEvaluator.kt` |
| Reasoning scale / multi-round | `DeliberationEngine.kt` |
| Real conflict + identity_pressure metrics | `ResonanceField.kt` |
| Hard-block set + identity-biased retrieval + full loop | `SubstrateCore.kt` |
| Immune hard-block + constraints | `CraniumImmuneLayer.kt` |
| LLM judge behind proxy | `judge/LlmJudgeContradiction.kt` |
| Project isolation / approve-reject | `product/.../ProjectStore.kt` |

## Package map (Android)

```
com.example.core.substrate.*   ← substrate/*.kt
com.example.core.immune.*      ← immune/*.kt
com.example.core.judge.*       ← judge/*.kt
com.example.core.product.*     ← product/src/main/java/.../product/*.kt
```

`SubstrateCore` expects Gemini via `GenerativeModel` and `CraniumImmuneLayer`.

## Benchmark / receipts

```bash
cd benchmark
python3 run_harness.py                          # mock
export CRANIUM_LLM=gemini GEMINI_API_KEY=...
python3 receipts_runner.py                      # live
python3 generate_audit_report.py results_real.json --out audit_report
```

## Restore note

GitHub `WorthWyl-game-changer` **main** currently hosts the React terminal.  
Recover Kotlin app history from older commits, or re-seed from this zip + your full `app/` tree from a pre-overwrite SHA.
