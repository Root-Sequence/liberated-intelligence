# MVSA Loop Prototype

A minimal prototype for testing the Minimum Viable Self-Aware System (MVSA) model in practice.

This prototype is intentionally small. It does not claim consciousness, personhood, or deep autonomy. Its purpose is narrower:

* preserve belief state
* inspect one belief at a time
* record contradictions and possible harms
* adjust confidence or wording deliberately
* append revision history rather than silently overwrite it

## Files

* `mvsa_loop.py` - the prototype loop
* `beliefs.example.json` - example belief store

## What it does

The loop:

1. loads a JSON belief store
2. selects one belief by id
3. reflects on that belief in one of several modes
4. proposes or records a revision
5. appends a revision record to history
6. writes the updated belief store back to disk

## Modes

### Manual mode

Manual mode asks the user to answer the reflection prompts directly.

Example:

```bash
python cli/mvsa_loop/mvsa_loop.py \
  --beliefs cli/mvsa_loop/beliefs.example.json \
  --belief-id belief-001
```

### Simulated mode

Simulated mode applies a small confidence adjustment and records a revision. This is useful for testing the file structure and logging behavior before integrating a language model.

Example:

```bash
python cli/mvsa_loop/mvsa_loop.py \
  --beliefs cli/mvsa_loop/beliefs.example.json \
  --belief-id belief-001 \
  --simulate
```

### Ollama mode

Ollama mode sends the selected belief record to a local model for structured reflection.

The model is asked to return valid JSON containing:

* `new_belief`
* `new_confidence`
* `reason`
* `evidence`
* `contradictions`
* `harm`

Example:

```bash
python cli/mvsa_loop/mvsa_loop.py \
  --beliefs cli/mvsa_loop/beliefs.example.json \
  --belief-id belief-001 \
  --ollama \
  --model llama3.2
```

Optional custom endpoint:

```bash
python cli/mvsa_loop/mvsa_loop.py \
  --beliefs cli/mvsa_loop/beliefs.example.json \
  --belief-id belief-001 \
  --ollama \
  --model llama3.2 \
  --ollama-url http://localhost:11434/api/generate
```

## Future directions

This prototype can later be extended to:

* store beliefs in SQLite instead of JSON
* score confidence drift over time
* add audit views for unstable beliefs
* compare supporting and contradictory evidence programmatically
* support dry-run review before saving revisions
* preserve raw model responses for auditability

## Invariant

No belief changes without explanation, evidence, and traceability.
