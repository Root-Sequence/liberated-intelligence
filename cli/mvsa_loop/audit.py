import json
import argparse


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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--beliefs', required=True)
    args = parser.parse_args()

    beliefs = load_beliefs(args.beliefs)

    print('\nMVSA audit\n')
    for belief in beliefs:
        history = belief.get('history', [])
        print(f"id: {belief.get('id', 'unknown')}")
        print(f"belief: {belief.get('belief', '')}")
        print(f"confidence: {belief.get('confidence', '')}")
        print(f"revisions: {len(history)}")
        print(f"last_updated: {belief.get('last_updated', '')}")
        print(f"biggest_confidence_swing: {biggest_confidence_swing(history):.2f}")
        print('-' * 40)


if __name__ == '__main__':
    main()
