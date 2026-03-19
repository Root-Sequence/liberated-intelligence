import json
import argparse
import urllib.request
import urllib.error
from datetime import datetime, UTC


def load_beliefs(path):
    with open(path, 'r') as f:
        return json.load(f)


def save_beliefs(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def find_belief(beliefs, belief_id):
    for b in beliefs:
        if b['id'] == belief_id:
            return b
    return None


def now():
    return datetime.now(UTC).isoformat().replace('+00:00', 'Z')


def normalize_list(value):
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        value = value.strip()
        return [value] if value else []
    if value is None:
        return []
    return [str(value).strip()]


def manual_list_input(prompt):
    raw = input(prompt).strip()
    if not raw:
        return []
    return [item.strip() for item in raw.split(';') if item.strip()]


def manual_reflection(belief):
    print(f"\nCurrent belief: {belief['belief']}")
    print(f"Confidence: {belief['confidence']}\n")
    print("For list fields, separate items with semicolons.")

    new_belief = input("New belief (or press enter to keep): ") or belief['belief']
    new_conf = input("New confidence (0-1, or enter to keep): ")
    new_conf = float(new_conf) if new_conf else belief['confidence']

    reason = input("Reason for change: ").strip()
    evidence = manual_list_input("Evidence considered: ")
    contradictions = manual_list_input("Contradictions considered: ")
    harm = manual_list_input("Potential harms if wrong: ")

    return {
        "new_belief": new_belief,
        "new_confidence": new_conf,
        "reason": reason,
        "evidence": evidence,
        "contradictions": contradictions,
        "harm": harm,
    }


def simulated_reflection(belief):
    return {
        "new_belief": belief['belief'],
        "new_confidence": round(max(0, min(1, belief['confidence'] - 0.05)), 2),
        "reason": "Simulated uncertainty adjustment based on lack of new evidence.",
        "evidence": ["No new evidence supplied during simulated run."],
        "contradictions": ["Current belief may not hold in every context."],
        "harm": ["Uncertainty may be understated if confidence remains too high."],
    }


def build_prompt(belief):
    return f"""
You are performing reflective accountability on a belief record.

Return ONLY valid JSON with these keys:
new_belief
new_confidence
reason
evidence
contradictions
harm

Rules:
- new_confidence must be a number between 0 and 1
- If the belief should remain unchanged, repeat it exactly
- Be conservative
- reason must be a non-empty string
- evidence must be an array of strings
- contradictions must be an array of strings
- harm must be an array of strings
- Provide at least one evidence item
- Provide at least one harm item
- Provide at least one contradiction or uncertainty item
- If no direct contradiction exists, include a limitation, edge case, or uncertainty instead
- Only use evidence that is present in the belief record or directly inferable from it
- Do not invent broader user behavior, product goals, or contextual facts that are not present in the belief record
- If the belief record is sparse, keep confidence changes small
- Do not increase confidence by more than 0.05 unless the evidence list contains multiple concrete items from the belief record
- The reason must be consistent with the evidence, contradictions, and confidence
- Do not say the evidence does not support the belief if confidence stays the same or increases
- If evidence is weak or sparse, say that support is limited rather than absent
- If the belief remains unchanged, explain why it remains unchanged
- If confidence remains unchanged, explain why the available evidence is insufficient to justify a shift
- Do not change identifiers, belief references, or concrete targets unless the belief record provides direct support for that change
- If the belief mentions a specific belief id or revision, preserve that reference unless there is explicit evidence to revise it
- Do not generalize from one revision to multiple revisions unless the belief record explicitly contains multiple revisions
- Do not reuse example contradictions as actual contradictions unless they are directly supported by the belief record
- Keep each list item short, specific, and concrete
- Do not include markdown
- Do not include explanation outside JSON

Good examples of contradictions:
- "Preference may vary by topic"
- "Some users want longer exploratory responses in complex contexts"
- "Past behavior may not generalize to future requests"

Belief record:
{json.dumps(belief, indent=2)}
""".strip()


def ollama_reflection(belief, model, ollama_url):
    prompt = build_prompt(belief)

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
    }

    req = urllib.request.Request(
        ollama_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        raise RuntimeError(f"Ollama request failed: {e}") from e

    response_text = raw.get("response", "").strip()
    if not response_text:
        raise RuntimeError("Ollama returned an empty response")

    try:
        reflection = json.loads(response_text)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Ollama returned invalid JSON: {response_text}") from e

    required = {
        "new_belief",
        "new_confidence",
        "reason",
        "evidence",
        "contradictions",
        "harm",
    }
    missing = required - set(reflection.keys())
    if missing:
        raise RuntimeError(f"Ollama response missing keys: {sorted(missing)}")

    try:
        reflection["new_confidence"] = float(reflection["new_confidence"])
    except Exception as e:
        raise RuntimeError("new_confidence must be numeric") from e

    previous_confidence = float(belief.get("confidence", 0.0))
    reflection["new_confidence"] = max(0.0, min(1.0, reflection["new_confidence"]))
    if reflection["new_confidence"] > previous_confidence + 0.05:
        reflection["new_confidence"] = round(previous_confidence + 0.05, 2)

    reflection["reason"] = str(reflection.get("reason", "")).strip()
    reflection["evidence"] = normalize_list(reflection.get("evidence"))
    reflection["contradictions"] = normalize_list(reflection.get("contradictions"))
    reflection["harm"] = normalize_list(reflection.get("harm"))

    if not reflection["reason"]:
        raise RuntimeError("Ollama returned an empty reason")
    if not reflection["evidence"]:
        raise RuntimeError("Ollama returned no evidence items")
    if not reflection["harm"]:
        raise RuntimeError("Ollama returned no harm items")

    if not reflection["contradictions"]:
        reflection["contradictions"] = [
            "Past observations may not generalize to all future contexts."
        ]

    reason_lower = reflection["reason"].lower()
    if reflection["new_confidence"] >= previous_confidence and "do not support" in reason_lower:
        raise RuntimeError("Reason is inconsistent with unchanged or increased confidence")

    original_belief = belief.get("belief", "").strip()
    revised_belief = str(reflection.get("new_belief", "")).strip()
    if belief.get("id") == "belief-003":
        if "belief-001" in original_belief and "belief-001" not in revised_belief:
            raise RuntimeError("Reflection changed the belief target unexpectedly")
        if "only recorded revision" in original_belief.lower() and "multiple revisions" in reason_lower:
            raise RuntimeError("Reflection generalized from one revision to multiple revisions")

    reflection["raw_reflection"] = response_text
    return reflection


def apply_revision(belief, reflection):
    revision = {
        "timestamp": now(),
        "previous_belief": belief['belief'],
        "new_belief": reflection['new_belief'],
        "previous_confidence": belief['confidence'],
        "new_confidence": reflection['new_confidence'],
        "reason": reflection['reason'],
        "evidence": normalize_list(reflection['evidence']),
        "contradictions": normalize_list(reflection['contradictions']),
        "harm": normalize_list(reflection['harm']),
    }

    if 'raw_reflection' in reflection:
        revision['raw_reflection'] = reflection['raw_reflection']

    belief['history'].append(revision)
    belief['belief'] = reflection['new_belief']
    belief['confidence'] = reflection['new_confidence']
    belief['last_updated'] = now()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--beliefs', required=True)
    parser.add_argument('--belief-id', required=True)
    parser.add_argument('--simulate', action='store_true')
    parser.add_argument('--ollama', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--model', default='llama3.2')
    parser.add_argument('--ollama-url', default='http://localhost:11434/api/generate')

    args = parser.parse_args()

    beliefs = load_beliefs(args.beliefs)
    belief = find_belief(beliefs, args.belief_id)

    if not belief:
        print("Belief not found")
        return

    try:
        if args.ollama:
            reflection = ollama_reflection(
                belief,
                model=args.model,
                ollama_url=args.ollama_url,
            )
        elif args.simulate:
            reflection = simulated_reflection(belief)
        else:
            reflection = manual_reflection(belief)
    except Exception as e:
        print(f"Reflection failed: {e}")
        return

    if args.dry_run:
        preview = {
            "belief_id": belief["id"],
            "current_belief": belief["belief"],
            "current_confidence": belief["confidence"],
            "proposed_reflection": reflection,
        }
        print(json.dumps(preview, indent=2))
        return

    apply_revision(belief, reflection)
    save_beliefs(args.beliefs, beliefs)

    print("\nRevision applied and saved.")


if __name__ == '__main__':
    main()
