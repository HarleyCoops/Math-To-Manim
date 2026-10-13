"""Render the saved TOI-4342 scene with the Astra local renderer and zero model calls."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from astra.local_render import render_existing

SCENE = ROOT / "examples/astra/toi4342_third_rhythm.py"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-q", "--quality", choices=("l", "m", "h"), default="m")
    args = parser.parse_args()
    if not SCENE.is_file():
        parser.error(f"Saved scene is missing: {SCENE}")
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    folder = ROOT / "runs/astra" / f"{timestamp}-toi4342-local-{uuid.uuid4().hex[:6]}"
    folder.mkdir(parents=True)
    ledger = {
        "status": "ready_for_local_render",
        "author_model": "gpt-6-astra",
        "model_calls": 0,
        "review_status": "not_reviewed",
        "source": str(SCENE.relative_to(ROOT)),
        "events": [],
    }
    (folder / "manifest.json").write_text(json.dumps(ledger, indent=2), encoding="utf-8")
    result = render_existing(folder, SCENE, args.quality)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
