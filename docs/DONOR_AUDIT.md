# Donor Audit

Status: bootstrap working document.

This audit extends existing donor work rather than replacing it. `Azimn/DUCK` already contains `docs/DONOR_AUDIT_v0.1.md`; that document is seed evidence and should be rechecked against live code before integration decisions are promoted.

## Decision vocabulary

`concept_only` means the donor is useful as prior art or design evidence.

`test_pattern` means the donor contributes an evaluation method or fixture but not production code.

`wrap` means the donor mechanism should initially run with its semantics intact behind an adapter.

`adapt` means reuse is promising but controlled modification is required.

`direct_reuse` means code may be imported substantially unchanged after revision, license, and tests are pinned.

`reject` means the mechanism should not enter the current integration path.

Every decision remains provisional until the relevant revision and tests are recorded.

## Internal donor seed

### Azimn/DUCK

Current live README describes a persistent subject simulator with an explicit subject-access firewall, motivated prospective agency, endogenous goal formation, route selection, persistent plan state, outcome-driven replanning, and optional inner cognition. The current line is valuable both as a mechanism donor and as a source of longitudinal causal tests.

Provisional decision: `wrap` or `adapt` at subsystem level. Do not make DUCK the base class for the new harness.

### Azimn/Persona-and-Jelly-Sandwich-

DUCK's earlier donor audit identifies this repository as the strongest source for paired-history causal continuity testing and the Gelatinblob sidecar as a later donor for path-dependent latent plasticity.

Provisional decision: `test_pattern` for paired-history continuity first. Gelatinblob remains `concept_only` or `adapt` pending a fresh audit.

### Azimn/TinyPersonaEngine

DUCK's earlier donor audit identifies a useful separation between authoritative world facts, perception, belief, experience, and subjective completion.

Provisional decision: `concept_only` and `test_pattern` until a perception/world-authority failure appears in the integration slice.

### Azimn/persona_engine_PYTHONX

DUCK's earlier audit treats this as a mature engineering quarry containing persistence, autobiographical provenance, commitments, replay/recovery, renderer authority boundaries, action-consequence loops, epistemic revision, and lifecycle tests.

Provisional decision: audit by mechanism, never wholesale adoption.

### Azimn/FirstPersonLoopTest

The live README describes a deliberately small runtime in which hidden numeric bodily state is converted to first-person natural-language experience before character access. It separates private inner thought from intentional speech and provides a scripted backend for architecture testing without an LLM.

Provisional decision: `adapt` candidate for substrate-to-phenomenology transduction and `test_pattern` for LLM-free control-flow tests.

### Azimn/rho

Existing DUCK donor notes identify a persistent heartbeat, scheduled check-ins, memory files, and task triggers.

Provisional decision: `concept_only` until continuous scheduling is needed, then compare against Anima's heartbeat before implementation.

## External donor seed

### huodebing-alt/anima

Verified license: MIT.

The live code separates several useful concerns. `anima/store.py` provides SQLite persistence, memory kinds, embedding-based recall, access reinforcement, strength decay, archive/purge behavior, self-model versioning, and goals. The embedding function and clock are injected, which makes isolated deterministic testing practical.

`anima/sleep.py` implements salience tagging, episode-to-semantic consolidation, reflection, dream recombination and insight mining, deterministic downscaling/forgetting, and self-model rewriting. Several phases depend directly on LLM prompts. The file includes explicit perspective normalization to repair cases where user facts drift into first-person summaries.

`anima/agent.py` implements the continuous heartbeat, fatigue and sleep pressure, sensors, restart continuity, reflex conversation, and a slower contemplative path. The scheduler itself is operationally useful, while the slow cognition path delegates thought and action proposals to the LLM.

Provisional subsystem decisions:

- memory persistence and deterministic memory dynamics: `adapt`
- retrieval reinforcement: `wrap` for controlled comparison
- decay, archive, purge: `adapt`
- heartbeat and sleep scheduling: `wrap`
- LLM consolidation: `wrap` as an experimental donor
- canonical self-model rewriting: `reject` as identity authority; potentially retain as a non-authoritative narrative-self experiment
- dream insight mining: `test_pattern` and ablation candidate only
- whole repository adoption: `reject`

## Audit order

The first code-level audits should cover Anima, DUCK, FirstPersonLoopTest, Persona-and-Jelly-Sandwich-, TinyPersonaEngine, and persona_engine_PYTHONX. The harness should then add newer external memory and agent systems only after their code, license, and reproducibility status are verified.

## Promotion rule

A donor mechanism moves from provisional to accepted only when its revision is pinned, its relevant tests are reproduced or replaced with stronger tests, its license/provenance is recorded, its adapter boundary is explicit, and an ablation or matched-baseline experiment supports the behavioral claim for which it is being adopted.
