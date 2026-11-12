"""Render the longer pi explainer with Math-To-Manim's retained-scene renderer.

The ordinary film budget is 20-240 seconds. This episode has an explicit
280-420-second reading budget; everything else (source screening, the
credential-free worker, real render evidence) is the normal render-existing path.
"""
import argparse
import json
from pathlib import Path
import shutil

from astra.client import MODEL
from astra.local_render import render_existing
from astra.models import STAGES
from astra.render_worker import PROFILES
from astra.rendering import validate_source
from astra.runs import digest, runs_root, save

ROOT = Path(__file__).resolve().parents[1]
PLANNED_DURATION = (280, 420)
FRAME_QUANTIZATION_TOLERANCE = 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--authoring-run', type=Path,
                        help='Optional local authoring run; otherwise verify the retained production record')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--quality', choices=PROFILES, default='m')
    args = parser.parse_args()
    candidate, output = args.candidate.resolve(), args.output.resolve()
    authoring = args.authoring_run.resolve() if args.authoring_run else None
    runs = runs_root(ROOT)
    if candidate.parent != ROOT / 'papers/pi-approximations':
        raise ValueError('Expected the retained pi episode candidate')
    if (authoring is not None and authoring.parent != runs) or output.parent != runs:
        raise ValueError('Expected direct Astra run folders')
    if authoring is not None:
        original = json.loads((authoring / 'manifest.json').read_text(encoding='utf-8'))
        if original['status'] != 'completed':
            raise ValueError('Authoring must be completed before delivery')
        if candidate.read_bytes() != (authoring / 'scene.json').read_bytes():
            raise ValueError('Candidate must exactly match the completed authored scene')
        authoring_id = authoring.name
    else:
        original = json.loads((candidate.parent / 'production.json').read_text(encoding='utf-8'))
        if original.get('authoring_status') != 'completed' or original.get('candidate_sha256') != digest(candidate):
            raise ValueError('Candidate must match its completed retained authoring record')
        authoring_id = original['run_id']
    validate_source(json.loads(candidate.read_text(encoding='utf-8'))['content'])
    output.mkdir(parents=True, exist_ok=False)
    if authoring is not None:
        for name in [f'{stage}.json' for stage in STAGES] + ['request.json', 'operator-delivery-brief.json']:
            shutil.copy2(authoring / name, output / name)
    else:
        shutil.copy2(candidate, output / 'scene.json')
        shutil.copy2(candidate.parent / 'production.json', output / 'source-provenance.json')
    save(output / 'manifest.json', dict(status='queued', model=MODEL, evaluator='disabled',
        execution='math_to_manim_render_worker', review_status='not_reviewed',
        authoring_run_id=authoring_id, run_id=output.name,
        candidate=candidate.relative_to(ROOT).as_posix(), candidate_sha256=digest(candidate),
        planned_duration_range_seconds=list(PLANNED_DURATION),
        frame_quantization_tolerance_seconds=FRAME_QUANTIZATION_TOLERANCE, events=[]))
    low, high = PLANNED_DURATION
    ledger = render_existing(output, candidate, args.quality,
                             duration_range=(low, high + FRAME_QUANTIZATION_TOLERANCE),
                             reason='Cloud render of the retained pi-episode candidate; no model calls, no approval inferred.')
    print(json.dumps(ledger, indent=2))


if __name__ == '__main__':
    main()
