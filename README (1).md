# LLM-Judge Contradiction Adapter

## Role

| Stage | Component | Job |
|-------|-----------|-----|
| 1 | `ContradictionEngine` (proxy v2) | Fast lexical / paraphrase / mention gates |
| 2 | `LlmJudgeContradiction` | Real model labels `contradicts \| neutral \| supports` per locked principle |

Use the judge for **diligence-grade** identity rejection. Keep the proxy as prefilter to save cost and catch slogan attacks offline.

## Wire-in (SubstrateCore sketch)

```kotlin
val judge = LlmJudgeContradiction(
    semantic = semantic,
    proxy = contradiction,
    model = generativeModel,
    alwaysJudgeAdversarial = true
)

// after generation, instead of contradiction.evaluate(...):
val verdict = judge.evaluate(output, field.memory.lockedIdentity(), metrics)
if (verdict.violated) { /* PROTECT reject / revise */ }
```

## Honest limits

- Judge quality = underlying model + prompt; still needs human spot-checks for published receipts.
- Cost/latency: budget 1 judge call per locked principle (capped at 6) on escalate paths.
- `matchKind == "llm_judge"` in logs for audit.

## Files

- `LlmJudgeContradiction.kt` — drop into `com.example.core.judge`
