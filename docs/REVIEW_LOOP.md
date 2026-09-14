# Automated Review Loop

Every substantive change should move through the same evidence loop. The loop is designed to make reinvention, weak causal claims, and architecture drift visible before merge.

```text
1. PROPOSE
   State the behavioral failure or research question.

2. SEARCH / REUSE CHECK
   Identify internal and external donors that already address the mechanism.
   Record why each is reused, adapted, wrapped, used as a baseline, or rejected.

3. IMPLEMENT OR ADAPT
   Make the smallest change capable of testing the claim.
   Preserve donor semantics where prior evidence depends on them.

4. DETERMINISTIC TEST
   Verify interfaces, persistence, invariants, reproducibility, and failure handling.

5. ADVERSARIAL REVIEW
   A reviewer tries to invalidate the change rather than improve its presentation.

6. BEHAVIORAL TEST
   Compare matched histories, baselines, ablations, or longitudinal trajectories.

7. REVISE
   The implementation agent responds to every high-severity objection with a change,
   evidence, or an explicit rejection rationale.

8. SECOND REVIEW
   Re-run the critique against the revised implementation and evidence.

9. MERGE DECISION
   Merge only when unresolved high-severity objections are absent and the evidence
   supports the claim actually made.
```

## Required adversarial questions

The reviewer must check whether the change rebuilds a mechanism that already exists, whether the strongest relevant donor was examined, whether a donor was modified enough to invalidate prior evidence, whether the claimed effect is actually caused by the new mechanism, whether a simpler baseline explains the result, whether language-model output is secretly doing work attributed to the architecture, whether the system can be ablated cleanly, whether state crosses an authority boundary incorrectly, whether persistence survives restart when claimed, and whether provenance and licensing are complete.

## Review artifacts

Each substantive experiment produces a machine-readable review artifact under `reviews/`. Bootstrap validation uses JSON so it can run on the Python standard library alone.

A review artifact contains an experiment identifier, implementation revision, reviewer role, verdict, severity-tagged objections, evidence references, and disposition for each objection. High-severity objections with disposition `open` block a passing review state.

## Revision-aware merge gate

A review cannot simply exist somewhere in history. CI requires a passing review that covers the latest substantive implementation state.

The reviewer records the exact implementation commit it examined. The review artifact must be committed after that implementation commit. Because adding the review file changes HEAD, exact equality between the reviewed revision and HEAD would be self-referential. The gate therefore accepts the review only when the reviewed implementation revision is an ancestor of HEAD and every later tree change is another JSON review artifact directly under `reviews/`.

Any code, test, donor-registry, workflow, or substantive documentation change after the reviewed implementation revision invalidates coverage and requires another review cycle. CI uses full git history to enforce this rule.

## Agent roles

The implementation agent optimizes for a correct minimal implementation. The reviewer optimizes for finding reasons the implementation or interpretation is wrong. The tester optimizes for reproducibility and adversarial cases. The synthesis pass decides what the evidence supports after those roles disagree.

These are logical roles. They may be performed by different models, repeated model calls, humans, or a mixture. The repository should not depend on one vendor or model to enforce the process.

## Iteration count

The loop continues until the acceptance criteria pass or the experiment is rejected. A fixed number of cycles is useful for stress testing, but merge status should depend on evidence and unresolved objections rather than an arbitrary cycle count.
