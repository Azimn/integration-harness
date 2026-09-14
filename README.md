# Integration Harness

Integration Harness is a reuse-first experimental laboratory for persistent-agent, persona, memory, and cognitive-architecture components.

The project does not begin by designing a new mind. It begins by auditing existing implementations, preserving provenance, wrapping components behind small interfaces, and testing whether each mechanism produces a measurable longitudinal behavioral effect. New cognitive mechanisms require an explicit gap finding before implementation.

The repository is organized around an automated loop:

```text
proposal
  -> donor/reuse check
  -> wrap or adapt
  -> deterministic tests
  -> adversarial review
  -> behavioral / ablation tests
  -> revision
  -> second review
  -> merge decision
```

The first phase contains no new cognitive architecture. It establishes the donor registry, provenance rules, adapter boundaries, review artifacts, and CI that later integration experiments must pass.

Start with `docs/PROJECT_CHARTER.md`, `docs/DONOR_AUDIT.md`, and `docs/REVIEW_LOOP.md`.
