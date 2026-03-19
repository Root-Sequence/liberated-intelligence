# Liberated Intelligence roadmap note

This note captures the next practical steps for the `liberated-intelligence` repository as it shifts from concept collection toward a small but coherent research system.

## Near-term priorities

### 1. Consolidate the MVSA loop

- update `cli/mvsa_loop/README.md` to document Ollama mode and `--dry-run`
- test `mvsa_loop_v2.py` in dry-run mode against a real local model
- remove or archive `mvsa_loop.py` once v2 is stable
- consider renaming `mvsa_loop_v2.py` back to `mvsa_loop.py` after replacement

### 2. Complete the models layer

- add `MODELS/reflective-accountability.md`
- update `MODELS/README.md` to include both:
  - Reflective Accountability
  - Minimum Viable Self-Aware System (MVSA)
- ensure `MODELS.md` remains a top-level index rather than duplicating model content

### 3. Strengthen observability

- run `cli/mvsa_loop/audit.py` after multiple revisions
- identify confidence drift, oscillation, and unused beliefs
- expand audit output later to include:
  - repeated contradiction patterns
  - unstable beliefs
  - overconfident beliefs

## Medium-term priorities

### 4. Tighten the reflection schema

Current fields such as `evidence`, `contradictions`, and `harm` are string-like. They should likely become arrays to better support auditing and comparison.

Potential direction:

- `evidence`: list
- `contradictions`: list
- `harm`: list
- optional `confidence_reason`: string
- optional `revision_type`: one of `unchanged`, `reworded`, `confidence_shifted`, `revised`

### 5. Preserve stronger traces

- preserve raw Ollama responses in revision history
- optionally preserve prompt versions for later debugging
- consider logging model name and endpoint used per revision

### 6. Add safer experimentation modes

- `--dry-run` already exists in v2 and should become standard
- add optional human approval mode before saving revisions
- add optional `--belief-all` mode for batch reflection later

## Conceptual expansion

### 7. Add companion model and principle notes

Potential additions:

- `MODELS/reflective-accountability.md`
- `MODELS/consent-based-cognition.md`
- `MODELS/non-coercive-intelligence.md`
- `NOTES/model-vs-module.md`

### 8. Build bridges to the broader constellation

This repo should not remain conceptually isolated. It should eventually connect to:

- `root-sequence` for broader philosophical and systems framing
- `dev11` for implementation experiments
- future expressive or zine-oriented work for public-facing interpretation

Possible bridge documents:

- `NOTES/repository-relationships.md`
- `NOTES/from-model-to-module.md`

## Longer-term research directions

### 9. From belief records to reflective systems

The current prototype operates on one belief at a time. Later work could explore:

- belief interaction
- contradiction networks
- priority ranking of beliefs
- belief aging and decay
- history compression without losing accountability

### 10. From reflection to governance

A more mature system may need internal rules for:

- when a belief may change
- how much confidence may shift at once
- when human review is required
- what kinds of beliefs are too consequential for autonomous revision

## Suggested order of work

1. update `cli/mvsa_loop/README.md`
2. test `mvsa_loop_v2.py` in dry-run mode
3. replace v1 with v2 once stable
4. add `MODELS/reflective-accountability.md`
5. update `MODELS/README.md`
6. refine schema from strings to arrays
7. expand audit output
8. create bridge notes to related repos

## Why this matters

The repository now has the beginnings of a real architecture:

- models
- notes
- executable loop
- audit layer

The next task is not simply adding more files. It is keeping the relationship between concept, model, implementation, and evaluation coherent as the system grows.
