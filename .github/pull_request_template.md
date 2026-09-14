## Research claim

What behavioral failure, research question, or infrastructure requirement does this change address?

## Reuse check

Which internal and external donors were examined before implementation?

Why is the selected approach `wrap`, `adapt`, `direct_reuse`, `test_pattern`, `concept_only`, or new implementation?

If new code implements a cognitive mechanism, what documented gap makes reimplementation necessary?

## Provenance

Source repository and revision:

License and attribution requirements:

Relevant donor files and tests:

## Evidence

Deterministic tests added or reproduced:

Behavioral baseline:

Ablation or matched-history comparison:

Observed effect:

## Authority boundaries

What state is authoritative?

What state is character-accessible?

What work is delegated to an LLM, if any?

## Adversarial review

Review artifact path:

Unresolved high-severity objections: none / explain

## Rollback

How can this mechanism be disabled or replaced without corrupting persistent state?

## Checklist

- [ ] Existing donors were searched before new implementation.
- [ ] Provenance and revision are recorded.
- [ ] License is verified before direct code reuse.
- [ ] Deterministic tests pass.
- [ ] The claimed behavioral effect has a baseline or ablation where applicable.
- [ ] Hidden substrate state does not leak into character experience unintentionally.
- [ ] LLM responsibilities are explicit.
- [ ] No open high-severity review objection remains if this PR is marked ready to merge.
