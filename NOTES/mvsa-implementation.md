# MVSA implementation note

This note translates the Minimum Viable Self-Aware System (MVSA) model into practical components.

MVSA is not only a philosophical model. If taken seriously, it implies certain architectural requirements for any system that claims to revise itself in a trustworthy way.

## Purpose

The goal is not to simulate personhood or claim consciousness. The goal is narrower:

- preserve belief state
- track revision history
- compare confidence against evidence
- expose the reasons for meaningful change
- reduce silent drift

This note is a bridge between `MODELS/mvsa.md` and any future implementation in `cli/`, `core_modules/`, or elsewhere.

## Core objects

### 1. Belief record

A belief record is the minimum unit of reflective state.

Suggested fields:

- `id`
- `belief`
- `confidence`
- `source`
- `assumptions`
- `supporting_evidence`
- `contradictory_evidence`
- `possible_falsifiers`
- `possible_harms_if_wrong`
- `created_at`
- `last_updated`
- `history`

Example shape:

```json
{
  "id": "belief-001",
  "belief": "Users prefer concise structured responses",
  "confidence": 0.72,
  "source": "observed interaction pattern",
  "assumptions": ["past preferences remain stable"],
  "supporting_evidence": ["multiple requests for concise summaries"],
  "contradictory_evidence": [],
  "possible_falsifiers": ["user explicitly requests long exploratory writing"],
  "possible_harms_if_wrong": ["over-compression of nuance"],
  "created_at": "2026-03-18T00:00:00Z",
  "last_updated": "2026-03-18T00:00:00Z",
  "history": []
}
```

### 2. Revision record

A revision record preserves continuity.

Suggested fields:

- `timestamp`
- `previous_belief`
- `new_belief`
- `previous_confidence`
- `new_confidence`
- `reason_for_change`
- `evidence_used`
- `contradictions_considered`
- `harm_check`

## Minimal loop

A minimal MVSA loop could look like this:

1. Load current belief records.
2. Select one belief for reflection.
3. Ask what supports it.
4. Ask what contradicts it.
5. Ask what alternative interpretations exist.
6. Ask what harm could follow if it is wrong.
7. Adjust the belief or confidence if warranted.
8. Append a revision record.
9. Preserve the prior state.

Compressed form:

`load -> inspect -> test -> compare -> evaluate -> revise -> log`

## Minimal components

### Memory layer
A persistent store for beliefs and revision history.

Possible formats:

- JSON for simplicity
- SQLite for durability and querying
- Markdown logs for human-readable inspection

### Reflection layer
A prompt or routine that interrogates one belief at a time.

Example questions:

- What does this belief claim?
- Why is it currently held?
- What evidence supports it?
- What evidence weakens it?
- What alternatives exist?
- What harm could result from being wrong?
- Should the belief change, or only its confidence?

### Update layer
A controlled mechanism for changing belief records.

Rules:

- no silent overwrites
- no confidence increase without stated reason
- no revision without evidence, contradiction review, or explicit uncertainty
- every meaningful change creates a revision record

### Audit layer
A way to inspect the arc of changes over time.

This could include:

- change logs
- confidence drift checks
- contradiction frequency
- beliefs with repeated revision instability

## Minimal invariant

No belief changes without explanation, evidence, and traceability.

Implementation should enforce this as a system rule, not just a textual principle.

## Failure risks in implementation

### 1. Performative reflection
The system generates critique text but does not actually modify state or preserve history.

### 2. Confidence inflation
Confidence rises through repetition rather than stronger evidence.

### 3. Memory erosion
Older revisions are compressed away until continuity becomes mostly decorative.

### 4. Hidden updates
Beliefs are rewritten without preserving prior state.

### 5. False justification
The system produces plausible reasons for change after the fact rather than tracing the actual reason.

## Prototype directions

### Smallest possible prototype

- one JSON file of belief records
- one script that selects a belief
- one reflection prompt
- one append-only log for revisions

### Slightly more advanced prototype

- SQLite belief store
- scheduled reflection loop
- contradiction scoring
- confidence trend analysis
- human review mode

## Candidate locations in this repo

Depending on what gets built, future implementation work could live under:

- `cli/` for user-facing tools
- `core_modules/` for small experimental components
- `NOTES/` for architecture and design notes

## Why this note exists

The model describes a threshold. This note describes what it would take to approach that threshold in practice.

MVSA should not remain only a compelling idea. It should become testable.
