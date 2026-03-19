import json
import argparse


FALLBACK_UNCERTAINTY = "Past observations may not generalize to all future contexts."


def load_beliefs(path):
    with open(path, 'r') as f:
        return json.load(f)


def biggest_confidence_swing(history):
    if not history:
        return 0.0
    swings = []
    for item in history:
        try:
            prev_conf = float(item.get('previous_confidence', 0.0))
            new_conf = float(item.get('new_confidence', 0.0))
            swings.append(abs(new_conf - prev_conf))
        except (TypeError, ValueError):
            continue
    return max(swings) if swings else 0.0


def last_revision(history):
    return history[-1] if history else None


def last_confidence_delta(history):
    item = last_revision(history)
    if not item:
        return 0.0
    try:
        prev_conf = float(item.get('previous_confidence', 0.0))
        new_conf = float(item.get('new_confidence', 0.0))
        return round(new_conf - prev_conf, 2)
    except (TypeError, ValueError):
        return 0.0


def count_list_field(item, key):
    if not item:
        return 0
    value = item.get(key, [])
    if isinstance(value, list):
        return len(value)
    if isinstance(value, str):
        return 1 if value.strip() else 0
    return 0


def fallback_generated_contradictions(item):
    if not item:
        return False
    contradictions = item.get('contradictions', [])
    if not isinstance(contradictions, list):
        return False
    return contradictions == [FALLBACK_UNCERTAINTY]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--beliefs', required=True)
    args = parser.parse_args()

    beliefs = load_beliefs(args.beliefs)

    print('\nMVSA audit v2\n')
    for belief in beliefs:
        history = belief.get('history', [])
        last = last_revision(history)

        print(f"id: {belief.get('id', 'unknown')}")
        print(f"belief: {belief.get('belief', '')}")
        print(f"confidence: {belief.get('confidence', '')}")
        print(f"revisions: {len(history)}")
        print(f"last_updated: {belief.get('last_updated', '')}")
        print(f"biggest_confidence_swing: {biggest_confidence_swing(history):.2f}")
        print(f"last_confidence_delta: {last_confidence_delta(history):.2f}")
        print(f"last_evidence_count: {count_list_field(last, 'evidence')}")
        print(f"last_contradiction_count: {count_list_field(last, 'contradictions')}")
        print(f"last_harm_count: {count_list_field(last, 'harm')}")
        print(f"last_contradictions_fallback: {fallback_generated_contradictions(last)}")
        if last:
            print(f"last_reason: {last.get('reason', '')}")
        print('-' * 40)


if __name__ == '__main__':
    main()
