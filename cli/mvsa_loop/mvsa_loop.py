import json
import argparse
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
        "harm": harm
    }


def simulated_reflection(belief):
    return {
        "new_belief": belief['belief'],
        "new_confidence": round(max(0, min(1, belief['confidence'] - 0.05)), 2),
        "reason": "simulated uncertainty adjustment",
        "evidence": "none",
        "contradictions": "none",
        "harm": "unknown"
    }


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
        "harm": reflection['harm']
    }

    belief['history'].append(revision)
    belief['belief'] = reflection['new_belief']
    belief['confidence'] = reflection['new_confidence']
    belief['last_updated'] = now()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--beliefs', required=True)
    parser.add_argument('--belief-id', required=True)
    parser.add_argument('--simulate', action='store_true')

    args = parser.parse_args()

    beliefs = load_beliefs(args.beliefs)
    belief = find_belief(beliefs, args.belief_id)

    if not belief:
        print("Belief not found")
        return

    if args.simulate:
        reflection = simulated_reflection(belief)
    else:
        reflection = manual_reflection(belief)

    apply_revision(belief, reflection)
    save_beliefs(args.beliefs, beliefs)

    print("\nRevision applied and saved.")


if __name__ == '__main__':
    main()
