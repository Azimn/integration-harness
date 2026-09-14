# Project Charter

## Purpose

Integration Harness exists to determine which existing mechanisms are worth combining into a persistent artificial subject or character, and which apparent gaps still require new implementation.

The project is an experimental integration platform, not a new monolithic cognitive architecture.

## Research question

Can a persistent character become measurably less artificial over long time horizons by combining already implemented mechanisms for memory, continuity, motivation, relationships, planning, self-modeling, consolidation, forgetting, associative recall, and autonomous operation?

## Governing rule

Reuse before reimplementation.

A mechanism may be implemented from scratch only after the repository records one of these findings:

1. no suitable donor implementation could be located;
2. available implementations cannot be reused because of licensing or provenance constraints;
3. available implementations fail the required behavioral test;
4. available implementations violate an authority, safety, or architecture boundary that cannot be preserved through wrapping or adaptation;
5. a clean implementation is necessary for a controlled baseline or ablation.

## Experimental discipline

Every adopted mechanism must have a named behavioral claim and a falsifiable test. Passing unit tests proves that software behaves as coded. It does not prove that the mechanism improves persistent character behavior.

Every experiment should include the strongest practical simpler baseline. When possible, mechanisms should be ablated independently.

The harness must distinguish developer-visible substrate state from character-accessible experience. Raw telemetry, retrieval scores, hidden identifiers, scalar relationship values, confidence values, and internal bookkeeping are not automatically part of the character's subjective world.

Language models are components, not architecture authorities. Canonical identity, persistence, world state, outcomes, and other authoritative state must have explicit owners outside free-form generated text unless an experiment deliberately tests the alternative.

## Provenance

Every donor entry records the source repository, revision, license, relevant files, tests, and the exact reuse decision. Direct copying of third-party code is permitted only when its license allows it and attribution requirements are preserved.

Prior internal experiments are donors too. Existing work should be audited before equivalent mechanisms are rewritten.

## Integration strategy

The default reuse unit is a narrow mechanism behind an adapter, not an entire repository. Whole-system adoption requires stronger evidence than module-level reuse.

The initial thin vertical slice is:

```text
experience
  -> state change
  -> memory / appraisal
  -> action or non-action
  -> outcome
  -> consolidation / learning
  -> changed response to a later matched situation
```

This slice must work before large numbers of subsystems are combined.

## Review policy

Every substantive change follows the process in `REVIEW_LOOP.md`. An adversarial reviewer is expected to search for reinvention, invalid comparisons, hidden LLM delegation, missing baselines, weak causal evidence, provenance problems, and unnecessary complexity.

## Current phase

Bootstrap only. Build donor registry, validation, review artifacts, CI, and the first donor audits. Do not add a new cognitive subsystem during this phase.
