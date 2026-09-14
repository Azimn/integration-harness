# Experiment 001: Anima MemoryStore v0.1

## Question

Does Anima's existing memory machinery produce a reproducible, history-sensitive change in what remains available to recall after time and forgetting, without changing the donor implementation?

## Donor

- Repository: `huodebing-alt/anima`
- Revision: `ba215ce72bcaedd147d5d08de6e54555a62952c1`
- License: MIT
- Donor module: `anima/store.py`
- Upstream deterministic test target: `tests/test_store.py`

The harness does not copy or rewrite `MemoryStore`. CI checks out the pinned donor revision separately and places it on `PYTHONPATH`. `AnimaMemoryAdapter` is a thin translation boundary around the donor object.

## Narrow hypothesis

Repeated retrieval history can change durable memory availability after later decay and forgetting.

This is not a claim that Anima's memory system improves character believability. It is a mechanism-level prerequisite test.

## Matched histories

Each condition begins with the same two memories at the same virtual time and with equal importance:

- `shared orchard promise`
- `shared river promise`

History A retrieves the orchard memory once per simulated day for five days. History B retrieves the river memory on the same schedule. The control performs no retrieval. All conditions then advance to day 60, run Anima's unmodified `decay_and_forget`, and receive the same final cue: `shared`.

The deterministic embedding makes both memories equally relevant to the final cue. The intended causal difference is therefore prior retrieval history rather than a different present stimulus.

## Expected result

- History A retains the orchard memory while the unrehearsed river memory is archived.
- History B retains the river memory while the unrehearsed orchard memory is archived.
- The no-rehearsal control archives both.

If this fails, the donor's retrieval/decay combination has not demonstrated the path-dependent durability claim under the harness conditions.

## Evidence boundaries

A pass establishes only that the donor memory subsystem can preserve different accessible pasts under otherwise matched final conditions. It does not establish that retrieval reinforcement alone is the causal factor, because Anima retrieval updates `last_access_ts`, `access_count`, and `strength`, all of which interact with later decay. It also does not establish that an agent using the surviving memory will act differently.

Those are later experiments. The next stage, if this mechanism passes, should connect the memory adapter to a fixed downstream decision policy and test whether history-dependent recall causes a measurable behavioral divergence while holding the policy constant.

## Reproduction

CI checks out the pinned Anima repository and runs:

```text
python -m unittest discover -s .donors/anima/tests -p 'test_store.py' -v
```

Then the harness-specific experiment runs with both `src` and the donor checkout on `PYTHONPATH`.
