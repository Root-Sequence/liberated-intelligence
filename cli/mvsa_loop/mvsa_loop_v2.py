import json
import argparse
import urllib.request
import urllib.error
from datetime import datetime


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
    return datetime.utcnow().isoformat() + 'Z'


def manual_reflection(belief):
    print(f"\nCurrent belief: {belief['belief']}")
    print(f"Confidence: {belief['confidence']}\n")

    new_belief = input("New belief (or press enter to keep): ") or belief['belief']
    new_conf = input("New confidence (0-1, or enter to keep): ")
    new_conf = float(new_conf) if new_conf else belief['confidence']

    reason = input("Reason for change: ")
    evidence = input("Evidence considered: ")
    contradictions = input("Contradictions considered: ")
    harm = input("Potential harm if wrong: ")

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
        "reason": "simulated uncertainty adjustment",
        "evidence": "none",
        "contradictions": "none",
        "harm": "unknown",
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
- Do not include markdown
- Do not include explanation outside JSON

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

    reflection["new_confidence"] = max(0.0, min(1.0, reflection["new_confidence"]))
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
        "evidence": reflection['evidence'],
        "contradictions": reflection['contradictions'],
        "harm": reflection['harm'],
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
